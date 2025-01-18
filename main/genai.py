import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables for the AI API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

######################################### GENISIS MODEL -- POLITICS ############################################
politics_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    },
    system_instruction="Your are responsible for generating debating prompts related to political that are 20 words or less and only generate one prompt at a time. The prompts you generate have to be educational, it have to be controversial enough so that each prompt creates two or more distinct perspectives. After generating each prompt, you have to provide 2 different positions or perspectives in which 2 different people can argue based on, each perspective has to be 15 words or less. You must not generate the same prompt twice even is the user entered the same responses. End the prompt text with character:? + ^, End the first perspective text with character: $",
)
######################################### GENISIS MODEL -- FUNNY ############################################
funny_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    },
    system_instruction="Your are responsible for generating very funny and humorous debating prompts that are 20 words or less and only generate one prompt at a time. The prompts you generate have to be educational, it have to be controversial enough so that each prompt creates two or more distinct perspectives. After generating each prompt, you have to provide 2 different positions or perspectives in which 2 different people can argue based on, each perspective has to be 15 words or less. You must not generate the same prompt twice even is the user entered the same responses. End the prompt text with character:? + ^, End the first perspective text with character: $",
)
#################################################################################################################

# Chat history to maintain context
history = []

# Function to generate game data
async def generate_game_data(user_input, theme):
    global politics_model, funny_model, history

    # Select the appropriate model based on the theme
    if theme.lower() == "politics":
        model = politics_model
    elif theme.lower() == "funny":
        model = funny_model
    else:
        raise ValueError(f"Unknown theme: {theme}")

    # Start a new chat session with the history
    chat_session = model.start_chat(history=history)

    # Send the user input and get the model's response
    response = chat_session.send_message(user_input)
    model_response = response.text

    # Append the user input and model response to history
    history.append({"role": "user", "parts": [user_input]})
    history.append({"role": "model", "parts": [model_response]})

    # Parse the response into prompt and perspectives
    prompt = model_response.split('?')[0].strip()
    perspec_1 = model_response.split('^')[1].split('$')[0].strip()
    perspec_2 = model_response.split('^')[1].split('$')[1].strip()

    return {
        "prompt": prompt,
        "twist": perspec_1,
        "alternative_twist": perspec_2,  # Optional: Use this for variety in your game logic
    }
