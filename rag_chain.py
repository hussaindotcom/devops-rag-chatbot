from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Suppress Chroma telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"


# Embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load Chroma
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})  # Top 3 chunks

# LLM setup (Gemini)
llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    temperature=0.1, 
    google_api_key=os.environ["GOOGLE_API_KEY"]
)

# Custom prompt for RAG (DevOps-focused)
prompt_template = """You are a helpful DevOps assistant. Use the following context from microservice docs to answer the question. Focus on deployment steps, troubleshooting, and be concise. If the service is mentioned (e.g., UserAuthService), prioritize its info.

Context: {context}

Question: {question}

Answer:"""
PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

# RAG Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": PROMPT},
    return_source_documents=True
)

def query_rag(question):
    result = qa_chain.invoke({"query": question})  # Use invoke
    return result["result"], result["source_documents"]

# Example usage
if __name__ == "__main__":
    response, sources = query_rag("How do I deploy the PaymentGatewayService?")
    print("Response:", response)
    for doc in sources:
        print("Source:", doc.metadata["service"])
