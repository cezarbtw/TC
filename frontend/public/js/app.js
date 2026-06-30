const EMOTIONS = {
    feliz: { color: '#fbbf24', label: 'Feliz' },
    triste: { color: '#60a5fa', label: 'Triste' },
    raiva: { color: '#f87171', label: 'Raiva' },
    surpresa: { color: '#fb923c', label: 'Surpresa' },
    medo: { color: '#a78bfa', label: 'Medo' },
    nojo: { color: '#34d399', label: 'Nojo' },
    neutro: { color: '#94a3b8', label: 'Neutro' },
};

const mockSessions = [
    {
        id: 1,
        name: 'Sessão 01',
        date: '2026-03-28',
        duration: '02:34',
        frames: 154,
        predominant: 'feliz',
        confidence: 72,
        probabilities: { feliz: 72, triste: 8, raiva: 3, surpresa: 5, medo: 2, nojo: 1, neutro: 9 },
        timeline: generateTimeline(154),
    },
    {
        id: 2,
        name: 'Sessão 02',
        date: '2026-03-30',
        duration: '03:12',
        frames: 192,
        predominant: 'neutro',
        confidence: 58,
        probabilities: { feliz: 15, triste: 12, raiva: 5, surpresa: 3, medo: 4, nojo: 3, neutro: 58 },
        timeline: generateTimeline(192),
    },
    {
        id: 3,
        name: 'Sessão 03',
        date: '2026-04-01',
        duration: '01:45',
        frames: 105,
        predominant: 'triste',
        confidence: 65,
        probabilities: { feliz: 10, triste: 65, raiva: 5, surpresa: 2, medo: 8, nojo: 1, neutro: 9 },
        timeline: generateTimeline(105),
    },
    {
        id: 4,
        name: 'Sessão 04',
        date: '2026-04-03',
        duration: '04:10',
        frames: 250,
        predominant: 'surpresa',
        confidence: 48,
        probabilities: { feliz: 20, triste: 5, raiva: 8, surpresa: 48, medo: 7, nojo: 2, neutro: 10 },
        timeline: generateTimeline(250),
    },
    {
        id: 5,
        name: 'Sessão 05',
        date: '2026-04-06',
        duration: '02:58',
        frames: 178,
        predominant: 'feliz',
        confidence: 61,
        probabilities: { feliz: 61, triste: 7, raiva: 4, surpresa: 10, medo: 3, nojo: 2, neutro: 13 },
        timeline: generateTimeline(178),
    },
];

function generateTimeline(frames) {
    const keys = Object.keys(EMOTIONS);
    const data = {};
    keys.forEach(k => data[k] = []);
    const points = Math.min(frames, 30);
    for (let i = 0; i < points; i++) {
        let remaining = 100;
        keys.forEach((k, idx) => {
            if (idx === keys.length - 1) {
                data[k].push(Math.max(0, remaining));
            } else {
                const val = Math.floor(Math.random() * (remaining / (keys.length - idx)));
                data[k].push(val);
                remaining -= val;
            }
        });
    }
    return data;
}

let currentSession = mockSessions[0];
let timelineChart = null;
let donutChart = null;

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);


function switchView(viewId) {
    $$('.view').forEach(v => v.classList.remove('active'));
    $(`#view-${viewId}`).classList.add('active');
    $$('.nav-item').forEach(n => n.classList.remove('active'));
    $(`#nav-${viewId}`).classList.add('active');
    const titles = { dashboard: 'Dashboard', sessions: 'Sessões', upload: 'Upload de Vídeo' };
    $('#page-title').textContent = titles[viewId] || 'Dashboard';
}

$('#nav-dashboard').addEventListener('click', e => { e.preventDefault(); switchView('dashboard'); });
$('#nav-sessions').addEventListener('click', e => { e.preventDefault(); switchView('sessions'); });
$('#nav-upload').addEventListener('click', e => { e.preventDefault(); switchView('upload'); });
$('#link-all-sessions').addEventListener('click', e => { e.preventDefault(); switchView('sessions'); });
$('#btn-new-upload-from-sessions').addEventListener('click', () => switchView('upload'));


$('#menu-toggle').addEventListener('click', () => {
    $('#sidebar').classList.toggle('open');
});


function renderDashboard(session) {
    currentSession = session;
    const emo = EMOTIONS[session.predominant];

    // REMOVE EMOTES
    //$('#stat-predominant .emotion-icon').textContent = emo.emoji;
    $('#predominant-emotion').textContent = emo.label;
    $('#predominant-confidence').textContent = `Confiança: ${session.confidence}%`;
    $('#video-duration').textContent = session.duration;
    $('#frames-count').textContent = session.frames;
    $('#sessions-count').textContent = mockSessions.length;

    // Probabilities
    renderProbabilities(session.probabilities);

    // Charts
    renderTimelineChart(session.timeline);
    renderDonutChart(session.probabilities);

    // Mini sessions
    renderMiniSessions();
}

function renderProbabilities(probs) {
    const list = $('#probabilities-list');
    list.innerHTML = '';
    const sorted = Object.entries(probs).sort((a, b) => b[1] - a[1]);
    sorted.forEach(([key, val]) => {
        const emo = EMOTIONS[key];
        const item = document.createElement('div');
        item.className = 'probability-item';
        item.innerHTML = `
            <div class="probability-meta">
                <span class="probability-label">${emo.label}</span>
                <span class="probability-value">${val}%</span>
            </div>
            <div class="probability-bar">
                <div class="probability-fill" style="background:${emo.color}"></div>
            </div>
        `;
        list.appendChild(item);
        // Animate bar
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

    const keys = Object.keys(EMOTIONS);
    const datasets = keys.map(k => ({
        label: EMOTIONS[k].label,
        data: timeline[k],
        borderColor: EMOTIONS[k].color,
        backgroundColor: EMOTIONS[k].color + '18',
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 4,
        tension: 0.4,
        fill: false,
    }));

    const labels = timeline[keys[0]].map((_, i) => `${i + 1}s`);

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
                    labels: {
                        color: '#8b8fa7',
                        font: { family: 'Inter', size: 11 },
                        boxWidth: 12,
                        boxHeight: 3,
                        padding: 16,
                        usePointStyle: false,
                    },
                },
                tooltip: {
                    backgroundColor: '#1c1e2e',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    titleColor: '#e8eaf0',
                    bodyColor: '#8b8fa7',
                    titleFont: { family: 'Inter', weight: '600' },
                    bodyFont: { family: 'Inter' },
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: ctx => `${ctx.dataset.label}: ${ctx.parsed.y}%`,
                    },
                },
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255,255,255,0.03)' },
                    ticks: { color: '#5a5e78', font: { family: 'Inter', size: 10 }, maxTicksLimit: 10 },
                },
                y: {
                    min: 0,
                    max: 100,
                    grid: { color: 'rgba(255,255,255,0.03)' },
                    ticks: { color: '#5a5e78', font: { family: 'Inter', size: 10 }, callback: v => v + '%' },
                },
            },
        },
    });
}

function renderDonutChart(probs) {
    const ctx = $('#donut-chart').getContext('2d');
    if (donutChart) donutChart.destroy();

    const keys = Object.keys(probs);
    const values = keys.map(k => probs[k]);
    const colors = keys.map(k => EMOTIONS[k].color);

    donutChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: keys.map(k => EMOTIONS[k].label),
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderColor: '#1c1e2e',
                borderWidth: 3,
                hoverOffset: 6,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '68%',
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1c1e2e',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    titleColor: '#e8eaf0',
                    bodyColor: '#8b8fa7',
                    titleFont: { family: 'Inter', weight: '600' },
                    bodyFont: { family: 'Inter' },
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: ctx => `${ctx.label}: ${ctx.parsed}%`,
                    },
                },
            },
        },
    });

    // Render legend
    const legend = $('#donut-legend');
    legend.innerHTML = '';
    keys.forEach(k => {
        const item = document.createElement('div');
        item.className = 'legend-item';
        item.innerHTML = `
            <span class="legend-dot" style="background:${EMOTIONS[k].color}"></span>
            <span class="legend-label">${EMOTIONS[k].label}</span>
            <span class="legend-value">${probs[k]}%</span>
        `;
        legend.appendChild(item);
    });
}

function renderMiniSessions() {
    const list = $('#sessions-mini-list');
    list.innerHTML = '';
    mockSessions.slice(0, 4).forEach(s => {
        const emo = EMOTIONS[s.predominant];
        const item = document.createElement('div');
        item.className = 'session-mini-item';
        item.innerHTML = `
            <div class="session-mini-info">
                <span class="session-mini-name">${s.name}</span>
                <span class="session-mini-date">${formatDate(s.date)}</span>
            </div>
            <span class="session-mini-emotion" style="color:${emo.color}">${emo.label}</span>
        `;
        item.addEventListener('click', () => {
            renderDashboard(s);
            switchView('dashboard');
        });
        list.appendChild(item);
    });
}

// --- Render Sessions Table ---
function renderSessionsTable() {
    const tbody = $('#sessions-table-body');
    tbody.innerHTML = '';
    mockSessions.forEach(s => {
        const emo = EMOTIONS[s.predominant];
        const tr = document.createElement('tr');
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
                    <span>${s.confidence}%</span>
                </div>
            </td>
            <td>
                <button class="btn-table-action" data-id="${s.id}">Ver detalhes</button>
            </td>
        `;
        tr.querySelector('.btn-table-action').addEventListener('click', () => {
            renderDashboard(s);
            switchView('dashboard');
        });
        tbody.appendChild(tr);
    });
}

// --- Upload ---
const uploadArea = $('#upload-area');
const fileInput = $('#file-input');
const uploadProgress = $('#upload-progress');
const uploadSuccess = $('#upload-success');

uploadArea.addEventListener('click', () => fileInput.click());
uploadArea.addEventListener('dragover', e => { e.preventDefault(); uploadArea.classList.add('dragover'); });
uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
uploadArea.addEventListener('drop', e => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener('change', () => {
    if (fileInput.files.length) handleFile(fileInput.files[0]);
});

function handleFile(file) {
    $('#progress-filename').textContent = file.name;
    uploadArea.classList.add('hidden');
    uploadProgress.classList.remove('hidden');
    uploadSuccess.classList.add('hidden');

    // Simulate upload & analysis
    let progress = 0;
    const progressFill = $('#progress-bar-fill');
    const progressText = $('#progress-text');
    const progressPercent = $('#progress-percent');

    const interval = setInterval(() => {
        progress += Math.random() * 12 + 3;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
            progressText.textContent = 'Análise concluída!';
            setTimeout(() => {
                uploadProgress.classList.add('hidden');
                uploadSuccess.classList.remove('hidden');
                // Add new mock session
                const newSession = createMockSession(file.name);
                mockSessions.unshift(newSession);
                renderSessionsTable();
            }, 600);
        } else if (progress > 50) {
            progressText.textContent = 'Analisando expressões...';
        }
        progressFill.style.width = Math.min(progress, 100) + '%';
        progressPercent.textContent = Math.floor(Math.min(progress, 100)) + '%';
    }, 300);
}

function createMockSession(filename) {
    const id = mockSessions.length + 1;
    const keys = Object.keys(EMOTIONS);
    const predominant = keys[Math.floor(Math.random() * keys.length)];
    const confidence = Math.floor(Math.random() * 35 + 40);
    const probs = {};
    let remaining = 100 - confidence;
    probs[predominant] = confidence;
    keys.filter(k => k !== predominant).forEach((k, i, arr) => {
        if (i === arr.length - 1) {
            probs[k] = Math.max(0, remaining);
        } else {
            const v = Math.floor(Math.random() * (remaining / (arr.length - i)));
            probs[k] = v;
            remaining -= v;
        }
    });
    return {
        id,
        name: `Sessão ${String(id).padStart(2, '0')}`,
        date: new Date().toISOString().split('T')[0],
        duration: `0${Math.floor(Math.random() * 4 + 1)}:${String(Math.floor(Math.random() * 60)).padStart(2, '0')}`,
        frames: Math.floor(Math.random() * 200 + 60),
        predominant,
        confidence,
        probabilities: probs,
        timeline: generateTimeline(Math.floor(Math.random() * 200 + 60)),
    };
}

$('#btn-view-results').addEventListener('click', () => {
    renderDashboard(mockSessions[0]);
    switchView('dashboard');
    // Reset upload state
    uploadArea.classList.remove('hidden');
    uploadProgress.classList.add('hidden');
    uploadSuccess.classList.add('hidden');
    fileInput.value = '';
});

// --- Chart time range controls ---
$$('.chart-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        $$('.chart-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const range = btn.dataset.range;
        const timeline = currentSession.timeline;
        if (range === 'all') {
            renderTimelineChart(timeline);
        } else {
            const limit = parseInt(range);
            const sliced = {};
            Object.keys(timeline).forEach(k => {
                sliced[k] = timeline[k].slice(0, limit);
            });
            renderTimelineChart(sliced);
        }
    });
});

// --- Utility ---
function formatDate(dateStr) {
    const [y, m, d] = dateStr.split('-');
    return `${d}/${m}/${y}`;
}

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
    renderDashboard(mockSessions[0]);
    renderSessionsTable();
});
