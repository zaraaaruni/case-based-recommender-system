import streamlit as st
import pandas as pd
import random
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import numpy as np

# Page config
st.set_page_config(
    page_title="Kuliner Bandung",
    page_icon="🍽",
    layout="wide"
)

# Load kuliner data
@st.cache_data
def load_data(url):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

sheet_url = "https://docs.google.com/spreadsheets/d/1TT-gGa8cZ7AWQTCxW8STkJdia7pJbvUO6It2_3QyxQY/edit?usp=sharing"
csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=csv")

def preprocess_data(df):
    df_processed = pd.get_dummies(df, columns=['kategori', 'lokasi'])
    scaler = MinMaxScaler()
    df_processed['harga_norm'] = scaler.fit_transform(df_processed[['harga']])
    harga_min, harga_max = df['harga'].min(), df['harga'].max()

    scaler_rating = MinMaxScaler()
    df_processed['rating_norm'] = scaler_rating.fit_transform(df_processed[['rating']])
    rating_min, rating_max = df['rating'].min(), df['rating'].max()

    df_processed = df_processed.drop(columns=['nama', 'harga', 'rating', 'jam_buka'], errors='ignore')

    # return min, max harga & rating buat scaling manual user input nanti
    return df_processed, harga_min, harga_max, rating_min, rating_max


def calculate_similarity(df_processed, user_prefs, harga_min, harga_max, rating_min, rating_max):
    user_vector = pd.Series(0, index=df_processed.columns)

    if 'kategori' in user_prefs:
        for kategori in user_prefs['kategori']:
            col_name = f'kategori_{kategori}'
            if col_name in df_processed.columns:
                user_vector[col_name] = 1

    if 'lokasi' in user_prefs:
        for lokasi in user_prefs['lokasi']:
            col_name = f'lokasi_{lokasi}'
            if col_name in df_processed.columns:
                user_vector[col_name] = 1

    if 'max_price' in user_prefs:
        max_price_norm = (user_prefs['max_price'] - harga_min) / (harga_max - harga_min)
        user_vector['harga_norm'] = 1 - max_price_norm

    if 'min_rating' in user_prefs:
        min_rating_norm = (user_prefs['min_rating'] - rating_min) / (rating_max - rating_min)
        user_vector['rating_norm'] = min_rating_norm

    feature_cols = [col for col in df_processed.columns
                    if col.startswith('kategori_') or col.startswith('lokasi_')
                    or col in ['harga_norm', 'rating_norm']]

    X = df_processed[feature_cols].values
    user_vec = user_vector[feature_cols].values.reshape(1, -1)

    similarity_scores = cosine_similarity(X, user_vec).flatten()
    similarity_scores = (similarity_scores + 1) / 2

    return similarity_scores


def get_recommendations(user_prefs, df, n=5):
    df_processed, harga_min, harga_max, rating_min, rating_max = preprocess_data(df)
    similarities = calculate_similarity(df_processed, user_prefs, harga_min, harga_max, rating_min, rating_max)
    df['similarity'] = similarities

    filtered = df.copy()
    if 'kategori' in user_prefs and user_prefs['kategori'] != ["Semua"]:
        filtered = filtered[filtered['kategori'].isin(user_prefs['kategori'])]
    if 'max_price' in user_prefs and user_prefs['max_price']:
        filtered = filtered[filtered['harga'] <= user_prefs['max_price']]  # Ini hard filter harga
    if 'min_rating' in user_prefs and user_prefs['min_rating']:
        filtered = filtered[filtered['rating'] >= user_prefs['min_rating']]
    if 'lokasi' in user_prefs and user_prefs['lokasi'] != ["Semua"]:
        filtered = filtered[filtered['lokasi'].isin(user_prefs['lokasi'])]

    # Ambil similarity di filtered saja
    filtered['similarity'] = df.loc[filtered.index, 'similarity']

    # Baru ambil top-N
    return filtered.nlargest(n, 'similarity')



def filter_data(df, category, max_price, min_rating, location):
    result = df.copy()
    if category != "Semua":
        result = result[result['kategori'] == category]
    if max_price:
        result = result[result['harga'] <= max_price]
    if min_rating:
        result = result[result['rating'] >= min_rating]
    if location != "Semua":
        result = result[result['lokasi'] == location]
    return result.sort_values('rating', ascending=False)

def main():
    st.title("🍽 Kuliner Bandung untuk Mahasiswa")
    st.write("Cari makanan enak dengan budget pas-pasan!")

    df = load_data(csv_url)

    st.sidebar.header("Filter Kuliner")
    category = st.sidebar.selectbox("Kategori", ["Semua"] + list(df['kategori'].unique()))
    location = st.sidebar.selectbox("Lokasi", ["Semua"] + sorted(df['lokasi'].unique()))
    max_price = st.sidebar.slider("Budget maksimal (Rp)", 5000, 50000, 25000, 2500)
    min_rating = st.sidebar.slider("Rating minimal", 3.0, 5.0, 4.0, 0.1)

    user_prefs = {
        'kategori': [category] if category != "Semua" else df['kategori'].unique().tolist(),
        'lokasi': [location] if location != "Semua" else df['lokasi'].unique().tolist(),
        'max_price': max_price,
        'min_rating': min_rating
    }

    recommendations = get_recommendations(user_prefs, df, n=5)
    filtered = filter_data(df, category, max_price, min_rating, location)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Kuliner", len(df))
    with col2:
        st.metric("Hasil Filter", len(filtered))
    with col3:
        avg_price = filtered['harga'].mean() if len(filtered) > 0 else 0
        st.metric("Rata-rata Harga", f"Rp {avg_price:,.0f}")

    st.write("---")
    st.subheader("🔥 Rekomendasi Untuk Anda")
    if len(recommendations) > 0:
        cols = st.columns(min(3, len(recommendations)))
        for idx, (_, row) in enumerate(recommendations.iterrows()):
            with cols[idx % len(cols)]:
                with st.container():
                    st.subheader(row['nama'])
                    st.write(f"{row['kategori']}** • {row['lokasi']}")
                    st.write(f"💰 Rp {row['harga']:,}")
                    st.write(f"⭐ {row['rating']}/5")
                    st.write(f"🕐 {row['jam_buka']}")
                    st.write(f"🔍 Kemiripan: {row['similarity']*100:.1f}%")
                    if row['harga'] <= 15000:
                        st.success("💚 Hemat")
                    elif row['harga'] <= 30000:
                        st.info("💙 Sedang")
                    else:
                        st.warning("💛 Mahal")
    else:
        st.warning("Tidak ada rekomendasi yang sesuai.")


    st.write("---")
    if len(filtered) == 0:
        st.warning("Tidak ada kuliner yang sesuai filter.")
    else:
        st.write(f"Menampilkan {len(filtered)} kuliner:")

        items_per_page = 10
        total_items = len(filtered)
        total_pages = (total_items - 1) // items_per_page + 1

        if 'page' not in st.session_state:
            st.session_state.page = 1

        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Sebelumnya") and st.session_state.page > 1:
                st.session_state.page -= 1
        with col3:
            if st.button("➡️ Selanjutnya") and st.session_state.page < total_pages:
                st.session_state.page += 1

        st.write(f"Halaman {st.session_state.page} dari {total_pages}")
        start_idx = (st.session_state.page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)

        for i in range(start_idx, end_idx, 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                idx = i + j
                if idx < end_idx:
                    row = filtered.iloc[idx]
                    with col:
                        with st.container():
                            st.subheader(row['nama'])
                            st.write(f"{row['kategori']}** • {row['lokasi']}")
                            st.write(f"💰 Rp {row['harga']:,}")
                            st.write(f"⭐ {row['rating']}/5")
                            st.write(f"🕐 {row['jam_buka']}")
                            if row['harga'] <= 15000:
                                st.success("💚 Hemat")
                            elif row['harga'] <= 30000:
                                st.info("💙 Sedang")
                            else:
                                st.warning("💛 Mahal")
                        st.write("")

    st.write("---")
    st.subheader("Rekomendasi Populer")
    col1, col2 = st.columns(2)
    with col1:
        st.write("*Rating Tertinggi:*")
        top_rated = df.nlargest(5, 'rating')
        for _, row in top_rated.iterrows():
            st.write(f"• {row['nama']} ({row['rating']}⭐)")
    with col2:
        st.write("*Paling Murah:*")
        cheapest = df.nsmallest(5, 'harga')
        for _, row in cheapest.iterrows():
            st.write(f"• {row['nama']} (Rp {row['harga']:,})")

    if st.checkbox("Tampilkan semua data"):
        st.dataframe(df, use_container_width=True)

    st.write("---")
    st.write("💡 *Tips:* Gunakan filter di sidebar untuk rekomendasi yang lebih personal!")

if __name__ == "__main__":
    main()
