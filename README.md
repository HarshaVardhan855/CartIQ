# CartIQ — Search Once. Compare Everywhere.

CartIQ is an AI-powered e-commerce product discovery and price comparison platform. It enables natural-language product search across marketplaces, groups identical products using an explainable 5-step matching engine, performs deterministic price comparisons, and routes users to genuine marketplace search destinations.

---

## 🎯 Core Capabilities

1. **Natural-Language Query Understanding**:
   - Primary LLM: Google Gemini 1.5 Flash
   - Automatic Fallback: Groq (Llama-3)
   - Deterministic Regex Rule Parser as resilience fallback

2. **Real Marketplace Search Flow**:
   - When authorized live API data is not configured, CartIQ constructs direct, clean search links to **Amazon**, **Flipkart**, and **Meesho**.
   - Search destinations preserve the user's actual search terms while stripping budget qualifiers deterministically (e.g., *"running shoes under ₹2000 for men"* → search for *"running shoes for men"*).
   - Affiliate tracking parameters (`AMAZON_ASSOCIATE_TAG`, `FLIPKART_AFFILIATE_ID`) are supported without exposing credentials in client-side code.

3. **5-Step Explainable Product Matching**:
   - Step 1: Brand matching
   - Step 2: Model & SKU extraction / matching
   - Step 3: Normalized product-name similarity (Jaccard & SequenceMatcher)
   - Step 4: Specification & feature set intersection
   - Step 5: Semantic embedding similarity

4. **Deterministic Python Comparison Engine**:
   - Calculates lowest price, highest price, potential savings, and best-offer marketplace in Python.

5. **Grounded AI Shopping Assistant (RAG Engine)**:
   - Answers user shopping questions strictly grounded in retrieved product offers.

6. **Controlled Development & Demo Mode**:
   - Provides a demo catalog for development, algorithm verification, and testing.
   - Demo offers are explicitly labeled as **DEMO DATA** to maintain total transparency.

---

## 🛡️ Data Integrity & Honesty Principle

> **CartIQ never fabricates marketplace prices, ratings, review counts, availability, product IDs, ASINs, or product URLs.**

- **Verified Marketplace Data**: Displayed only when returned by an authorized programmatic API or permitted product feed with valid credentials.
- **Direct Marketplace Search**: When live API feeds are not configured, CartIQ clearly displays source statuses as `Not Configured` and provides one-click direct search buttons to real marketplace destinations.
- **Demo Data**: Clearly labeled as `DEMO DATA` for testing and development only. Demo prices and availability are never misrepresented as "Live".
- **Product Link Validation**: Malformed, placeholder, or domain-mismatched product URLs are safely marked as `Product link unavailable` and never replaced with guessed URLs.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Pip

### 2. Installation
```bash
git clone https://github.com/HarshaVardhan855/CartIQ.git
cd CartIQ
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and provide your API keys:
```bash
cp .env.example .env
```

Configuration variables:
```env
# AI Providers
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key

# Email Notifications (Optional)
SENDGRID_API_KEY=your_sendgrid_key
SENDGRID_SENDER_EMAIL=noreply@cartiq.app

# Live Marketplace APIs (Optional)
AMAZON_API_KEY=
FLIPKART_API_KEY=
MEESHO_API_KEY=

# Affiliate Tracking Tags (Optional)
AMAZON_ASSOCIATE_TAG=
FLIPKART_AFFILIATE_ID=
```

### 4. Running the Application

**Run Streamlit UI**:
```bash
streamlit run app.py
```

**Run FastAPI Backend**:
```bash
uvicorn backend.main:app --reload --port 8000
```

---

## 🧪 Testing

Run the test suite with:
```bash
pytest -v
```
