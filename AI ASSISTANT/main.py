from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationEntityMemory
import requests
import wikipedia
import re
import csv
import os
import time
from tavily import TavilyClient
from typing import Optional
import string

# Initialize LLM
model = OllamaLLM(model="llama3.2")

# Memory 
memory = ConversationEntityMemory(
    llm=model,           # LLM instance
    return_messages=True
)
#memory.chat_memory.messages.clear()
last_topic = ""  # keeps track of the last topic
#memory.last_topic = ""  # store last topic keyword
memory.chat_memory.clear()

# Log conversation to CSV
def log_to_csv(user_msg, assistant_msg, filename="conversation_log.csv"):
    file_exists = os.path.isfile(filename)
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["User", "Assistant"])
        writer.writerow([user_msg, assistant_msg])

def extract_topic(question):
    stopwords = {"what", "is", "the", "of", "a", "an", "for", "please", "give", "show"}
    keywords = [word.lower() for word in question.split() if word.lower() not in stopwords]
    return " ".join(keywords)

def resolve_followup(question, last_topic):
    pronouns = ["it", "this", "that", "these", "those", "they", "its", "their"]
    question_words = [w.strip(string.punctuation).lower() for w in question.split()]
    
    # short question OR contains pronouns, append last topic
    if len(question_words) <= 3 or any(p in question_words for p in pronouns):
        if last_topic:
            return f"{question} (about: {last_topic})"
    return question


# Detect small talk
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
        "good night": "Sleep tight! 😴",
    }

    compliments = {
        "you're good": "Thanks! I appreciate that! ",
        "nice": "Glad you liked it!",
        "good job": "Thank you! I'm here to help anytime!",
        "well done": "Appreciate it! Let me know if you need anything else.",
    }

    identity = {
        "who are you": "I'm your personal AI study and conversation assistant. I can help you with study topics, generate code, explain concepts, or just have a friendly chat. 😊",
        "what can you do": "I can assist you with study content, motivation, coding questions, explain concepts, fetch real-time info, and respond like a human. Ask me anything!",
        "can you": "Absolutely! Just tell me what you’d like me to do. ",
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
        return "Yes, I can help with that!  Just give me more details."
    return None

# Detect follow-up for sources
def is_followup_for_sources(question: str) -> bool:
    return any(kw in question.lower() for kw in ["source", "reference", "where", "give link", "proof"])

# Detect casual questions
def is_casual_question(question: str) -> bool:
    casual_keywords = [
        "how are you",
        "hi",
        "hello",
        "good morning",
        "good night",
        "what can you do",
        "who are you",
        "you're good",
        "nice",
        "can you",
        "good job",
        "well done",
        "hey",
    ]
    return any(kw in question.lower() for kw in casual_keywords)

# Tavily search
def fetch_web_data(query):
    client = TavilyClient(api_key="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")
    try:
        print(f"\n Sending Tavily API request for: '{query}'")
        start = time.time()
        response = client.search(query=query, search_depth="advanced")
        end = time.time()
        print(f" Tavily API call completed in {end - start:.2f} seconds")
        results = response.get("results", [])
        formatted_results = []
        for result in results[:3]:
            title = result.get("title", "")
            content = result.get("content", "")
            url = result.get("url", "")
            formatted = f"[{title}]({url})" if url else title
            formatted_results.append(f"{formatted}: {content}")
        return "\n\n".join(formatted_results) if formatted_results else "No Tavily results found."
    except Exception as e:
        return f"Error fetching Tavily data: {e}"

# Wikipedia summary
def fetch_wikipedia_summary(query):
    try:
        print(f"\n Sending Wikipedia API request for: '{query}'")
        start = time.time()
        summary = wikipedia.summary(query, sentences=5)
        end = time.time()
        print(f" Wikipedia API call completed in {end - start:.2f} seconds")
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple topics found: {e.options[:3]}"
    except Exception as e:
        return f"Wikipedia error: {e}"

# Extract location
def extract_location_from_question(q: str):
    match = re.search(r"in (\w+(?: \w+)*)", q.lower())
    return match.group(1) if match else None

# Get location from IP
def get_user_location():
    try:
        ip_data = requests.get("http://ip-api.com/json/").json()
        return ip_data.get("city")
    except:
        return None

# Build prompt
def build_prompt_context(question, local_reviews, wiki_summary, web_data, chat_history):
    system_instruction = """
 You are a conversational AI assistant. 
 Always keep track of the full conversation history.
 If the user uses pronouns like "it", "they", "this", "that", etc., 
 you MUST resolve them to the most recent topic discussed in the conversation.
 If unclear, ask politely for clarification.
 Always answer questions specifically in the context of previous messages.
 Do not repeat greetings unless the user greets you again.
 Do not add phrases like 'It seems you are asking' or 'Based on previous conversation'.
"""

    study_keywords = [
        "study",
        "motivation",
        "focus",
        "routine",
        "procrastinate",
        "concentration",
        "exam",
        "revision",
        "define",
        "explain",
        "what is",
        "how does",
        "science",
        "physics",
        "math",
        "biology",
        "chemistry",
    ]
    is_study = any(kw in question.lower() for kw in study_keywords)
    is_casual = is_casual_question(question)

    base_prompt = f"""
{system_instruction}

Conversation history:
{chat_history}

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
"""
    elif is_casual:
        return base_prompt + "\n(You don't need to include sources for this casual conversation.)"
    else:
        return base_prompt + "\nInclude sources at the end."

# Main QnA
def answer_question(question: str) -> str:
    global last_topic  # use the global variable
    # Small talk check
    smalltalk_response = detect_smalltalk(question)
    if smalltalk_response:
        memory.chat_memory.add_user_message(question)
        memory.chat_memory.add_ai_message(smalltalk_response)
        log_to_csv(question, smalltalk_response)
        return smalltalk_response

    # Source follow-up
    if is_followup_for_sources(question):
        past_messages = memory.chat_memory.messages
        for past in reversed(past_messages):
            if past.type == "human":
                question = past.content
                break

    # Weather queries
    if "weather" in question.lower():
        location = extract_location_from_question(question) or get_user_location()
        if not location:
            return "Couldn't detect your location. Please mention the location."
        web_data = fetch_web_data(f"weather in {location}")
        weather_response = f"🌦️ Here's the weather in {location.title()}:\n\n{web_data}"
        memory.chat_memory.add_user_message(question)
        memory.chat_memory.add_ai_message(weather_response)
        log_to_csv(question, weather_response)
        return weather_response

    # Normal flow
    memory.chat_memory.add_user_message(question)

    chat_history = "\n".join([f"{m.type.capitalize()}: {m.content}" for m in memory.chat_memory.messages[-15:]])
    local_reviews = ""
    question_for_api = resolve_followup(question, last_topic)
    wiki_summary = fetch_wikipedia_summary(question_for_api)
    web_data = fetch_web_data(question_for_api) 

    prompt_text = build_prompt_context(
    question=question_for_api,
    local_reviews=local_reviews,
    wiki_summary=wiki_summary,
    web_data=web_data,
    chat_history=chat_history) 

    answer = model.invoke(prompt_text)

    memory.chat_memory.add_ai_message(answer)
    topic = extract_topic(question)
    if question_for_api == question:
      last_topic = topic
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
