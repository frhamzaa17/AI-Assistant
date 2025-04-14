from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever
import requests
import wikipedia
import re

# Compatibility for older Python versions (<3.10)
from typing import Optional

# model Initialization
model = OllamaLLM(model="llama3.2")

# In-memory history
conversation_history = []

# Detect small query
def detect_smalltalk(question: str) -> Optional[str]:
    q = question.lower().strip()
    if len(q.split()) > 6:
        return None

    greetings = {
        "how are you": "I'm doing well, thanks for asking! 😊 How about you?",
        "hi": "Hi there! 👋",
        "hello": "Hello! How can I help you today?",
        "hey": "Hey! What's up?",
        "good morning": "Good morning! ☀️ Hope you're feeling productive today!",
        "good evening": "Good evening! 🌙 How can I assist?",
        "good night": "Sleep tight! 😴"
    }

    compliments = {
        "you're good": "Thanks! I appreciate that! 😊",
        "nice": "Glad you liked it!",
        "good job": "Thank you! I'm here to help anytime!",
        "well done": "Appreciate it! Let me know if you need anything else.",
    }

    identity = {
        "who are you": "I'm your personal AI study and conversation assistant. I can help you with study topics, generate code, explain concepts, or just have a friendly chat. 😊",
        "what can you do": "I can assist you with study content, motivation, coding questions, explain concepts, fetch real-time info, and respond like a human. Ask me anything!",
        "can you": "Absolutely! Just tell me what you’d like me to do. 😊"
    }

    for k, v in greetings.items():
        if k == q:
            return v
    for k, v in compliments.items():
        if k in q:
            return v
    for k, v in identity.items():
        if k in q:
            return v
    if q.startswith("can you"):
        return "Yes, I can help with that! 😊 Just give me more details."
    return None

# Detect follow-up source requests
def is_followup_for_sources(question: str) -> bool:
    return any(kw in question.lower() for kw in ["source", "reference", "where", "give link", "proof"])

# Detect casual questions
def is_casual_question(question: str) -> bool:
    casual_keywords = [
        "how are you", "hi", "hello", "good morning", "good night", "what can you do", "who are you", 
        "you're good", "nice", "can you", "good job", "well done", "hey"
    ]
    return any(kw in question.lower() for kw in casual_keywords)

# SerpAPI
def fetch_web_data(query):
    API_KEY = "81338aaaaf9975be0987ad03e12ff0dbc4761706bd80bf08f3788e12cf1487a9"  # Replace with your SerpAPI key
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "api_key": API_KEY,
        "num": 3
    }
    try:
        response = requests.get(url, params=params)
        results = []
        for result in response.json().get("organic_results", []):
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            link = result.get("link", "")
            formatted = f"[{title}]({link})" if link else title
            results.append(f"{formatted}: {snippet}")
        return "\n\n".join(results) if results else "No web results found."
    except Exception as e:
        return f"Error fetching web data: {e}"

# Wikipedia summary
def fetch_wikipedia_summary(query):
    try:
        summary = wikipedia.summary(query, sentences=5)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple topics found: {e.options[:3]}"
    except Exception as e:
        return f"Wikipedia error: {e}"

# Location extraction
def extract_location_from_question(q: str):
    match = re.search(r"in (\w+(?: \w+)*)", q.lower())
    return match.group(1) if match else None

# Auto-detect location by IP
def get_user_location():
    try:
        ip_data = requests.get("http://ip-api.com/json/").json()
        return ip_data.get("city")
    except:
        return None

# Prompt builder
def build_prompt_context(question, local_reviews, wiki_summary, web_data, recent_context):
    study_keywords = [
        "study", "motivation", "focus", "routine", "procrastinate", "concentration", "exam", "revision",
        "define", "explain", "what is", "how does", "science", "physics", "math", "biology", "chemistry"
    ]
    is_study = any(kw in question.lower() for kw in study_keywords)
    is_casual = is_casual_question(question)

    base_prompt = f"""
Previous conversation:
{recent_context}

You are a helpful AI assistant. If the question is casual, reply naturally and warmly like a human. If it's factual or educational, be clear and informative.

📖 Wikipedia:
{wiki_summary}

🌐 Web insights:
{web_data}

User asked:
{question}
"""

    if is_study:
        return base_prompt + f"""

📚 Local insights:
{local_reviews}

Include sources:
- Wikipedia
- Google
- Local vector DB
"""
    elif is_casual:
        return base_prompt + "\n(You don't need to include sources for this casual conversation.)"
    else:
        return base_prompt + "\nInclude sources at the end."

# Main QnA logic
def answer_question(question: str) -> str:
    smalltalk_response = detect_smalltalk(question)
    if smalltalk_response:
        conversation_history.append({"role": "user", "content": question})
        conversation_history.append({"role": "assistant", "content": smalltalk_response})
        return smalltalk_response

    if is_followup_for_sources(question) and conversation_history:
        for past in reversed(conversation_history):
            if past["role"] == "user" and not is_followup_for_sources(past["content"]):
                question = past["content"]
                break

    # Weather detection
    if "weather" in question.lower():
        location = extract_location_from_question(question) or get_user_location()
        if not location:
            return "Couldn't detect your location. Please mention Location'."
        web_data = fetch_web_data(f"weather in {location}")
        return f"🌦️ Here's the weather in {location.title()}:\n\n{web_data}"

    conversation_history.append({"role": "user", "content": question})

    recent_context = "\n".join(
        [f"{item['role'].capitalize()}: {item['content']}" for item in conversation_history[-6:-1]]
    )

    docs = retriever.invoke(question)
    local_reviews = "\n\n".join([doc.page_content for doc in docs])
    wiki_summary = fetch_wikipedia_summary(question)
    web_data = fetch_web_data(question)

    prompt_text = build_prompt_context(question, local_reviews, wiki_summary, web_data, recent_context)
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | model

    answer = chain.invoke({
        "local_reviews": local_reviews,
        "web_data": web_data,
        "wiki_summary": wiki_summary,
        "question": question
    })

    conversation_history.append({"role": "assistant", "content": answer})
    return answer

# CLI for testing
if __name__ == "__main__":
    while True:
        print("\n--------------------------")
        user_input = input("Ask your question (q to quit): ")
        if user_input.lower() == "q":
            break
        reply = answer_question(user_input)
        print("\n🤖 AI Assistant:\n", reply)
