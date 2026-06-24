// API State Management
let API_URL = localStorage.getItem('streamplay_api_url') || 'http://127.0.0.1:8000';
let token = localStorage.getItem('streamplay_token') || null;
let currentUser = null;
let currentCategoryFilter = 'all';
let currentSortField = 'name';
let currentSortDesc = false;

// Simulated Player State
let playerTimer = null;
let playerProgressSeconds = 0;
let playerDurationSeconds = 0;
let playerActiveContentId = null;
let isPlayerPlaying = false;

// DOM Elements
const authSection = document.getElementById('authSection');
const mainContent = document.getElementById('mainContent');
const mainHeader = document.getElementById('mainHeader');
const authMessage = document.getElementById('authMessage');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const tabLoginBtn = document.getElementById('tabLoginBtn');
const tabRegisterBtn = document.getElementById('tabRegisterBtn');
const headerUsername = document.getElementById('headerUsername');
const logoutBtn = document.getElementById('logoutBtn');

// Nav items
const navItems = document.querySelectorAll('.nav-item');
const dashboardSections = document.querySelectorAll('.dashboard-section');

// API configurations
const apiUrlInput = document.getElementById('apiUrlInput');
const saveApiUrlBtn = document.getElementById('saveApiUrlBtn');
const apiStatusIndicator = document.getElementById('apiStatusIndicator');

// Search & filter
const searchInput = document.getElementById('searchInput');
const sortSelect = document.getElementById('sortSelect');
const sortOrderBtn = document.getElementById('sortOrderBtn');
const categoryChips = document.getElementById('categoryChips');
const catalogGrid = document.getElementById('catalogGrid');
const recommendationsContainer = document.getElementById('recommendationsContainer');
const recommendationsGrid = document.getElementById('recommendationsGrid');

// Hero banner
const heroBanner = document.getElementById('heroBanner');
const heroTitle = document.getElementById('heroTitle');
const heroDescription = document.getElementById('heroDescription');
const heroPlayBtn = document.getElementById('heroPlayBtn');
const heroInfoBtn = document.getElementById('heroInfoBtn');

// History Section
const historyList = document.getElementById('historyList');



// Modals
const detailModal = document.getElementById('detailModal');
const closeDetailModalBtn = document.getElementById('closeDetailModalBtn');
const modalBanner = document.getElementById('modalBanner');
const modalTitle = document.getElementById('modalTitle');
const modalYear = document.getElementById('modalYear');
const modalDuration = document.getElementById('modalDuration');
const modalDescription = document.getElementById('modalDescription');
const modalCategories = document.getElementById('modalCategories');
const modalPlayBtn = document.getElementById('modalPlayBtn');

// Player Modal
const playerModal = document.getElementById('playerModal');
const closePlayerModalBtn = document.getElementById('closePlayerModalBtn');
const playerContentTitle = document.getElementById('playerContentTitle');
const playerPlayPauseBtn = document.getElementById('playerPlayPauseBtn');
const playerCurrentTime = document.getElementById('playerCurrentTime');
const playerTotalTime = document.getElementById('playerTotalTime');
const playerProgressTrack = document.getElementById('playerProgressTrack');
const playerProgressFill = document.getElementById('playerProgressFill');

/* ==========================================================================
   INITIALIZATION & API CHECK
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    apiUrlInput.value = API_URL;
    checkApiStatus();
    setupEventListeners();
    
    if (token) {
        loadUserProfile();
    } else {
        showAuthScreen();
    }
});

// Check if API is running
async function checkApiStatus() {
    try {
        const response = await fetch(`${API_URL}/`);
        if (response.ok) {
            apiStatusIndicator.className = 'api-status online';
            apiStatusIndicator.innerHTML = '<i class="fa-solid fa-circle"></i> Online';
            return true;
        }
    } catch (e) {
        // Fallback or ignore
    }
    apiStatusIndicator.className = 'api-status offline';
    apiStatusIndicator.innerHTML = '<i class="fa-solid fa-circle"></i> Offline';
    return false;
}

/* ==========================================================================
   AUTHENTICATION LOGIC
   ========================================================================== */

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    showAuthAlert('Conectando...', 'success');
    
    try {
        // FastAPI OAuth2PasswordRequestForm expects email in "username" field, sent as form urlencoded
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);
        
        const response = await fetch(`${API_URL}/users/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: params
        });
        
        const data = await response.json();
        
        if (response.ok) {
            token = data.access_token;
            localStorage.setItem('streamplay_token', token);
            showAuthAlert('Inicio de sesión correcto. Cargando perfil...', 'success');
            await loadUserProfile();
        } else {
            showAuthAlert(data.detail || 'Credenciales inválidas', 'error');
        }
    } catch (err) {
        showAuthAlert('Error al conectar con la API. Verifica que esté iniciada.', 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    
    showAuthAlert('Creando usuario...', 'success');
    
    try {
        const response = await fetch(`${API_URL}/users/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAuthAlert('Registro completado. ¡Ahora puedes iniciar sesión!', 'success');
            setTimeout(() => {
                tabLoginBtn.click();
                document.getElementById('loginEmail').value = email;
                document.getElementById('loginPassword').value = '';
            }, 1500);
        } else {
            showAuthAlert(data.detail || 'Error al registrar el usuario', 'error');
        }
    } catch (err) {
        showAuthAlert('Error al conectar con el servidor', 'error');
    }
}

async function loadUserProfile() {
    try {
        const response = await fetch(`${API_URL}/users/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            headerUsername.textContent = currentUser.username;
            showDashboard();
            loadAllData();
        } else {
            // Token expired or invalid
            logout();
        }
    } catch (err) {
        showDashboard(); // show offline or stub interface
        showAuthAlert('Error al cargar perfil, utilizando datos locales o sin autenticación completa', 'error');
    }
}

function logout() {
    token = null;
    currentUser = null;
    localStorage.removeItem('streamplay_token');
    showAuthScreen();
}

function showAuthScreen() {
    authSection.classList.remove('hidden');
    mainContent.classList.add('hidden');
    mainHeader.classList.add('hidden');
    authMessage.classList.add('hidden');
}

function showDashboard() {
    authSection.classList.add('hidden');
    mainContent.classList.remove('hidden');
    mainHeader.classList.remove('hidden');
}

function showAuthAlert(msg, type) {
    authMessage.textContent = msg;
    authMessage.className = `alert alert-${type === 'error' ? 'error' : 'success'}`;
    authMessage.classList.remove('hidden');
}

/* ==========================================================================
   NAVIGATION & UI INTERACTIONS
   ========================================================================== */

function setupEventListeners() {
    // Auth Tabs
    tabLoginBtn.addEventListener('click', () => {
        tabLoginBtn.classList.add('active');
        tabRegisterBtn.classList.remove('active');
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
        authMessage.classList.add('hidden');
    });
    
    tabRegisterBtn.addEventListener('click', () => {
        tabRegisterBtn.classList.add('active');
        tabLoginBtn.classList.remove('active');
        registerForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
        authMessage.classList.add('hidden');
    });
    
    // Auth Forms Submission
    loginForm.addEventListener('submit', handleLogin);
    registerForm.addEventListener('submit', handleRegister);
    logoutBtn.addEventListener('click', logout);
    
    // Config Server Url
    saveApiUrlBtn.addEventListener('click', () => {
        API_URL = apiUrlInput.value.trim();
        localStorage.setItem('streamplay_api_url', API_URL);
        checkApiStatus().then(online => {
            alert(online ? 'API Conectada con éxito.' : 'No se pudo conectar con la API.');
            if (token) loadUserProfile();
        });
    });
    
    // Navigation bar links
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = item.getAttribute('data-target');
            
            navItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            
            dashboardSections.forEach(sec => {
                if (sec.id === targetId) {
                    sec.classList.remove('hidden');
                    sec.classList.add('active-section');
                } else {
                    sec.classList.add('hidden');
                    sec.classList.remove('active-section');
                }
            });
            
            if (targetId === 'historySection') {
                loadHistoryData();
            }
        });
    });
    
    // Catalog controls
    searchInput.addEventListener('input', debounce(() => {
        loadCatalogData();
    }, 400));
    
    sortSelect.addEventListener('change', () => {
        currentSortField = sortSelect.value;
        loadCatalogData();
    });
    
    sortOrderBtn.addEventListener('click', () => {
        currentSortDesc = !currentSortDesc;
        const icon = sortOrderBtn.querySelector('i');
        if (currentSortDesc) {
            icon.className = 'fa-solid fa-arrow-down-z-a';
        } else {
            icon.className = 'fa-solid fa-arrow-down-a-z';
        }
        loadCatalogData();
    });
    
    // Modals control
    closeDetailModalBtn.addEventListener('click', () => {
        detailModal.classList.add('hidden');
    });
    
    closePlayerModalBtn.addEventListener('click', closePlayer);
    
    playerPlayPauseBtn.addEventListener('click', togglePlayerPlay);
    playerProgressTrack.addEventListener('click', handlePlayerProgressSeek);
    

}

// Helper Debounce
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/* ==========================================================================
   DATA LOADING (CATALOG, CATEGORIES, HISTORY, RECOMMENDATIONS)
   ========================================================================== */

function loadAllData() {
    loadCategoryChips();
    loadCatalogData();
    loadRecommendations();
}

// Categories list
async function loadCategoryChips() {
    try {
        const response = await fetch(`${API_URL}/category/`);
        if (!response.ok) return;
        
        const categories = await response.json();
        
        // Reset and preserve the "All" chip
        categoryChips.innerHTML = '<button class="chip active" data-category-id="all">Todas</button>';
        
        categories.forEach(cat => {
            // Chips
            const btn = document.createElement('button');
            btn.className = 'chip';
            btn.textContent = cat.name;
            btn.setAttribute('data-category-id', cat.id);
            btn.addEventListener('click', () => {
                document.querySelectorAll('.category-chips .chip').forEach(c => c.classList.remove('active'));
                btn.classList.add('active');
                currentCategoryFilter = cat.id;
                loadCatalogData();
            });
            categoryChips.appendChild(btn);
        });
        
        // Restore all active click event
        const allBtn = categoryChips.querySelector('button[data-category-id="all"]');
        allBtn.addEventListener('click', () => {
            document.querySelectorAll('.category-chips .chip').forEach(c => c.classList.remove('active'));
            allBtn.classList.add('active');
            currentCategoryFilter = 'all';
            loadCatalogData();
        });
        
    } catch (e) {
        console.error('Error al cargar categorías', e);
    }
}

// Load Catalog Content
async function loadCatalogData() {
    catalogGrid.innerHTML = '<div class="loading-spinner"><i class="fa-solid fa-spinner spinner"></i> Cargando catálogo...</div>';
    
    try {
        const query = searchInput.value.trim();
        let url = `${API_URL}/contents/`;
        const params = new URLSearchParams();
        
        // If there's search text, use the search endpoint
        if (query) {
            url = `${API_URL}/contents/search`;
            params.append('q', query);
        } else if (currentCategoryFilter !== 'all') {
            params.append('category', currentCategoryFilter);
        }
        
        params.append('sort', currentSortField);
        params.append('descending', currentSortDesc);
        
        const response = await fetch(`${url}?${params.toString()}`, {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
        
        if (!response.ok) {
            catalogGrid.innerHTML = '<div class="error-msg">Error al cargar películas.</div>';
            return;
        }
        
        const contents = await response.json();
        
        if (contents.length === 0) {
            catalogGrid.innerHTML = '<div class="error-msg">No se encontraron películas.</div>';
            return;
        }
        
        catalogGrid.innerHTML = '';
        contents.forEach(movie => {
            const card = createMovieCard(movie);
            catalogGrid.appendChild(card);
        });
        
        // Load Hero banner with a random movie in the catalog
        if (contents.length > 0 && !query && currentCategoryFilter === 'all') {
            const randomIndex = Math.floor(Math.random() * contents.length);
            setupHeroBanner(contents[randomIndex]);
        }
        
    } catch (e) {
        catalogGrid.innerHTML = '<div class="error-msg">Servidor desconectado.</div>';
    }
}

function createMovieCard(movie) {
    const card = document.createElement('div');
    card.className = 'movie-card';
    
    card.innerHTML = `
        <img class="movie-card-img" src="${movie.image_url}" alt="${movie.name}" onerror="this.src='https://images.unsplash.com/photo-1440404653325-ab127d49abc1?q=80&w=400&auto=format&fit=crop'">
        <div class="movie-card-overlay">
            <h4 class="movie-card-title">${movie.name}</h4>
            <div class="movie-card-meta">
                <span><i class="fa-solid fa-calendar"></i> ${movie.release_year || 'N/A'}</span>
                <span><i class="fa-solid fa-clock"></i> ${movie.duration_minutes || 'N/A'} min</span>
            </div>
        </div>
    `;
    
    card.addEventListener('click', () => {
        showMovieDetails(movie.id);
    });
    
    return card;
}

function setupHeroBanner(movie) {
    heroBanner.style.backgroundImage = `url('${movie.banner_url || movie.image_url}')`;
    heroTitle.textContent = movie.name;
    heroDescription.textContent = movie.description || 'Sin descripción disponible.';
    
    // Play button
    const playHandler = () => startSimulatedPlayer(movie);
    heroPlayBtn.replaceWith(heroPlayBtn.cloneNode(true));
    document.getElementById('heroPlayBtn').addEventListener('click', playHandler);
    
    // Info button
    const infoHandler = () => showMovieDetails(movie.id);
    heroInfoBtn.replaceWith(heroInfoBtn.cloneNode(true));
    document.getElementById('heroInfoBtn').addEventListener('click', infoHandler);
}

// User Recommendations
async function loadRecommendations() {
    if (!currentUser) return;
    
    try {
        const response = await fetch(`${API_URL}/category/recommendations/${currentUser.id}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
            const recommendedCategories = await response.json();
            
            if (recommendedCategories.length === 0) {
                recommendationsContainer.classList.add('hidden');
                return;
            }
            
            // Get content for the top recommended category
            const topCat = recommendedCategories[0];
            const contentResponse = await fetch(`${API_URL}/contents/?category=${topCat.id}&limit=5`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            if (contentResponse.ok) {
                const contents = await contentResponse.json();
                
                if (contents.length > 0) {
                    recommendationsContainer.classList.remove('hidden');
                    const subtitle = recommendationsContainer.querySelector('.row-subtitle');
                    subtitle.textContent = `Basado en tu gusto por el género: ${topCat.name}`;
                    
                    recommendationsGrid.innerHTML = '';
                    contents.forEach(movie => {
                        recommendationsGrid.appendChild(createMovieCard(movie));
                    });
                } else {
                    recommendationsContainer.classList.add('hidden');
                }
            }
        }
    } catch (e) {
        console.error('Error al cargar recomendaciones', e);
    }
}

// User History
async function loadHistoryData() {
    historyList.innerHTML = '<div class="loading-spinner"><i class="fa-solid fa-spinner spinner"></i> Cargando historial...</div>';
    
    if (!token) {
        historyList.innerHTML = '<div class="error-msg">Inicia sesión para ver tu historial de visualizaciones.</div>';
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/history/`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            historyList.innerHTML = '<div class="error-msg">Error al cargar historial.</div>';
            return;
        }
        
        const historyItems = await response.json();
        
        if (historyItems.length === 0) {
            historyList.innerHTML = `
                <div class="empty-state" style="text-align:center; padding: 40px; color: var(--text-secondary);">
                    <i class="fa-solid fa-film" style="font-size: 3rem; margin-bottom:15px; color: var(--text-muted);"></i>
                    <p>Aún no has visto ningún contenido.</p>
                </div>
            `;
            return;
        }
        
        historyList.innerHTML = '';
        historyItems.forEach(item => {
            const card = document.createElement('div');
            card.className = 'history-card';
            
            const content = item.content || { name: 'Contenido Desconocido', image_url: '', duration_minutes: 120 };
            const progressMin = Math.round(item.progress / 60);
            const totalDurationMin = content.duration_minutes || 120;
            const progressPercent = Math.min(100, Math.round((progressMin / totalDurationMin) * 100));
            
            card.innerHTML = `
                <img class="history-thumbnail" src="${content.image_url}" alt="${content.name}" onerror="this.src='https://images.unsplash.com/photo-1440404653325-ab127d49abc1?q=80&w=100&auto=format&fit=crop'">
                <div class="history-info">
                    <div class="history-title">${content.name}</div>
                    <div class="history-meta">Visto el ${new Date(item.watched_at).toLocaleDateString()}</div>
                    <div class="progress-container">
                        <div class="progress-info-text">
                            <span>Visto: ${progressMin} min</span>
                            <span>Total: ${totalDurationMin} min (${progressPercent}%)</span>
                        </div>
                        <div class="progress-bar-bg">
                            <div class="progress-bar-fill" style="width: ${progressPercent}%"></div>
                        </div>
                    </div>
                </div>
            `;
            
            // Allow re-watching
            card.addEventListener('click', () => {
                startSimulatedPlayer(content, item.progress);
            });
            
            historyList.appendChild(card);
        });
        
    } catch (e) {
        historyList.innerHTML = '<div class="error-msg">Error al conectar con la API.</div>';
    }
}

/* ==========================================================================
   MODAL DISPLAY & DETAILS
   ========================================================================== */

async function showMovieDetails(contentId) {
    try {
        const response = await fetch(`${API_URL}/contents/${contentId}`);
        if (!response.ok) return;
        
        const movie = await response.json();
        
        modalBanner.style.backgroundImage = `url('${movie.banner_url || movie.image_url}')`;
        modalTitle.textContent = movie.name;
        modalYear.textContent = movie.release_year || 'N/A';
        modalDuration.textContent = `${movie.duration_minutes || 'N/A'} min`;
        modalDescription.textContent = movie.description || 'Sin descripción.';
        
        modalCategories.innerHTML = '';
        if (movie.categories) {
            movie.categories.forEach(cat => {
                const span = document.createElement('span');
                span.className = 'modal-cat-tag';
                span.textContent = cat.name;
                modalCategories.appendChild(span);
            });
        }
        
        // Setup play button in modal
        const playHandler = () => {
            detailModal.classList.add('hidden');
            startSimulatedPlayer(movie);
        };
        modalPlayBtn.replaceWith(modalPlayBtn.cloneNode(true));
        document.getElementById('modalPlayBtn').addEventListener('click', playHandler);
        
        detailModal.classList.remove('hidden');
        
    } catch (e) {
        alert('Error al conectar con el servidor.');
    }
}

/* ==========================================================================
   SIMULATED PLAYER SYSTEM
   ========================================================================== */

function startSimulatedPlayer(movie, resumeProgressSeconds = 0) {
    if (!token) {
        alert('Debes iniciar sesión para reproducir contenido.');
        tabLoginBtn.click();
        showAuthScreen();
        return;
    }
    
    playerActiveContentId = movie.id;
    playerDurationSeconds = (movie.duration_minutes || 120) * 60;
    playerProgressSeconds = resumeProgressSeconds;
    playerContentTitle.textContent = `Reproduciendo: ${movie.name}`;
    
    isPlayerPlaying = true;
    updatePlayerUI();
    playerModal.classList.remove('hidden');
    
    // Start simulation loop (saves progress every 5 seconds)
    let saveCounter = 0;
    playerTimer = setInterval(() => {
        if (isPlayerPlaying) {
            playerProgressSeconds += 5; // Simulates time progress (fast-forward slightly for testing)
            
            if (playerProgressSeconds >= playerDurationSeconds) {
                playerProgressSeconds = playerDurationSeconds;
                pausePlayer();
                saveWatchHistory(); // final save
                alert('¡Has terminado de ver este contenido!');
                closePlayer();
                return;
            }
            
            updatePlayerUI();
            
            saveCounter++;
            if (saveCounter >= 3) { // every 15 simulated seconds, send progress to API
                saveWatchHistory();
                saveCounter = 0;
            }
        }
    }, 1000);
}

function updatePlayerUI() {
    // Current progress fill
    const percent = (playerProgressSeconds / playerDurationSeconds) * 100;
    playerProgressFill.style.width = `${percent}%`;
    
    // Time texts
    playerCurrentTime.textContent = formatTime(playerProgressSeconds);
    playerTotalTime.textContent = formatTime(playerDurationSeconds);
    
    // Play/Pause icon
    const icon = playerPlayPauseBtn.querySelector('i');
    if (isPlayerPlaying) {
        icon.className = 'fa-solid fa-pause';
    } else {
        icon.className = 'fa-solid fa-play';
    }
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

function togglePlayerPlay() {
    isPlayerPlaying = !isPlayerPlaying;
    updatePlayerUI();
}

function pausePlayer() {
    isPlayerPlaying = false;
    updatePlayerUI();
}

function handlePlayerProgressSeek(e) {
    const rect = playerProgressTrack.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const width = rect.width;
    const percent = clickX / width;
    
    playerProgressSeconds = Math.round(percent * playerDurationSeconds);
    updatePlayerUI();
    saveWatchHistory(); // immediate save on seek
}

async function saveWatchHistory() {
    try {
        const response = await fetch(`${API_URL}/history/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                content_id: playerActiveContentId,
                progress: playerProgressSeconds
            })
        });
        
        if (response.ok) {
            console.log('Visualización registrada');
        }
    } catch (e) {
        console.error('Error al registrar progreso', e);
    }
}

function closePlayer() {
    if (playerTimer) {
        clearInterval(playerTimer);
        playerTimer = null;
    }
    
    // Final progress save
    if (playerActiveContentId && token) {
        saveWatchHistory();
    }
    
    playerModal.classList.add('hidden');
    
    // Refresh history grid if active
    const historySection = document.getElementById('historySection');
    if (historySection.classList.contains('active-section')) {
        loadHistoryData();
    }
    
    // Refresh recommendations since user watched something new
    loadRecommendations();
}

/* ==========================================================================
   ADMIN ACTIONS (POST CATEGORIES AND CONTENT)
   ========================================================================== */


