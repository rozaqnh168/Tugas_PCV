import cv2
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


def konvolusi(img, kernel):
    tinggi, lebar = img.shape
    ukuran_kernel = len(kernel)
    pad = ukuran_kernel // 2
    hasil = [[0.0 for _ in range(lebar)] for _ in range(tinggi)]

    for i in range(tinggi):
        for j in range(lebar):
            jumlah = 0.0
            for ki in range(ukuran_kernel):
                for kj in range(ukuran_kernel):
                    y = max(0, min(tinggi - 1, i + ki - pad))
                    x = max(0, min(lebar - 1, j + kj - pad))
                    jumlah += int(img[y, x]) * kernel[ki][kj]
            hasil[i][j] = jumlah

    return hasil


def ke_citra_uint8(img, hasil):
    citra = img.copy()
    for i in range(len(hasil)):
        for j in range(len(hasil[i])):
            nilai = max(0, min(255, int(hasil[i][j])))
            citra[i, j] = nilai
    return citra


def filter_mean(img, ukuran=3):
    nilai_kernel = 1.0 / (ukuran * ukuran)
    kernel = [[nilai_kernel for _ in range(ukuran)] for _ in range(ukuran)]
    return ke_citra_uint8(img, konvolusi(img, kernel))


def filter_gaussian(img, ukuran=3, sigma=1):
    tengah = ukuran // 2
    kernel = [[0.0 for _ in range(ukuran)] for _ in range(ukuran)]
    jumlah_kernel = 0.0

    for i in range(ukuran):
        for j in range(ukuran):
            x = i - tengah
            y = j - tengah
            nilai = math.exp(-(x ** 2 + y ** 2) / (2 * sigma ** 2))
            kernel[i][j] = nilai
            jumlah_kernel += nilai

    for i in range(ukuran):
        for j in range(ukuran):
            kernel[i][j] /= jumlah_kernel

    return ke_citra_uint8(img, konvolusi(img, kernel))


def filter_median(img, ukuran=3):
    pad = ukuran // 2
    tinggi, lebar = img.shape
    hasil = img.copy()

    for i in range(tinggi):
        for j in range(lebar):
            nilai = []
            for ki in range(ukuran):
                for kj in range(ukuran):
                    y = max(0, min(tinggi - 1, i + ki - pad))
                    x = max(0, min(lebar - 1, j + kj - pad))
                    nilai.append(int(img[y, x]))
            nilai.sort()
            hasil[i, j] = nilai[len(nilai) // 2]

    return hasil


def filter_sharpening(img):
    kernel = [
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0],
    ]
    return ke_citra_uint8(img, konvolusi(img, kernel))


def filter_sobel(img):
    kernel_x = [
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1],
    ]
    kernel_y = [
        [-1, -2, -1],
        [0, 0, 0],
        [1, 2, 1],
    ]

    gx = konvolusi(img, kernel_x)
    gy = konvolusi(img, kernel_y)
    hasil = [[0.0 for _ in range(len(gx[0]))] for _ in range(len(gx))]

    for i in range(len(gx)):
        for j in range(len(gx[i])):
            hasil[i][j] = math.sqrt(gx[i][j] ** 2 + gy[i][j] ** 2)

    return ke_citra_uint8(img, hasil)


if __name__ == "__main__":
    img = cv2.imread("gambar.jpg", cv2.IMREAD_GRAYSCALE)

    if img is None:
        print("Gambar tidak ditemukan, pastikan file gambar.jpg ada di folder yang sama")
        raise SystemExit(1)

    tampilkan_hasil(
        "Hasil Filter Spasial",
        [
            ("Gambar Asli", img),
            ("Filter Mean 3x3", filter_mean(img)),
            ("Filter Mean 5x5", filter_mean(img, 5)),
            ("Filter Gaussian", filter_gaussian(img)),
            ("Filter Median", filter_median(img)),
            ("Sharpening", filter_sharpening(img)),
            ("Deteksi Tepi Sobel", filter_sobel(img)),
        ],
    )

    print("Tekan sembarang tombol untuk keluar")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
