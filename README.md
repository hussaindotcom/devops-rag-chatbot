DevOps RAG Chatbot 🤖

A Retrieval-Augmented Generation (RAG) chatbot designed for DevOps professionals, powered by LangChain, Chroma, and Google’s Gemini API. Query deployment steps and troubleshoot AWS-based microservices (EKS, S3, Lambda) with a sleek Streamlit interface.

✨ Features

Microservice Expertise: Answers queries on 10 AWS microservices (e.g., UserAuthService, PaymentGatewayService).
RAG-Powered: Combines Chroma vector store for document retrieval with Gemini’s natural language generation.
Interactive UI: Streamlit web app for easy querying.
Secure: API keys stored in .env (not tracked by Git).
Scalable: Add new microservice docs easily.

🚀 Quick Start
Prerequisites

🐍 Python 3.11
📦 Git
🔑 Google Gemini API key (Get one)
💾 ~2GB disk space
🖥️ macOS/Linux (tested on macOS with Apple Silicon)

Installation

Clone the Repository:
git clone https://github.com/your-username/devops-rag-chatbot.git
cd devops-rag-chatbot


Set Up Virtual Environment:
python3.11 -m venv venv
source venv/bin/activate


Install Dependencies:
pip install -r requirements.txt


Configure Gemini API Key:Create a .env file:
echo "GOOGLE_API_KEY=your-api-key" > .env

Replace your-api-key with your Gemini API key. Requires python-dotenv.

Initialize Chroma DB:Embed microservice docs:
python3.11 docs.py

Creates ./chroma_db with 11 embedded chunks for 10 services.


Usage

Test the RAG Chain:Query directly:
python3.11 rag_chain.py

Example output:
Response: To deploy the PaymentGatewayService on EKS:
1. Create secret: `kubectl create secret generic stripe-keys ...`
...
Source: PaymentGatewayService


Launch Streamlit UI:Start the web app:
streamlit run app.py

Open http://localhost:8501. Try queries like:

"How do I deploy UserAuthService?"
"Troubleshoot BackupService."




📂 Project Structure



File/Folder
Description



.env
Gemini API key (not tracked)


.gitignore
Excludes venv, chroma_db, etc.


requirements.txt
Python dependencies


docs.py
Embeds microservice docs into Chroma DB


rag_chain.py
RAG pipeline with Gemini LLM


app.py
Streamlit frontend


chroma_db/
Chroma vector store (not tracked)



🛠️ Adding New Docs
To add microservice documentation:

Edit the DOCS dictionary in docs.py.
(Optional) Clear existing Chroma DB:rm -rf ./chroma_db


Re-run:python3.11 docs.py



🐞 Troubleshooting

Gemini API Errors:
404 NotFound: Verify model (gemini-flash-latest):curl "https://generativelanguage.googleapis.com/v1beta/models?key=$GOOGLE_API_KEY"


401/403: Regenerate key in Google AI Studio.


Chroma Telemetry: Suppressed via ANONYMIZED_TELEMETRY=False.
Port Conflicts: If localhost:8501 fails:streamlit run app.py --server.port 8502


Apple Silicon: For slow torch, upgrade:pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cpu



🤝 Contributing

Fork the repo.
Create a feature branch: git checkout -b feature-name.
Commit: git commit -m "Add feature".
Push: git push origin feature-name.
Open a pull request.

📜 License
MIT License
🙌 Acknowledgments

Built with LangChain, Chroma, and Google Gemini.
Inspired by AWS DevOps practices.


⭐ Star this repo if it helps you! For issues, open a ticket or contact the maintainer.


