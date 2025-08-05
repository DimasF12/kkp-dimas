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
            <p><strong>Pengeluaran Wajib:</strong> Rp ${user.pengeluaran_wajib.toLocaleString()}</p>
            <p><strong>Status Menikah:</strong> ${user.sudah_menikah ? 'Sudah' : 'Belum'}</p>
            <p><strong>Jumlah Tanggungan:</strong> ${user.jumlah_tanggungan}</p>
            <p><strong>Waktu Pengumpulan (bulan):</strong> ${user.waktu_pengumpulan_bulan}</p>
            <p><strong>Dana Darurat Saat Ini:</strong> Rp ${user.dana_darurat_saat_ini.toLocaleString()}</p>
            <p><strong>Target Investasi Bulanan:</strong> Rp ${user.target_investasi_bulanan.toLocaleString()}</p>
            <p><strong>Return Investasi (%):</strong> ${user.return_investasi}%</p>
        </div>
    `;
    document.getElementById("inputUser").innerHTML = inputHTML;
}

function renderInvestmentResult(hasil) {
    const hasilHTML = `
        <div style="padding: 10px; font-size: 14px;">
            <p><strong>Dana Darurat yang Dibutuhkan:</strong> Rp ${hasil.target_dana_darurat.toLocaleString()}</p>
            <p><strong>Kekurangan Dana:</strong> Rp ${hasil.kekurangan_dana.toLocaleString()}</p>
            <p><strong>Estimasi Dana Terkumpul:</strong> Rp ${hasil.estimasi_dana_terkumpul.toLocaleString()}</p>
            <p>
                <strong>Bulan Tanggungan:</strong> ${hasil.bulan_tanggungan}
                <i class="fa-solid fa-circle-info info-icon" onclick="toggleInfo('bulanTanggunganInfo')" style="cursor: pointer;"></i>
            </p>
            <div id="bulanTanggunganInfo" class="info-text" style="display: none;">
                Ini adalah jumlah bulan kamu bisa bertahan tanpa penghasilan dengan dana darurat yang ada.
            </div>
            <p><strong>Rekomendasi Instrumen:</strong> <span>${hasil.instrumen_rekomendasi}</span></p>

            ${hasil.strategi_rekomendasi ? `
                <div style="margin-top: 15px; padding: 10px; background-color: #fef3c7; border-left: 5px solid #facc15; font-style: italic;">
                    💭 <strong>Saran Strategi:</strong><br>
                    ${hasil.strategi_rekomendasi}
                </div>
            ` : ''}
        </div>
    `;
    document.getElementById("hasilAnalisa").innerHTML = hasilHTML;
}

function loadInvestmentCalculation() {
    const storedData = localStorage.getItem("dandurResult");

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
