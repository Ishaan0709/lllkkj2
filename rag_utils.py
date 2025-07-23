import os
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 📦 Load environment variables from .env
load_dotenv()

# 🔐 Get OpenAI API key from .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🧠 Build vector store from files in docs/
def build_vector_store():
    print("🔄 Building FAISS vector store...")
    docs_folder = "./docs"
    documents = []

    # Load each file in docs/
    for file in os.listdir(docs_folder):
        path = os.path.join(docs_folder, file)
        ext = file.lower().split(".")[-1]

        if ext == "txt":
            loader = TextLoader(path)
        elif ext == "pdf":
            loader = PyPDFLoader(path)
        else:
            print(f"⏩ Skipping unsupported file: {file}")
            continue

        documents.extend(loader.load())

    # Split text into chunks for embedding
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_docs = splitter.split_documents(documents)

    # Create vector store using OpenAI embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectorstore = FAISS.from_documents(split_docs, embeddings)
    vectorstore.save_local("faiss_index")
    print("✅ FAISS index built and saved.")

# 🔍 Retrieve relevant context from vector store
def retrieve_context(query: str, k=2) -> str:
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectorstore = FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )
    docs = vectorstore.similarity_search(query, k=k)
    context = "\n".join([doc.page_content for doc in docs])
    return context
