import base64
import json
import requests
import sys
import dotenv

config = dotenv.dotenv_values("env")


def test_api(image_path):
    API_URL = config["test_api_url"]

    # Read and encode the image to base64
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Create payload
    payload = json.dumps({"image": encoded_string})
    headers = {"Content-Type": "application/json"}
    
    # Send POST request
    response = requests.post(API_URL, headers=headers, data=payload)
    
    res = response.json()
    try:
        result = response.status_code, res["UserMatches"][0]["Similarity"], res["UserMatches"][0]["User"]["UserId"]
    except IndexError:
        result = 404, 0, "unidentified"
    return result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python recognition-api.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    test_api(image_path)
