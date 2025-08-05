function renderResponseMessage(message) {
}

function renderHasil(hasil){
    const responseElement = document.getElementById("responseInfo");
    const isUnfit = hasil.status.includes("Belum");

    responseElement.style.backgroundColor = isUnfit ? '#FF1818' : '#2DF95D'; // merah muda kalau tidak cocok, hijau muda kalau cocok
    responseElement.style.border = isUnfit ? '2px solid red' : '2px solid green';

    responseElement.innerHTML = `
      <p style="padding: 15px; font-size: 24px; font-weight: 600; color: #FFFFFF; position: realtive; margin: 0auto;">${hasil.status}</p>
    `;
}

function formatSaranTindakan(text) {
    if (!text.includes("\n")) {
        return `<p>${text}</p>`; // Kalau tidak ada newline, tampil biasa
    }

    const lines = text.split("\n").filter(line => line.trim() !== "");
    let listHTML = "<ol style='padding-left: 20px;'>";
    lines.forEach(line => {
        const cleaned = line.replace(/^[-–•]\s*/, '').trim();
        listHTML += `<li>${cleaned}</li>`;
    });
    listHTML += "</ol>";
    return listHTML;
}

function renderUserInput(user) {
    const inputHTML = `
        <div style="padding: 10px; font-size: 14px;">
            <p><strong>Target Pengumpulan Dana:</strong> ${user.waktu_target_bulan.toLocaleString()} Bulan</p>
            <p><strong>Harga Saat Ini:</strong> ${user.harga_barang.toLocaleString()}</p>
            <p><strong>DP barang (% dari harga):</strong> ${user.dp_persen}%</p>
            <p><strong>Asumsi Inflasi:</strong> ${user.inflasi}%</p>
            <p><strong>Target Investasi Bulanan:</strong> Rp ${user.investasi_bulanan.toLocaleString()}</p>
            <p><strong>Return Investasi (%):</strong> ${user.return_investasi}%</p>
        </div>
    `;
    document.getElementById("inputUser").innerHTML = inputHTML;
}

function renderInvestmentResult(hasil) {
    const dpRekom = hasil.dp_persen_disarankan !== null ? `${hasil.dp_persen_disarankan.toFixed(1)}%` : '-';
    const saranTindakan = hasil.saran_tindakan || '-';

    // Cek apakah statusnya "Tercapai" (tanpa emoji biar aman)
    const isTercapai = hasil.status.toLowerCase().includes("Tercapai");

    //  <p><strong>Dana Yang Perlu Kamu Kumpulkan:</strong> Rp ${hasil.dana_yang_perlu_dikumpulkan.toLocaleString()}</p>
    let hasilHTML = `
        <div style="padding: 10px; font-size: 14px; margin:3px;">
            <p><strong>Harga Barang Setelah Inflasi:</strong> </p>
            Rp ${hasil.harga_setelah_inflasi.toLocaleString()}</p>

            <p><strong>Kekurangan Dana Yang Kamu Perlukan :</strong></p>
            <p>Rp ${hasil.kekurangan_dana.toLocaleString()}</p>

            <p> <strong>Dana Yang Berhasil Terkumpul:</strong></p>
            <p>Rp ${hasil.total_dana_terkumpul.toLocaleString()}</p>
    `;

    // Tambahkan saran investasi HANYA jika status bukan "Tercapai"
    if (!isTercapai && hasil.saran_investasi) {
        hasilHTML += `<p><strong>Saran Investasi:</strong> ${hasil.saran_investasi}</p>`;
    }

    hasilHTML += `
            <p><strong>Saran Tindakan:</strong> ${formatSaranTindakan(saranTindakan)}</p>
        </div>
    `;

    document.getElementById("hasilAnalisa").innerHTML = hasilHTML;
}

function loadInvestmentCalculation() {
    const storedData = localStorage.getItem("impianResult");

    if (!storedData) {
        renderResponseMessage("❌ Data tidak ditemukan.");
        return;
    }

    try {
        const data = JSON.parse(storedData);

        // render semua data
        if (data.message) renderResponseMessage(data.message);
        // render inputuser
        if (data.inputUser) renderUserInput(data.inputUser);
        // render respon server
        if (data.hasil) renderInvestmentResult(data.hasil);
        if (data.hasil) renderHasil(data.hasil);

    } catch (error) {
        console.error("❌ Error saat parsing data:", error);
        renderResponseMessage("❌ Data rusak atau tidak valid.");
    }
}
// tombol info
function toggleInfo(id) {
    const el = document.getElementById(id);
    if (!el) return;

    if (el.classList.contains("show")) {
        el.classList.remove("show");
        setTimeout(() => {
            el.style.display = "none";
        }, 300);
    } else {
        el.style.display = "block";
        void el.offsetWidth;
        el.classList.add("show");
    }
}



window.addEventListener("DOMContentLoaded", loadInvestmentCalculation);
