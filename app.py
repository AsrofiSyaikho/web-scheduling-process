from flask import Flask, render_template, request, jsonify
from algorithms import fcfs, sjf, round_robin, hitung_rata_rata

app = Flask(__name__)


# ─────────────────────────────────────────
#  ROUTE UTAMA — Tampilkan Halaman Web
# ─────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ─────────────────────────────────────────
#  ROUTE API — Jalankan Simulasi
# ─────────────────────────────────────────

@app.route("/hitung", methods=["POST"])
def hitung():
    data       = request.get_json()
    proses     = data["proses"]
    algoritma  = data["algoritma"]
    quantum    = data.get("quantum", 1)

    if algoritma == "fcfs":
        hasil, timeline = fcfs(proses)

    elif algoritma == "sjf":
        hasil, timeline = sjf(proses)

    elif algoritma == "rr":
        hasil, timeline = round_robin(proses, float(quantum))

    else:
        return jsonify({"error": "Algoritma tidak dikenali"}), 400

    rata_rata = hitung_rata_rata(hasil)

    return jsonify({
        "hasil"    : hasil,
        "timeline" : timeline,
        "rata_rata": rata_rata
    })


# ─────────────────────────────────────────
#  JALANKAN SERVER
# ─────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)