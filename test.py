
import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create the model & customize it
generation_config = {
  "temperature": 2,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
#select model
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  #give a prompt for the ai, tell's model it's role
  system_instruction="Your are responsible for generating debating prompts that are 100 characters or less and only generate one prompt at a time. The prompts you generate have to be educational, it have to be controversial enough so that each prompt creates two or more distinct perspectives. After generating each prompt, you have to provide 2 different positions or perspectives in which 2 different people can argue based on. You must not generate the same prompt twice even is the user entered the same responses",
)

history = []#chat history dictionary
prompts = []#list of historical prompts

print("hello")

#takes care of i/o in terminal
while True:

    user_input = input("You: ")

    chat_session = model.start_chat(
        history=history
    )

    response = chat_session.send_message(user_input)
    model_response = response.text

    print(f"Bot: {model_response}")
    print()

    history.append({"role": "user", "parts": [user_input]})
    history.append({"role": "model", "parts": [model_response]})
    prompts.append(model_response.split('?')[0])#strip out the prompt, add to list

    print(prompts[-1])# print out newly added prompt
    for i, prompt in enumerate(prompts):#check data types within list --> string
        print(f"Object {i+1} type: {type(prompt)}")


