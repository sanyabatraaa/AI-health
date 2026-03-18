from flask import Flask, render_template, request
from src.helper import download_hugging_face_embeddings
from src.prompt import SYSTEM_PROMPT  
from langchain_pinecone import PineconeVectorStore
import google.generativeai as genai
from dotenv import load_dotenv
import os
import logging
from flask_cors import CORS


# Initialize Flask app and environment
app = Flask(__name__)

load_dotenv()
CORS(app)

logging.basicConfig(level=logging.INFO)

# API keys
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
genai.configure(api_key=GOOGLE_API_KEY)

# Embedding + Retriever setup
embeddings = download_hugging_face_embeddings()
index_name = "medibot"
docsearch = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embeddings)
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 5})






def convert_to_native_script_with_gemini(user_msg):
    """
    Uses Google Gemini model to convert transliterated (Latin-script) input into correct native script.
    """
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = (
            f"Detect the language of the following user input and convert it into the correct script.\n"
            f"Examples:\n"
            f"Input: 'mujhe bukhar hai, mai kya kru' --> Output: 'मुझे बुखार है, मैं क्या करूँ'\n"
            f"Input: 'sardi te khasi theek karan layi ki karna chahida' --> Output: 'ਸਰਦੀ ਤੇ ਖੰਸੀ ਠੀਕ ਕਰਨ ਲਈ ਕੀ ਕਰਨਾ ਚਾਹੀਦਾ'\n"
            f"Input: 'hello, how are you' --> Output: 'hello, how are you'\n\n"
            f"Now, convert the following input:\n"
            f"'{user_msg}'"
        )
        response = model.generate_content(prompt)
        if response and response.candidates:
            converted_text = response.candidates[0].content.parts[0].text.strip()
            return converted_text
        else:
            return user_msg  # fallback to original message
    except Exception as e:
        logging.error(f"Gemini transliteration error: {str(e)}")
        return user_msg


# Unified intent detection
def identifyIntent(query):
    """
    Determines if the query is greeting, assistant, exit, or other.
    """
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = (
            "Classify the user's message into one of the following categories:\n"
            "- 'greeting' (e.g., hello, hi)\n"
            "- 'assistant' (user is asking a medical question or requesting health help)\n"
            "- 'exit' (e.g., thank you, bye, talk later)\n"
            "- 'other' (anything unrelated to the above)\n\n"
            "Respond with only one of: greeting, assistant, exit, other.\n\n"
            f"User message: {query}"
        )
        response = model.generate_content(prompt)
        intent = response.text.strip().lower()
        if intent in ['greeting', 'assistant', 'exit', 'other']:
            return intent
        return 'assistant'  # fallback
    except Exception as e:
        logging.error("Intent detection failed: %s", str(e))
        return 'assistant'

# Gemini content generator
def generate_gemini_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        if response and response.candidates:
            return response.candidates[0].content.parts[0].text.strip()
        else:
            return "⚠️ I'm sorry, I couldn't generate a response."
    except Exception as e:
        logging.error("Gemini API Error: %s", str(e))
        return "⚠️ There was an issue generating a response."

# Multilingual rephraser for fixed responses
def multilingual_fixed_response(user_msg, base_text):
    """
    Rephrases a fixed response into the same language as the user's message.
    """
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = (
            f"User wrote: {user_msg}\n\n"
            f"Rephrase the following message in the same language as the user:\n"
            f"'{base_text}'"
        )
        response = model.generate_content(prompt)
        if response and response.candidates:
            return response.candidates[0].content.parts[0].text.strip()
        else:
            return base_text
    except Exception as e:
        logging.error("Multilingual fixed response error: %s", str(e))
        return base_text

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form.get("msg", "").strip()
    msg= convert_to_native_script_with_gemini(msg)
    print(msg)
    if not msg:
        return "⚠️ Please enter a valid query."

    if len(msg) > 500:
        return "⚠️ Query too long. Please keep it under 500 characters."

    logging.info("User Input: %s", msg)

    intent = identifyIntent(msg)
    logging.info("Identified Intent: %s", intent)

    if intent == "greeting":
        return multilingual_fixed_response(msg, "👋 Hello! I am your medical assistant. How can I help you today?")

    elif intent == "exit":
        return multilingual_fixed_response(msg, "😊 Feel free to ask me about medical assistance anytime. Thank you for choosing me!")

    elif intent == "other":
        return multilingual_fixed_response(msg, "⚠️ MediBot assists only with medical or health-related queries. Please rephrase accordingly.")

    # Proceed for medical assistant
    retrieved_docs = retriever.get_relevant_documents(msg)
    context = "\n".join([doc.page_content for doc in retrieved_docs]) if retrieved_docs else "No relevant medical information found."

    full_prompt = SYSTEM_PROMPT.format(context=context, query=msg)
    response = generate_gemini_response(full_prompt)

    logging.info("Gemini Response: %s", response)
    return response

# Run server
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
