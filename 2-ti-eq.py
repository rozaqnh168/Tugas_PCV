import cv2
import numpy as np
import math
import matplotlib.pyplot as plt

# ==========================================
# 1. TRANSFORMASI INTENSITAS (Looping Manual)
# ==========================================
def transformasi_manual_loop(img):
    tinggi, lebar = img.shape
    
    # Siapkan matriks kosong (berisi 0) dengan ukuran yang sama
    img_neg = np.zeros((tinggi, lebar), dtype=np.uint8)
    img_log = np.zeros((tinggi, lebar), dtype=np.uint8)
    img_gam04 = np.zeros((tinggi, lebar), dtype=np.uint8)
    img_gam25 = np.zeros((tinggi, lebar), dtype=np.uint8)
    
    # Konstanta untuk log
    c_log = 255 / math.log(256)
    
    # Looping baris (i) dan kolom (j) secara manual
    for i in range(tinggi):
        for j in range(lebar):
            r = float(img[i, j]) # Ambil nilai piksel (0-255) dan ubah ke float untuk perhitungan
            
            # a. Citra Negatif
            img_neg[i, j] = 255 - r
            
            # b. Transformasi Log
            val_log = c_log * math.log(1 + r)
            img_log[i, j] = min(max(int(round(val_log)), 0), 255) # Manual clipping
            
            # c. Gamma 0.4
            val_g04 = 255 * ((r / 255.0) ** 0.4)
            img_gam04[i, j] = min(max(int(round(val_g04)), 0), 255)
            
            # d. Gamma 2.5
            val_g25 = 255 * ((r / 255.0) ** 2.5)
            img_gam25[i, j] = min(max(int(round(val_g25)), 0), 255)
            
    return img_neg, img_log, img_gam04, img_gam25

# ==========================================
# 2 & 3. EKUALISASI HISTOGRAM (Looping Manual)
# ==========================================
def ekualisasi_manual_loop(img):
    tinggi, lebar = img.shape
    total_piksel = tinggi * lebar
    
    # --- Langkah 1: Hitung Histogram Manual ---
    # Buat list Python biasa berisi 0 sebanyak 256
    hist = [0] * 256 
    
    for i in range(tinggi):
        for j in range(lebar):
            nilai_piksel = img[i, j]
            hist[nilai_piksel] += 1
            
    # --- Langkah 2 & 3: Hitung PMF (Peluang) dan CDF Kumulatif ---
    cdf = [0.0] * 256
    jumlah_kumulatif = 0.0
    
    for k in range(256):
        peluang = hist[k] / total_piksel # PMF
        jumlah_kumulatif += peluang      # Ditambah terus secara kumulatif
        cdf[k] = jumlah_kumulatif        # Simpan CDF
        
    # --- Langkah 4: Hitung Nilai Pemetaan Piksel (Pembuatan LUT Manual) ---
    lut_eq = [0] * 256
    for k in range(256):
        lut_eq[k] = int(round(255 * cdf[k]))
        
    # --- Langkah 5: Ganti Piksel Lama ke Baru (Mapping Manual) ---
    img_eq = np.zeros((tinggi, lebar), dtype=np.uint8)
    for i in range(tinggi):
        for j in range(lebar):
            piksel_lama = img[i, j]
            img_eq[i, j] = lut_eq[piksel_lama] # Ganti dengan nilai baru dari LUT
            
    return img_eq, hist

# ==========================================
# EKSEKUSI PROGRAM
# ==========================================
if __name__ == "__main__":
    img = cv2.imread('gambar.jpg', 0)
    
    if img is None:
        print("Error: Gambar tidak ditemukan!")
        exit()

    print("Sedang memproses secara manual piksel demi piksel (ini akan memakan waktu beberapa detik)...")
    
    # Jalankan fungsi
    img_neg, img_log, img_gam04, img_gam25 = transformasi_manual_loop(img)
    img_eq, hist_manual = ekualisasi_manual_loop(img)
    
    print("Pemrosesan selesai. Menampilkan hasil...")
    
    # Plotting hasil
    plt.figure(figsize=(15, 8))
    
    plt.subplot(2, 3, 1), plt.imshow(img, cmap='gray'), plt.title('Original'), plt.axis('off')
    plt.subplot(2, 3, 2), plt.imshow(img_neg, cmap='gray'), plt.title('Negatif'), plt.axis('off')
    plt.subplot(2, 3, 3), plt.imshow(img_log, cmap='gray'), plt.title('Log'), plt.axis('off')
    plt.subplot(2, 3, 4), plt.imshow(img_gam04, cmap='gray'), plt.title('Gamma 0.4'), plt.axis('off')
    plt.subplot(2, 3, 5), plt.imshow(img_gam25, cmap='gray'), plt.title('Gamma 2.5'), plt.axis('off')
    plt.subplot(2, 3, 6), plt.imshow(img_eq, cmap='gray'), plt.title('Ekualisasi (Manual Loop)'), plt.axis('off')
    
    plt.tight_layout()
    plt.show()