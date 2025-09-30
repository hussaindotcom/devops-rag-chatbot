DevOps RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot for DevOps, built to answer queries about deploying and troubleshooting microservices on AWS EKS, S3, Lambda, and more. It uses a Chroma vector store for document retrieval and Google's Gemini API for generating concise, accurate responses.
Features

Microservice Docs: Answers questions based on 10 microservice deployment guides (e.g., UserAuthService, PaymentGatewayService).
RAG Architecture: Combines LangChain's retrieval with Gemini's generation for contextual, DevOps-focused responses.
Streamlit UI: Interactive web interface for querying deployment steps and troubleshooting tips.
Local Vector Store: Uses Chroma DB to store embedded microservice documentation.
Secure Setup: API keys managed via .env to prevent leakage.

Prerequisites

Python 3.11
Git
Google Gemini API key (Get one here)
~2GB disk space for dependencies and Chroma DB
macOS/Linux (tested on macOS with Apple Silicon)

Installation

Clone the Repository:
git clone https://github.com/hussaindotcom/devops-rag-chatbot.git
cd devops-rag-chatbot


Set Up Virtual Environment:
python3.11 -m venv venv
source venv/bin/activate


Install Dependencies:
pip install -r requirements.txt


Set Up Gemini API Key:Create a .env file in the project root:
echo "GOOGLE_API_KEY=your-api-key" > .env

Replace your-api-key with your Gemini API key.

Initialize Chroma DB:Run docs.py to embed microservice docs:
python3.11 docs.py

Creates ./chroma_db with 11 embedded chunks for 10 services.


Usage

Test the RAG Chain:Run rag_chain.py to query the chatbot directly:
python3.11 rag_chain.py

Example output:
Response: To deploy the PaymentGatewayService on EKS:
1. Create secret: `kubectl create secret generic stripe-keys ...`
...


Launch Streamlit UI:Start the web interface:
streamlit run app.py

Open http://localhost:8501 in your browser. Try queries like:

"How do I deploy UserAuthService?"
"Troubleshoot BackupService."



Adding New Docs
To add new microservice documentation:

Edit the DOCS dictionary in docs.py.
Delete the existing Chroma DB (if needed):rm -rf ./chroma_db

Re-run:python3.11 docs.py



Apple Silicon: If torch is slow, upgrade to torch==2.2.2:pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cpu



Contributing

Fork the repository.
Create a feature branch: git checkout -b feature-name.
Commit changes: git commit -m "Add feature".
Push: git push origin feature-name.
Open a pull request.

License
MIT License. See LICENSE for details.
Acknowledgments

Built with LangChain, Chroma, and Google Gemini.
Inspired by DevOps best practices for AWS microservices.


Star this repo if you find it helpful! For issues, open a ticket or contact the maintainer.
