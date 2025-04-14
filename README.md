# 🧠 AI Study Assistant

A fully local, privacy-focused AI chatbot that answers academic questions, generates code, and handles natural conversations—powered by **Ollama**, **LangChain**, **ChromaDB**, and **Streamlit**.

---

## 🚀 Features

- ✅ **Offline-first AI Assistant** using Ollama for local LLM inference  
- 🔍 **Semantic Search** over a 3000+ entry academic dataset via ChromaDB  
- 🌐 **Wikipedia Integration** using LangChain tools for factual answers  
- 📈 **Real-Time Web Data** using SerpAPI for current events and search  
- 💬 **Context-Aware Conversations** using `conversation_history` tracking  
- 💻 **Code Generation** from natural prompts  
- 🖥️ **Streamlit Interface** for real-time chat and user interaction  
- 📊 Responsive UI for both **desktop and mobile** devices  
- 🔄 Async processing for fast responses (~1.8s average)  
- 💡 Intent detection for small talk, compliments, identity questions, etc.  

---

## 📁 Project Structure

```
📦 ai assistant/
├── main.py                 # Core logic for LangChain, LLM, tools, vector search
├── streamlit_app.py        # UI built using Streamlit
├── vector.py               # Vector database setup and CSV ingestion
|── study_routine_chatbot_rich_dataset.csv   #academic Q&A entries
└── README.md               # This file
```

---

## 🧠 Tech Stack

| Component            | Technology            |
|---------------------|------------------------|
| LLM Backend          | [Ollama](https://ollama.com/) (e.g., LLaMA3.2) |
| Prompt Chaining      | [LangChain](https://www.langchain.com/) |
| Vector Search        | [ChromaDB](https://www.trychroma.com/) |
| UI                   | [Streamlit](https://streamlit.io/) |
| Web Search           | [SerpAPI](https://serpapi.com/) |
| Encyclopedia Access  | Wikipedia via LangChain |

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-study-assistant-chatbot.git
cd ai-study-assistant-chatbot
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate     # For Linux/macOS
venv\Scripts\activate        # For Windows
```

### 3. Install Required Python Libraries

```bash
pip install langchain chromadb streamlit sentence-transformers wikipedia python-dotenv
```

### 4. Start Ollama LLM

Make sure you have Ollama installed.

### 5. Launch the Chatbot Interface

```bash
streamlit run streamlit_app.py
```
---

## 🧾 Example Queries

- 📘 *"What is Newton’s Second Law?"*
- 🧪 *"Give a study plan for my exam"*
- 💻 *"Write a Python function to reverse a string."*
- 🌍 *"What's the capital of France?"* (Wikipedia)
- 🔍 *"Current stock price of Tesla?"* (Web Search)

---

## 📌 Upcoming Features

- 🧠 Summarization and long document support for research use-cases  
- 📝 Auto-update `study_routine_chatbot_rich_dataset.csv` with new Q&A entries from chats  
- 📤 Export chat history to `.txt` or `.csv` for future reference or study notes  
- 🔐 User sessions with persistent memory and personalized context  

## 🤝 Contributing

Pull requests are welcome! If you'd like to contribute, please fork the repo and submit a PR.

---

## 📫 Contact

For questions, feedback, or collaboration:  
**Name**: *Mohd Hamza Arshad*  
**Email**: *hamza.arshad@vit.edu.in*  
**LinkedIn**: [Hamza](https://www.linkedin.com/in/frhamzaa/)

---
