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


def rgb_ke_cmyk(r, g, b):
    r_ = r / 255
    g_ = g / 255
    b_ = b / 255

    k = 1 - max(r_, g_, b_)
    if k == 1:
        c, m, y = 0, 0, 0
    else:
        c = (1 - r_ - k) / (1 - k)
        m = (1 - g_ - k) / (1 - k)
        y = (1 - b_ - k) / (1 - k)

    return c, m, y, k


def rgb_ke_hsi(r, g, b):
    r_ = r / 255
    g_ = g / 255
    b_ = b / 255

    jumlah = r_ + g_ + b_
    min_rgb = min(r_, g_, b_)
    intensitas = jumlah / 3

    if jumlah == 0:
        saturasi = 0
    else:
        saturasi = 1 - (3 / jumlah) * min_rgb

    if saturasi == 0:
        hue = 0
    else:
        pembilang = 0.5 * ((r_ - g_) + (r_ - b_))
        penyebut = math.sqrt(
            (r_ - g_) ** 2 + (r_ - b_) * (g_ - b_)
        )
        if penyebut == 0:
            hue = 0
        else:
            rasio = max(-1.0, min(1.0, pembilang / penyebut))
            theta = math.acos(rasio)
            if b_ <= g_:
                hue = theta
            else:
                hue = 2 * math.pi - theta

    hue = hue * 180 / math.pi
    return hue, saturasi * 100, intensitas * 255


def rgb_ke_hsv(r, g, b):
    r_ = r / 255
    g_ = g / 255
    b_ = b / 255

    max_rgb = max(r_, g_, b_)
    min_rgb = min(r_, g_, b_)
    selisih = max_rgb - min_rgb

    value = max_rgb
    saturasi = 0 if max_rgb == 0 else selisih / max_rgb

    if selisih == 0:
        hue = 0
    elif max_rgb == r_:
        hue = 60 * (((g_ - b_) / selisih) % 6)
    elif max_rgb == g_:
        hue = 60 * (((b_ - r_) / selisih) + 2)
    else:
        hue = 60 * (((r_ - g_) / selisih) + 4)

    return hue, saturasi * 100, value * 255


def nilai_byte(nilai):
    return max(0, min(255, int(round(nilai))))


def konversi_citra(img):
    tinggi, lebar = img.shape[:2]
    citra_cmyk = img.copy()
    citra_hsi = img.copy()
    citra_hsv = img.copy()

    for i in range(tinggi):
        for j in range(lebar):
            b, g, r = (int(v) for v in img[i, j])

            c, m, y, _ = rgb_ke_cmyk(r, g, b)
            citra_cmyk[i, j] = [
                nilai_byte(y * 255),
                nilai_byte(m * 255),
                nilai_byte(c * 255),
            ]

            h, s, intensity = rgb_ke_hsi(r, g, b)
            citra_hsi[i, j] = [
                nilai_byte(h / 360 * 255),
                nilai_byte(s / 100 * 255),
                nilai_byte(intensity),
            ]

            h, s, value = rgb_ke_hsv(r, g, b)
            citra_hsv[i, j] = [
                nilai_byte(h / 360 * 255),
                nilai_byte(s / 100 * 255),
                nilai_byte(value),
            ]

    return citra_cmyk, citra_hsi, citra_hsv


if __name__ == "__main__":
    img = cv2.imread("gambar.jpg", cv2.IMREAD_COLOR)

    if img is None:
        print("Gambar tidak ditemukan, pastikan file gambar.jpg ada di folder yang sama")
        raise SystemExit(1)

    cmyk, hsi, hsv = konversi_citra(img)
    tampilkan_hasil(
        "Hasil Model Warna",
        [
            ("Gambar Asli", img),
            ("CMYK", cmyk),
            ("HSI", hsi),
            ("HSV", hsv),
        ],
    )

    b, g, r = (int(v) for v in img[0, 0])
    print("Contoh pixel baris 0 kolom 0")
    print("R =", r, "G =", g, "B =", b)
    print("CMYK =", rgb_ke_cmyk(r, g, b))
    print("HSI  =", rgb_ke_hsi(r, g, b))
    print("HSV  =", rgb_ke_hsv(r, g, b))

    print("Tekan sembarang tombol untuk keluar")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
