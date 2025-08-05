document.addEventListener("DOMContentLoaded", () => {
    const backButton = document.querySelector('.back-button');
    backButton.addEventListener('click', function () {
        window.location.href = ('index.html');
    });

    const form = document.getElementById("dandur-form");
    if (!form) {
      console.error("Form tidak ditemukan!");
      return;
    }
  
    let sudahMenikah = false; // Default status pernikahan
  
    // Pastikan tombol status ditemukan
    const statusButtons = document.querySelectorAll(".status-button");
    if (statusButtons.length === 0) {
      console.error("Tombol status pernikahan tidak ditemukan!");
      return;
    }
  
    // Menangani klik tombol status pernikahan
    statusButtons.forEach(button => {
      button.addEventListener("click", function () {
        // Hapus kelas 'active' dari semua tombol
        document.querySelectorAll(".status-button").forEach(btn => btn.classList.remove("active"));
        
        // Tambahkan kelas 'active' ke tombol yang diklik
        this.classList.add("active");
  
        // Set nilai status berdasarkan tombol yang diklik
        sudahMenikah = this.getAttribute("value") === "true";
      });
    });
  
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const calculateBtn = document.querySelector('.dandur-btn');
  
      // Ambil data dari form
      const pengeluaranWajib = parseFloat(document.getElementById("pengeluaran").value.replace(/\./g, ''));
      const jumlahTanggungan = parseInt(document.getElementById("tanggungan").value);
      const waktuPengumpulan = parseInt(document.getElementById("waktu").value);
      const danaDaruratSaatIni = parseFloat(document.getElementById("dana_saat_ini").value.replace(/\./g, ''));
      const targetInvestasiBulanan = parseFloat(document.getElementById("target_investasi").value.replace(/\./g, ''));
      const returnInvestasi = parseFloat(document.getElementById("return_investasi").value.replace(/\./g, ''));
  
      // Siapkan body request untuk dikirim ke backend
      const requestBody = {
        pengeluaran_wajib: pengeluaranWajib,
        sudah_menikah: sudahMenikah,  // Gunakan status pernikahan yang dipilih
        jumlah_tanggungan: jumlahTanggungan,
        waktu_pengumpulan_bulan: waktuPengumpulan,
        dana_darurat_saat_ini: danaDaruratSaatIni,
        target_investasi_bulanan: targetInvestasiBulanan,
        return_investasi: returnInvestasi
      };
      calculateBtn.disabled = true;
      calculateBtn.innerHTML = 'Calculating...';
  
      try {
        const response = await fetch("http://localhost:8000/dandur/calculate", {
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
        localStorage.setItem("dandurResult", JSON.stringify(finalData));
  
        // Redirect ke halaman hasil
        window.location.href = "hasil_dana-darurat.html";
      } catch (error) {
        alert("❌ Terjadi kesalahan: " + error.message);
      }finally {
        calculateBtn.disabled = false;
        calculateBtn.innerHTML = 'Ayo Cek Investasi Mu <i class="fa-solid fa-bullseye" style="margin: 7px;"></i>';
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
  