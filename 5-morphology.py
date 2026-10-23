import cv2
import random
import tempfile
import os
import math
import numpy as np


def tampilkan_hasil(judul, hasil):
    if not hasil:
        raise ValueError("Daftar hasil visualisasi tidak boleh kosong")

    lebar_panel = 480
    tinggi_gambar = 300
    tinggi_judul = 42
    jumlah_kolom = min(3, math.ceil(math.sqrt(len(hasil))))
    jumlah_baris = math.ceil(len(hasil) / jumlah_kolom)
    panel_hasil = []

    for nama, citra in hasil:
        if citra.ndim == 2:
            citra = cv2.cvtColor(citra, cv2.COLOR_GRAY2BGR)

        tinggi, lebar = citra.shape[:2]
        skala = min(lebar_panel / lebar, tinggi_gambar / tinggi)
        ukuran = (max(1, round(lebar * skala)), max(1, round(tinggi * skala)))
        citra = cv2.resize(
            citra,
            ukuran,
            interpolation=cv2.INTER_AREA if skala < 1 else cv2.INTER_LINEAR,
        )

        panel = np.full(
            (tinggi_gambar + tinggi_judul, lebar_panel, 3),
            32,
            dtype=np.uint8,
        )
        y = tinggi_judul + (tinggi_gambar - citra.shape[0]) // 2
        x = (lebar_panel - citra.shape[1]) // 2
        panel[y:y + citra.shape[0], x:x + citra.shape[1]] = citra
        cv2.putText(
            panel,
            nama,
            (12, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        panel_hasil.append(panel)

    while len(panel_hasil) < jumlah_baris * jumlah_kolom:
        panel_hasil.append(
            np.full(
                (tinggi_gambar + tinggi_judul, lebar_panel, 3),
                32,
                dtype=np.uint8,
            )
        )

    baris = [
        cv2.hconcat(panel_hasil[i:i + jumlah_kolom])
        for i in range(0, len(panel_hasil), jumlah_kolom)
    ]
    kanvas = cv2.vconcat(baris)

    cv2.namedWindow(judul, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(judul, min(kanvas.shape[1], 1600), min(kanvas.shape[0], 1000))
    cv2.imshow(judul, kanvas)


def erosi(img, kernel):
    tinggi = len(img)
    lebar = len(img[0])
    tinggi_kernel = len(kernel)
    lebar_kernel = len(kernel[0])
    pad_y = tinggi_kernel // 2
    pad_x = lebar_kernel // 2
    hasil = [[0 for _ in range(lebar)] for _ in range(tinggi)]

    for i in range(tinggi):
        for j in range(lebar):
            semua_aktif = True
            for ki in range(tinggi_kernel):
                for kj in range(lebar_kernel):
                    if kernel[ki][kj] != 1:
                        continue
                    y = i + ki - pad_y
                    x = j + kj - pad_x
                    if y < 0 or y >= tinggi or x < 0 or x >= lebar:
                        semua_aktif = False
                    elif img[y][x] != 255:
                        semua_aktif = False
            if semua_aktif:
                hasil[i][j] = 255

    return hasil


def dilasi(img, kernel):
    tinggi = len(img)
    lebar = len(img[0])
    tinggi_kernel = len(kernel)
    lebar_kernel = len(kernel[0])
    pad_y = tinggi_kernel // 2
    pad_x = lebar_kernel // 2
    hasil = [[0 for _ in range(lebar)] for _ in range(tinggi)]

    for i in range(tinggi):
        for j in range(lebar):
            ada_aktif = False
            for ki in range(tinggi_kernel):
                for kj in range(lebar_kernel):
                    if kernel[ki][kj] != 1:
                        continue
                    y = i + ki - pad_y
                    x = j + kj - pad_x
                    if 0 <= y < tinggi and 0 <= x < lebar and img[y][x] == 255:
                        ada_aktif = True
            if ada_aktif:
                hasil[i][j] = 255

    return hasil


def opening(img, kernel):
    return dilasi(erosi(img, kernel), kernel)


def closing(img, kernel):
    return erosi(dilasi(img, kernel), kernel)


def buat_contoh_gambar():
    citra = [[0 for _ in range(300)] for _ in range(300)]

    for y in range(50, 120):
        for x in range(50, 120):
            citra[y][x] = 255

    for y in range(50, 120):
        for x in range(180, 250):
            citra[y][x] = 255

    for y in range(75, 95):
        for x in range(205, 225):
            citra[y][x] = 0

    for i in range(150, 280):
        for x in range(i - 100, i - 92):
            citra[i][x] = 255

    generator = random.Random(10)
    for _ in range(30):
        x = generator.randint(0, 299)
        y = generator.randint(0, 299)
        citra[y][x] = 255

    return citra


def matriks_ke_citra(matriks):
    tinggi = len(matriks)
    lebar = len(matriks[0])
    data = bytearray()
    for baris in matriks:
        for nilai in baris:
            data.append(max(0, min(255, int(nilai))))

    konten_pgm = bytearray(
        b"P5\n" + str(lebar).encode() + b" " + str(tinggi).encode() + b"\n255\n"
    )
    konten_pgm.extend(data)
    nama_file = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as file:
            nama_file = file.name
            file.write(konten_pgm)
        citra = cv2.imread(nama_file, cv2.IMREAD_GRAYSCALE)
        if citra is None:
            raise RuntimeError("Gagal mengubah matriks morfologi menjadi citra OpenCV")
        return citra
    finally:
        if nama_file is not None and os.path.exists(nama_file):
            os.remove(nama_file)


if __name__ == "__main__":
    img = buat_contoh_gambar()
    kernel = [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0],
    ]

    tampilkan_hasil(
        "Hasil Morfologi",
        [
            ("Citra Biner Awal", matriks_ke_citra(img)),
            ("Erosi", matriks_ke_citra(erosi(img, kernel))),
            ("Dilasi", matriks_ke_citra(dilasi(img, kernel))),
            ("Opening", matriks_ke_citra(opening(img, kernel))),
            ("Closing", matriks_ke_citra(closing(img, kernel))),
        ],
    )

    print("Tekan sembarang tombol untuk keluar")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
