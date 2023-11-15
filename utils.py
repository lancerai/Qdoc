import openai
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Access your environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')
gsearch_api_key = os.getenv('GSEARCH_API_KEY')
cse_id = os.getenv('CSE_ID')

# openai.api_key  = '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'
# gsearch_api_key = "AIzaSyAwfkaJACo1JBx8_IQurhHfUQwmfGiht4Q"
# cse_id = "322de28083504460d"

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def download_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes

        # Assuming the content is text-based, you can access it using response.text
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading the URL: {e}")
        return None

def extract_visible_text(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        # Get the visible text content using .get_text() method of BeautifulSoup
        visible_text = soup.get_text()
        return visible_text
    except Exception as e:
        print(f"An error occurred while extracting text: {e}")
        return None

def summarize_from_url(url, instruction="Summarize the article to a 5-year-old child in English"):
    html_text = download_url(url)
    text = extract_visible_text(html_text)
    prompt = f"""
    {instruction}:
    {text}
    """

    response = get_completion(prompt)
    return response

def get_article_text(url):
    html_text = download_url(url)
    if html_text:
        content = extract_visible_text(html_text)
        return content
    else:
        return None  # Handle case where download or extraction fails

def display_pdf_content(url, num_pages=1):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes

        pdf_content = response.content

        pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
        num_pages = pdf_document.page_count
        print(num_pages)

        full_text = ""

        for page_num in range(num_pages):
            page = pdf_document.load_page(page_num)
            page_text = page.get_text("text")
            #print(f"Page {page_num + 1}:\n{page_text}\n{'-' * 40}")
            full_text += page_text

        pdf_document.close()

        return full_text

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading the PDF: {e}")

def summarize_from_pdf(url, instruction="Summarize the pdf to a 5-year-old child in English"):
    pdf_text = display_pdf_content(url)
    prompt = f"""
    {instruction}:
    {pdf_text}
    """

    response = get_completion(prompt)
    return response

def convert_history(conversation_history):
    history_string = ""
    for message in conversation_history:
        history_string += f"{message['role']}: {message['message']}\n"
    return history_string

def generate_answer(question, article_text, conversation_history, model="gpt-3.5-turbo"):
    conversation_history = convert_history(conversation_history)
    print(conversation_history)
    prompt = f"""
    Previous conversation: {conversation_history}
    Answer the question using conversation history, given article, and your common knowledge.
    Article: {article_text}
    Question: {question}
    Answer:
    """
    response = get_completion(prompt, model)
    return response.strip()

# Example usage
# pdf_url = "https://arxiv.org/pdf/1706.03762.pdf"
# print(summarize_from_pdf(pdf_url))

# text = get_article_text("https://www.cnbc.com/2023/08/14/hawaii-wildfires-leave-at-least-96-dead-more-than-5b-in-damage.html")
# test = generate_answer("what is the death toll", text)
# print(test)