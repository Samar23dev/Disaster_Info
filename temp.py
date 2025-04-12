import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

PROMPT = 'Describe a cat in a few sentences'
MODEL = 'gemini-1.5-flash'
print('** GenAI text: %r model & prompt %r\n' % (MODEL, PROMPT))

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel(MODEL)
response = model.generate_content(PROMPT)
print(response.text)