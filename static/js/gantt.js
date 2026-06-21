// ─────────────────────────────────────────
//  MODUL BERSAMA: WARNA & RENDER GANTT CHART
//  Dipakai oleh halaman Simulasi Tunggal (main.js)
//  dan halaman Bandingkan Algoritma (compare.js).
//
//  Sebelumnya logika ini ada 1x di main.js. Sekarang
//  dipindah ke sini supaya tidak duplikat saat halaman
//  perbandingan butuh menggambar 3 gantt chart sekaligus.
// ─────────────────────────────────────────

const WARNA = [
    "#1a73e8", "#00bfa5", "#e53935", "#fb8c00",
    "#8e24aa", "#3949ab", "#e91e63", "#00897b",
    "#f4511e", "#7cb342"
];


// ─────────────────────────────────────────
//  PETA WARNA PER PROSES
// ─────────────────────────────────────────

function buatPetaWarna(proses) {
    const peta = {};
    proses.forEach((p, i) => {
        peta[p.nama] = WARNA[i % WARNA.length];
    });
    return peta;
}


// ─────────────────────────────────────────
//  RENDER SATU GANTT CHART KE ELEMEN YANG DIBERIKAN
// ─────────────────────────────────────────

function renderGanttChart(elChart, elLabel, timeline, petaWarna) {
    const totalWaktu = timeline[timeline.length - 1].finish;

    elChart.innerHTML = "";
    elLabel.innerHTML = "";

    // Buat semua blok dulu
    const blocks = timeline.map(item => {
        const durasi = item.finish - item.start;
        const lebar  = Math.max((durasi / totalWaktu) * 100, 4);
        const warna  = petaWarna[item.nama] || "#1a73e8";

        const block = document.createElement("div");
        block.className = "gantt-block";
        block.style.width           = `${lebar}%`;
        block.style.backgroundColor = warna;
        block.title                 = `${item.nama}: ${item.start} → ${item.finish}`;
        block.textContent           = item.nama;

        elChart.appendChild(block);
        return block;
    });

    // Animasi blok per blok dengan delay bertahap
    blocks.forEach((block, i) => {
        setTimeout(() => {
            block.classList.add("muncul");
        }, i * 120);
    });

    // Label waktu
    let htmlLabel = "";
    timeline.forEach(item => {
        const durasi = item.finish - item.start;
        const lebar  = Math.max((durasi / totalWaktu) * 100, 4);
        htmlLabel += `<div class="gantt-time" style="width:${lebar}%">${item.start}</div>`;
    });
    htmlLabel += `<div class="gantt-time">${timeline[timeline.length - 1].finish}</div>`;
    elLabel.innerHTML = htmlLabel;
}
