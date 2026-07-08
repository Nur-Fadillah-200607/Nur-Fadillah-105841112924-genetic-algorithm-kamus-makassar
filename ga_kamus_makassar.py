"""
=====================================================================
 TUGAS ALGORITMA GENETIKA (GENETIC ALGORITHM)
 Studi Kasus : Pencarian Kata dalam Kamus Bahasa Daerah (Bahasa Makassar)
=====================================================================

Konsep:
- Setiap individu (kromosom) adalah untai huruf acak sepanjang kata target.
- Fitness dihitung dari jumlah huruf yang cocok dengan kata target
  pada posisi yang sama (persis seperti contoh KOTA/KITA/DATA/KASA
  pada materi kuliah).
- Seleksi orang tua memakai Roulette Wheel Selection.
- Reproduksi memakai Single-Point Crossover.
- Variasi memakai Mutasi Gen (mengganti satu huruf secara acak).
- Program berhenti kalau individu dengan fitness = 1.0 (semua huruf
  cocok) ditemukan, atau jumlah generasi maksimum tercapai.

Alfabet gen yang dipakai mengikuti ejaan Bahasa Makassar, yaitu
26 huruf latin + tanda apostrof (') yang melambangkan bunyi hentak
glotal (mis. pada kata "ca'di'", "je'ne'").
"""

import random

ALFABET = "abcdefghijklmnopqrstuvwxyz'"

# ---------------------------------------------------------------
# 1. KAMUS BAHASA MAKASSAR (minimal 10 kata, sesuai ketentuan tugas)
#    Sumber acuan kosakata: kamus umum Bahasa Makassar sehari-hari.
# ---------------------------------------------------------------
KAMUS = [
    {"kata": "nakke",   "arti": "saya / aku"},
    {"kata": "katte",   "arti": "kamu / engkau"},
    {"kata": "anne",    "arti": "ini"},
    {"kata": "anjo",    "arti": "itu"},
    {"kata": "kemae",   "arti": "di mana"},
    {"kata": "tena",    "arti": "tidak / bukan"},
    {"kata": "lompo",   "arti": "besar"},
    {"kata": "jai",     "arti": "banyak"},
    {"kata": "rua",     "arti": "dua"},
    {"kata": "tallu",   "arti": "tiga"},
    {"kata": "lima",    "arti": "lima"},
    {"kata": "baine",   "arti": "perempuan / wanita"},
    {"kata": "maraeng", "arti": "lain"},
    {"kata": "sikura",  "arti": "beberapa"},
]

# ---------------------------------------------------------------
# Parameter Algoritma Genetika
# ---------------------------------------------------------------
UKURAN_POPULASI = 8
PROB_MUTASI = 0.1
MAKS_GENERASI = 200

# ---------------------------------------------------------------
# State global (dipakai supaya menu 4-9 bisa dijalankan bertahap
# untuk satu generasi, sesuai kebutuhan laporan)
# ---------------------------------------------------------------
state = {
    "target": None,          # kata target (string)
    "populasi": [],          # list string kromosom
    "fitness": [],           # list nilai fitness sejajar dg populasi
    "probabilitas": [],      # list probabilitas seleksi
    "interval": [],          # list (batas_bawah, batas_atas)
    "induk": [],             # pasangan induk terpilih [(p1,p2), ...]
    "anak": [],              # hasil crossover (sebelum mutasi)
    "anak_mutasi": [],       # hasil setelah mutasi
    "generasi_ke": 0,
}


# =================================================================
# FUNGSI-FUNGSI ALGORITMA GENETIKA
# =================================================================

def buat_individu(panjang):
    """Membuat satu kromosom acak sepanjang `panjang` huruf."""
    return "".join(random.choice(ALFABET) for _ in range(panjang))


def buat_populasi_awal(target):
    panjang = len(target)
    return [buat_individu(panjang) for _ in range(UKURAN_POPULASI)]


def hitung_fitness(individu, target):
    """Fitness = (jumlah huruf yang cocok pada posisi sama) / panjang kata."""
    cocok = sum(1 for a, b in zip(individu, target) if a == b)
    return cocok / len(target)


def hitung_semua_fitness(populasi, target):
    return [hitung_fitness(ind, target) for ind in populasi]


def hitung_probabilitas_dan_interval(fitness_list):
    total = sum(fitness_list)
    probabilitas = []
    interval = []
    batas_bawah = 0.0
    if total == 0:
        # Semua individu fitness 0 -> beri probabilitas seragam
        n = len(fitness_list)
        probabilitas = [1 / n] * n
    else:
        probabilitas = [f / total for f in fitness_list]

    for p in probabilitas:
        batas_atas = batas_bawah + p
        interval.append((round(batas_bawah, 4), round(batas_atas, 4)))
        batas_bawah = batas_atas
    return probabilitas, interval


def roulette_wheel_selection(populasi, interval, jumlah_dipilih):
    """Memilih induk berdasarkan angka acak [0,1) yang jatuh pada interval."""
    terpilih = []
    for _ in range(jumlah_dipilih):
        r = random.random()
        for i, (bawah, atas) in enumerate(interval):
            if bawah <= r < atas or (i == len(interval) - 1 and r >= bawah):
                terpilih.append(populasi[i])
                break
    return terpilih


def single_point_crossover(induk1, induk2):
    """Crossover satu titik potong, menghasilkan 2 anak."""
    panjang = len(induk1)
    if panjang < 2:
        return induk1, induk2
    titik = random.randint(1, panjang - 1)
    anak1 = induk1[:titik] + induk2[titik:]
    anak2 = induk2[:titik] + induk1[titik:]
    return anak1, anak2


def mutasi(individu, prob_mutasi):
    """Mengganti satu atau lebih gen secara acak berdasarkan probabilitas mutasi."""
    hasil = list(individu)
    for i in range(len(hasil)):
        if random.random() < prob_mutasi:
            hasil[i] = random.choice(ALFABET)
    return "".join(hasil)


# =================================================================
# MENU-MENU PROGRAM
# =================================================================

def menu_tampilkan_kamus():
    print("\n=== KAMUS BAHASA MAKASSAR ===")
    print(f"{'No':<4}{'Kata':<12}{'Arti'}")
    for i, entri in enumerate(KAMUS, start=1):
        print(f"{i:<4}{entri['kata']:<12}{entri['arti']}")


def menu_cari_kata():
    kunci = input("Masukkan kata atau arti yang dicari: ").strip().lower()
    hasil = [e for e in KAMUS if kunci in e["kata"].lower() or kunci in e["arti"].lower()]
    if hasil:
        print("\nDitemukan:")
        for e in hasil:
            print(f"  {e['kata']} = {e['arti']}")
    else:
        print("Kata tidak ditemukan dalam kamus.")


def pilih_target():
    menu_tampilkan_kamus()
    try:
        pilihan = int(input("\nPilih nomor kata yang akan dijadikan target GA: "))
        target = KAMUS[pilihan - 1]["kata"]
        print(f"Kata target dipilih: '{target}'")
        return target
    except (ValueError, IndexError):
        print("Pilihan tidak valid, memakai kata pertama sebagai default.")
        return KAMUS[0]["kata"]


def menu_jalankan_ga():
    """Menjalankan algoritma genetika penuh (otomatis) sampai solusi ditemukan."""
    target = pilih_target()
    populasi = buat_populasi_awal(target)
    generasi = 0
    terbaik = None

    print(f"\nMenjalankan GA untuk mencari kata: '{target}'")
    while generasi < MAKS_GENERASI:
        fitness_list = hitung_semua_fitness(populasi, target)
        terbaik_idx = fitness_list.index(max(fitness_list))
        terbaik = (populasi[terbaik_idx], fitness_list[terbaik_idx])

        print(f"Generasi {generasi:>3} | Individu terbaik: '{terbaik[0]}' "
              f"| Fitness: {terbaik[1]:.2f}")

        if terbaik[1] == 1.0:
            print(f"\n>> Kata target '{target}' berhasil ditemukan pada generasi ke-{generasi}!")
            break

        probabilitas, interval = hitung_probabilitas_dan_interval(fitness_list)
        populasi_baru = []
        while len(populasi_baru) < UKURAN_POPULASI:
            induk1, induk2 = roulette_wheel_selection(populasi, interval, 2)
            anak1, anak2 = single_point_crossover(induk1, induk2)
            anak1 = mutasi(anak1, PROB_MUTASI)
            anak2 = mutasi(anak2, PROB_MUTASI)
            populasi_baru.extend([anak1, anak2])
        populasi = populasi_baru[:UKURAN_POPULASI]
        generasi += 1

    # simpan state akhir untuk ditampilkan lewat menu lain bila perlu
    state["target"] = target
    state["populasi"] = populasi
    state["generasi_ke"] = generasi


def menu_tampilkan_populasi():
    """Membuat / menampilkan populasi awal untuk SATU generasi (dipakai
    bersama menu 5-9 untuk demonstrasi bertahap, sesuai kebutuhan laporan)."""
    target = pilih_target()
    state["target"] = target
    state["populasi"] = buat_populasi_awal(target)
    state["fitness"] = []
    state["probabilitas"] = []
    state["interval"] = []
    state["induk"] = []
    state["anak"] = []
    state["anak_mutasi"] = []
    state["generasi_ke"] = 0

    print(f"\nPopulasi awal untuk kata target '{target}' "
          f"({UKURAN_POPULASI} individu, panjang {len(target)} gen):")
    for i, ind in enumerate(state["populasi"], start=1):
        print(f"  Individu {i}: {ind}")


def _pastikan_populasi_ada():
    if not state["populasi"] or not state["target"]:
        print("Belum ada populasi. Menjalankan 'Tampilkan Populasi' dahulu...")
        menu_tampilkan_populasi()


def menu_hasil_fitness():
    _pastikan_populasi_ada()
    target = state["target"]
    populasi = state["populasi"]
    state["fitness"] = hitung_semua_fitness(populasi, target)

    print(f"\n=== PERHITUNGAN FITNESS (target: '{target}') ===")
    print(f"{'Individu':<10}{'Kromosom':<15}{'Huruf Benar':<14}{'Fitness'}")
    for i, (ind, fit) in enumerate(zip(populasi, state["fitness"]), start=1):
        benar = int(round(fit * len(target)))
        print(f"{i:<10}{ind:<15}{benar:<14}{fit:.2f}")


def menu_seleksi_roulette():
    if not state["fitness"]:
        print("Belum ada nilai fitness. Menjalankan 'Hasil Fitness' dahulu...")
        menu_hasil_fitness()

    probabilitas, interval = hitung_probabilitas_dan_interval(state["fitness"])
    state["probabilitas"] = probabilitas
    state["interval"] = interval

    print("\n=== TABEL PROBABILITAS & INTERVAL (Roulette Wheel) ===")
    print(f"{'Individu':<10}{'Fitness':<10}{'Probabilitas':<14}{'Interval'}")
    for i, (ind, fit, p, (b, a)) in enumerate(
        zip(state["populasi"], state["fitness"], probabilitas, interval), start=1
    ):
        print(f"{i:<10}{fit:<10.2f}{p:<14.3f}{b:.3f} - {a:.3f}")

    jumlah_induk = UKURAN_POPULASI  # akan dipasangkan 2-2 untuk crossover
    terpilih = roulette_wheel_selection(state["populasi"], interval, jumlah_induk)
    state["induk"] = [(terpilih[i], terpilih[i + 1]) for i in range(0, len(terpilih) - 1, 2)]

    print("\nPasangan induk terpilih:")
    for i, (p1, p2) in enumerate(state["induk"], start=1):
        print(f"  Pasangan {i}: '{p1}'  x  '{p2}'")


def menu_crossover():
    if not state["induk"]:
        print("Belum ada pasangan induk. Menjalankan 'Seleksi Roulette' dahulu...")
        menu_seleksi_roulette()

    print("\n=== CROSSOVER (Single-Point) ===")
    anak = []
    for i, (p1, p2) in enumerate(state["induk"], start=1):
        a1, a2 = single_point_crossover(p1, p2)
        anak.extend([a1, a2])
        print(f"  Induk {i}: '{p1}' x '{p2}'  ->  Anak: '{a1}', '{a2}'")
    state["anak"] = anak[:UKURAN_POPULASI]


def menu_mutasi():
    if not state["anak"]:
        print("Belum ada hasil crossover. Menjalankan 'Cross Over' dahulu...")
        menu_crossover()

    print(f"\n=== MUTASI GEN (probabilitas mutasi = {PROB_MUTASI}) ===")
    hasil = []
    for i, anak in enumerate(state["anak"], start=1):
        termutasi = mutasi(anak, PROB_MUTASI)
        hasil.append(termutasi)
        tanda = "  <-- termutasi" if termutasi != anak else ""
        print(f"  Anak {i}: '{anak}'  ->  '{termutasi}'{tanda}")
    state["anak_mutasi"] = hasil


def menu_generasi_baru():
    if not state["anak_mutasi"]:
        print("Belum ada hasil mutasi. Menjalankan 'Mutasi' dahulu...")
        menu_mutasi()

    populasi_baru = state["anak_mutasi"][:UKURAN_POPULASI]
    fitness_baru = hitung_semua_fitness(populasi_baru, state["target"])
    state["generasi_ke"] += 1

    print(f"\n=== POPULASI GENERASI KE-{state['generasi_ke']} ===")
    print(f"{'Individu':<10}{'Kromosom':<15}{'Fitness'}")
    for i, (ind, fit) in enumerate(zip(populasi_baru, fitness_baru), start=1):
        print(f"{i:<10}{ind:<15}{fit:.2f}")

    terbaik_idx = fitness_baru.index(max(fitness_baru))
    print(f"\nIndividu terbaik generasi ini: '{populasi_baru[terbaik_idx]}' "
          f"(fitness {fitness_baru[terbaik_idx]:.2f}) | Target: '{state['target']}'")

    # generasi baru menjadi populasi aktif, siap dievaluasi ulang lewat menu 5
    state["populasi"] = populasi_baru
    state["fitness"] = []
    state["probabilitas"] = []
    state["interval"] = []
    state["induk"] = []
    state["anak"] = []
    state["anak_mutasi"] = []


# =================================================================
# PROGRAM UTAMA
# =================================================================

def tampilkan_menu():
    print("\n=== Kamus Bahasa Daerah (Bahasa Makassar) & Algoritma Genetika ===")
    print("1. Tampilkan Kamus")
    print("2. Cari Kata")
    print("3. Jalankan Algoritma Genetika")
    print("4. Tampilkan Populasi")
    print("5. Hasil Fitness")
    print("6. Seleksi Roulette")
    print("7. Cross Over")
    print("8. Mutasi")
    print("9. Generasi Baru")
    print("10. Keluar")


def main():
    aksi = {
        "1": menu_tampilkan_kamus,
        "2": menu_cari_kata,
        "3": menu_jalankan_ga,
        "4": menu_tampilkan_populasi,
        "5": menu_hasil_fitness,
        "6": menu_seleksi_roulette,
        "7": menu_crossover,
        "8": menu_mutasi,
        "9": menu_generasi_baru,
    }

    while True:
        tampilkan_menu()
        pilihan = input("Pilih menu (1-10): ").strip()
        if pilihan == "10":
            print("Terima kasih. Program selesai.")
            break
        fungsi = aksi.get(pilihan)
        if fungsi:
            fungsi()
        else:
            print("Pilihan tidak valid, silakan coba lagi.")


if __name__ == "__main__":
    main()
