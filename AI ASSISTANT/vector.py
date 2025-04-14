# vector.py
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd

# Load your CSV converts into DataFrame
df = pd.read_csv("study_routine_chatbot_rich_dataset.csv")

# Initialize embeddings model, CONVERT dataset into vector embeddings
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# Directory to store (NUMERIC PATTERN) Chroma vector DB
db_location = "./chroma_study_routine_db"
add_documents = not os.path.exists(db_location)

if add_documents:
    documents = []
    ids = []

    for i, row in df.iterrows():
        content = (
            f"Category: {row['Category']}. "
            f"Subcategory: {row['Subcategory']}. "
            f"Question: {row['Question']}. "
            f"Answer: {row['Answer']}."
        )
        document = Document(
            page_content=content,
            metadata={
                "category": row.get("Category", None),
                "subcategory": row.get("Subcategory", None),
                "question": row.get("Question", None),
                "answer": row.get("Answer", None)
            },
            id=str(i)
        )
        documents.append(document)
        ids.append(str(i))

vector_store = Chroma( # Load Chroma vector store with the given embeddings(searchable using AI)
    collection_name="study_routine_coach",
    persist_directory=db_location,
    embedding_function=embeddings
)

# Only add documents if the database is being created for the first time
if add_documents:
    vector_store.add_documents(documents=documents, ids=ids)

# retriever to fetch top 5 relevant entries
retriever = vector_store.as_retriever(search_kwargs={"k": 5})
