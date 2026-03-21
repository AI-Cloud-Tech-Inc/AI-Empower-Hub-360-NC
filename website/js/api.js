// ============================================================
// Empower Hub 360 - API Client
// Central module for all backend API communication
// Base URL: http://localhost:8003
// ============================================================

const API = (() => {
    const BASE = '';           // empty = same origin (served by FastAPI)
    const PREFIX = '/api/v1';

    // ── Core fetch helper ──────────────────────────────────
    async function request(method, path, body = null) {
        const opts = {
            method,
            headers: { 'Content-Type': 'application/json' },
        };
        if (body) opts.body = JSON.stringify(body);

        try {
            const res = await fetch(`${BASE}${PREFIX}${path}`, opts);
            const data = await res.json();
            return { ok: res.ok, status: res.status, data };
        } catch (err) {
            console.error(`[API] ${method} ${path} failed:`, err);
            return { ok: false, status: 0, data: null, error: err.message };
        }
    }

    // ── Health ─────────────────────────────────────────────
    async function healthCheck() {
        try {
            const res = await fetch(`${BASE}/health`);
            return res.ok;
        } catch {
            return false;
        }
    }

    // ── Chatbot ───────────────────────────────────────────
    async function chat(message, context = 'general') {
        return request('POST', '/chatbot/chat', { message, context });
    }

    async function createSession(userId) {
        return request('POST', `/chatbot/sessions?user_id=${userId}`);
    }

    // ── Consulting ────────────────────────────────────────
    async function submitConsultation({ name, email, company, service_type, message }) {
        return request('POST', '/consulting/consultation', {
            name, email, company, service_type: service_type || 'general', message: message || ''
        });
    }

    async function getServices() {
        return request('GET', '/consulting/services');
    }

    async function generateStrategy({ company_name, industry, current_tools = [], goals = [] }) {
        return request('POST', '/consulting/strategy', { company_name, industry, current_tools, goals });
    }

    // ── Automation ────────────────────────────────────────
    async function getWorkflows() {
        return request('GET', '/automation/workflows');
    }

    async function createWorkflow({ name, trigger, actions }) {
        return request('POST', '/automation/workflows', { name, trigger, actions });
    }

    async function getTasks() {
        return request('GET', '/automation/tasks');
    }

    async function createTask({ title, description = '', priority = 'medium' }) {
        return request('POST', '/automation/tasks', { title, description, priority });
    }

    async function executeWorkflow(workflowId) {
        return request('POST', `/automation/execute/${workflowId}`);
    }

    return {
        healthCheck,
        chat,
        createSession,
        submitConsultation,
        getServices,
        generateStrategy,
        getWorkflows,
        createWorkflow,
        getTasks,
        createTask,
        executeWorkflow,
    };
})();

// ── Toast Notification System ─────────────────────────────
const Toast = (() => {
    function show(message, type = 'success', duration = 4000) {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        const icons = { success: '✓', error: '✕', info: 'ℹ', warning: '⚠' };
        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || 'ℹ'}</span>
            <span class="toast-msg">${message}</span>
        `;
        container.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => toast.classList.add('toast-show'));

        // Remove after duration
        setTimeout(() => {
            toast.classList.remove('toast-show');
            toast.addEventListener('transitionend', () => toast.remove());
        }, duration);
    }

    return { show, success: m => show(m, 'success'), error: m => show(m, 'error'), info: m => show(m, 'info'), warning: m => show(m, 'warning') };
})();

// ── Server Status Badge ───────────────────────────────────
(async () => {
    const alive = await API.healthCheck();
    const badge = document.getElementById('server-status');
    if (badge) {
        badge.textContent = alive ? '🟢 API Online' : '🔴 API Offline';
        badge.style.color = alive ? '#22c55e' : '#ef4444';
    }
    if (!alive) {
        console.warn('[Empower Hub] Backend API is offline. Start the server: uvicorn src.main:app --port 8003');
    }
})();
