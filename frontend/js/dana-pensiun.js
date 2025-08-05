document.addEventListener("DOMContentLoaded", () => {
  const backButton = document.querySelector('.back-button');
  backButton.addEventListener('click', function () {
      window.location.href = ('index.html');
  });

  const form = document.getElementById("pensiunForm");
  if (!form) {
    console.error("Form tidak ditemukan!");
    return;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const calculateBtn = document.querySelector('.danpen-btn');

    // Ambil data dari form
    const pengeluaranBulanan = parseFloat(document.getElementById("pengeluaran_bulanan").value.replace(/\./g, ''));
    const usia = parseInt(document.getElementById("usia_saat_ini").value);
    const targetPensiun = parseInt(document.getElementById("target_usia_pensiun").value);
    const inflasi = parseInt(document.getElementById("inflasi").value.replace(/\./g, ''));
    const danaSaatIni = parseFloat(document.getElementById("dana_pensiun_saat_ini").value.replace(/\./g, ''));
    const targetInvestasiBulanan = parseFloat(document.getElementById("target_investasi_bulanan").value.replace(/\./g, ''));
    const returnInvestasi = parseFloat(document.getElementById("return_investasi").value.replace(/\./g, ''));

    // Siapkan body request untuk dikirim ke backend
    const requestBody = {
      pengeluaran_bulanan: pengeluaranBulanan,
      usia_saat_ini: usia,  
      target_usia_pensiun: targetPensiun,
      inflasi: inflasi,
      dana_pensiun_saat_ini: danaSaatIni,
      target_investasi_bulanan: targetInvestasiBulanan,
      return_investasi: returnInvestasi
    };
    calculateBtn.disabled = true;
    calculateBtn.innerHTML = 'Calculating...';
    try {
      const response = await fetch("http://localhost:8000/danpen/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error("Gagal menghitung dana darurat.");
      }

      const result = await response.json();

      const finalData = {
        message: "✅ Kalkulasi dana darurat berhasil.",
        inputUser: requestBody,
        hasil: result
      };

      // Simpan ke localStorage
      localStorage.setItem("danpenResult", JSON.stringify(finalData));

      // Redirect ke halaman hasil
      window.location.href = "hasil_dana-pensiun.html";
    } catch (error) {
      alert("❌ Terjadi kesalahan: " + error.message);
    }finally {
      calculateBtn.disabled = false;
      calculateBtn.innerHTML = 'Ayo Cek Investasi Mu <i class="fa-solid fa-bullseye" style="margin: 7px;"></i>';
  }
  });

  // menambahkan atribut titik
  const currencyInputs = document.querySelectorAll('.input-field input:not(.years-input):not(.percent-input)');
  currencyInputs.forEach(input => {
      input.addEventListener('input', function () {
          let value = this.value.replace(/\D/g, '');
          if (value.length > 3) {
              value = value.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
          }
          this.value = value;
      });
  });

  const numberInputs = document.querySelectorAll('.years-input, .percent-input');
  numberInputs.forEach(input => {
      input.addEventListener('input', function () {
          this.value = this.value.replace(/\D/g, '');
      });
  });
});
