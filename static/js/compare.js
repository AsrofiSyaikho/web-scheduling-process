// ─────────────────────────────────────────
//  ELEMEN HTML — HALAMAN BANDINGKAN ALGORITMA
// ─────────────────────────────────────────

const elJumlahC       = document.getElementById("jumlah-proses-c");
const elQuantumC      = document.getElementById("quantum-c");
const elBtnGenerateC  = document.getElementById("btn-generate-c");
const elBtnBandingkan = document.getElementById("btn-bandingkan");
const elLoadingC      = document.getElementById("loading-c");
const elTabelInputC   = document.getElementById("container-tabel-input-c");
const elSectionGanttB = document.getElementById("section-gantt-banding");
const elSectionHasilB = document.getElementById("section-hasil-banding");
const elTabelBanding  = document.getElementById("container-tabel-banding");
const elBarChartB     = document.getElementById("bar-chart-banding");

const ganttFcfs = {
    chart: document.getElementById("gantt-chart-fcfs"),
    label: document.getElementById("gantt-label-fcfs")
};
const ganttSjf = {
    chart: document.getElementById("gantt-chart-sjf"),
    label: document.getElementById("gantt-label-sjf")
};
const ganttRr = {
    chart: document.getElementById("gantt-chart-rr"),
    label: document.getElementById("gantt-label-rr")
};


// ─────────────────────────────────────────
//  GENERATE TABEL INPUT
//  ID Proses (P1, P2, ...) dibuat otomatis — tidak ada
//  input manual untuk ID, sama seperti halaman simulasi tunggal.
// ─────────────────────────────────────────

elBtnGenerateC.addEventListener("click", () => {
    const n = parseInt(elJumlahC.value);

    if (isNaN(n) || n < 1 || n > 10) {
        alert("Jumlah proses harus antara 1 sampai 10!");
        return;
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>Proses</th>
                    <th>Arrival Time</th>
                    <th>Burst Time</th>
                </tr>
            </thead>
            <tbody>
    `;

    for (let i = 0; i < n; i++) {
        html += `
            <tr>
                <td><strong>P${i + 1}</strong></td>
                <td><input type="number" id="arrival-c-${i}" min="0" value="0"></td>
                <td><input type="number" id="burst-c-${i}"   min="1" value="1"></td>
            </tr>
        `;
    }

    html += `</tbody></table>`;

    elTabelInputC.innerHTML       = html;
    elBtnBandingkan.style.display = "inline-block";
    elSectionGanttB.style.display = "none";
    elSectionHasilB.style.display = "none";
});


// ─────────────────────────────────────────
//  JALANKAN PERBANDINGAN 3 ALGORITMA
// ─────────────────────────────────────────

elBtnBandingkan.addEventListener("click", async () => {
    const n       = parseInt(elJumlahC.value);
    const quantum = parseFloat(elQuantumC.value);
    const proses  = [];

    for (let i = 0; i < n; i++) {
        const arrival = parseInt(document.getElementById(`arrival-c-${i}`).value);
        const burst   = parseInt(document.getElementById(`burst-c-${i}`).value);

        if (isNaN(arrival) || isNaN(burst) || burst < 1) {
            alert(`Data P${i + 1} tidak valid!`);
            return;
        }

        // nama/ID tetap dibuat otomatis di sini, dan backend juga
        // akan menimpanya secara otomatis demi konsistensi
        proses.push({ nama: `P${i + 1}`, arrival, burst });
    }

    elLoadingC.classList.add("aktif");
    elBtnBandingkan.disabled      = true;
    elBtnBandingkan.style.opacity = "0.7";

    try {
        const response = await fetch("/hitung_semua", {
            method : "POST",
            headers: { "Content-Type": "application/json" },
            body   : JSON.stringify({ proses, quantum })
        });

        const data = await response.json();

        if (data.error) {
            alert("Error: " + data.error);
            return;
        }

        tampilkanPerbandingan(data, proses);

    } catch (err) {
        alert("Gagal terhubung ke server!");
        console.error(err);
    } finally {
        elLoadingC.classList.remove("aktif");
        elBtnBandingkan.disabled      = false;
        elBtnBandingkan.style.opacity = "1";
    }
});


// ─────────────────────────────────────────
//  TAMPILKAN HASIL PERBANDINGAN
//  (3 gantt chart + tabel ringkasan + bar chart)
// ─────────────────────────────────────────

function tampilkanPerbandingan(data, proses) {
    const petaWarna = buatPetaWarna(proses);

    // 3 gantt chart memakai fungsi bersama dari gantt.js
    renderGanttChart(ganttFcfs.chart, ganttFcfs.label, data.fcfs.timeline, petaWarna);
    renderGanttChart(ganttSjf.chart,  ganttSjf.label,  data.sjf.timeline,  petaWarna);
    renderGanttChart(ganttRr.chart,   ganttRr.label,   data.rr.timeline,   petaWarna);

    elSectionGanttB.style.display = "block";

    const algoritma = [
        { kode: "fcfs", nama: "FCFS",        data: data.fcfs },
        { kode: "sjf",  nama: "SJF",         data: data.sjf  },
        { kode: "rr",   nama: "Round Robin", data: data.rr   }
    ];

    const terbaikWt  = Math.min(...algoritma.map(a => a.data.rata_rata.avg_wt));
    const terbaikTat = Math.min(...algoritma.map(a => a.data.rata_rata.avg_tat));

    // ── Tabel ringkasan, baris terbaik (WT/TAT terkecil) ditandai ──
    let htmlTabel = `
        <table>
            <thead>
                <tr>
                    <th>Algoritma</th>
                    <th>Rata-rata Waiting Time</th>
                    <th>Rata-rata Turnaround Time</th>
                </tr>
            </thead>
            <tbody>
    `;

    algoritma.forEach(a => {
        const isWtTerbaik  = a.data.rata_rata.avg_wt  === terbaikWt;
        const isTatTerbaik = a.data.rata_rata.avg_tat === terbaikTat;

        htmlTabel += `
            <tr>
                <td><strong>${a.nama}</strong></td>
                <td class="${isWtTerbaik ? 'sel-terbaik' : ''}">${a.data.rata_rata.avg_wt}${isWtTerbaik ? ' 🏆' : ''}</td>
                <td class="${isTatTerbaik ? 'sel-terbaik' : ''}">${a.data.rata_rata.avg_tat}${isTatTerbaik ? ' 🏆' : ''}</td>
            </tr>
        `;
    });

    htmlTabel += `</tbody></table>`;
    elTabelBanding.innerHTML = htmlTabel;

    // ── Bar chart sederhana, native CSS, tanpa library tambahan ──
    const maxNilai = Math.max(
        ...algoritma.map(a => Math.max(a.data.rata_rata.avg_wt, a.data.rata_rata.avg_tat))
    );

    let htmlBar = `<div class="bar-chart-judul">Grafik Perbandingan Rata-rata Waktu</div><div class="bar-chart">`;

    algoritma.forEach(a => {
        const tinggiWt  = maxNilai > 0 ? (a.data.rata_rata.avg_wt  / maxNilai) * 100 : 0;
        const tinggiTat = maxNilai > 0 ? (a.data.rata_rata.avg_tat / maxNilai) * 100 : 0;

        htmlBar += `
            <div class="bar-group">
                <div class="bar-pair">
                    <div class="bar bar-wt"  style="height:${tinggiWt}%"  title="Waiting Time: ${a.data.rata_rata.avg_wt}"></div>
                    <div class="bar bar-tat" style="height:${tinggiTat}%" title="Turnaround Time: ${a.data.rata_rata.avg_tat}"></div>
                </div>
                <div class="bar-group-label">${a.nama}</div>
            </div>
        `;
    });

    htmlBar += `</div>
        <div class="bar-chart-legenda">
            <span><i class="kotak-warna bar-wt"></i>Waiting Time</span>
            <span><i class="kotak-warna bar-tat"></i>Turnaround Time</span>
        </div>`;

    elBarChartB.innerHTML = htmlBar;

    elSectionHasilB.style.display = "block";

    setTimeout(() => {
        elSectionGanttB.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 200);
}
