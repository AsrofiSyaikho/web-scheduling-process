from flask import Flask, render_template, request, jsonify
from algorithms import fcfs, sjf, round_robin, hitung_rata_rata, bandingkan_semua

app = Flask(__name__)


# ─────────────────────────────────────────
#  VALIDASI INPUT (dipakai oleh /hitung & /hitung_semua)
# ─────────────────────────────────────────

def ambil_dan_validasi_proses(data):
    """
    Membaca & memvalidasi payload JSON dari frontend.
    Mengembalikan (proses, quantum) jika valid, atau melempar ValueError
    berisi pesan yang jelas jika tidak valid.

    ID/nama setiap proses SELALU digenerate otomatis di sini (P1, P2, ...)
    berdasarkan urutannya, sehingga ID tidak pernah bergantung pada input
    manual dari client — konsisten untuk halaman simulasi tunggal maupun
    halaman perbandingan algoritma.
    """
    if not isinstance(data, dict):
        raise ValueError("Payload request tidak valid")

    proses = data.get("proses")
    if not isinstance(proses, list) or len(proses) == 0:
        raise ValueError("Data proses kosong atau tidak valid")

    if len(proses) > 10:
        raise ValueError("Jumlah proses maksimal 10")

    for i, p in enumerate(proses):
        if not isinstance(p, dict) or "arrival" not in p or "burst" not in p:
            raise ValueError(f"Proses ke-{i + 1} tidak memiliki arrival/burst")

        try:
            p["arrival"] = int(p["arrival"])
            p["burst"]   = int(p["burst"])
        except (TypeError, ValueError):
            raise ValueError(f"Arrival/burst proses ke-{i + 1} harus berupa angka")

        if p["arrival"] < 0 or p["burst"] < 1:
            raise ValueError(
                f"Arrival tidak boleh negatif & burst minimal 1 (proses ke-{i + 1})"
            )

        # ID proses otomatis — mengabaikan nama apa pun yang dikirim client
        p["nama"] = f"P{i + 1}"

    quantum = data.get("quantum", 1)
    try:
        quantum = float(quantum)
    except (TypeError, ValueError):
        raise ValueError("Quantum harus berupa angka")

    if quantum <= 0:
        raise ValueError("Quantum harus lebih besar dari 0")

    return proses, quantum


# ─────────────────────────────────────────
#  ROUTE HALAMAN
# ─────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/bandingkan")
def bandingkan():
    return render_template("compare.html")


# ─────────────────────────────────────────
#  ROUTE API — Jalankan Simulasi (1 algoritma)
# ─────────────────────────────────────────

@app.route("/hitung", methods=["POST"])
def hitung():
    data      = request.get_json(silent=True)
    algoritma = (data or {}).get("algoritma")

    try:
        proses, quantum = ambil_dan_validasi_proses(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if algoritma == "fcfs":
        hasil, timeline = fcfs(proses)

    elif algoritma == "sjf":
        hasil, timeline = sjf(proses)

    elif algoritma == "rr":
        hasil, timeline = round_robin(proses, quantum)

    else:
        return jsonify({"error": "Algoritma tidak dikenali"}), 400

    rata_rata = hitung_rata_rata(hasil)

    return jsonify({
        "hasil"    : hasil,
        "timeline" : timeline,
        "rata_rata": rata_rata
    })


# ─────────────────────────────────────────
#  ROUTE API — Bandingkan Semua Algoritma
# ─────────────────────────────────────────

@app.route("/hitung_semua", methods=["POST"])
def hitung_semua():
    data = request.get_json(silent=True)

    try:
        proses, quantum = ambil_dan_validasi_proses(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(bandingkan_semua(proses, quantum))


# ─────────────────────────────────────────
#  JALANKAN SERVER
# ─────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
