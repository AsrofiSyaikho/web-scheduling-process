import copy


# ─────────────────────────────────────────
#  FCFS
# ─────────────────────────────────────────

def fcfs(proses):
    p = copy.deepcopy(proses)
    p.sort(key=lambda x: x["arrival"])

    waktu = 0
    timeline = []

    for pr in p:
        if waktu < pr["arrival"]:
            waktu = pr["arrival"]

        pr["start"]          = waktu
        pr["waiting_time"]   = waktu - pr["arrival"]
        pr["finish"]         = waktu + pr["burst"]
        pr["turnaround_time"] = pr["finish"] - pr["arrival"]

        timeline.append({
            "nama" : pr["nama"],
            "start": pr["start"],
            "finish": pr["finish"]
        })

        waktu += pr["burst"]

    return p, timeline


# ─────────────────────────────────────────
#  SJF
# ─────────────────────────────────────────

def sjf(proses):
    p = copy.deepcopy(proses)
    n = len(p)

    # OPTIMASI: tandai proses selesai dengan flag boolean (O(1) per cek)
    # alih-alih `x not in selesai` yang harus membandingkan seluruh isi
    # dict satu per satu pada setiap iterasi (O(n) per cek -> O(n^2) total).
    for x in p:
        x["_selesai"] = False

    selesai  = []
    timeline = []
    waktu    = 0

    while len(selesai) < n:
        tersedia = [x for x in p if not x["_selesai"] and x["arrival"] <= waktu]

        if not tersedia:
            # OPTIMASI: lompat langsung ke arrival time proses berikutnya
            # yang belum selesai, bukan menambah waktu satu per satu.
            # Penting saat ada jeda arrival time yang besar (mis. 0 lalu 100000),
            # supaya tidak melakukan ribuan iterasi kosong yang sia-sia.
            waktu = min(x["arrival"] for x in p if not x["_selesai"])
            continue

        pilihan = min(tersedia, key=lambda x: x["burst"])

        pilihan["start"]           = waktu
        pilihan["waiting_time"]    = waktu - pilihan["arrival"]
        pilihan["finish"]          = waktu + pilihan["burst"]
        pilihan["turnaround_time"] = pilihan["finish"] - pilihan["arrival"]
        pilihan["_selesai"]        = True

        timeline.append({
            "nama"  : pilihan["nama"],
            "start" : pilihan["start"],
            "finish": pilihan["finish"]
        })

        waktu += pilihan["burst"]
        selesai.append(pilihan)

    # Bersihkan field internal sebelum dikembalikan ke caller
    for x in selesai:
        del x["_selesai"]

    return selesai, timeline


# ─────────────────────────────────────────
#  ROUND ROBIN
# ─────────────────────────────────────────

def round_robin(proses, quantum):
    p = copy.deepcopy(proses)
    n = len(p)

    for x in p:
        x["sisa_burst"]      = x["burst"]
        x["waiting_time"]    = 0
        x["turnaround_time"] = 0
        x["finish"]          = 0

    p.sort(key=lambda x: x["arrival"])

    antrian  = [p[0]]
    waktu    = p[0]["arrival"]
    idx      = 1
    timeline = []

    # OPTIMASI/REFACTOR: blok "tambahkan proses yang sudah arrival ke antrian"
    # sebelumnya ditulis dua kali (duplikat). Sekarang jadi satu fungsi
    # pembantu yang dipanggil di kedua cabang (proses selesai / belum selesai).
    def masukkan_proses_baru():
        nonlocal idx
        while idx < n and p[idx]["arrival"] <= waktu:
            antrian.append(p[idx])
            idx += 1

    while antrian:
        sekarang = antrian.pop(0)

        if sekarang["sisa_burst"] <= quantum:
            timeline.append({
                "nama"  : sekarang["nama"],
                "start" : waktu,
                "finish": waktu + sekarang["sisa_burst"]
            })
            waktu                       += sekarang["sisa_burst"]
            sekarang["sisa_burst"]       = 0
            sekarang["finish"]           = waktu
            sekarang["turnaround_time"]  = waktu - sekarang["arrival"]
            sekarang["waiting_time"]     = sekarang["turnaround_time"] - sekarang["burst"]

            masukkan_proses_baru()
        else:
            timeline.append({
                "nama"  : sekarang["nama"],
                "start" : waktu,
                "finish": waktu + quantum
            })
            waktu                  += quantum
            sekarang["sisa_burst"] -= quantum

            # Proses yang baru datang masuk antrian dulu sebelum proses
            # yang di-requeue (sesuai urutan FIFO Round Robin yang benar)
            masukkan_proses_baru()
            antrian.append(sekarang)

        if not antrian and idx < n:
            waktu = p[idx]["arrival"]
            antrian.append(p[idx])
            idx += 1

    return p, timeline


# ─────────────────────────────────────────
#  HITUNG RATA-RATA
# ─────────────────────────────────────────

def hitung_rata_rata(hasil):
    n = len(hasil)

    if n == 0:
        return {"avg_wt": 0, "avg_tat": 0}

    total_wt  = sum(p["waiting_time"]    for p in hasil)
    total_tat = sum(p["turnaround_time"] for p in hasil)

    return {
        "avg_wt" : round(total_wt  / n, 2),
        "avg_tat": round(total_tat / n, 2)
    }


# ─────────────────────────────────────────
#  BANDINGKAN SEMUA ALGORITMA SEKALIGUS
#  (dipakai oleh halaman perbandingan)
# ─────────────────────────────────────────

def bandingkan_semua(proses, quantum):
    """
    Menjalankan FCFS, SJF, dan Round Robin terhadap data proses yang
    persis sama, lalu mengembalikan hasil + timeline + rata-rata
    ketiganya sekaligus dalam satu struktur, sehingga frontend cukup
    melakukan satu kali request untuk menampilkan perbandingan.
    """
    hasil_fcfs, timeline_fcfs = fcfs(proses)
    hasil_sjf,  timeline_sjf  = sjf(proses)
    hasil_rr,   timeline_rr   = round_robin(proses, quantum)

    return {
        "fcfs": {
            "hasil"    : hasil_fcfs,
            "timeline" : timeline_fcfs,
            "rata_rata": hitung_rata_rata(hasil_fcfs)
        },
        "sjf": {
            "hasil"    : hasil_sjf,
            "timeline" : timeline_sjf,
            "rata_rata": hitung_rata_rata(hasil_sjf)
        },
        "rr": {
            "hasil"    : hasil_rr,
            "timeline" : timeline_rr,
            "rata_rata": hitung_rata_rata(hasil_rr)
        }
    }