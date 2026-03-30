// ─────────────────────────────────────────
//  WARNA GANTT CHART
// ─────────────────────────────────────────

const WARNA = [
    "#1a73e8", "#00bfa5", "#e53935", "#fb8c00",
    "#8e24aa", "#3949ab", "#e91e63", "#00897b",
    "#f4511e", "#7cb342"
];


// ─────────────────────────────────────────
//  ELEMEN HTML
// ─────────────────────────────────────────

const elJumlah       = document.getElementById("jumlah-proses");
const elAlgoritma    = document.getElementById("algoritma");
const elQuantum      = document.getElementById("quantum");
const elGroupQuantum = document.getElementById("group-quantum");
const elBtnGenerate  = document.getElementById("btn-generate");
const elBtnHitung    = document.getElementById("btn-hitung");
const elLoading      = document.getElementById("loading");
const elTabelInput   = document.getElementById("container-tabel-input");
const elSectionGantt = document.getElementById("section-gantt");
const elSectionHasil = document.getElementById("section-hasil");
const elGanttChart   = document.getElementById("gantt-chart");
const elGanttLabel   = document.getElementById("gantt-label");
const elTabelHasil   = document.getElementById("container-tabel-hasil");
const elRataRata     = document.getElementById("rata-rata");


// ─────────────────────────────────────────
//  TAMPILKAN / SEMBUNYIKAN TIME QUANTUM
// ─────────────────────────────────────────

elAlgoritma.addEventListener("change", () => {
    elGroupQuantum.style.display = elAlgoritma.value === "rr" ? "flex" : "none";
});


// ─────────────────────────────────────────
//  GENERATE TABEL INPUT
// ─────────────────────────────────────────

elBtnGenerate.addEventListener("click", () => {
    const n = parseInt(elJumlah.value);

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
                <td><input type="number" id="arrival-${i}" min="0" value="0"></td>
                <td><input type="number" id="burst-${i}"   min="1" value="1"></td>
            </tr>
        `;
    }

    html += `</tbody></table>`;

    elTabelInput.innerHTML       = html;
    elBtnHitung.style.display    = "inline-block";
    elSectionGantt.style.display = "none";
    elSectionHasil.style.display = "none";
});


// ─────────────────────────────────────────
//  JALANKAN SIMULASI
// ─────────────────────────────────────────

elBtnHitung.addEventListener("click", async () => {
    const n         = parseInt(elJumlah.value);
    const algoritma = elAlgoritma.value;
    const quantum   = parseFloat(elQuantum.value);
    const proses    = [];

    for (let i = 0; i < n; i++) {
        const arrival = parseInt(document.getElementById(`arrival-${i}`).value);
        const burst   = parseInt(document.getElementById(`burst-${i}`).value);

        if (isNaN(arrival) || isNaN(burst) || burst < 1) {
            alert(`Data P${i + 1} tidak valid!`);
            return;
        }

        proses.push({ nama: `P${i + 1}`, arrival, burst });
    }

    // Tampilkan loading spinner
    elLoading.classList.add("aktif");
    elBtnHitung.disabled     = true;
    elBtnHitung.style.opacity = "0.7";

    try {
        const response = await fetch("/hitung", {
            method : "POST",
            headers: { "Content-Type": "application/json" },
            body   : JSON.stringify({ proses, algoritma, quantum })
        });

        const data = await response.json();

        if (data.error) {
            alert("Error: " + data.error);
            return;
        }

        // Sembunyikan loading
        elLoading.classList.remove("aktif");
        elBtnHitung.disabled      = false;
        elBtnHitung.style.opacity = "1";

        tampilkanGantt(data.timeline, proses);
        tampilkanHasil(data.hasil, data.rata_rata);

    } catch (err) {
        elLoading.classList.remove("aktif");
        elBtnHitung.disabled      = false;
        elBtnHitung.style.opacity = "1";
        alert("Gagal terhubung ke server!");
        console.error(err);
    }
});


// ─────────────────────────────────────────
//  TAMPILKAN GANTT CHART — ANIMASI BLOK PER BLOK
// ─────────────────────────────────────────

function tampilkanGantt(timeline, proses) {
    const petaWarna = {};
    proses.forEach((p, i) => {
        petaWarna[p.nama] = WARNA[i % WARNA.length];
    });

    const totalWaktu = timeline[timeline.length - 1].finish;

    elGanttChart.innerHTML = "";
    elGanttLabel.innerHTML = "";

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

        elGanttChart.appendChild(block);
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
    elGanttLabel.innerHTML = htmlLabel;

    elSectionGantt.style.display = "block";
}


// ─────────────────────────────────────────
//  TAMPILKAN TABEL HASIL — FADE IN PER BARIS
// ─────────────────────────────────────────

function tampilkanHasil(hasil, rataRata) {
    let htmlTabel = `
        <table>
            <thead>
                <tr>
                    <th>Proses</th>
                    <th>Arrival Time</th>
                    <th>Burst Time</th>
                    <th>Waiting Time</th>
                    <th>Turnaround Time</th>
                </tr>
            </thead>
            <tbody>
    `;

    hasil.forEach(p => {
        htmlTabel += `
            <tr>
                <td><strong>${p.nama}</strong></td>
                <td>${p.arrival}</td>
                <td>${p.burst}</td>
                <td>${p.waiting_time}</td>
                <td>${p.turnaround_time}</td>
            </tr>
        `;
    });

    htmlTabel += `</tbody></table>`;
    elTabelHasil.innerHTML       = htmlTabel;
    elSectionHasil.style.display = "block";

    // Animasi fade-in per baris tabel
    const rows = elTabelHasil.querySelectorAll("tbody tr");
    rows.forEach((row, i) => {
        setTimeout(() => {
            row.classList.add("muncul");
        }, i * 100);
    });

    // Animasi rata-rata box
    elRataRata.innerHTML = `
        <div class="rata-rata-box" id="box-wt">
            <div class="label">Rata-rata Waiting Time</div>
            <div class="nilai">${rataRata.avg_wt}</div>
        </div>
        <div class="rata-rata-box" id="box-tat">
            <div class="label">Rata-rata Turnaround Time</div>
            <div class="nilai">${rataRata.avg_tat}</div>
        </div>
    `;

    setTimeout(() => document.getElementById("box-wt").classList.add("muncul"),  hasil.length * 100 + 100);
    setTimeout(() => document.getElementById("box-tat").classList.add("muncul"), hasil.length * 100 + 220);

    // Smooth scroll ke Gantt Chart
    setTimeout(() => {
        elSectionGantt.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 200);
}