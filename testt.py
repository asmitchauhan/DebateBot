import google.generativeai as genai

# Replace with your actual key from https://makersuite.google.com/app/apikey
genai.configure(api_key="AIzaSyD1hygm83i9hhJ_tWz97qMi5jQPZfRZ_kM")

model = genai.GenerativeModel(model_name="models/gemini-pro")
chat = model.start_chat()
response = chat.send_message("Who is the Prime Minister of India?")
print(response.text)
