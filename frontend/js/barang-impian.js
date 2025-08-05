document.addEventListener("DOMContentLoaded", () => {
    const backButton = document.querySelector('.back-button');
    backButton.addEventListener('click', function () {
        window.location.href = ('index.html');
    });

    const form = document.getElementById("barang_impian-form");
    if (!form) {
      console.error("Form tidak ditemukan!");
      return;
    }
  
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const calculateBtn = document.querySelector('.barang_impian-btn');
  
      // Ambil data dari form
      const target_bulan = parseInt(document.getElementById("target_bulan").value);
      const harga_barang = parseFloat(document.getElementById("harga_barang").value.replace(/\./g, ''));
      const dp_barang = parseInt(document.getElementById("dp_barang").value);
      const inflasi = parseInt(document.getElementById("inflasi").value);
      const targetInvestasiBulanan = parseFloat(document.getElementById("target_investasi").value.replace(/\./g, ''));
      const returnInvestasi = parseFloat(document.getElementById("return_investasi").value.replace(/\./g, ''));
  
      // Siapkan body request untuk dikirim ke backend
      const requestBody = {
        waktu_target_bulan: target_bulan,
        harga_barang: harga_barang, 
        dp_persen: dp_barang,
        inflasi: inflasi,
        investasi_bulanan: targetInvestasiBulanan,
        return_investasi: returnInvestasi
      };
      calculateBtn.disabled = true;
      calculateBtn.innerHTML = 'Calculating...';
  
      try {
        const response = await fetch("http://localhost:8000/barangimpian/calculate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(requestBody),
        });
  
        if (!response.ok) {
          throw new Error("Gagal menghitung barang impian.");
        }
  
        const result = await response.json();
  
        const finalData = {
          message: "✅ Kalkulasi barang impian berhasil.",
          inputUser: requestBody,
          hasil: result
        };
  
        // Simpan ke localStorage
        localStorage.setItem("impianResult", JSON.stringify(finalData));
  
        // Redirect ke halaman hasil
        window.location.href = "hasil_barang-impian.html";
      } catch (error) {
        alert("❌ Terjadi kesalahan: " + error.message);
      }finally {
        calculateBtn.disabled = false;
        calculateBtn.innerHTML = 'Ayo Cek Analisa Mu <i class="fa-solid fa-bullseye" style="margin: 7px;"></i>';
    }
    });

    // menambahkan atribut titik
    const currencyInputs = document.querySelectorAll('.input-field input:not(.month-input):not(.percent-input):not(.people-input)');
    currencyInputs.forEach(input => {
        input.addEventListener('input', function () {
            let value = this.value.replace(/\D/g, '');
            if (value.length > 3) {
                value = value.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
            }
            this.value = value;
        });
    });

    const numberInputs = document.querySelectorAll('.month-input, .percent-input, .people-input');
    numberInputs.forEach(input => {
        input.addEventListener('input', function () {
            this.value = this.value.replace(/\D/g, '');
        });
    });
  });
  