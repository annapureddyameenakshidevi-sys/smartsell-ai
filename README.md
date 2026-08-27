🛍️ SmartSell AI

Agentic Commerce & Merchant Growth Assistant

SmartSell AI is an AI-inspired commerce assistant that helps users find suitable products based on natural-language requests.

Features

- 🔎 Natural-language product search
- 💰 Budget-based product filtering
- 🛒 Shopping cart management
- 💳 Checkout workflow
- 💡 Smart upsell and cross-sell suggestions
- 📝 Audit trail for user actions
- 🔐 Razorpay Test Mode integration
- 🖥️ Streamlit web interface

 Tech Stack

- Python
- Streamlit
- Razorpay
- JSON
- python-dotenv

 Project Structure

```text
smartsell-ai/
├── app/
│   └── main.py
├── data/
│   └── products.json
├── .gitignore
└── requirements.txt

 How to Run

```bash
pip install -r requirements.txt
streamlit run app/main.py

Payment Integration

Razorpay is configured for Test Mode. API credentials are stored securely in environment variables and are not included in the repository.

 Note

This is a demonstration/MVP project. Payment processing uses Razorpay Test Mode and does not process real payments.
