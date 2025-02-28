from google import genai
import dotenv
import time 

def reason(prompt, file_path):
    config = dotenv.dotenv_values("env")
    client = genai.Client(api_key=config["gemini_token"])
    video_file = client.files.upload(file=file_path)

    while video_file.state.name == "PROCESSING":
        print('.', end='')
        time.sleep(1)
        video_file = client.files.get(name=video_file.name)
    
    response = client.models.generate_content(
        model = "gemini-1.5-pro",
        contents = [
            video_file,
            prompt
        ]
    )

    return response.text

# test
# print(reason("Summarise this video", "pics/world.mp4"))