// Render pesan utama
function renderResponseMessage(message) {
    const responseElement = document.getElementById("responseInfo");

    // Cek apakah strategi dianggap tidak cocok
    const isUnfit = message.includes("belum");

    responseElement.style.backgroundColor = isUnfit ? '#FF1818' : '#2DF95D'; // merah muda kalau tidak cocok, hijau muda kalau cocok
    responseElement.style.border = isUnfit ? '2px solid red' : '2px solid green';

    responseElement.innerHTML = `
      <p style="padding: 15px; font-size: 16px; font-weight: 600; color: #FFFFFF; position: realtive; margin: 0auto;">${message}</p>
    `;
}


// Render input user
function renderUserInput(user) {
    const inputHTML = `
      <div style="padding: 20px; font-size: 14px;">
        <p><strong>Uang Saat Ini:</strong> Rp ${user.uangSaatIni.toLocaleString()}</p>
        <p><strong>Target Investasi Bulanan:</strong> Rp ${user.targetInvestasi.toLocaleString()}</p>
        <p><strong>Return Investasi (per tahun):</strong> ${user.returnInvestasi}%</p>
        <p><strong>Waktu Investasi:</strong> ${user.waktuDibutuhkan} tahun</p>
        <p><strong>Target Dana:</strong> Rp ${user.targetUang.toLocaleString()}</p>
      </div>
    `;
    document.getElementById("inputUser").innerHTML = inputHTML;
}

// Render hasil investasi dan analisa
function renderInvestmentResult(data) {
    const hasilHTML = `
      <p><strong>Total Hasil Investasi:</strong> Rp ${data.hasilInvestasi.toLocaleString()}</p>
      <p><strong>Total Uang Dibutuhkan:</strong> Rp ${data.totalUangDibutuhkan.toLocaleString()}</p>
    `;
    document.getElementById("hasilAnalisa").innerHTML = hasilHTML;
}

// Render saran investasi berdasarkan profil risiko
function renderInvestmentAdvice(resiko) {
    const adviceHTML = `
        <p><strong>Profil Risiko:</strong> ${resiko}</p>
    `;
    document.getElementById("resiko").innerHTML = adviceHTML;
}

// rekomendasi
function renderRecommendations(rekomendasi) {
    const container = document.getElementById('saran');

    if (!container) {
        console.error('Element tidak ditemukan di HTML!');
        return;
    }

    container.innerHTML = ''; // Bersihkan dulu sebelum render baru

    rekomendasi.forEach((item, index) => {
        const div = document.createElement('div');
        div.classList.add('recommendation-card');
        div.innerHTML = `
            <h2>${index + 1}. ${item.investment_type}</h2>
            <p>Return: ${item.return_rate}%</p>
            <p>Risiko: ${item.risk_level}</p>
        `;
        container.appendChild(div);
    });
}


// Ambil data dari localStorage dan render ke halaman
function loadInvestmentCalculation() {
    const storedData = localStorage.getItem('calculatorResult');

    if (!storedData) {
        renderResponseMessage('❌ Data kalkulasi tidak ditemukan.');
        return;
    }

    const data = JSON.parse(storedData);

    if (data.message) {
        renderResponseMessage(data.message);
    }

    if (data.inputUser) {
        renderUserInput(data.inputUser);
    }

    if (data.hasilInvestasi && data.totalUangDibutuhkan) {
        renderInvestmentResult(data);
    } else {
        renderResponseMessage('❌ Data hasil kalkulasi tidak lengkap.');
    }

    if (data.risk_profile) {
        renderInvestmentAdvice(data.risk_profile.resiko, data.risk_profile.keterangan);
    } else {
        renderResponseMessage('❌ Profil risiko tidak ditemukan.');
    }

    if (data.rekomendasi && Array.isArray(data.rekomendasi)) {
        renderRecommendations(data.rekomendasi);
    }
}



// Jalankan saat halaman dimuat
window.addEventListener("DOMContentLoaded", loadInvestmentCalculation);
