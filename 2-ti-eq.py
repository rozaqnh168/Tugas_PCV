import cv2
import math


def jumlah_kanal(img):
    return 1 if len(img.shape) == 2 else img.shape[2]


def ambil_nilai(img, i, j, k, kanal):
    return img[i, j] if kanal == 1 else img[i, j, k]


def simpan_nilai(img, i, j, k, kanal, nilai):
    if kanal == 1:
        img[i, j] = nilai
    else:
        img[i, j, k] = nilai


def ubah_ke_abu_abu(img):
    if len(img.shape) == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def buat_panel(judul, citra, ukuran=(320, 240)):
    if len(citra.shape) == 2:
        citra = cv2.cvtColor(citra, cv2.COLOR_GRAY2BGR)

    panel = cv2.resize(citra, ukuran)
    panel = cv2.copyMakeBorder(
        panel, 32, 0, 0, 0, cv2.BORDER_CONSTANT, value=(45, 45, 45)
    )
    cv2.putText(
        panel,
        judul,
        (10, 23),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )
    return panel


def negative(img):
    hasil = img.copy()
    tinggi, lebar = img.shape[:2]
    kanal = jumlah_kanal(img)

    for i in range(tinggi):
        for j in range(lebar):
            for k in range(kanal):
                nilai = 255 - ambil_nilai(img, i, j, k, kanal)
                simpan_nilai(hasil, i, j, k, kanal, nilai)

    return hasil


def log_transform(img, c=1):
    hasil = img.copy()
    tinggi, lebar = img.shape[:2]
    kanal = jumlah_kanal(img)
    nilai_maksimum = 0

    for i in range(tinggi):
        for j in range(lebar):
            for k in range(kanal):
                nilai_pixel = int(ambil_nilai(img, i, j, k, kanal))
                nilai = c * math.log(1 + nilai_pixel)
                if nilai > nilai_maksimum:
                    nilai_maksimum = nilai

    for i in range(tinggi):
        for j in range(lebar):
            for k in range(kanal):
                nilai_pixel = int(ambil_nilai(img, i, j, k, kanal))
                nilai = c * math.log(1 + nilai_pixel)
                if nilai_maksimum > 0:
                    nilai = int(nilai / nilai_maksimum * 255)
                else:
                    nilai = 0
                simpan_nilai(hasil, i, j, k, kanal, nilai)

    return hasil


def gamma_correction(img, gamma, c=1):
    hasil = img.copy()
    tinggi, lebar = img.shape[:2]
    kanal = jumlah_kanal(img)

    for i in range(tinggi):
        for j in range(lebar):
            for k in range(kanal):
                nilai = ambil_nilai(img, i, j, k, kanal) / 255.0
                nilai = c * math.pow(nilai, gamma) * 255
                nilai = max(0, min(255, int(nilai)))
                simpan_nilai(hasil, i, j, k, kanal, nilai)

    return hasil


def contrast_stretching(img):
    hasil = img.copy()
    tinggi, lebar = img.shape[:2]
    kanal = jumlah_kanal(img)
    r_min = 255
    r_max = 0

    for i in range(tinggi):
        for j in range(lebar):
            for k in range(kanal):
                nilai = ambil_nilai(img, i, j, k, kanal)
                r_min = min(r_min, nilai)
                r_max = max(r_max, nilai)

    for i in range(tinggi):
        for j in range(lebar):
            for k in range(kanal):
                nilai = ambil_nilai(img, i, j, k, kanal)
                if r_max == r_min:
                    hasil_nilai = 0
                else:
                    hasil_nilai = int((nilai - r_min) / (r_max - r_min) * 255)
                simpan_nilai(hasil, i, j, k, kanal, hasil_nilai)

    return hasil


def histogram(img):
    img = ubah_ke_abu_abu(img)

    hist = [0] * 256
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            hist[img[i, j]] += 1

    return hist


def equalize_histogram(img):
    img = ubah_ke_abu_abu(img)

    hist = histogram(img)
    total = img.shape[0] * img.shape[1]

    kumulatif = [0] * 256
    jumlah = 0
    for i in range(256):
        jumlah += hist[i]
        kumulatif[i] = jumlah

    peta = [0] * 256
    for i in range(256):
        peta[i] = round(kumulatif[i] / total * 255)

    hasil = img.copy()
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            hasil[i, j] = peta[img[i, j]]

    return hasil


def tampilkan_histogram(img, judul):
    hist = histogram(img)
    abu_abu = ubah_ke_abu_abu(img)
    kanvas = cv2.cvtColor(cv2.resize(abu_abu, (512, 300)), cv2.COLOR_GRAY2BGR)
    for y in range(kanvas.shape[0]):
        for x in range(kanvas.shape[1]):
            kanvas[y, x, 0] = 0
            kanvas[y, x, 1] = 0
            kanvas[y, x, 2] = 0

    nilai_max = max(hist)
    if nilai_max == 0:
        return kanvas

    for i in range(256):
        tinggi = int(hist[i] / nilai_max * 290)
        x1 = i * 2
        cv2.line(kanvas, (x1, 300), (x1, 300 - tinggi), (255, 255, 255), 1)

    return kanvas


if __name__ == "__main__":
    img = cv2.imread("gambar.jpg", cv2.IMREAD_COLOR)

    if img is None:
        print("Gambar tidak ditemukan, pastikan file gambar.jpg ada di folder yang sama")
        exit()

    neg = negative(img)
    log = log_transform(img)
    gamma = gamma_correction(img, 0.5)
    stretch = contrast_stretching(img)
    eq = equalize_histogram(img)
    histogram_asli = tampilkan_histogram(img, "Asli")
    histogram_ekualisasi = tampilkan_histogram(eq, "Ekualisasi")

    panel_atas = cv2.hconcat(
        [
            buat_panel("Gambar Asli (Berwarna)", img),
            buat_panel("Negative", neg),
            buat_panel("Log Transform", log),
            buat_panel("Gamma 0.5", gamma),
        ]
    )
    panel_bawah = cv2.hconcat(
        [
            buat_panel("Contrast Stretching", stretch),
            buat_panel("Ekualisasi (Grayscale)", eq),
            buat_panel("Histogram Asli (Grayscale)", histogram_asli),
            buat_panel("Histogram Ekualisasi (Grayscale)", histogram_ekualisasi),
        ]
    )
    semua_hasil = cv2.vconcat([panel_atas, panel_bawah])

    cv2.namedWindow("Hasil Pengolahan Citra", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Hasil Pengolahan Citra", 1280, 600)
    cv2.imshow("Hasil Pengolahan Citra", semua_hasil)

    print("Tekan sembarang tombol untuk keluar")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
