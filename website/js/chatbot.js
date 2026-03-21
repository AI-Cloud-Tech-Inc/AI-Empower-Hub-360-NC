// ============================================================
// Empower Hub 360 - Live AI Chat Widget
// Powered by Gemini via /api/v1/chatbot/chat
// ============================================================

let chatOpen = false;
let chatHistory = [];

function toggleChat() {
    const widget = document.getElementById('chat-widget');
    const trigger = document.getElementById('chat-trigger');
    chatOpen = !chatOpen;
    if (widget) widget.classList.toggle('chat-open', chatOpen);
    if (trigger) trigger.classList.toggle('chat-active', chatOpen);
    if (chatOpen) {
        setTimeout(() => {
            const input = document.getElementById('chat-input');
            if (input) input.focus();
        }, 300);
    }
}

function appendMessage(role, text) {
    const container = document.getElementById('chat-messages');
    if (!container) return;

    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;

    // Convert markdown-like line breaks
    const formatted = text.replace(/\n/g, '<br>');
    div.innerHTML = `<div class="msg-bubble">${formatted}</div>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function appendTypingIndicator() {
    const container = document.getElementById('chat-messages');
    if (!container) return null;
    const div = document.createElement('div');
    div.className = 'chat-msg bot typing-indicator-wrap';
    div.id = 'typing-indicator';
    div.innerHTML = `<div class="msg-bubble typing-indicator"><span></span><span></span><span></span></div>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return div;
}

async function sendChat() {
    const input = document.getElementById('chat-input');
    if (!input) return;

    const message = input.value.trim();
    if (!message) return;

    input.value = '';
    appendMessage('user', message);
    chatHistory.push({ role: 'user', text: message });

    // Show typing indicator
    const indicator = appendTypingIndicator();

    // Determine context from current page
    const path = window.location.pathname;
    let context = 'general';
    if (path.includes('services')) context = 'services';
    else if (path.includes('tools')) context = 'tools';
    else if (path.includes('about')) context = 'about';
    else if (path.includes('careers')) context = 'careers';

    try {
        const result = await API.chat(message, context);
        if (indicator) indicator.remove();

        if (result.ok && result.data) {
            const reply = result.data.response || 'I got your message! Our team will follow up shortly.';
            appendMessage('bot', reply);
            chatHistory.push({ role: 'bot', text: reply });
        } else {
            appendMessage('bot', '⚠️ I\'m having trouble connecting right now. Please try again or contact us at empowerhub360nc@gmail.com');
        }
    } catch (err) {
        if (indicator) indicator.remove();
        appendMessage('bot', '⚠️ Connection error. Please make sure the server is running on port 8003.');
    }
}

// Allow pressing Enter to send
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('chat-input');
    if (input) {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChat();
            }
        });
    }

    // Auto-open chat after 8 seconds on homepage only
    const isHome = window.location.pathname === '/' || window.location.pathname.endsWith('index.html');
    if (isHome) {
        setTimeout(() => {
            if (!chatOpen) toggleChat();
        }, 8000);
    }
});
