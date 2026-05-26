import numpy as np

def calculate_godelian_io(theta_air, theta_lahan, theta_udara, status_harga, utilisasi, kompetisi, X_target):
    # 1. Matriks Transaksi Dasar (Baseline Z)
    Z_base = np.array([
        [10.0, 40.0, 10.0],
        [20.0, 60.0, 30.0],
        [15.0, 25.0, 40.0]
    ])
    
    # 2. Hitung Nilai Campuran Rezim 1 (Daya Dukung Alam)
    # Rata-rata geometris dari Air, Lahan, dan Udara
    theta_nat = (theta_air * theta_lahan * theta_udara) ** (1/3)
    f_nat = 1.0 / theta_nat
    
    # 3. Hitung Nilai Sektoral Rezim 2 (Kapasitas Pasar)
    # Sektor 1: Stabilitas Harga Komoditas
    mapping_harga = {"Stabil": 1.0, "Fluktuatif": 0.75, "Spekulatif/Kacau": 0.50}
    theta_mkt_1 = mapping_harga.get(status_harga, 1.0)
    
    # Sektor 2: Utilisasi Pabrik Manufaktur (Formula Logistik)
    theta_mkt_2 = 1.0 - (utilisasi / 100.0) ** 2
    
    # Sektor 3: Kepadatan Kompetisi Jasa
    mapping_kompetisi = {"Rendah / Blue Ocean": 1.0, "Padat / Kompetitif": 0.70, "Perang Harga": 0.35}
    theta_mkt_3 = mapping_kompetisi.get(kompetisi, 1.0)
    
    # 4. Asimilasi Struktur Matriks Transaksi Baru (Z')
    Z_prime = np.zeros((3, 3))
    
    # Baris 1 (Alam) dipengaruhi pembengkakan biaya alam (f_nat) dan stabilitas harga hulu (theta_mkt_1)
    Z_prime[0, 0] = Z_base[0, 0] * f_nat * 0.9 * theta_mkt_1
    Z_prime[0, 1] = Z_base[0, 1] * f_nat * theta_mkt_2 * theta_mkt_1
    Z_prime[0, 2] = Z_base[0, 2] * f_nat * 1.0 * theta_mkt_1
    
    # Baris 2 (Manufaktur) & Baris 3 (Jasa) dipengaruhi kapasitas pasar kolom masing-masing
    Z_prime[1, 0] = Z_base[1, 0] * 0.9
    Z_prime[1, 1] = Z_base[1, 1] * theta_mkt_2
    Z_prime[1, 2] = Z_base[1, 2] * 1.0
    
    Z_prime[2, 0] = Z_base[2, 0] * 0.9
    Z_prime[2, 1] = Z_base[2, 1] * theta_mkt_2
    Z_prime[2, 2] = Z_base[2, 2] * theta_mkt_3
    
    # 5. Hitung Koefisien Teknis A = Z' / X
    A = Z_prime / X_target
    
    # 6. Hitung Invers Leontief (I - A)^-1 dengan Penanganan Error (Paralisis)
    I = np.eye(3)
    try:
        L = np.linalg.inv(I - A)
        # Jika nilai invers negatif atau tidak realistis akibat singularitas terselubung
        if np.any(L < 0):
            L = np.zeros((3, 3))
            error_mode = True
        else:
            error_mode = False
    except np.linalg.LinAlgError:
        L = np.zeros((3, 3))
        error_mode = True
        
    # 7. Hitung Multiplier Output
    multipliers = L.sum(axis=0) if not error_mode else np.array([0.0, 0.0, 0.0])
    
    return Z_prime, A, L, multipliers, error_mode, theta_nat
