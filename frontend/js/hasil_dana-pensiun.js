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

function renderUserInput(user) {
    const inputHTML = `
        <div style="padding: 10px; font-size: 14px;">
            <p><strong>Pengeluaran Bulanan:</strong> Rp ${user.pengeluaran_bulanan.toLocaleString()}</p>
            <p><strong>Usia Saat Ini:</strong> ${user.usia_saat_ini}</p>
            <p><strong>Target Usia Pensiun:</strong> ${user.target_usia_pensiun}</p>
            <p><strong>Asumsi Inflasi:</strong> ${user.inflasi.toLocaleString()}</p>
            <p><strong>Dana Pensiun Saat Ini:</strong> Rp ${user.dana_pensiun_saat_ini.toLocaleString()}</p>
            <p><strong>Target Investasi Bulanan:</strong> Rp ${user.target_investasi_bulanan.toLocaleString()}</p>
            <p><strong>Return Investasi (%):</strong> ${user.return_investasi} /tahun</p>
        </div>
    `;
    document.getElementById("inputUser").innerHTML = inputHTML;
}

function renderInvestmentResult(hasil) {
    const instrumenList = hasil.instrumen_rekomendasi?.map(item => `<li>${item}</li>`).join("") || "";

    const hasilHTML = `
        <div style="padding: 10px; font-size: 14px;">
            <p><strong>Estimasi Dana Yang Terkumpul:</strong> Rp ${hasil.total_dana_terkumpul.toLocaleString()}</p>
            <p><strong>Kekurangan Dana:</strong> Rp ${hasil.kekurangan_dana.toLocaleString()}</p>
            <p><strong>Target Dana Pensiun:</strong> Rp ${hasil.target_dana_pensiun.toLocaleString()}</p>
            <p><strong>Tahun Persiapan:</strong> ${hasil.tahun_persiapan}</p>
            <p><strong>Saran Tindakan:</strong> ${hasil.saran_tindakan || "-"}</p>
            <p><strong>Rekomendasi Instrumen Investasi:</strong></p>
            <ul>${instrumenList}</ul>
            <p><strong>Strategi Tambahan:</strong> ${hasil.strategi_rekomendasi || "-"}</p>
        </div>
    `;
    document.getElementById("hasilAnalisa").innerHTML = hasilHTML;
}


function loadInvestmentCalculation() {
    const storedData = localStorage.getItem("danpenResult");

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
window.addEventListener("DOMContentLoaded", loadInvestmentCalculation);
