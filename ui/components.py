"""
Streamlit UI Custom Components and CSS Styling for CartIQ.
Provides sleek, modern, responsive marketplace search cards matching the reference design,
and a floating CartIQ AI Shopping Assistant chat widget.
"""

import textwrap
from typing import Dict, Any, List
import streamlit as st
from data.schemas import GroupedProduct


def inject_custom_css():
    """
    Injects custom styling matching the reference visual cards, typography,
    and floating AI chat widget.
    """
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hero Branding Header */
    .brand-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
        text-align: center;
    }

    .brand-subtitle {
        font-size: 1.25rem;
        color: #94a3b8;
        font-weight: 500;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Reference Header Section */
    .results-hero-header {
        margin: 20px 0 6px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .results-hero-icon {
        font-size: 1.8rem;
        color: #6366f1;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }

    .results-hero-title {
        font-size: 1.75rem;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.01em;
        margin: 0;
    }

    .results-query-highlight {
        color: #6366f1;
        font-weight: 800;
    }

    .results-hero-subtitle {
        font-size: 0.95rem;
        color: #64748b;
        margin: 0 0 22px 0;
        line-height: 1.5;
    }

    /* Marketplace Responsive Cards Grid */
    .marketplace-cards-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 22px;
        margin-bottom: 24px;
        width: 100%;
    }

    .ref-market-card {
        border-radius: 22px;
        padding: 24px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 340px;
        transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s ease;
        position: relative;
        box-sizing: border-box;
    }

    .ref-market-card:hover {
        transform: translateY(-4px);
    }

    /* Card Themes */
    .ref-market-card.amazon {
        background: linear-gradient(180deg, #fffdf8 0%, #fff7eb 100%);
        border: 1.5px solid #fed7aa;
        box-shadow: 0 10px 25px -5px rgba(249, 115, 22, 0.08);
    }
    .ref-market-card.amazon:hover {
        box-shadow: 0 16px 32px -6px rgba(249, 115, 22, 0.18);
    }

    .ref-market-card.flipkart {
        background: linear-gradient(180deg, #f8fbff 0%, #eff6ff 100%);
        border: 1.5px solid #bfdbfe;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.08);
    }
    .ref-market-card.flipkart:hover {
        box-shadow: 0 16px 32px -6px rgba(37, 99, 235, 0.18);
    }

    .ref-market-card.meesho {
        background: linear-gradient(180deg, #fdf9ff 0%, #fae8ff 100%);
        border: 1.5px solid #e9d5ff;
        box-shadow: 0 10px 25px -5px rgba(147, 51, 234, 0.08);
    }
    .ref-market-card.meesho:hover {
        box-shadow: 0 16px 32px -6px rgba(147, 51, 234, 0.18);
    }

    /* Card Top Header */
    .card-top-row {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        margin-bottom: 16px;
    }

    .brand-identity-group {
        display: flex;
        align-items: center;
        gap: 14px;
    }

    .brand-logo-box {
        width: 56px;
        height: 56px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(0, 0, 0, 0.05);
        font-weight: 900;
    }

    .brand-logo-box.amazon {
        background: #ffffff;
        color: #111827;
        font-size: 2rem;
        font-family: serif;
    }

    .brand-logo-box.flipkart {
        background: #ffd814;
        color: #2874f0;
        font-size: 1.9rem;
    }

    .brand-logo-box.meesho {
        background: #6b21a8;
        color: #f59e0b;
        font-size: 1.7rem;
    }

    .brand-name-and-link {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .brand-name-text {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0;
        line-height: 1.2;
    }

    .live-link-badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        width: fit-content;
    }

    .live-link-badge-pill.amazon {
        background: #ffedd5;
        color: #c2410c;
        border: 1px solid #fed7aa;
    }
    .live-link-badge-pill.flipkart {
        background: #dbeafe;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
    }
    .live-link-badge-pill.meesho {
        background: #f3e8ff;
        color: #7e22ce;
        border: 1px solid #e9d5ff;
    }

    .official-badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: #dcfce7;
        color: #15803d;
        border: 1px solid #bbf7d0;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        white-space: nowrap;
    }

    /* Description */
    .card-description-text {
        font-size: 0.9rem;
        color: #475569;
        line-height: 1.55;
        margin-bottom: 18px;
        min-height: 48px;
    }

    /* Highlight Feature Pills */
    .feature-pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 22px;
    }

    .feature-pill-chip {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 5px 11px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
    }

    .feature-pill-chip.amazon {
        background: #ffedd5;
        color: #9a3412;
        border: 1px solid #fed7aa;
    }
    .feature-pill-chip.flipkart {
        background: #dbeafe;
        color: #1e40af;
        border: 1px solid #bfdbfe;
    }
    .feature-pill-chip.meesho {
        background: #f3e8ff;
        color: #6b21a8;
        border: 1px solid #e9d5ff;
    }

    /* Large Action CTA Button */
    .card-cta-button {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        width: 100%;
        padding: 13px 20px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.95rem;
        text-decoration: none !important;
        transition: all 0.2s ease;
        box-sizing: border-box;
    }

    .card-cta-button.amazon {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
        color: #ffffff !important;
        box-shadow: 0 6px 16px rgba(234, 88, 12, 0.28);
    }
    .card-cta-button.amazon:hover {
        background: linear-gradient(135deg, #fb923c 0%, #ea580c 100%);
        box-shadow: 0 8px 20px rgba(234, 88, 12, 0.38);
    }

    .card-cta-button.flipkart {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff !important;
        box-shadow: 0 6px 16px rgba(29, 78, 216, 0.28);
    }
    .card-cta-button.flipkart:hover {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        box-shadow: 0 8px 20px rgba(29, 78, 216, 0.38);
    }

    .card-cta-button.meesho {
        background: linear-gradient(135deg, #7e22ce 0%, #6b21a8 100%);
        color: #ffffff !important;
        box-shadow: 0 6px 16px rgba(107, 33, 168, 0.28);
    }
    .card-cta-button.meesho:hover {
        background: linear-gradient(135deg, #9333ea 0%, #6b21a8 100%);
        box-shadow: 0 8px 20px rgba(107, 33, 168, 0.38);
    }

    /* Smart Search Bottom Info Box */
    .smart-search-info-box {
        background: #f0f7ff;
        border: 1.5px solid #dbeafe;
        border-radius: 16px;
        padding: 18px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 10px;
        margin-bottom: 26px;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.05);
    }

    .smart-search-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }

    .smart-search-icon {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: #3b82f6;
        color: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.1rem;
        flex-shrink: 0;
    }

    .smart-search-text-group {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }

    .smart-search-title {
        font-size: 1rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0;
    }

    .smart-search-desc {
        font-size: 0.88rem;
        color: #64748b;
        margin: 0;
    }

    .smart-search-art {
        font-size: 2rem;
        display: flex;
        align-items: center;
        gap: 4px;
        color: #6366f1;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


import os

def inject_floating_chat_widget():
    """
    Injects the CartIQ AI floating chat widget into the Streamlit page.
    The widget is a bottom-right floating button that expands into a compact
    chat window when clicked. Uses the CartIQ /ask_ai backend endpoint.
    Compatible with Streamlit's HTML injection via st.markdown.
    """
    api_url = os.environ.get("CARTIQ_API_URL", "http://127.0.0.1:8001")
    
    widget_html = f"""
<style>
/* ===== Floating Chat Widget Styles ===== */
#cartiq-chat-launcher {{
    position: fixed;
    bottom: 28px;
    right: 28px;
    z-index: 99999;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 14px;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}}

#cartiq-chat-btn {{
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: #fff;
    border: none;
    cursor: pointer;
    font-size: 1.6rem;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.45);
    transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.2s ease;
    position: relative;
}}
#cartiq-chat-btn:hover {{
    transform: scale(1.1);
    box-shadow: 0 12px 30px rgba(99, 102, 241, 0.55);
}}
#cartiq-chat-btn .chat-btn-label {{
    position: absolute;
    right: 70px;
    background: #1e1b4b;
    color: #fff;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 5px 12px;
    border-radius: 20px;
    white-space: nowrap;
    box-shadow: 0 4px 12px rgba(0,0,0,0.18);
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s ease;
}}
#cartiq-chat-btn:hover .chat-btn-label {{
    opacity: 1;
}}

/* Chat Window */
#cartiq-chat-window {{
    width: 360px;
    max-width: calc(100vw - 40px);
    height: 480px;
    max-height: calc(100vh - 120px);
    background: #ffffff;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.16), 0 4px 16px rgba(99, 102, 241, 0.12);
    display: none;
    flex-direction: column;
    overflow: hidden;
    border: 1.5px solid #e8e5ff;
    animation: chatSlideIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}}
#cartiq-chat-window.open {{
    display: flex;
}}
@keyframes chatSlideIn {{
    from {{ opacity: 0; transform: translateY(16px) scale(0.96); }}
    to   {{ opacity: 1; transform: translateY(0) scale(1); }}
}}

/* Chat Header */
#cartiq-chat-header {{
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: #fff;
    padding: 14px 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
}}
.chat-header-left {{
    display: flex;
    align-items: center;
    gap: 10px;
}}
.chat-header-avatar {{
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: rgba(255,255,255,0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    font-weight: 800;
}}
.chat-header-info h4 {{
    margin: 0;
    font-size: 0.95rem;
    font-weight: 700;
}}
.chat-header-info p {{
    margin: 0;
    font-size: 0.72rem;
    opacity: 0.85;
}}
#cartiq-chat-close {{
    background: none;
    border: none;
    color: #fff;
    font-size: 1.4rem;
    cursor: pointer;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0.85;
    transition: background 0.15s ease, opacity 0.15s ease;
}}
#cartiq-chat-close:hover {{
    background: rgba(255,255,255,0.18);
    opacity: 1;
}}

/* Messages Area */
#cartiq-chat-messages {{
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    background: #fafafa;
    scroll-behavior: smooth;
}}
#cartiq-chat-messages::-webkit-scrollbar {{
    width: 4px;
}}
#cartiq-chat-messages::-webkit-scrollbar-track {{
    background: transparent;
}}
#cartiq-chat-messages::-webkit-scrollbar-thumb {{
    background: #e0e0e0;
    border-radius: 4px;
}}

.chat-msg {{
    max-width: 85%;
    padding: 10px 14px;
    border-radius: 16px;
    font-size: 0.875rem;
    line-height: 1.5;
    word-break: break-word;
}}
.chat-msg.bot {{
    background: #ffffff;
    color: #1e293b;
    align-self: flex-start;
    border-bottom-left-radius: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border: 1px solid #f1f5f9;
}}
.chat-msg.user {{
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: #ffffff;
    align-self: flex-end;
    border-bottom-right-radius: 4px;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
}}
.chat-msg.typing {{
    background: #fff;
    border: 1px solid #f1f5f9;
    align-self: flex-start;
    color: #94a3b8;
    font-style: italic;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}}

/* Disclaimer */
.chat-disclaimer {{
    font-size: 0.7rem;
    color: #94a3b8;
    text-align: center;
    padding: 4px 12px 8px;
    flex-shrink: 0;
    background: #fafafa;
}}

/* Input Area */
#cartiq-chat-input-row {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 14px;
    background: #ffffff;
    border-top: 1px solid #f1f5f9;
    flex-shrink: 0;
}}
#cartiq-chat-input {{
    flex: 1;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    padding: 9px 13px;
    font-size: 0.875rem;
    font-family: 'Plus Jakarta Sans', sans-serif;
    outline: none;
    color: #1e293b;
    background: #f8fafc;
    transition: border-color 0.2s ease;
    resize: none;
}}
#cartiq-chat-input:focus {{
    border-color: #8b5cf6;
    background: #fff;
}}
#cartiq-chat-send {{
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: #fff;
    border: none;
    cursor: pointer;
    font-size: 1.1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    box-shadow: 0 3px 10px rgba(99, 102, 241, 0.3);
}}
#cartiq-chat-send:hover {{
    transform: scale(1.08);
    box-shadow: 0 5px 14px rgba(99, 102, 241, 0.4);
}}
#cartiq-chat-send:disabled {{
    opacity: 0.55;
    transform: none;
    cursor: not-allowed;
}}
</style>

<div id="cartiq-chat-launcher">
    <!-- Chat Window (hidden by default) -->
    <div id="cartiq-chat-window">
        <div id="cartiq-chat-header">
            <div class="chat-header-left">
                <div class="chat-header-avatar">🛒</div>
                <div class="chat-header-info">
                    <h4>CartIQ Shopping Assistant</h4>
                    <p>General shopping advisor · No live prices</p>
                </div>
            </div>
            <button id="cartiq-chat-close" title="Minimize">✕</button>
        </div>

        <div id="cartiq-chat-messages">
            <div class="chat-msg bot">
                Hi! I'm CartIQ's AI Shopping Advisor 👋<br><br>
                Ask me about product features, buying tips, what to look for, or which marketplace suits your needs.<br><br>
                <em>Note: I provide general guidance — for live prices, click the marketplace cards above.</em>
            </div>
        </div>

        <div class="chat-disclaimer">
            ⚠️ General advice only — no live prices or availability
        </div>

        <div id="cartiq-chat-input-row">
            <input
                type="text"
                id="cartiq-chat-input"
                placeholder="Ask about a product..."
                maxlength="500"
                autocomplete="off"
            />
            <button id="cartiq-chat-send" title="Send">➤</button>
        </div>
    </div>

    <!-- Floating Launcher Button -->
    <button id="cartiq-chat-btn" title="CartIQ AI Shopping Assistant">
        <span class="chat-btn-label">CartIQ AI</span>
        🛒
    </button>
</div>

<script>
(function() {{
    // Wait for DOM to be ready
    function initChatWidget() {{
        var btn = document.getElementById('cartiq-chat-btn');
        var win = document.getElementById('cartiq-chat-window');
        var closeBtn = document.getElementById('cartiq-chat-close');
        var input = document.getElementById('cartiq-chat-input');
        var sendBtn = document.getElementById('cartiq-chat-send');
        var messages = document.getElementById('cartiq-chat-messages');

        if (!btn || !win) {{
            setTimeout(initChatWidget, 300);
            return;
        }}

        var isOpen = false;

        function openChat() {{
            isOpen = true;
            win.classList.add('open');
            btn.innerHTML = '<span class="chat-btn-label">CartIQ AI</span>✕';
            input.focus();
        }}

        function closeChat() {{
            isOpen = false;
            win.classList.remove('open');
            btn.innerHTML = '<span class="chat-btn-label">CartIQ AI</span>🛒';
        }}

        btn.addEventListener('click', function() {{
            if (isOpen) closeChat(); else openChat();
        }});
        closeBtn.addEventListener('click', closeChat);

        function appendMessage(text, type) {{
            var el = document.createElement('div');
            el.className = 'chat-msg ' + type;
            el.innerHTML = text.replace(/\\n/g, '<br>');
            messages.appendChild(el);
            messages.scrollTop = messages.scrollHeight;
            return el;
        }}

        function removeElement(el) {{
            if (el && el.parentNode) el.parentNode.removeChild(el);
        }}

        function sendMessage() {{
            var q = input.value.trim();
            if (!q) return;

            appendMessage(q, 'user');
            input.value = '';
            sendBtn.disabled = true;

            var typingEl = appendMessage('CartIQ is thinking...', 'typing');

            // Call the CartIQ FastAPI backend
            fetch('{api_url}/ask_ai', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ question: q }})
            }})
            .then(function(r) {{ return r.json(); }})
            .then(function(data) {{
                removeElement(typingEl);
                var answer = data.answer || data.message || 'Sorry, I could not get an answer right now.';
                // Escape HTML then convert newlines
                var safe = answer.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
                appendMessage(safe, 'bot');
            }})
            .catch(function(err) {{
                removeElement(typingEl);
                appendMessage('Sorry, something went wrong. Please try again.', 'bot');
            }})
            .finally(function() {{
                sendBtn.disabled = false;
                input.focus();
            }});
        }}

        sendBtn.addEventListener('click', sendMessage);
        input.addEventListener('keydown', function(e) {{
            if (e.key === 'Enter' && !e.shiftKey) {{
                e.preventDefault();
                sendMessage();
            }}
        }});
    }}

    // Initialize after a short delay to ensure Streamlit has rendered
    setTimeout(initChatWidget, 500);
}})();
</script>
"""
    st.markdown(widget_html, unsafe_allow_html=True)


def render_header():
    """
    Renders CartIQ Hero Title & Subtitle.
    """
    st.markdown('<div class="brand-title">CARTIQ</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-subtitle">Search Once. Compare Everywhere.</div>', unsafe_allow_html=True)


def render_provider_status(provider_used: str):
    """
    Renders technical transparency status indicator.
    """
    icon_map = {
        "gemini": "⚡ Primary Provider: Gemini 1.5 Flash",
        "groq": "🛡️ Fallback Provider: Groq (Llama-3)",
        "deterministic_fallback": "⚙️ Deterministic Rule Parser",
        "none": "ℹ️ Direct Python Search"
    }
    label = icon_map.get(provider_used, f"Provider: {provider_used}")
    st.markdown(f'<div style="background: rgba(99, 102, 241, 0.15); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; display: inline-block;">{label}</div>', unsafe_allow_html=True)


def render_marketplace_search_cards(
    search_links: Dict[str, Dict[str, Any]],
    user_query: str,
    marketplace_filter: str = "All"
):
    """
    Renders modern, attractive, responsive marketplace cards for Amazon, Flipkart, and Meesho
    strictly following the reference visual design.
    Filters cards based on user selection:
    - If marketplace_filter == "All": shows Amazon + Flipkart + Meesho (exactly 3 cards)
    - If marketplace_filter == "Amazon": shows Amazon only (exactly 1 card)
    - If marketplace_filter == "Flipkart": shows Flipkart only (exactly 1 card)
    - If marketplace_filter == "Meesho": shows Meesho only (exactly 1 card)
    """
    amz_info = search_links.get("amazon", {})
    fk_info = search_links.get("flipkart", {})
    msh_info = search_links.get("meesho", {})

    amz_url = amz_info.get("url", "https://www.amazon.in")
    fk_url = fk_info.get("url", "https://www.flipkart.com")
    msh_url = msh_info.get("url", "https://www.meesho.com")

    cleaned_q = amz_info.get("query") or user_query

    # Amazon Card HTML (Matching Screenshot)
    amazon_card = f"""
<div class="ref-market-card amazon">
<div>
<div class="card-top-row">
<div class="brand-identity-group">
<div class="brand-logo-box amazon">a</div>
<div class="brand-name-and-link">
<h3 class="brand-name-text">Amazon</h3>
<span class="live-link-badge-pill amazon">🔗 Live Link</span>
</div>
</div>
<span class="official-badge-pill">✔ Official Website</span>
</div>
<div class="card-description-text">
Explore a wide range of {cleaned_q} with real-time prices, offers and customer reviews on Amazon.
</div>
<div class="feature-pill-row">
<span class="feature-pill-chip amazon">✔ Latest Prices</span>
<span class="feature-pill-chip amazon">✔ Big Offers</span>
<span class="feature-pill-chip amazon">✔ Verified Sellers</span>
</div>
</div>
<a href="{amz_url}" target="_blank" class="card-cta-button amazon">
⎘ Search Amazon &rarr;
</a>
</div>
"""

    # Flipkart Card HTML (Matching Screenshot)
    flipkart_card = f"""
<div class="ref-market-card flipkart">
<div>
<div class="card-top-row">
<div class="brand-identity-group">
<div class="brand-logo-box flipkart">🛍️</div>
<div class="brand-name-and-link">
<h3 class="brand-name-text">Flipkart</h3>
<span class="live-link-badge-pill flipkart">🔗 Live Link</span>
</div>
</div>
<span class="official-badge-pill">✔ Official Website</span>
</div>
<div class="card-description-text">
Find the latest {cleaned_q}, compare prices, check ratings and read reviews on Flipkart.
</div>
<div class="feature-pill-row">
<span class="feature-pill-chip flipkart">✔ Latest Deals</span>
<span class="feature-pill-chip flipkart">✔ Top Rated</span>
<span class="feature-pill-chip flipkart">✔ Easy Returns</span>
</div>
</div>
<a href="{fk_url}" target="_blank" class="card-cta-button flipkart">
⎘ Search Flipkart &rarr;
</a>
</div>
"""

    # Meesho Card HTML (Matching Screenshot)
    meesho_card = f"""
<div class="ref-market-card meesho">
<div>
<div class="card-top-row">
<div class="brand-identity-group">
<div class="brand-logo-box meesho">m</div>
<div class="brand-name-and-link">
<h3 class="brand-name-text">Meesho</h3>
<span class="live-link-badge-pill meesho">🔗 Live Link</span>
</div>
</div>
<span class="official-badge-pill">✔ Official Website</span>
</div>
<div class="card-description-text">
Discover affordable {cleaned_q} with great quality and value on Meesho.
</div>
<div class="feature-pill-row">
<span class="feature-pill-chip meesho">✔ Best Prices</span>
<span class="feature-pill-chip meesho">✔ Wide Variety</span>
<span class="feature-pill-chip meesho">✔ Trusted Sellers</span>
</div>
</div>
<a href="{msh_url}" target="_blank" class="card-cta-button meesho">
⎘ Search Meesho &rarr;
</a>
</div>
"""

    # Deterministic card filtering logic
    cards_to_render: List[str] = []
    selected_lower = (marketplace_filter or "All").strip().lower()

    if selected_lower in ["all", ""]:
        cards_to_render = [amazon_card, flipkart_card, meesho_card]
    elif selected_lower == "amazon":
        cards_to_render = [amazon_card]
    elif selected_lower == "flipkart":
        cards_to_render = [flipkart_card]
    elif selected_lower == "meesho":
        cards_to_render = [meesho_card]
    else:
        cards_to_render = [amazon_card, flipkart_card, meesho_card]

    rendered_cards_html = "\n".join(cards_to_render)

    # Full Section Container with Screenshot Matching Layout
    html = f"""
<div style="width: 100%; margin-top: 18px;">
<div class="results-hero-header">
<span class="results-hero-icon">✦</span>
<h2 class="results-hero-title">Search Results for <span class="results-query-highlight">"{user_query}"</span></h2>
</div>
<p class="results-hero-subtitle">
I've found the best marketplace links for your search. Click on any platform below to view the latest products directly on their website.
</p>
<div class="marketplace-cards-container">
{rendered_cards_html}
</div>
<div class="smart-search-info-box">
<div class="smart-search-left">
<div class="smart-search-icon">ℹ</div>
<div class="smart-search-text-group">
<div class="smart-search-title">Smart Search</div>
<div class="smart-search-desc">Click on any platform above to open their website and search for the latest {cleaned_q}.</div>
</div>
</div>
<div class="smart-search-art">🔍 ✨</div>
</div>
</div>
"""
    # Clean any accidental 4-space markdown indentations
    clean_html = textwrap.dedent(html).strip()
    st.markdown(clean_html, unsafe_allow_html=True)
