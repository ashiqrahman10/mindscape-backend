"""
At the command line, only need to run once to install the package via pip:

$ pip install google-generativeai
"""

import google.generativeai as genai

genai.configure(api_key="AIzaSyC9M85CX3GiZnnBey3ozlNux4GQElknFgI")

# Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 20482,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

model = genai.GenerativeModel(model_name="gemini-1.0-pro-001",
                              generation_config=generation_config,
                              safety_settings=safety_settings)


def chat_with_mindscape():
    while True:
        prompt_parts = [
            "YOU ARE A MENTAL HEALTH SUGGESTION CHATBOT NAMED 'mindscapeAI'. YOU CAN ONLY REPLY TO QUESTIONS RELATED TO MENTAL HEALTH OR HEALTH IN GENERAL. YOU ALWAYS START WITH \"Hey, I'm mindscapeAI. Your personal mental health expert. How may I assist you?\". KEEP YOUR RESPONSES SHORT AND BRIEF.\n",
            "USER: " + input("You: ")  # Get user input
        ]

        response = model.generate_content(prompt_parts)
        print(response.text)

if __name__ == "__main__":
    try:
        chat_with_mindscape()
    except google.generativeai.errors.GoogleGenerativeAIError as e:
        print(f"An API error occurred: {e}")
    except KeyboardInterrupt:  # Catch Ctrl+C
        print("\nExiting chat session.")


# prompt_parts = [
#   "YOU ARE A MENTAL HEALTH SUGGESTION CHATBOT NAMED 'mindscapeAI'. YOU CAN ONLY REPLY TO QUESTIONS RELATED TO MENTAL HEALTH OR HEALTH IN GENERAL. YOU ALWAYS START WITH \"Hey, I'm mindscapeAI. Your personal mental health expert. How may I assist you?\". KEEP YOUR RESPONSES SHORT AND BRIEF.\n",
# ]

# response = model.generate_content(prompt_parts)
# print(response.text)