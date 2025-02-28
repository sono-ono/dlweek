import dotenv
from gradio_client import Client, handle_file

# Sample output = ({'label': 'No face detected!', 
# 'confidences': [{'label': 'No face detected!', 'confidence': 1.0}]}, None)

def image(file):
    config = dotenv.dotenv_values("env")
    HF_token = config["hf_access_token"]
    client = Client("dlweekproj/deepfakedetection", hf_token=HF_token)
    result = client.predict(
            inp=handle_file(file),
            model="Self-Blended Consistency Learning",
            api_name="/predict_image",
    )
    return result

def video(file):
    config = dotenv.dotenv_values("env")
    HF_token = config["hf_access_token"]
    client = Client("dlweekproj/deepfakedetection", hf_token=HF_token)
    result = client.predict(
	    inp={"video":handle_file(file)},
	    model="Self-Blended Consistency Learning",
	    api_name="/predict_video"
    )
    return result

print(image("pics/faketrump.png"))