// --- Auth Logic ---
const Auth = {
    TOKEN_KEY: 'sentiment_jwt_token',
    USER_KEY: 'sentiment_user_info',
    API_LOGIN: '/auth/login',
    API_REGISTER: '/auth/register',
    API_ME: '/auth/me',

    async login(username, password) {
        try {
            const response = await fetch(this.API_LOGIN, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await response.json();
            if (response.ok && data.status === 'success') {
                this.setToken(data.access_token);
                this.setUser(data.user);
                return true;
            } else {
                throw new Error(data.message || 'Login failed');
            }
        } catch (error) {
            console.error('Login Error:', error);
            throw error;
        }
    },

    logout() {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
        window.location.reload();
    },

    setToken(token) { localStorage.setItem(this.TOKEN_KEY, token); },
    getToken() { return localStorage.getItem(this.TOKEN_KEY); },
    setUser(user) { localStorage.setItem(this.USER_KEY, JSON.stringify(user)); },
    getUser() { return JSON.parse(localStorage.getItem(this.USER_KEY)); },
    isLoggedIn() { return !!this.getToken(); },

    async fetchAuth(url, options = {}) {
        const token = this.getToken();
        if (!token) return null;
        const headers = { ...options.headers, 'Authorization': `Bearer ${token}` };
        return fetch(url, { ...options, headers });
    }
};

// --- DOM Elements ---
const inputText = document.getElementById('inputText');
const charCount = document.getElementById('charCount');
const analyzeBtn = document.getElementById('analyzeBtn');
const clearBtn = document.getElementById('clearBtn');
const resultCard = document.getElementById('resultCard');
const sentimentLabel = document.getElementById('sentimentLabel');
const sentimentIcon = document.getElementById('sentimentIcon');
const sentimentDesc = document.getElementById('sentimentDesc');
const confidenceScore = document.getElementById('confidenceScore');
const historyList = document.getElementById('historyList');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');
const authButtons = document.getElementById('auth_buttons');
const confirmLoginBtn = document.getElementById('confirmLoginBtn');

// Views
const analyzeView = document.getElementById('analyze_view');
const dashboardView = document.getElementById('dashboard_view');
const socialView = document.getElementById('social_view');
const batchView = document.getElementById('batch_view');
const trainingView = document.getElementById('training_view');
const guideView = document.getElementById('guide_view');
const aboutView = document.getElementById('about_view');

// Page Navigation
function showPage(page) {
    // Hide everything first
    const views = [analyzeView, dashboardView, socialView, batchView, trainingView, guideView, aboutView];
    const navs = [document.querySelector('.max-w-7xl + div'), document.querySelector('.flex.justify-center.mb-8')];
    // ^ Selecting the Header and Tab Nav container roughly if they don't have IDs. 
    // Wait, let's look at index.html again. Header is lines 107-120. Tab Nav is 123-146.
    // They are just divs inside <main>. 

    // Better strategy: Add IDs to the Header and TabNav in index.html first? 
    // Or just toggle them via js.

    // Let's assume we will manage them.
    const headerEl = document.querySelector('main > div > div.text-center.mb-12');
    const tabNavEl = document.querySelector('main > div > div.flex.justify-center.mb-8');

    views.forEach(v => v && v.classList.add('hidden'));

    if (page === 'home') {
        if (headerEl) headerEl.classList.remove('hidden');
        if (tabNavEl) tabNavEl.classList.remove('hidden');
        // Show current tab
        const currentTab = localStorage.getItem('currentTab') || 'analyze';
        switchTab(currentTab);
    } else if (page === 'guide') {
        if (headerEl) headerEl.classList.add('hidden');
        if (tabNavEl) tabNavEl.classList.add('hidden');
        guideView.classList.remove('hidden');
    } else if (page === 'about') {
        if (headerEl) headerEl.classList.add('hidden');
        if (tabNavEl) tabNavEl.classList.add('hidden');
        aboutView.classList.remove('hidden');
    }
}

// Tabs
const tabAnalyze = document.getElementById('tab_analyze');
const tabDashboard = document.getElementById('tab_dashboard');
const tabSocial = document.getElementById('tab_social');
const tabBatch = document.getElementById('tab_batch');
const tabTraining = document.getElementById('tab_training');

// Social Elements
const socialUrl = document.getElementById('socialUrl');
const analyzeSocialBtn = document.getElementById('analyzeSocialBtn');
const socialResult = document.getElementById('socialResult');
const socialCommentsList = document.getElementById('socialCommentsList');
const socialPos = document.getElementById('socialPos');
const socialNeg = document.getElementById('socialNeg');
const socialNeu = document.getElementById('socialNeu');

// Aspect Elements
const aspectSection = document.getElementById('aspectSection');
const aspectList = document.getElementById('aspectList');

// Stats Elements
const totalCountEl = document.getElementById('totalCount');
const barPos = document.getElementById('barPos');
const barNeg = document.getElementById('barNeg');
const barNeu = document.getElementById('barNeu');
const countPos = document.getElementById('countPos');
const countNeg = document.getElementById('countNeg');
const countNeu = document.getElementById('countNeu');

// Batch Elements
const batchFile = document.getElementById('batchFile');
const dropZone = document.getElementById('dropZone');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const removeFileBtn = document.getElementById('removeFileBtn');
const analyzeBatchBtn = document.getElementById('analyzeBatchBtn');
const batchResult = document.getElementById('batchResult');
const batchTableBody = document.getElementById('batchTableBody');
const downloadCsvBtn = document.getElementById('downloadCsvBtn');
const batchPos = document.getElementById('batchPos');
const batchNeg = document.getElementById('batchNeg');
const batchNeu = document.getElementById('batchNeu');
let batchData = [];

// Training Elements
const trainFile = document.getElementById('trainFile');
const trainDropZone = document.getElementById('trainDropZone');
const trainFileInfo = document.getElementById('trainFileInfo');
const trainFileName = document.getElementById('trainFileName');
const removeTrainFileBtn = document.getElementById('removeTrainFileBtn');
const startTrainingBtn = document.getElementById('startTrainingBtn');
const trainingStatus = document.getElementById('trainingStatus');

// Styles
const sentimentStyles = {
    'Positif': { color: '#A6E3C5', icon: '😊', desc: 'Sentimen positif kuat terdeteksi.' },
    'Negatif': { color: '#F5B8C2', icon: '😔', desc: 'Sentimen negatif terdeteksi.' },
    'Netral': { color: '#BFD7EE', icon: '😐', desc: 'Sentimen netral atau objektif.' }
};

// --- Initialization ---
function init() {
    checkAuthState();
    loadHistory();

    // Event Listeners
    if (inputText) inputText.addEventListener('input', updateCharCount);
    if (analyzeBtn) analyzeBtn.addEventListener('click', analyzeSentiment);
    if (clearBtn) clearBtn.addEventListener('click', clearInput);
    if (clearHistoryBtn) clearHistoryBtn.addEventListener('click', clearHistory);

    if (confirmLoginBtn) confirmLoginBtn.addEventListener('click', handleLogin);
    if (analyzeSocialBtn) analyzeSocialBtn.addEventListener('click', analyzeSocialMedia);

    // Batch Listeners
    if (batchFile) batchFile.addEventListener('change', handleFileSelect);
    if (dropZone) {
        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('border-[#6FB8FF]', 'bg-[#F8FBFF]'); });
        dropZone.addEventListener('dragleave', (e) => { e.preventDefault(); dropZone.classList.remove('border-[#6FB8FF]', 'bg-[#F8FBFF]'); });
        dropZone.addEventListener('drop', handleFileDrop);
    }
    if (removeFileBtn) removeFileBtn.addEventListener('click', removeFile);
    if (analyzeBatchBtn) analyzeBatchBtn.addEventListener('click', analyzeBatch);
    if (downloadCsvBtn) downloadCsvBtn.addEventListener('click', downloadBatchCsv);

    // Training Listeners
    if (trainFile) trainFile.addEventListener('change', handleTrainFileSelect);
    if (trainDropZone) {
        trainDropZone.addEventListener('dragover', (e) => { e.preventDefault(); trainDropZone.classList.add('border-[#6FB8FF]', 'bg-[#F8FBFF]'); });
        trainDropZone.addEventListener('dragleave', (e) => { e.preventDefault(); trainDropZone.classList.remove('border-[#6FB8FF]', 'bg-[#F8FBFF]'); });
        trainDropZone.addEventListener('drop', handleTrainFileDrop);
    }
    if (removeTrainFileBtn) removeTrainFileBtn.addEventListener('click', removeTrainFile);
    if (startTrainingBtn) startTrainingBtn.addEventListener('click', startTraining);
}

function checkAuthState() {
    if (Auth.isLoggedIn()) {
        const user = Auth.getUser();
        authButtons.innerHTML = `
            <span class="text-sm font-medium text-[#1A1F36] mr-2">Hi, ${user ? user.username : 'User'}</span>
            <button onclick="Auth.logout()" class="text-sm font-medium text-[#667085] hover:text-[#F5B8C2] transition-colors">Keluar</button>
        `;
    } else {
        authButtons.innerHTML = `
            <a href="/register" class="px-5 py-2 rounded-xl text-[#667085] text-sm font-semibold hover:text-[#1A1F36] transition-colors mr-2">Daftar</a>
            <button onclick="document.getElementById('loginModal').classList.remove('hidden')" class="px-5 py-2 rounded-xl bg-white text-[#1A1F36] text-sm font-semibold shadow-sm border border-[#E2E8F0] hover:bg-[#F8FBFF] transition-all">Masuk</button>
        `;
    }
}

async function handleLogin() {
    const u = document.getElementById('loginUsername').value;
    const p = document.getElementById('loginPassword').value;
    const err = document.getElementById('loginError');

    try {
        await Auth.login(u, p);
        document.getElementById('loginModal').classList.add('hidden');
        checkAuthState();
        loadHistory(); // Reload history from server
        loadDashboardData(); // Reload dashboard if active
    } catch (e) {
        err.textContent = e.message;
        err.classList.remove('hidden');
    }
}

function updateCharCount() {
    const len = inputText.value.length;
    charCount.textContent = `${len} / 500 karakter`;
    if (len > 0) clearBtn.classList.remove('hidden');
    else clearBtn.classList.add('hidden');
}

function clearInput() {
    inputText.value = '';
    updateCharCount();
    resultCard.classList.add('hidden');
}

async function analyzeSentiment() {
    const text = inputText.value.trim();
    if (!text) return;

    // Loading State
    analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Menganalisis...';
    analyzeBtn.disabled = true;

    try {
        // Determine API endpoint based on auth
        const url = Auth.isLoggedIn() ? '/api/classify' : '/api/classify';

        const headers = { 'Content-Type': 'application/json' };
        if (Auth.isLoggedIn()) {
            headers['Authorization'] = `Bearer ${Auth.getToken()}`;
        }

        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ text_input: text })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.message || 'Analysis failed');
        }

        const result = await response.json();
        showResult(result);
        loadHistory(); // Refresh history

    } catch (error) {
        alert(error.message || 'Terjadi kesalahan saat analisis.');
        console.error(error);
    } finally {
        analyzeBtn.innerHTML = '<span>Analisis Sekarang</span><i class="fas fa-arrow-right text-xs"></i>';
        analyzeBtn.disabled = false;
    }
}

function showResult(data) {
    const style = sentimentStyles[data.sentiment] || sentimentStyles['Netral'];

    sentimentLabel.textContent = data.sentiment;
    sentimentLabel.style.color = style.color.replace('0.2', '1'); // Use solid color
    sentimentIcon.textContent = style.icon;
    sentimentDesc.textContent = style.desc;
    confidenceScore.textContent = `${Math.round(data.confidence * 100)}% Confidence`;

    // Handle Aspects
    if (data.aspects && data.aspects.length > 0) {
        aspectSection.classList.remove('hidden');
        aspectList.innerHTML = data.aspects.map(a => {
            const aStyle = sentimentStyles[a.sentiment] || sentimentStyles['Netral'];
            const bgColor = aStyle.color;
            return `
                <div class="px-3 py-1 rounded-full text-xs font-medium text-[#1A1F36] flex items-center gap-2 border border-black/5" style="background-color: ${bgColor}">
                    <span class="font-bold">${a.aspect}:</span>
                    <span>${a.sentiment}</span>
                </div>
            `;
        }).join('');
    } else {
        aspectSection.classList.add('hidden');
    }

    resultCard.classList.remove('hidden');
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function loadHistory() {
    let history = [];
    if (Auth.isLoggedIn()) {
        try {
            const res = await Auth.fetchAuth('/api/history');
            if (res && res.ok) {
                const data = await res.json();
                history = data.history;
            }
        } catch (e) { console.error("History fetch error", e); }
    } else {
        history = JSON.parse(sessionStorage.getItem('sentimentHistory') || '[]');
    }

    renderHistory(history);
    updateStats(history);
}

function renderHistory(history) {
    if (history.length === 0) {
        historyList.innerHTML = `<tr><td colspan="2" class="py-8 text-center"><p class="text-[#94A3B8]">Belum ada riwayat</p></td></tr>`;
        clearHistoryBtn.classList.add('hidden');
        return;
    }

    if (!Auth.isLoggedIn()) clearHistoryBtn.classList.remove('hidden');
    else clearHistoryBtn.classList.add('hidden');

    historyList.innerHTML = history.map(item => {
        const style = sentimentStyles[item.sentiment] || sentimentStyles['Netral'];
        const time = new Date(item.created_at || item.timestamp).toLocaleString('id-ID', { hour: '2-digit', minute: '2-digit' });

        let actionBtn = '';
        if (Auth.isLoggedIn()) {
            actionBtn = `
                <button onclick="openFeedbackModal(${item.id})" class="ml-2 text-[10px] text-[#94A3B8] hover:text-[#6FB8FF] transition-colors" title="Koreksi Sentimen">
                    <i class="fas fa-pen"></i>
                </button>
            `;
        }

        return `
            <tr class="border-b border-[#EEF2F7] last:border-0 hover:bg-[#F8FBFF] transition-colors">
                <td class="py-3 pl-2">
                    <p class="text-[#1A1F36] font-medium line-clamp-2" title="${escapeHtml(item.text)}">${escapeHtml(item.text)}</p>
                    <p class="text-[10px] text-[#94A3B8]">${time}</p>
                </td>
                <td class="py-3 pr-2 text-right align-top">
                    <div class="flex flex-col items-end gap-1">
                        <span class="inline-block px-2 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider text-[#1A1F36]" style="background-color: ${style.color}">${item.sentiment}</span>
                        ${actionBtn}
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function updateStats(history) {
    if (!history) history = [];
    const total = history.length;
    totalCountEl.textContent = total;

    if (total === 0) {
        barPos.style.width = '0%'; barNeg.style.width = '0%'; barNeu.style.width = '0%';
        countPos.textContent = '0%'; countNeg.textContent = '0%'; countNeu.textContent = '0%';
        return;
    }

    const pos = history.filter(i => i.sentiment === 'Positif').length;
    const neg = history.filter(i => i.sentiment === 'Negatif').length;
    const neu = history.filter(i => i.sentiment === 'Netral').length;

    const posPct = Math.round((pos / total) * 100);
    const negPct = Math.round((neg / total) * 100);
    const neuPct = Math.round((neu / total) * 100);

    setTimeout(() => {
        barPos.style.width = `${posPct}%`;
        barNeg.style.width = `${negPct}%`;
        barNeu.style.width = `${neuPct}%`;
    }, 100);

    countPos.textContent = `${posPct}%`;
    countNeg.textContent = `${negPct}%`;
    countNeu.textContent = `${neuPct}%`;
}

function clearHistory() {
    sessionStorage.removeItem('sentimentHistory');
    loadHistory();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// --- Dashboard Logic ---
let trendChartInstance = null;

function switchTab(tab) {
    localStorage.setItem('currentTab', tab);
    // Reset all tabs
    [analyzeView, dashboardView, socialView, batchView, trainingView].forEach(el => el && el.classList.add('hidden'));
    [tabAnalyze, tabDashboard, tabSocial, tabBatch, tabTraining].forEach(el => {
        if (el) {
            el.classList.remove('bg-white', 'text-[#1A1F36]', 'shadow-sm');
            el.classList.add('text-[#667085]');
        }
    });

    if (tab === 'analyze') {
        analyzeView.classList.remove('hidden');
        tabAnalyze.classList.add('bg-white', 'text-[#1A1F36]', 'shadow-sm');
        tabAnalyze.classList.remove('text-[#667085]');
    } else if (tab === 'dashboard') {
        dashboardView.classList.remove('hidden');
        tabDashboard.classList.add('bg-white', 'text-[#1A1F36]', 'shadow-sm');
        tabDashboard.classList.remove('text-[#667085]');
        loadDashboardData();
    } else if (tab === 'social') {
        socialView.classList.remove('hidden');
        tabSocial.classList.add('bg-white', 'text-[#1A1F36]', 'shadow-sm');
        tabSocial.classList.remove('text-[#667085]');
    } else if (tab === 'batch') {
        batchView.classList.remove('hidden');
        tabBatch.classList.add('bg-white', 'text-[#1A1F36]', 'shadow-sm');
        tabBatch.classList.add('bg-white', 'text-[#1A1F36]', 'shadow-sm');
        tabBatch.classList.remove('text-[#667085]');
    } else if (tab === 'training') {
        trainingView.classList.remove('hidden');
        tabTraining.classList.add('bg-white', 'text-[#1A1F36]', 'shadow-sm');
        tabTraining.classList.remove('text-[#667085]');
    }
}

// --- Batch Logic ---
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) showFileInfo(file);
}

function handleFileDrop(e) {
    e.preventDefault();
    dropZone.classList.remove('border-[#6FB8FF]', 'bg-[#F8FBFF]');
    const file = e.dataTransfer.files[0];
    if (file && (file.name.endsWith('.csv') || file.name.endsWith('.xlsx'))) {
        batchFile.files = e.dataTransfer.files;
        showFileInfo(file);
    } else {
        alert('Harap upload file CSV atau Excel.');
    }
}

function showFileInfo(file) {
    fileName.textContent = file.name;
    fileInfo.classList.remove('hidden');
    dropZone.classList.add('hidden');
    analyzeBatchBtn.disabled = false;
}

function removeFile() {
    batchFile.value = '';
    fileInfo.classList.add('hidden');
    dropZone.classList.remove('hidden');
    analyzeBatchBtn.disabled = true;
    batchResult.classList.add('hidden');
    batchData = [];
}

async function analyzeBatch() {
    const file = batchFile.files[0];
    if (!file) return;

    analyzeBatchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Memproses...';
    analyzeBatchBtn.disabled = true;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const token = Auth.getToken();
        const headers = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const response = await fetch('/api/batch-classify', {
            method: 'POST',
            headers: headers,
            body: formData
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.message || 'Gagal memproses file');

        batchData = data.results;
        renderBatchResults(data);

    } catch (error) {
        alert(error.message);
    } finally {
        analyzeBatchBtn.innerHTML = 'Mulai Analisis Batch';
        analyzeBatchBtn.disabled = false;
    }
}

function renderBatchResults(data) {
    batchPos.textContent = data.stats.Positif;
    batchNeg.textContent = data.stats.Negatif;
    batchNeu.textContent = data.stats.Netral;

    // Show top 10
    const previewData = data.results.slice(0, 10);

    batchTableBody.innerHTML = previewData.map(item => {
        const style = sentimentStyles[item.sentiment] || sentimentStyles['Netral'];
        return `
            <tr class="border-b border-[#EEF2F7] hover:bg-[#F8FBFF]">
                <td class="px-4 py-3 font-medium text-[#1A1F36] whitespace-normal" title="${escapeHtml(item.text)}">${escapeHtml(item.text)}</td>
                <td class="px-4 py-3">
                    <span class="px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider text-[#1A1F36]" style="background-color: ${style.color}">${item.sentiment}</span>
                </td>
                <td class="px-4 py-3 text-[#667085]">${Math.round(item.confidence * 100)}%</td>
            </tr>
        `;
    }).join('');

    batchResult.classList.remove('hidden');
}

function downloadBatchCsv() {
    if (!batchData || batchData.length === 0) return;

    const csvContent = "data:text/csv;charset=utf-8,"
        + "Text,Sentiment,Confidence\n"
        + batchData.map(e => `"${e.text.replace(/"/g, '""')}","${e.sentiment}","${e.confidence}"`).join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "hasil_analisis_sentimen.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    document.body.removeChild(link);
}

// --- Training Logic ---
function handleTrainFileSelect(e) {
    const file = e.target.files[0];
    if (file) showTrainFileInfo(file);
}

function handleTrainFileDrop(e) {
    e.preventDefault();
    trainDropZone.classList.remove('border-[#6FB8FF]', 'bg-[#F8FBFF]');
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.csv')) {
        trainFile.files = e.dataTransfer.files;
        showTrainFileInfo(file);
    } else {
        alert('Harap upload file CSV.');
    }
}

function showTrainFileInfo(file) {
    trainFileName.textContent = file.name;
    trainFileInfo.classList.remove('hidden');
    trainDropZone.classList.add('hidden');
    startTrainingBtn.disabled = false;
}

function removeTrainFile() {
    trainFile.value = '';
    trainFileInfo.classList.add('hidden');
    trainDropZone.classList.remove('hidden');
    startTrainingBtn.disabled = true;
    trainingStatus.classList.add('hidden');
}

async function startTraining() {
    const file = trainFile.files[0];
    if (!file) return;

    if (!confirm('Proses training akan memakan waktu beberapa menit. Lanjutkan?')) return;

    startTrainingBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Memulai...';
    startTrainingBtn.disabled = true;
    trainingStatus.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const token = Auth.getToken();
        const headers = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const response = await fetch('/api/upload-train-data', {
            method: 'POST',
            headers: headers,
            body: formData
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.message || 'Gagal memulai training');

        // Start polling for status
        pollTrainingStatus();

    } catch (error) {
        alert(error.message);
        trainingStatus.classList.add('hidden');
        startTrainingBtn.innerHTML = 'Mulai Training';
        startTrainingBtn.disabled = false;
    }
}

async function pollTrainingStatus() {
    const pollInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/training-status');
            const data = await response.json();

            if (!data.is_training) {
                clearInterval(pollInterval);
                trainingStatus.classList.add('hidden');
                startTrainingBtn.innerHTML = 'Mulai Training';
                startTrainingBtn.disabled = false;

                if (data.message) {
                    alert(data.message);
                }
            }
        } catch (e) {
            console.error("Polling error", e);
            clearInterval(pollInterval);
            trainingStatus.classList.add('hidden');
            startTrainingBtn.innerHTML = 'Mulai Training';
            startTrainingBtn.disabled = false;
        }
    }, 2000); // Check every 2 seconds
}

async function analyzeSocialMedia() {
    const url = socialUrl.value.trim();
    if (!url) return;

    analyzeSocialBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Memproses...';
    analyzeSocialBtn.disabled = true;
    socialResult.classList.add('hidden');

    try {
        const response = await fetch('/api/scrape', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.message || 'Gagal mengambil data');

        renderSocialResults(data);
    } catch (error) {
        alert(error.message);
    } finally {
        analyzeSocialBtn.innerHTML = 'Analisis';
        analyzeSocialBtn.disabled = false;
    }
}

function renderSocialResults(data) {
    socialPos.textContent = data.stats.Positif;
    socialNeg.textContent = data.stats.Negatif;
    socialNeu.textContent = data.stats.Netral;

    socialCommentsList.innerHTML = data.results.map(item => {
        const style = sentimentStyles[item.sentiment] || sentimentStyles['Netral'];
        return `
            <div class="p-3 rounded-xl bg-[#F8FBFF] border border-[#EEF2F7]">
                <div class="flex justify-between items-start mb-1">
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider text-[#1A1F36]" 
                          style="background-color: ${style.color}">${item.sentiment}</span>
                    <span class="text-[10px] text-[#94A3B8]">${Math.round(item.confidence * 100)}%</span>
                </div>
                <p class="text-sm text-[#3D4458]">${escapeHtml(item.text)}</p>
            </div>
        `;
    }).join('');

    socialResult.classList.remove('hidden');
}

async function loadDashboardData() {
    const loginMsg = document.getElementById('dashboard_login_msg');
    const content = document.getElementById('dashboard_content');

    if (!Auth.isLoggedIn()) {
        loginMsg.classList.remove('hidden');
        content.classList.add('hidden');
        return;
    }

    loginMsg.classList.add('hidden');
    content.classList.remove('hidden');

    try {
        // Fetch Trend Data
        const trendRes = await Auth.fetchAuth('/api/stats/trend');
        if (trendRes && trendRes.ok) {
            const trendData = await trendRes.json();
            renderTrendChart(trendData);
        }

        // Fetch Word Cloud Data
        const cloudRes = await Auth.fetchAuth('/api/stats/wordcloud');
        if (cloudRes && cloudRes.ok) {
            const cloudData = await cloudRes.json();
            renderWordCloud(cloudData);
        }
    } catch (e) {
        console.error("Dashboard Load Error", e);
    }
}

function renderTrendChart(data) {
    const ctx = document.getElementById('trendChart').getContext('2d');
    if (trendChartInstance) trendChartInstance.destroy();

    // Data comes pre-formatted from backend
    const labels = data.dates;
    const posData = data.positive;
    const negData = data.negative;
    const neuData = data.neutral;

    trendChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                { label: 'Positif', data: posData, borderColor: '#A6E3C5', backgroundColor: 'rgba(166, 227, 197, 0.2)', tension: 0.4, fill: true },
                { label: 'Negatif', data: negData, borderColor: '#F5B8C2', backgroundColor: 'rgba(245, 184, 194, 0.2)', tension: 0.4, fill: true },
                { label: 'Netral', data: neuData, borderColor: '#BFD7EE', backgroundColor: 'rgba(191, 215, 238, 0.2)', tension: 0.4, fill: true }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'top', labels: { font: { family: 'Inter' } } }, tooltip: { callbacks: { label: function (context) { let label = context.dataset.label || ''; if (label) { label += ': '; } if (context.parsed.y !== null) { label += context.parsed.y; } return label; } } } },
            scales: { y: { beginAtZero: true, grid: { borderDash: [5, 5] }, ticks: { callback: function (value) { if (Number.isInteger(value)) { return value; } } } }, x: { grid: { display: false } } }
        }
    });
}

function renderWordCloud(data) {
    const canvas = document.getElementById('wordCloudCanvas');
    const loading = document.getElementById('wordcloud_loading');
    const container = canvas.parentElement;

    if (!data || data.length === 0) {
        loading.classList.add('hidden');
        // Show empty state
        return;
    }

    loading.classList.remove('hidden');
    const maxWeight = Math.max(...data.map(item => item.weight));
    const list = data.map(item => [item.text, (item.weight / maxWeight) * 50 + 10]);

    canvas.width = container.offsetWidth;
    canvas.height = container.offsetHeight;

    // Fallback to hide loader
    const loaderTimeout = setTimeout(() => {
        loading.classList.add('hidden');
    }, 2000);

    WordCloud(canvas, {
        list: list,
        gridSize: 8,
        weightFactor: 1,
        fontFamily: 'Inter, sans-serif',
        color: function () {
            const colors = ['#6FB8FF', '#F5B8C2', '#A6E3C5', '#1A1F36', '#667085'];
            return colors[Math.floor(Math.random() * colors.length)];
        },
        rotateRatio: 0.5,
        rotationSteps: 2,
        backgroundColor: 'transparent',
        drawOutOfBound: false,
        shrinkToFit: true,
        onWordCloudStop: function () {
            clearTimeout(loaderTimeout);
            loading.classList.add('hidden');
        }
    });
}

// Navbar Scroll Effect
window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (window.scrollY > 10) {
        navbar.classList.add('bg-white/40', 'backdrop-blur-xl', 'shadow-soft', 'border-b', 'border-white/30');
        navbar.classList.remove('py-4'); navbar.classList.add('py-3');
    } else {
        navbar.classList.remove('bg-white/40', 'backdrop-blur-xl', 'shadow-soft', 'border-b', 'border-white/30');
        navbar.classList.remove('py-3'); navbar.classList.add('py-4');
    }
});

// Feedback Logic
function openFeedbackModal(id) {
    document.getElementById('feedbackAnalysisId').value = id;
    document.getElementById('feedbackModal').classList.remove('hidden');
}

async function submitFeedback(correction) {
    const id = document.getElementById('feedbackAnalysisId').value;
    const modal = document.getElementById('feedbackModal');

    try {
        const response = await Auth.fetchAuth(`/api/feedback/${id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ correction: correction })
        });

        const data = await response.json();
        if (response.ok) {
            alert('Terima kasih! Masukan Anda telah disimpan.');
            modal.classList.add('hidden');
            loadHistory(); // Reload to show updated data if we were showing corrections
        } else {
            throw new Error(data.message);
        }
    } catch (e) {
        alert('Gagal menyimpan masukan: ' + e.message);
    }
}

// Start
document.addEventListener('DOMContentLoaded', init);
