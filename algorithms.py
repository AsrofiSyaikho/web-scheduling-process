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
    selesai  = []
    timeline = []
    waktu    = 0

    while len(selesai) < n:
        tersedia = [x for x in p if x["arrival"] <= waktu and x not in selesai]

        if not tersedia:
            waktu += 1
            continue

        pilihan = min(tersedia, key=lambda x: x["burst"])

        pilihan["start"]          = waktu
        pilihan["waiting_time"]   = waktu - pilihan["arrival"]
        pilihan["finish"]         = waktu + pilihan["burst"]
        pilihan["turnaround_time"] = pilihan["finish"] - pilihan["arrival"]

        timeline.append({
            "nama"  : pilihan["nama"],
            "start" : pilihan["start"],
            "finish": pilihan["finish"]
        })

        waktu += pilihan["burst"]
        selesai.append(pilihan)

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
        else:
            timeline.append({
                "nama"  : sekarang["nama"],
                "start" : waktu,
                "finish": waktu + quantum
            })
            waktu                  += quantum
            sekarang["sisa_burst"] -= quantum

            while idx < n and p[idx]["arrival"] <= waktu:
                antrian.append(p[idx])
                idx += 1

            antrian.append(sekarang)

        while idx < n and p[idx]["arrival"] <= waktu:
            antrian.append(p[idx])
            idx += 1

        if not antrian and idx < n:
            waktu = p[idx]["arrival"]
            antrian.append(p[idx])
            idx += 1

    return p, timeline


# ─────────────────────────────────────────
#  HITUNG RATA-RATA
# ─────────────────────────────────────────

def hitung_rata_rata(hasil):
    n         = len(hasil)
    total_wt  = sum(p["waiting_time"]    for p in hasil)
    total_tat = sum(p["turnaround_time"] for p in hasil)

    return {
        "avg_wt" : round(total_wt  / n, 2),
        "avg_tat": round(total_tat / n, 2)
    }