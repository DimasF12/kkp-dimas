document.addEventListener('DOMContentLoaded', () => {
    // --- Deklarasi Elemen DOM ---
    const analysisPeriodSelect = document.getElementById('analysisPeriod');
    const incomeExpensePieChartElement = document.getElementById('incomeExpensePieChart');
    if (!incomeExpensePieChartElement) {
        console.error("Error: Elemen canvas untuk Pie Chart tidak ditemukan di HTML.");
        return; 
    }
    const incomeExpensePieChartCanvas = incomeExpensePieChartElement.getContext('2d');
    const mlInsightsContainer = document.getElementById('mlInsightsContainer');
    const noInsightsMessage = document.getElementById('noInsightsMessage');
    const conclusionContent = document.getElementById('conclusionContent');

    const cumulativeBalanceElement = document.getElementById('cumulativeBalance');
    const emergencyFundRatioElement = document.getElementById('emergencyFundRatio');
    const totalSavingsAmountElement = document.getElementById('totalSavingsAmount');
    const savingsRateElement = document.getElementById('savingsRate');

    const chartUnavailableMessage = document.getElementById('chartUnavailableMessage');

    const savingsProjectionChartElement = document.getElementById('savingsProjectionChart');
    if (!savingsProjectionChartElement) {
        console.error("Error: Elemen canvas untuk Proyeksi Tabungan tidak ditemukan di HTML.");
        return;
    }
    const savingsProjectionChartCanvas = savingsProjectionChartElement.getContext('2d');
    const savingsProjectionUnavailableMessage = document.getElementById('savingsProjectionUnavailableMessage');

    const infoIcons = document.querySelectorAll('.info-icon');
    let activePopup = null;

    let userRiskProfile = localStorage.getItem('monifyRiskProfile') || 'medium';
    let userInvestmentGoal = localStorage.getItem('monifyInvestmentGoal') || 'long_term_growth';

    let incomeExpenseChart;
    let savingsProjectionChart; 
    let allCategories = []; // Variabel global untuk menyimpan semua kategori


    // --- FUNGSI: Mengambil Kategori dari Backend (Ditinggikan ke scope DOMContentLoaded) ---
    async function fetchAndCacheCategories() {
        const url = "http://127.0.0.1:8000/categories/";

        try {
            const response = await fetch(url, { credentials: "include" });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Gagal memuat kategori: ${response.status}`);
            }
            allCategories = await response.json();
        } catch (error) {
            console.error("Error fetching categories:", error);
            alert("Terjadi masalah saat memuat kategori. Analisa mungkin tidak akurat.");
            allCategories = [];
        }
    }


    // --- Mengambil Data Analisis dari Backend (Diperbarui untuk memanggil endpoint analisis baru) ---
    async function fetchAnalysisDataFromBackend(period) {
        // PERBAIKAN: Memanggil endpoint analisis yang baru di backend
        const url = `http://127.0.0.1:8000/analysis/analysis/insights/?period=${period}`; // Endpoint GET dengan parameter period

        try {
            const response = await fetch(url, {
                credentials: "include",
            });

            if (!response.ok) {
                if (response.status === 401) {
                    alert("Sesi berakhir atau Anda belum login. Silakan login kembali.");
                    window.location.href = "/login.html";
                } else {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `Gagal memuat data analisis: ${response.status}`);
                }
            }

            const data = await response.json();
            return data; // Backend akan mengembalikan objek yang sudah terstruktur
        } catch (error) {
            console.error("Error fetching analysis data:", error);
            alert("Terjadi masalah saat memuat data analisis Anda. Silakan coba lagi nanti.");
            return null; // Mengembalikan null jika ada error
        }
    }

    const formatRupiah = (amount) => {
        return new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: 'IDR',
            minimumFractionDigits: 0
        }).format(amount);
    };

    // Fungsi ini tidak lagi memfilter, hanya mempersiapkan data untuk pie chart
    const preparePieChartData = (incomeTotal, expenseTotal) => { 
        const mainLabels = ['Pemasukan', 'Pengeluaran'];
        const mainData = [incomeTotal, expenseTotal];
        const mainColors = ['#2AFF51', '#FD2121'];
        return { mainLabels, mainData, mainColors };
    };

    const renderPieChart = (labels, data, colors) => {
        if (incomeExpenseChart) {
            incomeExpenseChart.destroy();
        }
        incomeExpenseChart = new Chart(incomeExpensePieChartCanvas, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{ data: data, backgroundColor: colors, hoverOffset: 10 }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { font: { family: 'Inter', size: 14 }, color: '#333' } },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                if (label) { label += ': '; }
                                if (context.parsed !== null) {
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = (context.parsed / total * 100).toFixed(1);
                                    label += formatRupiah(context.parsed) + ' (' + percentage + '%)';
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });
    };

    // --- FUNGSI TAMPILAN PROYEKSI TABUNGAN (Diperbarui untuk menerima data dari backend) ---
    const renderSavingsProjectionChart = (projectionData) => {
        if (savingsProjectionChart) {
            savingsProjectionChart.destroy();
        }

        if (!projectionData || projectionData.length === 0) {
            savingsProjectionChartElement.style.display = 'none';
            savingsProjectionUnavailableMessage.classList.remove('hidden');
            savingsProjectionUnavailableMessage.textContent = 'Tidak ada cukup data historis untuk proyeksi.';
            return;
        } else {
            savingsProjectionChartElement.style.display = 'block';
            savingsProjectionUnavailableMessage.classList.add('hidden');
        }

        const labels = projectionData.map(d => {
            const dateObj = new Date(d.date);
            return dateObj.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' });
        });

        const data = projectionData.map(d => d.predicted_balance);

        savingsProjectionChart = new Chart(savingsProjectionChartCanvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Proyeksi Saldo',
                    data: data,
                    borderColor: 'var(--monify-blue-primary)',
                    backgroundColor: 'rgba(47, 128, 237, 0.2)',
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', labels: { color: 'var(--monify-text-dark)' } },
                    tooltip: { callbacks: { label: function(context) { return `Saldo: ${formatRupiah(context.parsed.y)}`; } } }
                },
                scales: {
                    x: { grid: { display: false }, ticks: { color: 'var(--monify-text-dark)' } },
                    y: {
                        grid: { color: 'var(--monify-gray-light)' },
                        ticks: {
                            callback: function(value) { return formatRupiah(value); },
                            color: 'var(--monify-text-dark)'
                        }
                    }
                }
            }
        });
    };

    // --- FUNGSI UTAMA: updateAnalysis (Sekarang Memanggil Backend untuk Semua Data Analisis) ---
    const updateAnalysis = async () => {
        if (!incomeExpensePieChartElement) {
            console.error("Error: Elemen canvas untuk Pie Chart tidak ditemukan di HTML.");
            return; 
        }

        const selectedPeriod = analysisPeriodSelect.value;
        const analysisResults = await fetchAnalysisDataFromBackend(selectedPeriod); // Panggil fungsi baru

        if (!analysisResults) { // Jika ada error saat fetch
            // Set semua UI ke state error/kosong
            incomeExpensePieChartElement.style.display = 'none';
            if (chartUnavailableMessage) {
                chartUnavailableMessage.classList.remove('hidden');
                chartUnavailableMessage.textContent = 'Gagal memuat data analisis. Silakan coba lagi.';
            }
            mlInsightsContainer.innerHTML = `<p class="text-center text-red-500 py-10">Gagal memuat wawasan. Coba lagi nanti.</p>`;
            cumulativeBalanceElement.textContent = formatRupiah(0);
            emergencyFundRatioElement.textContent = `0.0 Bulan Pengeluaran`;
            totalSavingsAmountElement.textContent = formatRupiah(0);
            savingsRateElement.textContent = `0.0% dari Pemasukan`;
            conclusionContent.innerHTML = `<p class="text-red-500">Gagal memuat kesimpulan.</p>`;
            
            if (savingsProjectionChart) savingsProjectionChart.destroy();
            savingsProjectionChartElement.style.display = 'none';
            if (savingsProjectionUnavailableMessage) {
                savingsProjectionUnavailableMessage.classList.remove('hidden');
                savingsProjectionUnavailableMessage.textContent = 'Gagal memuat proyeksi.';
            }
            return; // Keluar dari fungsi jika gagal memuat data analisis
        }

        // --- Update UI dengan data dari backend ---

        // 1. Chart Pemasukan & Pengeluaran
        const { income_total_filtered, expense_total_filtered } = analysisResults.summary_metrics;
        if (income_total_filtered === 0 && expense_total_filtered === 0) {
            incomeExpensePieChartElement.style.display = 'none';
            if (chartUnavailableMessage) {
                chartUnavailableMessage.classList.remove('hidden');
                chartUnavailableMessage.textContent = 'Tidak ada data untuk periode ini.';
            }
        } else {
            incomeExpensePieChartElement.style.display = 'block';
            if (chartUnavailableMessage) {
                chartUnavailableMessage.classList.add('hidden');
            }
            renderPieChart(
                ['Pemasukan', 'Pengeluaran'],
                [income_total_filtered, expense_total_filtered],
                ['#2AFF51', '#FD2121']
            );
        }
        
        // 2. Metrik Keuangan Utama
        cumulativeBalanceElement.textContent = formatRupiah(analysisResults.summary_metrics.cumulative_balance);
        emergencyFundRatioElement.textContent = `${analysisResults.summary_metrics.emergency_fund_ratio.toFixed(1)} Bulan Pengeluaran`;
        totalSavingsAmountElement.textContent = formatRupiah(analysisResults.summary_metrics.net_balance_filtered);
        savingsRateElement.textContent = `${analysisResults.summary_metrics.savings_rate_filtered.toFixed(1)}% dari Pemasukan`;

        if (analysisResults.summary_metrics.net_balance_filtered <= 0) {
            totalSavingsAmountElement.style.color = 'var(--monify-red-primary)';
        } else {
            totalSavingsAmountElement.style.color = 'var(--monify-blue-dark)';
        }

        // 3. Wawasan dari MONIFY AI (Insights)
        mlInsightsContainer.innerHTML = ''; // Kosongkan dulu
        if (analysisResults.insights.length === 0) {
            noInsightsMessage.classList.remove('hidden');
            noInsightsMessage.textContent = 'Tidak ada wawasan baru untuk periode ini.';
        } else {
            noInsightsMessage.classList.add('hidden');
            analysisResults.insights.forEach(insight => {
                const insightCard = document.createElement('div');
                insightCard.classList.add('insight-card');
                insightCard.innerHTML = `
                    <h3 class="insight-title">${insight.title}</h3>
                    <p class="insight-text">${insight.description}</p>
                `;
                mlInsightsContainer.appendChild(insightCard);
            });
        }

        // 4. Proyeksi Tabungan
         console.log("Data proyeksi yang diterima:", analysisResults.projection_data);
        renderSavingsProjectionChart(analysisResults.projection_data);

        // 5. Kesimpulan
        renderConclusion(analysisResults.conclusion);
        function renderConclusion(conclusion) {
            if (conclusion && typeof conclusion === "object" && conclusion.text) {
                conclusionContent.innerHTML = `
                    <p class="font-semibold">Kesimpulan: ${conclusion.text}</p>
                    <p class="mt-2">${conclusion.reason}</p>
                `;
            } else {
                conclusionContent.innerHTML = `
                    <p class="text-red-500">Gagal memuat Kesimpulan</p>
                `;
            }
        }
    };

    // --- Event Listener dropdown dan popup ---
    analysisPeriodSelect.value = 'last_month';
    analysisPeriodSelect.addEventListener('change', updateAnalysis);

    infoIcons.forEach(icon => {
        icon.addEventListener('click', (event) => {
            const popupId = icon.dataset.popupId;
            const popup = document.getElementById(popupId);

            if (activePopup && activePopup !== popup) {
                activePopup.classList.remove('show');
            }

            popup.classList.toggle('show');
            activePopup = popup.classList.contains('show') ? popup : null;

            event.stopPropagation();
        });
    });

    document.addEventListener('click', (event) => {
        if (activePopup && !activePopup.contains(event.target)) {
            activePopup.classList.remove('show');
            activePopup = null;
        }
    });

    const backButton = document.querySelector('.back-button');
    if (backButton) {
        backButton.addEventListener('click', () => {
            history.back();
        });
    }

    // --- Inisialisasi Halaman ---
    async function initAnalysisPage() {
        await fetchAndCacheCategories(); // Pastikan kategori dimuat dulu
        updateAnalysis(); // Lalu panggil updateAnalysis
    }
    initAnalysisPage();
});