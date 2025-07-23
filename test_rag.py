# test_rag.py

from rag_utils import build_vector_store, retrieve_context

# Step 1: Build the FAISS index from docs/
build_vector_store()

# Step 2: Ask a question
query = "What is coronary artery bypass surgery?"

# Step 3: Retrieve and print relevant context
context = retrieve_context(query)
print("\n🔍 Retrieved Context:")
print(context)