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
    """
    SJF Preemptive (Shortest Remaining Time First / SRTF).
    Setiap satu satuan waktu, CPU selalu memilih proses dengan
    sisa burst terkecil dari semua proses yang sudah tiba.
    Jika ada proses baru yang tiba dengan sisa burst lebih kecil
    dari proses yang sedang berjalan, proses tersebut langsung
    di-interrupt dan digantikan.
    """
    p = copy.deepcopy(proses)
    n = len(p)

    for x in p:
        x["sisa_burst"]   = x["burst"]
        x["_selesai"]     = False
        x["waiting_time"] = 0
        x["finish"]       = 0

    selesai       = []
    timeline_raw  = []
    selesai_count = 0

    # Mulai dari arrival time terkecil
    waktu = min(x["arrival"] for x in p)

    while selesai_count < n:
        tersedia = [x for x in p if not x["_selesai"] and x["arrival"] <= waktu]

        if not tersedia:
            waktu = min(x["arrival"] for x in p if not x["_selesai"])
            continue

        # Pilih proses dengan sisa burst terkecil; tiebreaker: arrival lebih awal
        pilihan = min(tersedia, key=lambda x: (x["sisa_burst"], x["arrival"]))

        # Jalankan 1 unit waktu
        timeline_raw.append((pilihan["nama"], waktu))
        pilihan["sisa_burst"] -= 1
        waktu += 1

        if pilihan["sisa_burst"] == 0:
            pilihan["_selesai"]        = True
            pilihan["finish"]          = waktu
            pilihan["turnaround_time"] = waktu - pilihan["arrival"]
            pilihan["waiting_time"]    = pilihan["turnaround_time"] - pilihan["burst"]
            selesai.append(pilihan)
            selesai_count += 1

    # Kompres timeline_raw (unit per unit) menjadi blok berurutan per proses
    timeline = []
    for nama, t in timeline_raw:
        if timeline and timeline[-1]["nama"] == nama:
            timeline[-1]["finish"] = t + 1
        else:
            timeline.append({"nama": nama, "start": t, "finish": t + 1})

    # Bersihkan field internal
    for x in selesai:
        del x["_selesai"]
        del x["sisa_burst"]

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