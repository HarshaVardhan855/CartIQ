# 🛒 CartIQ — Search Once. Compare Everywhere.

> **Smart Shopping Made Simple.** An AI-powered e-commerce product discovery and price comparison platform that searches products across marketplaces, groups identical products, compares prices, ratings, and offers—all with transparent, explainable AI.

---

## 🎯 Why CartIQ?

Tired of hunting for the best deal across multiple marketplaces? CartIQ does the heavy lifting:

✨ **Smart Search** — Understand what you're looking for, even if you say it differently  
💰 **Best Prices** — Compare prices across Amazon, Flipkart, Meesho, and more in seconds  
🎯 **Smart Matching** — Group identical products using advanced AI matching (not just keywords)  
🤖 **Ask Anything** — Our AI shopping assistant answers your questions based on real product data  
🔍 **Transparency First** — Know exactly how we matched products and where prices come from  

---

## 🚀 How It Works

### 1️⃣ **Natural Language Understanding**
You type what you want. CartIQ understands your intent—whether you say "Nike running shoes under ₹2000" or "affordable sneakers for marathons."

- **Primary AI**: Google Gemini 1.5 Flash (Fast, intelligent)
- **Backup AI**: Groq Llama-3 (Always available)
- **Resilience Layer**: Deterministic rule-based parsing (Zero LLM dependency)

### 2️⃣ **Multi-Marketplace Search**
CartIQ searches across real marketplaces:
- 🔗 Direct marketplace links (Amazon, Flipkart, Meesho)
- 📊 Live price & availability data (when APIs are configured)
- 🏷️ Affiliate tracking support (transparent, secure)

### 3️⃣ **Explainable Product Matching** (5-Step Process)
Instead of black-box matching, CartIQ shows its work:

| Step | What It Does |
|------|-------------|
| 🏢 **Brand Matching** | Ensures same brand across matches |
| 📦 **Model & SKU** | Extracts product variants accurately |
| 📝 **Name Similarity** | Uses Jaccard & sequence matching for normalized comparison |
| ⚙️ **Specs & Features** | Matches technical specifications and feature sets |
| 🧠 **Semantic AI** | Final intelligent comparison using embeddings |

### 4️⃣ **Price Comparison Engine**
Deterministic Python logic calculates:
- ✅ Lowest price (with marketplace)
- 📈 Highest price for comparison
- 💸 Potential savings
- ⭐ Best offer marketplace

### 5️⃣ **AI Shopping Assistant** (RAG-Powered)
Ask questions → Get answers grounded in real product data  
"Should I buy this phone?" → Answer based on actual specs, ratings, and prices from matched products

---

## 🛡️ Our Data Integrity Promise

### ✅ **Real Data Only**
- **Never** fabricates prices, ratings, reviews, or availability
- **Never** hides product limitations or guesses at unavailable information
- **Never** replaces product URLs with guesses

### 📊 **Clear Status Labeling**
| Status | Meaning |
|--------|---------|
| ✅ **Live Data** | Real marketplace API data |
| ⚠️ **Not Configured** | API not set up; use direct marketplace links |
| 🧪 **DEMO DATA** | Test data for development only (clearly marked) |

### 🔗 **Smart Link Handling**
- ✅ Valid product links → Direct to marketplace
- ❌ Broken/malformed links → Marked as "Product link unavailable"
- 🚫 No guessing, no redirects to unrelated pages

---

## 💻 Tech Stack

| Component | Technology |
|-----------|------------|
| **AI/LLM** | Google Gemini 1.5 Flash, Groq Llama-3 |
| **Search Understanding** | NLP with regex resilience layer |
| **Matching Engine** | Jaccard, SequenceMatcher, Semantic Embeddings |
| **Frontend** | Streamlit (interactive UI) |
| **Backend** | FastAPI (RESTful API) |
| **Language** | Python 3.10+ |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/HarshaVardhan855/CartIQ.git
cd CartIQ

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
```

**Required Variables:**
```env
# AI Providers (at least one required)
GEMINI_API_KEY=your_gemini_key_here
GROQ_API_KEY=your_groq_key_here

# Optional: Email Notifications
SENDGRID_API_KEY=your_sendgrid_key
SENDGRID_SENDER_EMAIL=noreply@cartiq.app

# Optional: Live Marketplace APIs
AMAZON_API_KEY=your_amazon_api_key
FLIPKART_API_KEY=your_flipkart_api_key
MEESHO_API_KEY=your_meesho_api_key

# Optional: Affiliate Tracking
AMAZON_ASSOCIATE_TAG=your_tag
FLIPKART_AFFILIATE_ID=your_id
```

### Running the Application

**Option 1: Interactive UI (Streamlit)**
```bash
streamlit run app.py
```
Visit `http://localhost:8501` in your browser.

**Option 2: REST API (FastAPI)**
```bash
uvicorn backend.main:app --reload --port 8000
```
API docs available at `http://localhost:8000/docs`

---

## 🧪 Testing

Run the complete test suite:
```bash
pytest -v
```

---

## 📊 Project Structure

```
CartIQ/
├── app.py                 # Streamlit frontend
├── backend/
│   ├── main.py           # FastAPI server
│   ├── ai_engine.py      # LLM integration & query understanding
│   ├── matcher.py        # 5-step product matching
│   ├── comparator.py     # Price comparison logic
│   └── rag_assistant.py  # AI shopping assistant
├── tests/                # Test suite
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

---

## 🎓 Key Features for Different Users

### 👥 **For End Users**
- 🔍 One search box, compare thousands of products
- 💰 Instantly see price differences across marketplaces
- ⭐ Read aggregated ratings and reviews
- 🤖 Ask an AI shopping assistant for recommendations

### 💼 **For Business**
- 📈 Attract price-conscious shoppers
- 💳 Monetize via affiliate commissions
- 🔗 Direct traffic to partner marketplaces
- 📊 Analytics on search trends

### 👨‍💻 **For Developers & Researchers**
- 🧪 Advanced product matching algorithms
- 🎯 Explainable AI decision-making
- 🔌 REST API for integration
- 📚 Well-documented, clean Python codebase

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📝 License

This project is open-source. Check the LICENSE file for details.

---

## 🙋 Support & Questions

- 📧 Open an issue on GitHub for bugs or feature requests
- 💬 Check existing issues for Q&A
- 🐛 Found a bug? Help us improve—report it!

---

## ✨ Future Roadmap

- 🌍 International marketplace support
- 📱 Mobile app
- 🔔 Price drop alerts
- 👥 User wishlists & comparison history
- 🎁 Deal discovery & trending products
- 🗣️ Multi-language support

---

<div align="center">

**Made with ❤️ for smarter shopping**

⭐ Star this repo if CartIQ saved you money!

</div>
