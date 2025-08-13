// Data Services dengan icon Font Awesome
const services = [
    {
        icon: 'fas fa-money-bill-wave fa-2xl',
        title: 'Money Tracker',
        description: 'Lacak pengeluaran harian'
    },
    {
        icon: 'fas fa-calculator fa-2xl',
        title: 'Kalkulator Investasi',
        description: 'Hitung potensi keuntungan'
    },
    {
        icon: 'fas fa-piggy-bank fa-2xl',
        title: 'Dana Darurat',
        description: 'Siapkan dana tak terduga'
    },
    {
        icon: 'fas fa-person-cane fa-2xl',
        title: 'Dana Pensiun',
        description: 'Persiapan masa depan'
    },
    {
        icon: 'fas fa-shopping-bag fa-2xl',
        title: 'Barang Impian',
        description: 'Rencanakan pembelian'
    },
    {
        icon: 'fas fa-right-from-bracket fa-2xl',
        title: 'Logout',
        description: 'Keluar dari aplikasi'
    }
];

// DOM Elements
const servicesGrid = document.getElementById('servicesGrid');
const profileCard = document.getElementById('profileCard');
const themeToggle = document.getElementById('themeToggle');
const backButton = document.getElementById('backButton');

// Ambil data user dari backend
async function getCurrentUser() {
    try {
        const res = await fetch('https://nhkdqrpw-8000.asse.devtunnels.ms/auth/me', {
            method: 'GET',
            credentials: 'include',  // <- ini wajib!
        });
        if (!res.ok) throw new Error('Not authenticated');
        return await res.json();
    } catch {
        return null;
    }
}

// Cek apakah user sudah login
async function isAuthenticated() {
    const user = await getCurrentUser();
    return user !== null;
}

// Logout user
async function logout() {
    try {
        const response = await fetch("https://nhkdqrpw-8000.asse.devtunnels.ms/auth/logout", {
            method: 'POST',
            credentials: 'include'
        });
        if (response.ok) {
            alert("Logout berhasil!");
            window.location.reload();
        } else {
            alert("Logout gagal!");
        }
    } catch (error) {
        alert("Terjadi kesalahan saat logout!");
    }
}

// Toggle dark mode
function toggleDarkMode() {
    const themeIcon = document.getElementById('themeIcon');
    const currentTheme = document.documentElement.getAttribute('data-theme');
    themeIcon.style.transform = 'rotate(360deg)';
    setTimeout(() => themeIcon.style.transform = 'rotate(0)', 300);

    if (currentTheme === 'dark') {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
        setTimeout(() => {
            themeIcon.classList.replace('fa-sun', 'fa-moon');
            themeIcon.style.color = 'var(--icon-moon)';
        }, 150);
    } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        setTimeout(() => {
            themeIcon.classList.replace('fa-moon', 'fa-sun');
            themeIcon.style.color = 'var(--icon-sun)';
        }, 150);
    }
}

// Cek tema yang sudah disimpan di localStorage
function checkSavedTheme() {
    const savedTheme = localStorage.getItem('theme');
    const themeIcon = document.getElementById('themeIcon');

    if (savedTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        themeIcon.classList.replace('fa-moon', 'fa-sun');
        themeIcon.style.color = 'var(--icon-sun)';
    } else {
        themeIcon.classList.replace('fa-sun', 'fa-moon');
        themeIcon.style.color = 'var(--icon-moon)';
    }
}

// Tampilkan loading spinner
function showLoading() {
    profileCard.classList.add('loading');
    servicesGrid.innerHTML = '<div class="loading-spinner"></div>';
}

// Hilangkan loading dan render UI
async function hideLoading() {
    profileCard.classList.remove('loading');
    await renderProfile();
    await renderServices();
}

// Render profile user di dashboard
async function renderProfile() {
    const user = await getCurrentUser();
    const usernameEl = document.getElementById("usernameDisplay");

    if (user) {
        usernameEl.textContent = `Hi, ${user.username}`;
    } else {
        usernameEl.textContent = `Silakan login dulu`;
    }
}


// Render services grid sesuai status login
async function renderServices() {
    servicesGrid.innerHTML = '';
    const loggedIn = await isAuthenticated();

    services.forEach(service => {
        const isLogout = service.title === 'Logout';
        const title = isLogout && !loggedIn ? 'Login' : service.title;
        const description = isLogout && !loggedIn ? 'Masuk ke aplikasi' : service.description;
        const iconClass = isLogout && !loggedIn ? 'fas fa-right-to-bracket fa-2xl' : service.icon;
        const fileName = title.toLowerCase().replace(/\s+/g, '-') + '.html';

        const serviceCard = document.createElement('article');
        serviceCard.className = 'card service-card';
        serviceCard.innerHTML = `
            <div class="service-icon">
                <i class="${iconClass}"></i>
            </div>
            <h3 class="service-title">${title}</h3>
            <p class="service-description">${description}</p>
        `;

        serviceCard.addEventListener('click', async () => {
            if (title === 'Money Tracker' && !loggedIn) {
                alert('Silakan login terlebih dahulu untuk mengakses Money Tracker.');
                window.location.href = 'screen.html';
                return;
            }

            if (title === 'Logout') {
                await logout();
                return;
            }

            if (title === 'Login') {
                window.location.href = 'screen.html';
                return;
            }

            window.location.href = fileName;
        });

        servicesGrid.appendChild(serviceCard);
    });
}

// Setup tombol back (jika ada)
function setupBackButton() {
    backButton?.addEventListener('click', () => {
        console.log('Navigasi kembali');
    });
}

// Inisialisasi aplikasi
function init() {
    checkSavedTheme();
    showLoading();
    setupBackButton();
    setTimeout(hideLoading, 1500); // simulasi loading
    themeToggle?.addEventListener('click', toggleDarkMode);
}

// Mulai aplikasi
init();
