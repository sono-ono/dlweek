from google import genai
import dotenv
import time 

def reason(prompt, file_path):
    config = dotenv.dotenv_values("env")
    client = genai.Client(api_key=config["gemini_token"])
    media_file = client.files.upload(file=file_path)

    while media_file.state.name == "PROCESSING":
        print('.', end='')
        time.sleep(1)
        media_file = client.files.get(name=media_file.name)
    
    response = client.models.generate_content(
        model = "gemini-1.5-pro",
        contents = [
            media_file,
            prompt
        ]
    )

    return response.text

# test
# print(reason("Summarise this video", "pics/world.mp4"))