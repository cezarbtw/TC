/**
 * EmotionLens — Front End
 * Conectado ao back end FastAPI em API_BASE_URL
 */

const API_BASE_URL = 'http://localhost:8000/api';

const EMOTIONS = {
    feliz:    { color: '#fbbf24', label: 'Feliz' },
    triste:   { color: '#60a5fa', label: 'Triste' },
    raiva:    { color: '#f87171', label: 'Raiva' },
    surpresa: { color: '#fb923c', label: 'Surpresa' },
    medo:     { color: '#a78bfa', label: 'Medo' },
    nojo:     { color: '#34d399', label: 'Nojo' },
    neutro:   { color: '#94a3b8', label: 'Neutro' },
};

let allSessions   = [];   // cache das sessões carregadas
let currentSession = null;
let timelineChart  = null;
let donutChart     = null;

const $  = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);


// ═══════════════════════════════════════════════════════════════════════════════
// NAVEGAÇÃO
// ═══════════════════════════════════════════════════════════════════════════════

function switchView(viewId) {
    $$('.view').forEach(v => v.classList.remove('active'));
    $(`#view-${viewId}`).classList.add('active');
    $$('.nav-item').forEach(n => n.classList.remove('active'));
    $(`#nav-${viewId}`).classList.add('active');
    const titles = { dashboard: 'Dashboard', sessions: 'Sessões', upload: 'Upload de Vídeo' };
    $('#page-title').textContent = titles[viewId] || 'Dashboard';
}

$('#nav-dashboard').addEventListener('click',  e => { e.preventDefault(); switchView('dashboard'); });
$('#nav-sessions').addEventListener('click',   e => { e.preventDefault(); switchView('sessions'); });
$('#nav-upload').addEventListener('click',     e => { e.preventDefault(); switchView('upload'); });
$('#link-all-sessions').addEventListener('click', e => { e.preventDefault(); switchView('sessions'); });
$('#btn-new-upload-from-sessions').addEventListener('click', () => switchView('upload'));
$('#menu-toggle').addEventListener('click', () => $('#sidebar').classList.toggle('open'));


// ═══════════════════════════════════════════════════════════════════════════════
// API — FUNÇÕES DE COMUNICAÇÃO
// ═══════════════════════════════════════════════════════════════════════════════

async function apiFetch(path, options = {}) {
    const res = await fetch(`${API_BASE_URL}${path}`, options);
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || 'Erro desconhecido na API.');
    }
    return res.json();
}

async function loadSessions() {
    try {
        allSessions = await apiFetch('/sessions');
        renderSessionsTable();
        renderMiniSessions();
        $('#sessions-count').textContent = allSessions.length;
    } catch (err) {
        console.error('Erro ao carregar sessões:', err);
        showToast('Não foi possível carregar as sessões.', 'error');
    }
}

async function loadSessionDetail(sessionId) {
    try {
        const session = await apiFetch(`/sessions/${sessionId}`);
        renderDashboard(session);
        switchView('dashboard');
    } catch (err) {
        console.error('Erro ao carregar sessão:', err);
        showToast('Não foi possível carregar os detalhes da sessão.', 'error');
    }
}


// ═══════════════════════════════════════════════════════════════════════════════
// DASHBOARD
// ═══════════════════════════════════════════════════════════════════════════════

function renderDashboard(session) {
    currentSession = session;
    const emo = EMOTIONS[session.predominant];

    $('#predominant-emotion').textContent    = emo.label;
    $('#predominant-confidence').textContent = `Confiança: ${Math.round(session.confidence)}%`;
    $('#video-duration').textContent         = session.duration;
    $('#frames-count').textContent           = session.frames;
    $('#sessions-count').textContent         = allSessions.length;

    renderProbabilities(session.probabilities);
    renderTimelineChart(session.timeline);
    renderDonutChart(session.probabilities);
    renderMiniSessions();
}

function renderProbabilities(probs) {
    const list = $('#probabilities-list');
    list.innerHTML = '';
    const sorted = Object.entries(probs).sort((a, b) => b[1] - a[1]);
    sorted.forEach(([key, val]) => {
        const emo  = EMOTIONS[key];
        const item = document.createElement('div');
        item.className = 'probability-item';
        item.innerHTML = `
            <div class="probability-meta">
                <span class="probability-label">${emo.label}</span>
                <span class="probability-value">${Math.round(val)}%</span>
            </div>
            <div class="probability-bar">
                <div class="probability-fill" style="background:${emo.color}"></div>
            </div>
        `;
        list.appendChild(item);
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                item.querySelector('.probability-fill').style.width = val + '%';
            });
        });
    });
}

function renderTimelineChart(timeline) {
    const ctx = $('#timeline-chart').getContext('2d');
    if (timelineChart) timelineChart.destroy();

    const keys     = Object.keys(EMOTIONS);
    const datasets = keys.map(k => ({
        label:           EMOTIONS[k].label,
        data:            timeline[k] || [],
        borderColor:     EMOTIONS[k].color,
        backgroundColor: EMOTIONS[k].color + '18',
        borderWidth:     2,
        pointRadius:     0,
        pointHoverRadius: 4,
        tension:         0.4,
        fill:            false,
    }));

    const labels = (timeline[keys[0]] || []).map((_, i) => `${i + 1}s`);

    timelineChart = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#8b8fa7', font: { family: 'Inter', size: 11 }, boxWidth: 12, boxHeight: 3, padding: 16 },
                },
                tooltip: {
                    backgroundColor: '#1c1e2e', borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1,
                    titleColor: '#e8eaf0', bodyColor: '#8b8fa7',
                    titleFont: { family: 'Inter', weight: '600' }, bodyFont: { family: 'Inter' },
                    padding: 12, cornerRadius: 8,
                    callbacks: { label: ctx => `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(1)}%` },
                },
            },
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#5a5e78', font: { family: 'Inter', size: 10 }, maxTicksLimit: 10 } },
                y: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#5a5e78', font: { family: 'Inter', size: 10 }, callback: v => v + '%' } },
            },
        },
    });
}

function renderDonutChart(probs) {
    const ctx    = $('#donut-chart').getContext('2d');
    if (donutChart) donutChart.destroy();

    const keys   = Object.keys(EMOTIONS);
    const values = keys.map(k => probs[k] ?? 0);
    const colors = keys.map(k => EMOTIONS[k].color);

    donutChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: keys.map(k => EMOTIONS[k].label),
            datasets: [{ data: values, backgroundColor: colors, borderColor: '#1c1e2e', borderWidth: 3, hoverOffset: 6 }],
        },
        options: {
            responsive: true, maintainAspectRatio: true, cutout: '68%',
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1c1e2e', borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1,
                    titleColor: '#e8eaf0', bodyColor: '#8b8fa7',
                    padding: 12, cornerRadius: 8,
                    callbacks: { label: ctx => `${ctx.label}: ${ctx.parsed.toFixed(1)}%` },
                },
            },
        },
    });

    // Legenda manual
    const legend = $('#donut-legend');
    legend.innerHTML = '';
    keys.forEach(k => {
        const item = document.createElement('div');
        item.className = 'legend-item';
        item.innerHTML = `
            <span class="legend-dot" style="background:${EMOTIONS[k].color}"></span>
            <span class="legend-label">${EMOTIONS[k].label}</span>
            <span class="legend-value">${Math.round(probs[k] ?? 0)}%</span>
        `;
        legend.appendChild(item);
    });
}

function renderMiniSessions() {
    const list = $('#sessions-mini-list');
    list.innerHTML = '';
    allSessions.slice(0, 4).forEach(s => {
        const emo  = EMOTIONS[s.predominant];
        const item = document.createElement('div');
        item.className = 'session-mini-item';
        item.innerHTML = `
            <div class="session-mini-info">
                <span class="session-mini-name">${s.name}</span>
                <span class="session-mini-date">${formatDate(s.date)}</span>
            </div>
            <span class="session-mini-emotion" style="color:${emo.color}">${emo.label}</span>
        `;
        item.addEventListener('click', () => loadSessionDetail(s.id));
        list.appendChild(item);
    });
}


// ═══════════════════════════════════════════════════════════════════════════════
// TABELA DE SESSÕES
// ═══════════════════════════════════════════════════════════════════════════════

function renderSessionsTable() {
    const tbody = $('#sessions-table-body');
    tbody.innerHTML = '';
    allSessions.forEach(s => {
        const emo = EMOTIONS[s.predominant];
        const tr  = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${s.name}</strong></td>
            <td>${formatDate(s.date)}</td>
            <td>${s.duration}</td>
            <td>
                <span class="emotion-tag" style="background:${emo.color}18;color:${emo.color}">
                    ${emo.label}
                </span>
            </td>
            <td>
                <div class="confidence-bar-mini">
                    <div class="bar"><div class="fill" style="width:${s.confidence}%"></div></div>
                    <span>${Math.round(s.confidence)}%</span>
                </div>
            </td>
            <td>
                <button class="btn-table-action" data-id="${s.id}">Ver detalhes</button>
            </td>
        `;
        tr.querySelector('.btn-table-action').addEventListener('click', () => loadSessionDetail(s.id));
        tbody.appendChild(tr);
    });
}


// ═══════════════════════════════════════════════════════════════════════════════
// UPLOAD
// ═══════════════════════════════════════════════════════════════════════════════

const uploadArea     = $('#upload-area');
const fileInput      = $('#file-input');
const uploadProgress = $('#upload-progress');
const uploadSuccess  = $('#upload-success');

uploadArea.addEventListener('click',     () => fileInput.click());
uploadArea.addEventListener('dragover',  e => { e.preventDefault(); uploadArea.classList.add('dragover'); });
uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
uploadArea.addEventListener('drop', e => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener('change', () => {
    if (fileInput.files.length) handleFile(fileInput.files[0]);
});

async function handleFile(file) {
    $('#progress-filename').textContent = file.name;
    uploadArea.classList.add('hidden');
    uploadProgress.classList.remove('hidden');
    uploadSuccess.classList.add('hidden');

    const progressFill    = $('#progress-bar-fill');
    const progressText    = $('#progress-text');
    const progressPercent = $('#progress-percent');

    // Animação de progresso enquanto o servidor processa
    let fakeProgress = 0;
    const ticker = setInterval(() => {
        // Avança rápido até 85%, depois espera a resposta real
        const increment = fakeProgress < 50 ? 8 : fakeProgress < 80 ? 2 : 0.3;
        fakeProgress = Math.min(fakeProgress + increment, 85);
        progressFill.style.width    = fakeProgress + '%';
        progressPercent.textContent = Math.floor(fakeProgress) + '%';
        progressText.textContent    = fakeProgress > 50 ? 'Analisando expressões...' : 'Enviando vídeo...';
    }, 300);

    try {
        const formData = new FormData();
        formData.append('file', file);

        const data = await apiFetch('/upload', { method: 'POST', body: formData });

        clearInterval(ticker);
        progressFill.style.width    = '100%';
        progressPercent.textContent = '100%';
        progressText.textContent    = 'Análise concluída!';

        // Atualiza cache com a nova sessão no topo
        await loadSessions();

        setTimeout(() => {
            uploadProgress.classList.add('hidden');
            uploadSuccess.classList.remove('hidden');
            // Guarda a sessão retornada para abrir no dashboard
            currentSession = data.session;
        }, 600);

    } catch (err) {
        clearInterval(ticker);
        progressFill.style.width    = '0%';
        progressPercent.textContent = '0%';
        progressText.textContent    = 'Erro no processamento.';
        showToast(err.message, 'error');
        setTimeout(() => {
            uploadArea.classList.remove('hidden');
            uploadProgress.classList.add('hidden');
            fileInput.value = '';
        }, 2000);
    }
}

$('#btn-view-results').addEventListener('click', () => {
    if (currentSession) {
        renderDashboard(currentSession);
    }
    switchView('dashboard');
    // Reseta upload
    uploadArea.classList.remove('hidden');
    uploadProgress.classList.add('hidden');
    uploadSuccess.classList.add('hidden');
    fileInput.value = '';
});


// ═══════════════════════════════════════════════════════════════════════════════
// CONTROLES DO GRÁFICO DE TIMELINE
// ═══════════════════════════════════════════════════════════════════════════════

$$('.chart-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        $$('.chart-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        if (!currentSession) return;
        const range    = btn.dataset.range;
        const timeline = currentSession.timeline;
        if (range === 'all') {
            renderTimelineChart(timeline);
        } else {
            const limit  = parseInt(range);
            const sliced = {};
            Object.keys(timeline).forEach(k => { sliced[k] = timeline[k].slice(0, limit); });
            renderTimelineChart(sliced);
        }
    });
});


// ═══════════════════════════════════════════════════════════════════════════════
// UTILITÁRIOS
// ═══════════════════════════════════════════════════════════════════════════════

function formatDate(dateStr) {
    const [y, m, d] = dateStr.split('-');
    return `${d}/${m}/${y}`;
}

function showToast(message, type = 'info') {
    // Toast simples — você pode estilizar no CSS
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}


// ═══════════════════════════════════════════════════════════════════════════════
// INICIALIZAÇÃO
// ═══════════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', async () => {
    await loadSessions();
    // Se houver sessões, renderiza a mais recente no dashboard
    if (allSessions.length > 0) {
        await loadSessionDetail(allSessions[0].id);
    }
});
