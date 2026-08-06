import os

from dotenv import load_dotenv
from google import genai

from prompts import SYSTEM_PROMPT
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
def ask_gemini(question):
    try:
        prompt = f"""
        {SYSTEM_PROMPT}

        User Question:
        {question}
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text

    except Exception as e:
        return f"Error: {str(e)}"