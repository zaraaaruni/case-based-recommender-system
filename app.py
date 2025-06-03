import streamlit as st
import pandas as pd

# Konfigurasi halaman
st.set_page_config(
    page_title="Bandung Kuliner Explorer",
    page_icon="🍽️",
    layout="centered"
)

# Data kuliner Bandung
@st.cache_data
def load_kuliner_data():
    kuliner_data = {
        'nama': [
            'Warung Nasi Ampera', 'Bakso Malang Karapitan', 'Mie Ayam Tumini', 
            'Surabi Enhaii', 'Batagor Kingsley', 'Cuanki Serayu', 
            'Kedai Kopi Aroma', 'Lotek Mahmud', 'Siomay Bandung Ahan',
            'Martabak Mesir', 'Es Durian Runtuh', 'Cendol Elizabeth'
        ],
        'kategori': [
            'Makanan Berat', 'Makanan Berat', 'Makanan Berat',
            'Snack', 'Snack', 'Snack',
            'Minuman', 'Makanan Ringan', 'Makanan Ringan',
            'Dessert', 'Dessert', 'Dessert'
        ],
        'jenis': [
            'Nasi', 'Bakso', 'Mie',
            'Surabi', 'Batagor', 'Cuanki',
            'Kopi', 'Salad', 'Siomay',
            'Martabak', 'Es Buah', 'Minuman Tradisional'
        ],
        'harga': [25000, 15000, 12000, 8000, 20000, 10000, 25000, 8000, 12000, 35000, 15000, 10000],
        'rating': [4.4, 4.2, 4.1, 4.5, 4.6, 4.0, 4.1, 4.2, 4.4, 4.3, 4.2, 4.5],
        'lokasi': [
            'Kebon Kawung', 'Karapitan', 'Cihampelas', 'Riau', 'Kebon Kawung', 'Serayu',
            'Braga', 'Kebon Kawung', 'Kebon Kawung', 'Riau', 'Cihampelas', 'Riau'
        ],
        'jam_buka': [
            '08:00-22:00', '10:00-21:00', '09:00-20:00', '14:00-22:00', '10:00-21:00', '11:00-20:00',
            '07:00-23:00', '10:00-18:00', '08:00-19:00', '16:00-24:00', '12:00-22:00', '13:00-21:00'
        ],
        'deskripsi': [
            'Nasi dengan berbagai lauk khas Sunda yang lezat dan porsi mengenyangkan',
            'Bakso Malang autentik dengan kuah gurih dan isian lengkap',
            'Mie ayam legendaris dengan rasa yang tak terlupakan, favorit mahasiswa',
            'Surabi khas Bandung dengan berbagai topping manis dan gurih',
            'Batagor goreng renyah dengan bumbu kacang yang nikmat',
            'Cuanki hangat dengan isian tahu dan bakso, cocok untuk cuaca dingin',
            'Kopi specialty dengan suasana vintage dan harga terjangkau',
            'Salad tradisional dengan bumbu kacang pedas yang segar',
            'Siomay khas Bandung dengan bumbu kacang dan sambal yang pas',
            'Martabak manis dengan berbagai rasa dan topping melimpah',
            'Es durian segar dengan daging durian asli, surga bagi pecinta durian',
            'Cendol tradisional dengan santan dan gula merah yang autentik'
        ],
        'cocok_untuk': [
            'Makan siang, Makan malam', 'Makan siang, Nongkrong', 'Makan siang, Cepat saji',
            'Sore hari, Dessert', 'Cemilan, Makan ringan', 'Cemilan, Cuaca dingin',
            'Nongkrong, Kerja', 'Makan siang, Sehat', 'Cemilan, Makan ringan',
            'Malam hari, Dessert', 'Siang hari, Dessert', 'Sore hari, Minuman'
        ]
    }
    
    return pd.DataFrame(kuliner_data)

# Fungsi rekomendasi
def get_recommendations(df, kategori=None, max_harga=None, min_rating=None, lokasi=None):
    result = df.copy()
    
    # Filter berdasarkan kategori
    if kategori and kategori != "Semua":
        result = result[result['kategori'] == kategori]
    
    # Filter berdasarkan harga
    if max_harga:
        result = result[result['harga'] <= max_harga]
    
    # Filter berdasarkan rating
    if min_rating:
        result = result[result['rating'] >= min_rating]
    
    # Filter berdasarkan lokasi
    if lokasi and lokasi != "Semua":
        result = result[result['lokasi'] == lokasi]
    
    # Urutkan berdasarkan rating tertinggi
    result = result.sort_values('rating', ascending=False)
    
    return result

def main():
    # Header dengan styling
    st.markdown("""
    <div style='text-align: center; padding: 1rem; margin-bottom: 2rem;'>
        <h1>🍽️ Bandung Kuliner Explorer</h1>
        <p style='font-size: 1.2rem; color: #666;'>Temukan kuliner terbaik di Bandung untuk mahasiswa</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    kuliner_df = load_kuliner_data()
    
    # Filter Section
    st.markdown("### 🔍 Cari Kuliner Sesuai Selera")
    
    # Filter dalam kolom
    col1, col2 = st.columns(2)
    
    with col1:
        kategori = st.selectbox(
            "🍴 Kategori:",
            ["Semua"] + sorted(kuliner_df['kategori'].unique())
        )
        
        lokasi = st.selectbox(
            "📍 Lokasi:",
            ["Semua"] + sorted(kuliner_df['lokasi'].unique())
        )
    
    with col2:
        budget = st.slider(
            "💰 Budget maksimal (Rp):",
            min_value=5000,
            max_value=50000,
            value=25000,
            step=5000,
            format="Rp %d"
        )
        
        min_rating = st.slider(
            "⭐ Rating minimal:",
            min_value=1.0,
            max_value=5.0,
            value=4.0,
            step=0.1
        )
    
    # Tombol pencarian
    if st.button("🔍 Cari Kuliner", type="primary", use_container_width=True):
        recommendations = get_recommendations(kuliner_df, kategori, budget, min_rating, lokasi)
        
        st.markdown("---")
        
        if recommendations.empty:
            st.error("😅 Tidak ada kuliner yang sesuai dengan kriteria. Coba ubah filter!")
        else:
            st.success(f"🎉 Ditemukan {len(recommendations)} kuliner yang cocok untuk Anda!")
            
            # Tampilkan hasil
            for idx, row in recommendations.iterrows():
                with st.container():
                    # Header kuliner
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"## 🍽️ {row['nama']}")
                    
                    with col2:
                        # Rating dengan warna
                        if row['rating'] >= 4.5:
                            st.markdown(f"<h3 style='color: green;'>⭐ {row['rating']}/5</h3>", unsafe_allow_html=True)
                        elif row['rating'] >= 4.0:
                            st.markdown(f"<h3 style='color: orange;'>⭐ {row['rating']}/5</h3>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<h3 style='color: red;'>⭐ {row['rating']}/5</h3>", unsafe_allow_html=True)
                    
                    # Info utama
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**🏷️ Kategori:** {row['kategori']}")
                        st.markdown(f"**🍜 Jenis:** {row['jenis']}")
                    
                    with col2:
                        st.markdown(f"**💰 Harga:** Rp {row['harga']:,}")
                        st.markdown(f"**📍 Lokasi:** {row['lokasi']}")
                    
                    with col3:
                        st.markdown(f"**🕐 Jam Buka:** {row['jam_buka']}")
                        st.markdown(f"**👥 Cocok untuk:** {row['cocok_untuk']}")
                    
                    # Deskripsi
                    st.markdown(f"**📝 Deskripsi:** {row['deskripsi']}")
                    
                    # Badge harga
                    if row['harga'] <= 10000:
                        st.markdown("🟢 **Budget Friendly**")
                    elif row['harga'] <= 20000:
                        st.markdown("🟡 **Harga Sedang**")
                    else:
                        st.markdown("🟠 **Harga Premium**")
                    
                    st.markdown("---")
    
    # Quick Stats
    st.markdown("### 📊 Statistik Kuliner Bandung")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Kuliner", len(kuliner_df))
    
    with col2:
        st.metric("Rata-rata Rating", f"{kuliner_df['rating'].mean():.1f}/5")
    
    with col3:
        st.metric("Harga Rata-rata", f"Rp {kuliner_df['harga'].mean():.0f}")
    
    with col4:
        budget_friendly = len(kuliner_df[kuliner_df['harga'] <= 15000])
        st.metric("Budget Friendly", f"{budget_friendly}/{len(kuliner_df)}")
    
    # Rekomendasi cepat
    st.markdown("### 🔥 Rekomendasi Populer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**⭐ Rating Tertinggi:**")
        top_rated = kuliner_df.nlargest(3, 'rating')[['nama', 'rating', 'harga']]
        for _, row in top_rated.iterrows():
            st.markdown(f"• **{row['nama']}** - {row['rating']}/5 (Rp {row['harga']:,})")
    
    with col2:
        st.markdown("**💰 Paling Terjangkau:**")
        cheapest = kuliner_df.nsmallest(3, 'harga')[['nama', 'harga', 'rating']]
        for _, row in cheapest.iterrows():
            st.markdown(f"• **{row['nama']}** - Rp {row['harga']:,} ({row['rating']}/5)")
    
    # Data lengkap
    with st.expander("📋 Lihat Semua Data Kuliner"):
        st.dataframe(
            kuliner_df[['nama', 'kategori', 'harga', 'rating', 'lokasi', 'jam_buka']], 
            use_container_width=True,
            hide_index=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 10px; margin-top: 2rem;'>
        <h4 style='color: #495057; margin-bottom: 0.5rem;'>🎓 Khusus untuk Mahasiswa Bandung</h4>
        <p style='color: #6c757d; margin-bottom: 0;'>Temukan kuliner terbaik dengan budget terbatas!</p>
        <p style='color: #6c757d; font-size: 0.9rem;'>💡 Tips: Gunakan filter untuk menemukan kuliner sesuai budget dan selera Anda</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
