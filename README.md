# 📷 Pengolahan Citra dan Video (PCV)

Kumpulan tugas mata kuliah **Pengolahan Citra dan Video** — Departemen Teknik Komputer ITS.
Repo ini berisi implementasi dasar pengolahan citra menggunakan **Python**, **OpenCV**, **NumPy**, dan **Matplotlib**, mulai dari manipulasi kanal warna, transformasi intensitas, hingga ekualisasi histogram.

---

## 🧰 Teknologi yang Digunakan

| Teknologi | Fungsi |
|-----------|--------|
| ![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white) | Bahasa pemrograman utama |
| ![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?logo=opencv&logoColor=white) | Membaca, memproses, dan menampilkan citra/video |
| ![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white) | Operasi matriks/array citra |
| ![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?logo=matplotlib) | Visualisasi & perbandingan hasil |

---

## 📂 Struktur Repository

```
Tugas_PCV/
├── README.md                  → Dokumentasi repo (file ini)
├── 2-ti-eq.py                 → Tugas 2: Transformasi Intensitas & Ekualisasi Histogram
└── filter/
    ├── 1-Intro.py             → Tugas 1: Filter gambar & video webcam real-time
    └── gambar.jpg             → Citra contoh yang dipakai sebagai input
```

---

## 📝 Penjelasan Isi File & Folder

### `2-ti-eq.py` — Transformasi Intensitas & Ekualisasi Histogram
Program pengolah citra grayscale yang menghitung **setiap piksel secara manual (looping)** tanpa fungsi bawaan OpenCV. Menghasilkan 5 variasi citra:

1. **Citra Negatif** — `s = 255 - r`, membalik nilai intensitas piksel.
2. **Transformasi Log** — `s = c · log(1 + r)`, mencerahkan area gelap.
3. **Gamma 0.4** — `s = 255 · (r/255)^0.4`, menaikkan kecerahan (under-exposed look).
4. **Gamma 2.5** — `s = 255 · (r/255)^2.5`, menurunkan kecerahan.
5. **Ekualisasi Histogram Manual** — dihitung 5 langkah:
   - Histogram manual (hitung frekuensi tiap nilai piksel 0–255)
   - PMF (peluang tiap nilai)
   - CDF (peluang kumulatif)
   - LUT (tabel pemetaan `round(255 · cdf)`)
   - Mapping piksel lama → nilai baru

Hasilnya ditampilkan berdampingan dalam satu figure Matplotlib.

### `filter/` — Folder Tugas 1
Berisi materi pengenalan OpenCV dan aset gambarnya:

- **`1-Intro.py`** — Berisi dua bagian:
  - **Filter Gambar** *(dikomentari sebagai docstring)*: mengakses piksel satu per satu dan meng-nol-kan lapisan Green dan Blue (`gambar[i,j,1]=0` dan `gambar[i,j,0]=0`) sehingga hanya kanal **Red** yang tampil.
  - **Video Webcam**: membuka kamera (`cv2.VideoCapture(0)`), memberi filter kanal merah pada setiap frame secara real-time, lalu menampilkan jendela video. Tekan `ESC` atau tutup jendela untuk berhenti.
- **`gambar.jpg`** — Citra input contoh untuk diolah.

---

## 🚀 Cara Menjalankan

1. **Install dependensi**

   ```bash
   pip install opencv-python numpy matplotlib
   ```

2. **Jalankan program**

   ```bash
   # Tugas 2 — pastikan gambar.jpg berada di folder yang sama
   # saat program dijalankan (mis. jalankan dari dalam folder filter/)
   python 2-ti-eq.py

   # Tugas 1 — filter video webcam (butuh akses kamera)
   cd filter
   python 1-Intro.py
   ```

---

## ✨ Ide Pengembangan

- [ ] Vektorisasi dengan NumPy agar pemrosesan lebih cepat
- [ ] Filter warna lain (hijau, biru, grayscale) pada video webcam
- [ ] Menambahkan operasi morfologi & konvolusi (filter rata-rata, Sobel)
- [ ] GUI interaktif dengan slider (trackbar OpenCV)

---

<p align="center">Dibuat dengan ☕ dan OpenCV untuk Tugas PCV</p>
