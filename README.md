<p align="center">
    <img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg" align="center" width="30%">
</p>
<p align="center"><h1 align="center">FINQUANT PRO</h1></p>
<p align="center">
	<em><code>Your AI Fund Manager - Brutally Honest Stock Advice</code></em>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/sidlihe/FinQuant_Agnet.git?style=default&logo=opensourceinitiative&logoColor=white&color=00e0ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/sidlihe/FinQuant_Agnet.git?style=default&logo=git&logoColor=white&color=00e0ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/sidlihe/FinQuant_Agnet.git?style=default&color=00e0ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/sidlihe/FinQuant_Agnet.git?style=default&color=00e0ff" alt="repo-language-count">
</p>
<p align="center">
	<img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="python">
	<img src="https://img.shields.io/badge/Stock%20Analysis-AI%20Powered-green" alt="ai">
	<img src="https://img.shields.io/badge/Recommendations-Data%20Driven-orange" alt="data-driven">
</p>
<br>

## 🚀 What is FinQuant Pro?

**FinQuant Pro is your personal AI fund manager** that gives you brutally honest, data-driven stock advice. Just type any Indian stock name and get institutional-grade analysis with clear **BUY/HOLD/SELL** recommendations.

### 🎯 Real Examples - See It Working

**For Stock You OWN:**


---

## ✨ Why Use FinQuant Pro?

| Feature | Benefit |
|---------|---------|
| **🤖 AI-Powered Analysis** | Get fund manager-level insights without the fees |
| **📊 Real Data** | Live fundamentals from Screener + technicals from Yahoo Finance |
| **🎯 Clear Recommendations** | Specific BUY/HOLD/SELL advice with exact price targets |
| **💼 Personalized** | Different advice if you own the stock vs new investment |
| **📈 Risk Assessment** | Understand the risks before you invest |
| **💾 Professional Reports** | Save all analysis for future reference |

---

## 🛠️ How It Works

1. **Tell us the stock** (any name - "tcs", "reliance", "irfc")
2. **We identify it** automatically with correct NSE ticker
3. **Fetch live data** - fundamentals + technical charts
4. **AI analyzes everything** and gives specific advice
5. **Get your report** with clear action plan

---

## 🚀 Quick Start

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/sidlihe/FinQuant_Agnet.git
cd FinQuant_Agnet.git

# 2. Create virtual environment
python -m venv venv

# 3. Activate environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirement.txt

# 5. Setup environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

FinQuant_Pro/
├── main.py                 # 🎯 Main application (run this!)
├── outputs/               # 📊 Your stock analysis reports
├── info_json/            # 💾 Raw data files
├── requirements.txt       # 📦 Dependencies
└── src/
    ├── tools.py          # 🔧 Stock data tools
    ├── config.py         # ⚙️ Configuration
    ├── logger.py         # 📝 Logging setup
    └── scraper/          # 🌐 Web data collection	



$ python main.py

Which stock to analyze? 
Stock name: tata motors

✅ Found: Tata Motors | TATAMOTORS.NS
📊 Fetching data... (takes 10-20 seconds)
🤔 Analyzing with AI...

🎯 FINAL RECOMMENDATION:
**VERDICT** → STRONG BUY
**Buy Zone**: ₹950 - ₹980
**Stop Loss**: ₹920  
**Target**: ₹1100 - ₹1150
**Time Frame**: 3-6 months

💾 Report saved: outputs/TATA_MOTORS_ANALYSIS_28-Nov-2025.md