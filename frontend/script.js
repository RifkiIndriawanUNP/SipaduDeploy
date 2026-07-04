// API Configuration
const API_BASE_URL = window.location.origin + '/api';

// State Management
let currentPage = 'dashboard';

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Aplikasi dimulai');
    testConnection();
    setupNavigation();
    loadKabupatenList();
    setupSearchListener();
});

// Test connection on load
async function testConnection() {
    try {
        console.log('🔌 Mencoba koneksi ke server...');
        const response = await fetch(`${API_BASE_URL}/test`);
        const data = await response.json();
        console.log('✅ Koneksi berhasil:', data);
        
        if (data.data_loaded) {
            console.log(`✅ Data loaded: ${data.total_kabupaten} kabupaten tersedia`);
        } else {
            console.error('❌ Server berjalan tapi data kosong');
        }
    } catch (error) {
        console.error('❌ GAGAL KONEKSI ke server:', error);
        console.log('Pastikan backend berjalan di http://localhost:5000');
        console.log('Jalankan: cd backend && python app.py');
    }
}

// Navigation Setup
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            navigateTo(page);
        });
    });
}

function navigateTo(page) {
    console.log('Navigasi ke:', page);
    
    // Update navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-page') === page) {
            link.classList.add('active');
        }
    });
    
    // Update pages
    document.querySelectorAll('.page').forEach(p => {
        p.classList.remove('active');
    });
    
    const targetPage = document.getElementById(`${page}-page`);
    if (targetPage) {
        targetPage.classList.add('active');
    }
    
    currentPage = page;
    
    // Load data if needed
    if (page === 'kabupaten') {
        loadKabupatenList();
    }
}

// Search Setup
function setupSearchListener() {
    const searchInput = document.getElementById('searchInput');
    
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchKabupaten();
            }
        });
        
        searchInput.addEventListener('input', function() {
            if (this.value.length >= 2) {
                searchKabupaten();
            } else if (this.value.length === 0) {
                document.getElementById('searchResults').innerHTML = '';
                document.getElementById('detailResult').innerHTML = '';
            }
        });
    }
}

// Search Kabupaten
async function searchKabupaten() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;
    
    const keyword = searchInput.value.trim();
    
    if (keyword.length === 0) {
        document.getElementById('searchResults').innerHTML = '';
        return;
    }
    
    const searchResults = document.getElementById('searchResults');
    searchResults.innerHTML = '<div class="loading">🔍 Mencari...</div>';
    
    try {
        console.log(`Mencari: "${keyword}"`);
        const url = `${API_BASE_URL}/search?q=${encodeURIComponent(keyword)}`;
        console.log('URL:', url);
        
        const response = await fetch(url);
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Hasil search:', result);
        
        if (result.status === 'success') {
            displaySearchResults(result.data);
        } else {
            searchResults.innerHTML = '<div class="error-message">❌ Gagal mencari data</div>';
        }
    } catch (error) {
        console.error('❌ Error search:', error);
        searchResults.innerHTML = `
            <div class="error-message">
                ❌ Gagal terhubung ke server<br>
                <small>Error: ${error.message}</small><br>
                <small>Pastikan backend berjalan di port 5000</small>
            </div>`;
    }
}

function displaySearchResults(kabupatenList) {
    const searchResults = document.getElementById('searchResults');
    
    if (!kabupatenList || kabupatenList.length === 0) {
        searchResults.innerHTML = '<div class="error-message">❌ Kabupaten/Kota tidak ditemukan</div>';
        return;
    }
    
    console.log('Menampilkan hasil search:', kabupatenList);
    
    searchResults.innerHTML = kabupatenList.map(kab => 
        `<div class="result-card" onclick="showKabupatenDetail('${kab}')">
            📍 ${kab}
        </div>`
    ).join('');
}

// Load Kabupaten List
async function loadKabupatenList() {
    const kabupatenList = document.getElementById('kabupatenList');
    
    if (!kabupatenList) return;
    
    kabupatenList.innerHTML = '<div class="loading">📊 Memuat data kabupaten...</div>';
    
    try {
        console.log('Mengambil daftar kabupaten...');
        const response = await fetch(`${API_BASE_URL}/kabupaten`);
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Data kabupaten:', result);
        
        if (result.status === 'success') {
            displayKabupatenList(result.data);
        } else {
            kabupatenList.innerHTML = '<div class="error-message">❌ Gagal memuat data</div>';
        }
    } catch (error) {
        console.error('❌ Error load kabupaten:', error);
        kabupatenList.innerHTML = `
            <div class="error-message">
                ❌ Gagal terhubung ke server<br>
                <small>${error.message}</small>
            </div>`;
    }
}

function displayKabupatenList(kabupatenList) {
    const kabupatenElement = document.getElementById('kabupatenList');
    
    if (!kabupatenElement) return;
    
    if (!kabupatenList || kabupatenList.length === 0) {
        kabupatenElement.innerHTML = '<div class="error-message">Tidak ada data kabupaten</div>';
        return;
    }
    
    kabupatenElement.innerHTML = kabupatenList.map(kab => 
        `<div class="kabupaten-card" onclick="showKabupatenDetail('${kab}')">
            📍 ${kab}
        </div>`
    ).join('');
}

// Show Kabupaten Detail
async function showKabupatenDetail(kabupatenName) {
    document.getElementById('notFound').classList.add('hidden');
    const rs = document.getElementById('resultSection');
    rs.className = 'max-w-6xl mx-auto px-6 py-10 fade-in';
    
    // Debug: cek nama yang dikirim
    console.log('🔍 Searching for:', kabupatenName);
    console.log('🔍 Encoded:', encodeURIComponent(kabupatenName));
    
    // Show loading state
    document.getElementById('resultHeader').innerHTML = `
        <div class="flex items-center justify-between flex-wrap gap-3">
            <div>
                <p class="text-xs text-ink/40 font-medium mb-0.5">Memuat data...</p>
                <h2 class="font-display font-bold text-pine text-2xl">${formatKabupatenName(kabupatenName)}</h2>
            </div>
        </div>`;
    
    document.getElementById('infraBars').innerHTML = '<div class="text-center text-ink/40 py-8">Memuat data infrastruktur...</div>';
    document.getElementById('ibadahList').innerHTML = '<div class="text-center text-ink/40 py-8">Memuat data tempat ibadah...</div>';
    
    try {
        // Coba beberapa format URL
        const urls = [
            `${API_BASE_URL}/kabupaten/${encodeURIComponent(kabupatenName)}`,
            `${API_BASE_URL}/kabupaten/${encodeURIComponent(kabupatenName.toUpperCase())}`,
        ];
        
        console.log('🔗 Trying URLs:', urls);
        
        let response = null;
        let result = null;
        
        // Coba URL pertama
        for (const url of urls) {
            try {
                console.log('🔗 Fetching:', url);
                response = await fetch(url);
                console.log('📡 Response status:', response.status);
                
                if (response.ok) {
                    result = await response.json();
                    console.log('✅ Success with URL:', url);
                    break;
                }
            } catch (e) {
                console.log('❌ Failed URL:', url, e.message);
            }
        }
        
        if (!response || !response.ok) {
            // Coba search dulu
            console.log('🔄 Trying search API...');
            const searchResponse = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(kabupatenName)}`);
            const searchResult = await searchResponse.json();
            
            console.log('Search result:', searchResult);
            
            if (searchResult.status === 'success' && searchResult.data.length > 0) {
                // Gunakan nama exact dari hasil search
                const exactName = searchResult.data[0];
                console.log('✅ Found via search:', exactName);
                response = await fetch(`${API_BASE_URL}/kabupaten/${encodeURIComponent(exactName)}`);
                result = await response.json();
            } else {
                throw new Error('Data tidak ditemukan');
            }
        }
        
        if (result && result.status === 'success') {
            console.log('✅ Displaying results');
            displayFuzzyResults(result.data);
        } else {
            console.log('❌ No results');
            showNotFound(kabupatenName);
        }
    } catch (error) {
        console.error('❌ Error:', error);
        
        // Tampilkan error detail untuk debugging
        document.getElementById('resultSection').innerHTML = `
            <div class="text-center py-12">
                <p class="text-red-500 mb-2">Error: ${error.message}</p>
                <p class="text-sm text-ink/40">Cek console browser untuk detail</p>
                <button onclick="debugAPI()" class="mt-4 text-jade font-semibold text-sm hover:underline">Debug API</button>
            </div>
        `;
    }
}

function displayKabupatenDetail(data) {
    const detailResult = document.getElementById('detailResult');
    if (!detailResult) return;
    
    const infra = data.infrastruktur;
    
    let html = `
        <div class="kabupaten-header">
            <h3>📍 ${data.kabupaten}</h3>
            <div class="kabupaten-info">
                <span>👥 Penduduk: ${data.jumlah_penduduk.toLocaleString()}</span>
                <span>📐 Luas Wilayah: ${data.luas_wilayah.toLocaleString()} km²</span>
            </div>
        </div>
        
        <h3>Hasil Identifikasi Infrastruktur</h3>
        <div class="infrastructure-grid">
    `;
    
    // Rumah Sakit
    if (infra.rumah_sakit) {
        html += createInfrastructureCard('🏥 Rumah Sakit', [
            ['Jumlah', infra.rumah_sakit.data_asli],
            ['Jumlah Ideal', infra.rumah_sakit.jumlah_ideal],
            ['Nilai Fuzzy', infra.rumah_sakit.fuzzy_value],
            ['Status', infra.rumah_sakit.status, true]
        ]);
    }
    
    // Puskesmas
    if (infra.puskesmas) {
        html += createInfrastructureCard('🏨 Puskesmas', [
            ['Jumlah', infra.puskesmas.data_asli],
            ['Jumlah Ideal', infra.puskesmas.jumlah_ideal],
            ['Nilai Fuzzy', infra.puskesmas.fuzzy_value],
            ['Status', infra.puskesmas.status, true]
        ]);
    }
    
    // SD
    if (infra.sd) {
        html += createInfrastructureCard('🏫 Sekolah Dasar', [
            ['Jumlah SD', infra.sd.data_asli],
            ['Penduduk Usia SD', infra.sd.penduduk_usia_sd.toLocaleString()],
            ['Jumlah Ideal', infra.sd.jumlah_ideal],
            ['Nilai Fuzzy', infra.sd.fuzzy_value],
            ['Status', infra.sd.status, true]
        ]);
    }
    
    // SMP
    if (infra.smp) {
        html += createInfrastructureCard('🏫 SMP', [
            ['Jumlah SMP', infra.smp.data_asli],
            ['Penduduk Usia SMP', infra.smp.penduduk_usia_smp.toLocaleString()],
            ['Jumlah Ideal', infra.smp.jumlah_ideal],
            ['Nilai Fuzzy', infra.smp.fuzzy_value],
            ['Status', infra.smp.status, true]
        ]);
    }
    
    // SMU
    if (infra.smu) {
        html += createInfrastructureCard('🏫 SMU', [
            ['Jumlah SMU', infra.smu.data_asli],
            ['Penduduk Usia SMU', infra.smu.penduduk_usia_smu.toLocaleString()],
            ['Jumlah Ideal', infra.smu.jumlah_ideal],
            ['Nilai Fuzzy', infra.smu.fuzzy_value],
            ['Status', infra.smu.status, true]
        ]);
    }
    
    // Jalan
    if (infra.jalan) {
        html += createInfrastructureCard('🛣️ Jalan', [
            ['Panjang Jalan', `${infra.jalan.panjang_jalan} km`],
            ['RDI', infra.jalan.rdi],
            ['Nilai Fuzzy', infra.jalan.fuzzy_value],
            ['Status', infra.jalan.status, true]
        ]);
    }
    
    // Pasar
    if (infra.pasar) {
        html += createInfrastructureCard('🏪 Pasar', [
            ['Jumlah Pasar', infra.pasar.jumlah_pasar],
            ['PKP', `${infra.pasar.pkp}%`],
            ['Nilai Fuzzy', infra.pasar.fuzzy_value],
            ['Status', infra.pasar.status, true]
        ]);
    }
    
    html += `</div>`;
    
    // Tempat Ibadah
    if (infra.tempat_ibadah) {
        const icons = {islam:'☪️', kristen:'✝️', katolik:'⛪', hindu:'🕉️', budha:'☸️'};
        document.getElementById('ibadahList').innerHTML = Object.entries(infra.tempat_ibadah).map(([agama, d]) => {
            // Hitung warna berdasarkan status masing-masing agama
            const statusColor = getStatusColor(d.status);
            
            return `
            <div class="flex gap-3 items-start p-3.5 rounded-xl border border-pine/8">
                <span class="text-2xl">${icons[agama]||'🕌'}</span>
                <div class="flex-1">
                    <p class="text-sm font-semibold text-ink capitalize">${agama}</p>
                    <div class="grid grid-cols-2 gap-2 mt-1 text-xs text-ink/50">
                        <span>Tempat Ibadah: <strong class="text-ink">${d.tempat_ibadah}</strong></span>
                        <span>Pemeluk: <strong class="text-ink">${d.jumlah_pemeluk.toLocaleString()}</strong></span>
                        <span>Rasio: <strong class="text-ink">${d.rasio}</strong></span>
                        <span>Fuzzy: <strong class="text-ink">${d.fuzzy_value}</strong></span>
                    </div>
                    <span class="text-[10px] font-bold px-2 py-0.5 rounded-full mt-2 inline-block" style="background:${statusColor}20;color:${statusColor}">${d.status}</span>
                </div>
            </div>`;
        }).join('');
    }
    
    detailResult.innerHTML = html;
    console.log('✅ Detail berhasil ditampilkan');
}

// Helper Functions
function createInfrastructureCard(title, rows) {
    let card = `<div class="infrastructure-card"><h4>${title}</h4>`;
    
    rows.forEach(([label, value, isStatus]) => {
        if (isStatus) {
            const statusClass = getStatusClass(value);
            card += `
                <div class="info-row">
                    <span class="info-label">${label}</span>
                    <span class="status-badge status-${statusClass}">${value}</span>
                </div>`;
        } else {
            card += `
                <div class="info-row">
                    <span class="info-label">${label}</span>
                    <span class="info-value">${value}</span>
                </div>`;
        }
    });
    
    card += '</div>';
    return card;
}

function createIbadahCard(agamaName, ibadah) {
    return `
        <div class="ibadah-card">
            <h5>${agamaName}</h5>
            <div class="info-row">
                <span class="info-label">Tempat Ibadah</span>
                <span class="info-value">${ibadah.tempat_ibadah}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Jumlah Pemeluk</span>
                <span class="info-value">${ibadah.jumlah_pemeluk.toLocaleString()}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Rasio</span>
                <span class="info-value">${ibadah.rasio}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Nilai Fuzzy</span>
                <span class="info-value">${ibadah.fuzzy_value}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Status</span>
                <span class="status-badge status-${getStatusClass(ibadah.status)}">${ibadah.status}</span>
            </div>
        </div>
    `;
}

function getStatusClass(status) {
    const statusMap = {
        'Sangat Layak': 'sangat-layak',
        'Layak': 'layak',
        'Cukup Layak': 'cukup-layak',
        'Kurang Layak': 'kurang-layak',
        'Tidak Layak': 'tidak-layak',
        'Sangat Tidak Layak': 'sangat-tidak-layak'
    };
    return statusMap[status] || 'tidak-layak';
}

async function debugAPI() {
    console.log('🔧 Debugging API...');
    try {
        // Test basic connection
        const testRes = await fetch(`${API_BASE_URL}/test`);
        const testData = await testRes.json();
        console.log('Test API:', testData);
        
        // Get all names
        const namesRes = await fetch(`${API_BASE_URL}/kabupaten`);
        const namesData = await namesRes.json();
        console.log('All names:', namesData);
        
        // Get debug names
        const debugRes = await fetch(`${API_BASE_URL}/debug/names`);
        const debugData = await debugRes.json();
        console.log('Debug names:', debugData);
        
        alert('Debug info di console. Buka F12 > Console');
    } catch (e) {
        console.error('Debug error:', e);
    }
}
