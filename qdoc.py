from flask import Flask, render_template, request, jsonify
from utils import summarize_from_url, get_article_text, summarize_from_pdf, generate_answer

app = Flask(__name__)

conversation_history = [] # Initialize conversation history as a global variable

@app.route('/')
def home():
    return render_template('index.html') # Render the home page using the 'index.html' template
    
@app.route('/summarize', methods=['POST'])
def summarize():
    url = request.form.get('user_input2', '').strip() # Get the article URL from the form data

    # Check if the URL is empty
    if not url:
        return "Please provide a valid article URL or PDF."
    
    # Check if the URL ends with ".pdf" to determine if it's a PDF file
    if url.endswith(".pdf"):
        result = summarize_from_pdf(url)
    else:
        result = summarize_from_url(url)
    return result

@app.route('/query', methods=['POST'])
def query():
    global conversation_history
    user_question = request.form.get('user_input3', '').strip()  # Get the user's question from the form
    article_url = request.form.get('user_input2', '').strip()  # Get the article URL from the form

    # Check if the user question or article URL is empty
    if not user_question or not article_url:
        return "Please provide both a valid question and article URL."
        
    conversation_history.append({"role": "user", "message": user_question}) # Add the user's question to the conversation history
    article_text = get_article_text(article_url) # Get the text of the article from the provided URL

    # Check if article text retrieval was successful
    if article_text is None:
        return "Failed to retrieve article text."

    answer = generate_answer(user_question, article_text[:16000], conversation_history)
    conversation_history.append({"role": "system", "message": answer}) # Add the system's answer to the conversation history

    return jsonify(conversation_history)

@app.route('/refresh', methods=['POST'])
def refresh():
    global conversation_history
    conversation_history.clear()
    return ('', 204)  # Return an empty response with a status code 204 (No Content)

if __name__ == '__main__':
    app.run()
