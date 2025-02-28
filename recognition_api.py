import base64
import json
import requests
import sys


def test_api(image_path):
    with open("env", "r") as f:
        API_URL = f.read()

    # Read and encode the image to base64
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Create payload
    payload = json.dumps({"image": encoded_string})
    headers = {"Content-Type": "application/json"}
    
    # Send POST request
    response = requests.post(API_URL, headers=headers, data=payload)
    
    return response.status_code, response.json()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python recognition-api.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    test_api(image_path)
