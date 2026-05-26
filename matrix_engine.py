import numpy as np

def calculate_godelian_io(theta_air, theta_lahan, theta_udara, status_harga, utilisasi, kompetisi, X_target):
    # --- [Blok 1 - 4: Masih sama dengan kode sebelumnya] ---
    Z_base = np.array([
        [10.0, 40.0, 10.0],
        [20.0, 60.0, 30.0],
        [15.0, 25.0, 40.0]
    ])
    
    theta_nat = (theta_air * theta_lahan * theta_udara) ** (1/3)
    f_nat = 1.0 / theta_nat
    
    mapping_harga = {"Stabil": 1.0, "Fluktuatif": 0.75, "Spekulatif/Kacau": 0.50}
    theta_mkt_1 = mapping_harga.get(status_harga, 1.0)
    theta_mkt_2 = 1.0 - (utilisasi / 100.0) ** 2
    
    mapping_kompetisi = {"Rendah / Blue Ocean": 1.0, "Padat / Kompetitif": 0.70, "Perang Harga": 0.35}
    theta_mkt_3 = mapping_kompetisi.get(kompetisi, 1.0)
    
    Z_prime = np.zeros((3, 3))
    Z_prime[0, 0] = Z_base[0, 0] * f_nat * 0.9 * theta_mkt_1
    Z_prime[0, 1] = Z_base[0, 1] * f_nat * theta_mkt_2 * theta_mkt_1
    Z_prime[0, 2] = Z_base[0, 2] * f_nat * 1.0 * theta_mkt_1
    Z_prime[1, 0] = Z_base[1, 0] * 0.9
    Z_prime[1, 1] = Z_base[1, 1] * theta_mkt_2
    Z_prime[1, 2] = Z_base[1, 2] * 1.0
    Z_prime[2, 0] = Z_base[2, 0] * 0.9
    Z_prime[2, 1] = Z_base[2, 1] * theta_mkt_2
    Z_prime[2, 2] = Z_base[2, 2] * theta_mkt_3
    
    X = np.array(X_target)
    A = Z_prime / X
    
    I = np.eye(3)
    try:
        L = np.linalg.inv(I - A)
        error_mode = np.any(L < 0) or np.any(np.isnan(L))
    except np.linalg.LinAlgError:
        L = np.zeros((3, 3))
        error_mode = True
        
    multipliers = L.sum(axis=0) if not error_mode else np.array([0.0, 0.0, 0.0])
    
    # =========================================================
    # KODE BARU: EKSTENSION INDIKATOR MAKRO TER-RELAKSASI
    # =========================================================
    macro_indicators = {}
    
    if not error_mode:
        # 1. Koefisien Dasar Normal (per unit output)
        # [S1_Alam, S2_Manufaktur, S3_Jasa]
        c_pajak = np.array([0.05, 0.12, 0.08])
        c_upah = np.array([0.20, 0.25, 0.40])
        c_tenaga_kerja = np.array([0.15, 0.10, 0.25])  # Orang per 100jt output
        c_subsidi_base = np.array([0.08, 0.04, 0.02])
        
        # 2. Distorsi Parameter Rezim terhadap Koefisien Makro
        # Perang harga di Sektor 3 memotong margin pajak riil
        c_pajak_distorted = c_pajak * np.array([1.0, 1.0, theta_mkt_3])
        
        # Kompetisi ekstrem memaksa efisiensi upah buruh di manufaktur & jasa
        c_upah_distorted = c_upah * np.array([1.0, theta_mkt_2, theta_mkt_3])
        
        # Kelumpuhan alam (Rezim 1) menghambat penyerapan tenaga kerja fisik di hulu
        c_tk_distorted = c_tenaga_kerja * np.array([theta_nat, 1.0, 1.0])
        
        # 3. Kalkulasi Nilai Capaian Makro Sektoral (Koefisien x Output Aktual)
        pajak_sektoral = c_pajak_distorted * X
        pendapatan_rt = c_upah_distorted * X
        tenaga_kerja = c_tk_distorted * X
        
        # Kasus Subsidi Mubazir: Semakin jenuh pasar S2, subsidi yang terserap malah naik tapi tidak efisien
        subsidi_sektoral = (c_subsidi_base * (1.5 - theta_mkt_2)) * X
        
        # Pertumbuhan Ekonomi / PDB (Nilai Tambah Bruto total)
        # Di bawah Rezim 1, komponen PDB S1 "seolah naik" karena pembengkakan biaya ekstraksi
        v_base = np.array([0.45, 0.35, 0.45])
        v_distorted = v_base * np.array([f_nat, 1.0, 1.0])
        pdb_sektoral = v_distorted * X
        
        # Agregasi Total Komoditas Makro
        macro_indicators = {
            "PDB Total": np.sum(pdb_sektoral),
            "Pendapatan Rumah Tangga": np.sum(pendapatan_rt),
            "Penerimaan Pajak": np.sum(pajak_sektoral),
            "Subsidi Digelontorkan": np.sum(subsidi_sektoral),
            "Penyerapan Tenaga Kerja": np.sum(tenaga_kerja)
        }
    else:
        macro_indicators = {
            "PDB Total": 0.0, "Pendapatan Rumah Tangga": 0.0, "Penerimaan Pajak": 0.0,
            "Subsidi Digelontorkan": 0.0, "Penyerapan Tenaga Kerja": 0.0
        }
        
    return Z_prime, A, L, multipliers, error_mode, theta_nat, macro_indicators
