document.addEventListener('DOMContentLoaded', function () {
    const backButton = document.querySelector('.back-button');
    backButton.addEventListener('click', function () {
        window.location.href = ('index.html');
    });

    const calculateBtn = document.querySelector('.calculate-btn');
    const inputFields = document.querySelectorAll('.input-field input');

    calculateBtn.addEventListener('click', async function () {
        let isValid = true;

        inputFields.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                input.style.borderBottom = '1px solid red';
            } else {
                input.style.borderBottom = '1px solid black';
            }
        });

        if (!isValid) {
            alert('Semua kolom wajib diisi!');
            return;
        }

        // Ambil nilai input dan bersihkan
        const [uangCapaiInput, waktuInput, uangSaatIniInput, targetInvestasiInput, returnInvestasiInput] = inputFields;

        const uangCapai = parseFloat(uangCapaiInput.value.replace(/\./g, ''));
        const waktu = parseInt(waktuInput.value);
        const uangSaatIni = parseFloat(uangSaatIniInput.value.replace(/\./g, ''));
        const targetInvestasi = parseFloat(targetInvestasiInput.value.replace(/\./g, ''));
        const returnInvestasi = parseFloat(returnInvestasiInput.value);

        const requestBody = {
            uangSaatIni,
            targetInvestasi,
            returnInvestasi,
            waktu,
            uangCapai
        };

        calculateBtn.disabled = true;
        calculateBtn.innerHTML = 'Calculating...';

        try {
            const response = await fetch("http://localhost:8000/calculator/calculator", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(requestBody)
            });

            const data = await response.json();

            if (response.ok) {
                // Simpan hasil ke localStorage
                localStorage.setItem('calculatorResult', JSON.stringify(data));

                // Alihkan ke halaman hasil_calculator.html
                window.location.href = 'hasil_calculator.html';
            } else {
                document.getElementById('error-message').innerHTML = "Terjadi kesalahan: " + data.detail;
            }
        } catch (err) {
            document.getElementById('error-message').innerHTML = "Gagal terhubung ke server: " + err.message;
        } finally {
            calculateBtn.disabled = false;
            calculateBtn.innerHTML = 'Ayo Cek Investasi Mu <i class="fa-solid fa-bullseye" style="margin: 7px;"></i>';
        }
    });

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
