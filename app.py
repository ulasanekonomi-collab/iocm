import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matrix_engine import calculate_godelian_io

st.set_page_config(page_title="Simulasi I-O Gödelian", layout="wide")
st.title("📊 Dashboard Utama Simulator Input-Output Lingkungan & Pasar")
st.write("Pengembang : **Yuhka Sundaya** | *Mengelola Alam, Merencanakan Kesejahteraan*")
st.markdown("---")

# ==========================================
# SIDEBAR KONTROL INPUT (BREAKDOWN USER)
# ==========================================
st.sidebar.header("🌲 REZIM 1: DAYA DUKUNG LINGKUNGAN")
status_air = st.sidebar.selectbox("1. Status Air Wilayah", ["Aman", "Siaga", "Krisis"])
mapping_air = {"Aman": 1.0, "Siaga": 0.6, "Krisis": 0.2}

status_lahan = st.sidebar.selectbox("2. Rasio Tutupan Hijau (RTH)", ["> 30% (Ideal)", "10% - 30% (Terdegradasi)", "< 10% (Kritis)"])
mapping_lahan = {"> 30% (Ideal)": 1.0, "10% - 30% (Terdegradasi)": 0.6, "< 10% (Kritis)": 0.2}

aqi_input = st.sidebar.slider("3. Indeks Kualitas Udara (AQI) Real-time", min_value=0, max_value=300, value=50, step=10)
theta_udara_calc = 100.0 / aqi_input if aqi_input > 100 else 1.0

st.sidebar.header("🏪 REZIM 2: KAPASITAS MARKET")
harga_hulu = st.sidebar.selectbox("4. Tren Harga Bahan Baku (S1)", ["Stabil", "Fluktuatif", "Spekulatif/Kacau"])
utilisasi_mfg = st.sidebar.slider("5. Utilisasi Mesin Pabrik (S2) %", min_value=10, max_value=100, value=60, step=5)
kompetisi_jasa = st.sidebar.selectbox("6. Kepadatan Pasar Jasa (S3)", ["Rendah / Blue Ocean", "Padat / Kompetitif", "Perang Harga"])

st.sidebar.header("💰 TARGET OUTPUT MAKRO (X)")
X1 = st.sidebar.number_input("Output Sektor 1 (Alam)", value=100.0)
X2 = st.sidebar.number_input("Output Sektor 2 (Manufaktur)", value=150.0)
X3 = st.sidebar.number_input("Output Sektor 3 (Jasa)", value=180.0)
X_target = [X1, X2, X3]

# ==========================================
# RUNNING ENGINE COMPUTATION
# ==========================================
Z_prime, A, L, multipliers, error_mode, theta_nat_computed = calculate_godelian_io(
    mapping_air[status_air], mapping_lahan[status_lahan], theta_udara_calc,
    harga_hulu, utilisasi_mfg, kompetisi_jasa, X_target
)

# ==========================================
# DISPLAY PANEL UTAMA
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔄 Matriks Transaksi Ter-Relaksasi ($Z'$)")
    df_Z = pd.DataFrame(Z_prime, columns=["S1 (Alam)", "S2 (Manufaktur)", "S3 (Jasa)"], index=["S1 (Alam)", "S2 (Manufaktur)", "S3 (Jasa)"])
    st.dataframe(df_Z.style.format("{:.2f}"))
    
    st.subheader("📐 Matriks Koefisien Teknis Baru ($A'$)")
    df_A = pd.DataFrame(A, columns=["S1 (Alam)", "S2 (Manufaktur)", "S3 (Jasa)"], index=["S1 (Alam)", "S2 (Manufaktur)", "S3 (Jasa)"])
    st.dataframe(df_A.style.format("{:.4f}"))

with col2:
    st.subheader("🔮 Matriks Kebalikan Leontief Terkoreksi $(I - A')^{-1}$")
    if error_mode:
        st.error("🚨 **Paralisis Gödelian Terjadi!** Batas ekologis dan saturasi pasar saling mengunci. Struktur ekonomi kehilangan konsistensi logisnya untuk bisa tumbuh.")
    else:
        df_L = pd.DataFrame(L, columns=["S1 (Alam)", "S2 (Manufaktur)", "S3 (Jasa)"], index=["S1 (Alam)", "S2 (Manufaktur)", "S3 (Jasa)"])
        st.dataframe(df_L.style.format("{:.4f}"))

    st.subheader("📈 Analisis Daya Ungkit (Multiplier Output)")
    if not error_mode:
        df_mult = pd.DataFrame({"Sektor": ["S1 (Alam)", "S2 (Manufaktur)", "S3 (Jasa)"], "Multiplier": multipliers})
        fig, ax = plt.subplots(figsize=(6, 3.2))
        bars = ax.bar(df_mult["Sektor"], df_mult["Multiplier"], color=['#2ecc71', '#e74c3c', '#3498db'])
        ax.set_ylim(0, max(multipliers) * 1.2 if max(multipliers) > 0 else 3)
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05, f"{yval:.3f}", ha='center', va='bottom', fontweight='bold')
        st.pyplot(fig)
    else:
        st.warning("Grafik dimatikan karena sistem dalam status kelumpuhan struktural.")

# Narasi Kritik Akademik
st.subheader("🧠 Catatan Evaluasi Kebijakan (Kritik Logika)")
st.info(f"""
* **Indeks Komposit Kesehatan Alam ($\\theta_{{nat}}$):** {theta_nat_computed:.3f} 
* **Catatan Lapangan:** Jika indikator multiplier Sektor 2 membengkak tinggi saat kualitas udara buruk atau air kritis, secara visual menunjukkan**'Pertumbuhan Semu'** akibat pemborosan struktural. Sebaliknya, jika utilisasi pabrik diset terlalu tinggi (>85%) dan terjadi perang harga di sektor jasa, daya ungkit ekonomi akan runtuh, membuktikan batas saturasi pasar.
""")
