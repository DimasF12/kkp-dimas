document.addEventListener("DOMContentLoaded", () => {
    // --- Deklarasi Elemen DOM ---
    const transactionForm = document.getElementById("transactionForm");
    const transactionIdInput = document.getElementById("transactionId");
    const typeInput = document.getElementById("type");
    const categoryIdInput = document.getElementById("category_id"); // Deklarasi baru untuk Kategori
    const amountInput = document.getElementById("amount");
    const dateInput = document.getElementById("date");
    const descriptionInput = document.getElementById("description");
    
    const filterTypeEl = document.getElementById("filterType");
    const filterDateEl = document.getElementById("filterDate");
    const applyFiltersBtn = document.getElementById("applyFilters");

    const transactionsContainer = document.getElementById("transactionsContainer");
    const totalIncomeEl = document.getElementById("total_income");
    const totalExpenseEl = document.getElementById("total_expense");
    const balanceEl = document.getElementById("balance");

    const saveButton = transactionForm.querySelector('button[type="submit"]');
    const viewAnalysisBtn = document.getElementById('viewAnalysisBtn');

    let isEditMode = false;
    let allCategories = []; // Variabel global untuk menyimpan semua kategori dari backend

    // --- Validasi Elemen HTML ---
    if (!transactionForm || !filterTypeEl || !filterDateEl || !applyFiltersBtn || !transactionsContainer ||
        !transactionIdInput || !typeInput || !amountInput || !dateInput || !descriptionInput || !categoryIdInput || // Tambah categoryIdInput
        !totalIncomeEl || !totalExpenseEl || !balanceEl || !saveButton || !viewAnalysisBtn) {
        console.error("Some elements are missing in the HTML. Please check all IDs.");
        return;
    }

    // --- Event Listeners Awal ---
    transactionForm.addEventListener("submit", handleSubmitTransaction);
    filterDateEl.addEventListener("change", loadTransactions);
    filterTypeEl.addEventListener("change", loadTransactions);
    applyFiltersBtn.addEventListener("click", loadTransactions);

    // Event listener untuk perubahan Tipe Transaksi (untuk memfilter kategori)
    typeInput.addEventListener("change", () => {
        populateCategoriesDropdown(typeInput.value);
    });

    // Event listener untuk tombol "Lihat Hasil Analisa"
    viewAnalysisBtn.addEventListener('click', () => {
        window.location.href = 'analisa.html';
    });

    // --- Inisialisasi: Muat Kategori dan Transaksi ---
    initMoneyTracker(); // Panggil fungsi inisialisasi baru

    // --- Fungsi Inisialisasi ---
    async function initMoneyTracker() {
        await fetchAndPopulateCategories(); // Ambil dan isi kategori terlebih dahulu
        await loadTransactions(); // Lalu muat transaksi
    }

    // --- Fungsi Utilitas ---
    const formatRupiah = (amount) => {
        return new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: 'IDR',
            minimumFractionDigits: 0
        }).format(amount);
    };

    // --- FUNGSI BARU: Mengambil Kategori dari Backend ---
    async function fetchAndPopulateCategories() {
        const url = "https://nhkdqrpw-8000.asse.devtunnels.ms/categories/"; // Endpoint Anda untuk kategori

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
                    throw new Error(errorData.detail || `Gagal memuat kategori: ${response.status}`);
                }
            }

            allCategories = await response.json(); // Simpan semua kategori
            populateCategoriesDropdown(typeInput.value); // Isi dropdown sesuai tipe awal (atau kosong)

        } catch (error) {
            console.error("Error fetching categories:", error);
            alert("Terjadi masalah saat memuat kategori. Silakan coba lagi nanti.");
            allCategories = [];
        }
    }

    // --- FUNGSI BARU: Mengisi Dropdown Kategori ---
    function populateCategoriesDropdown(selectedType) {
        categoryIdInput.innerHTML = '<option value="">Pilih Kategori</option>'; // Reset dropdown

        const filteredCategories = allCategories.filter(cat => {
            if (!selectedType) return cat.is_default; // Tampilkan hanya default jika belum ada tipe yang dipilih
            return cat.type === 'both' || cat.type === selectedType;
        });

        filteredCategories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.id; // Nilai opsi adalah ID kategori
            option.textContent = category.name;
            categoryIdInput.appendChild(option);
        });
    }

    // --- Fungsi Utama: Memuat Transaksi ---
    async function loadTransactions() {
        const dateFilter = filterDateEl.value;
        const typeFilter = filterTypeEl.value;

        let url = "https://nhkdqrpw-8000.asse.devtunnels.ms/transactions/transactions/";
        const params = new URLSearchParams();

        if (dateFilter) {
            params.append("date", dateFilter);
        }
        if (typeFilter) {
            params.append("type", typeFilter === "income" ? "true" : "false");
        }
        
        if (params.toString()) {
            url += `?${params.toString()}`;
        }

        try {
            const response = await fetch(url, {
                credentials: "include",
            });

            if (!response.ok) {
                if (response.status === 401) {
                    alert("Silakan login terlebih dahulu!");
                    window.location.href = "/login.html";
                } else {
                    const errorData = await response.json();
                    alert(`Error: ${errorData.detail || "Terjadi kesalahan saat memuat transaksi."}`);
                }
                return;
            }

            const transactions = await response.json();
            transactionsContainer.innerHTML = "";

            let totalIncome = 0;
            let totalExpense = 0;

            if (transactions.length === 0) {
                transactionsContainer.innerHTML = '<p class="text-center text-gray-500 py-10">Belum ada transaksi.</p>';
            } else {
                const sortedTransactions = [...transactions].sort((a, b) => new Date(b.date) - new Date(a.date));

                sortedTransactions.forEach(transaction => {
                    const isIncome = transaction.transaction_type === true; // Menggunakan transaction_type
                    const amountDisplay = formatRupiah(transaction.amount);
                    const typeDisplay = isIncome ? 'Pendapatan' : 'Pengeluaran';
                    const amountClass = isIncome ? 'text-green-600' : 'text-red-600';
                    
                    // Dapatkan nama kategori dari allCategories berdasarkan category_id
                    const categoryName = allCategories.find(cat => cat.id === transaction.category_id)?.name || 'Tidak Diketahui';

                    const transactionElement = document.createElement("div");
                    transactionElement.classList.add("transaction-item", "flex", "justify-between", "items-center", "p-4", "mb-4", "rounded-lg", "shadow-md", "bg-white", "border", "border-gray-200");
                    
                    transactionElement.innerHTML = `
                        <div class="transaction-details flex flex-col">
                            <p class="text-lg font-semibold ${amountClass}">${isIncome ? '+' : '-'} ${amountDisplay}</p>
                            <p class="text-sm text-gray-600">${transaction.description || 'N/A'}</p>
                            <p class="text-xs text-gray-400">${new Date(transaction.transaction_date).toLocaleDateString('id-ID', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
                            <p class="text-xs text-gray-400">Tipe: ${typeDisplay} | Kategori: ${categoryName}</p>
                        </div>
                        <div class="transaction-actions flex space-x-2">
                            <button onclick="editTransaction(${transaction.id}, ${transaction.transaction_type}, ${transaction.amount}, '${transaction.transaction_date}', '${transaction.description || ''}', ${transaction.category_id})" 
                                class="edit-btn main-button px-4 py-2 bg-yellow-500 hover:bg-yellow-600">Edit</button>
                            <button onclick="deleteTransaction(${transaction.id})" 
                                class="delete-btn secondary-button px-4 py-2">Delete</button>
                        </div>
                    `;

                    transactionsContainer.appendChild(transactionElement);

                    if (isIncome) totalIncome += transaction.amount;
                    else totalExpense += transaction.amount;
                });
            }

            updateFinancialSummary(totalIncome, totalExpense);

        } catch (error) {
            console.error("Error loading transactions:", error);
            alert("Gagal menghubungi server atau memuat transaksi.");
        }
    }

    function updateFinancialSummary(income, expense) {
        const balance = income - expense;
        totalIncomeEl.textContent = formatRupiah(income);
        totalExpenseEl.textContent = formatRupiah(expense);
        balanceEl.textContent = formatRupiah(balance);
    }

    async function handleSubmitTransaction(e) {
        e.preventDefault();

        const transactionId = transactionIdInput.value;
        const typeValue = typeInput.value;
        const transaction_type = typeValue === "income"; // Gunakan transaction_type
        const amount = parseFloat(amountInput.value);
        const transaction_date = dateInput.value; // Gunakan transaction_date
        const description = descriptionInput.value;
        const category_id = parseInt(categoryIdInput.value); // Ambil ID kategori

        if (!typeValue || isNaN(amount) || !transaction_date || !category_id) { // Validasi category_id
            alert("Semua field wajib diisi!");
            return;
        }
        if (amount <= 0) {
            alert("Jumlah harus lebih besar dari nol.");
            return;
        }

        const transactionData = { 
            transaction_type, // Kirim transaction_type
            amount, 
            transaction_date, // Kirim transaction_date
            description,
            category_id // Kirim category_id
        };

        let url = "https://nhkdqrpw-8000.asse.devtunnels.ms/transactions/transactions";
        let method = "POST";

        if (transactionId) {
            url += `/${transactionId}`;
            method = "PUT";
        }

        try {
            const response = await fetch(url, {
                method,
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include",
                body: JSON.stringify(transactionData),
            });

            const result = await response.json();
            if (response.ok) {
                alert(`Transaksi berhasil ${transactionId ? 'diperbarui' : 'ditambahkan'}!`);
                loadTransactions();
                cancelEdit();
            } else {
                alert(`Error: ${result.detail || "Terjadi kesalahan saat menyimpan transaksi."}`);
            }
        } catch (error) {
            console.error("Fetch error:", error);
            alert("Gagal menghubungi server.");
        }
    }

    // --- Fungsi CRUD Global ---
    window.deleteTransaction = async function(id) {
        const confirmDelete = confirm("Apakah kamu yakin ingin menghapus transaksi ini?");
        if (!confirmDelete) return;

        try {
            const response = await fetch(`https://nhkdqrpw-8000.asse.devtunnels.ms/transactions/transactions/${id}`, {
                method: "DELETE",
                credentials: "include",
            });

            if (response.status === 204) {
                alert("Transaksi berhasil dihapus!");
                loadTransactions();
            } else {
                const result = await response.json();
                alert(`Error: ${result.detail || "Terjadi kesalahan saat menghapus transaksi."}`);
            }

        } catch (error) {
            console.error("Fetch error:", error);
            alert("Gagal menghubungi server.");
        }
    };



    // Fungsi editTransaction yang diperbarui untuk scroll dan kategori
    window.editTransaction = function(id, type, amount, date, description, category_id) { // Tambah category_id
        transactionIdInput.value = id;
        typeInput.value = type ? "income" : "expense"; // Sesuaikan nilai boolean
        amountInput.value = amount;
        dateInput.value = date;
        descriptionInput.value = description;
        populateCategoriesDropdown(typeInput.value);
        categoryIdInput.value = category_id; 

        isEditMode = true;
        saveButton.textContent = "Perbarui Transaksi 🔄";

        transactionForm.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    };
    
    window.cancelEdit = function() {
        transactionIdInput.value = "";
        transactionForm.reset();
        isEditMode = false;
        saveButton.textContent = "Simpan 💾";
        populateCategoriesDropdown(typeInput.value); // Reset dropdown kategori
    }
});