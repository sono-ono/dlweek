import base64
import json
import requests
import sys
import dotenv

config = dotenv.dotenv_values("env")


def test_api(image_path):
    print(f"[DEBUG] recognition_api.test_api called with image_path: {image_path}")
    try:
        print("[DEBUG] Loading API URL from config")
        API_URL = config["test_api_url"]
        print(f"[DEBUG] API URL: {API_URL}")

        # Read and encode the image to base64
        print(f"[DEBUG] Reading and encoding image file: {image_path}")
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        print(f"[DEBUG] Image encoded, length: {len(encoded_string)}")
        
        # Create payload
        print("[DEBUG] Creating payload")
        payload = json.dumps({"image": encoded_string})
        headers = {"Content-Type": "application/json"}
        
        # Send POST request
        print("[DEBUG] Sending POST request to API")
        response = requests.post(API_URL, headers=headers, data=payload)
        print(f"[DEBUG] Response received, status code: {response.status_code}")
        
        res = response.json()
        print(f"[DEBUG] Response JSON: {res}")
        try:
            result = response.status_code, res["UserMatches"][0]["Similarity"], res["UserMatches"][0]["User"]["UserId"]
            print(f"[DEBUG] Extracted result: {result}")
        except IndexError:
            print("[DEBUG] IndexError: No user matches found")
            result = 404, 0, "unidentified"
        return result
    except Exception as e:
        print(f"[DEBUG] Exception in recognition_api.test_api: {str(e)}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        raise  # Re-raise the exception after logging

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python recognition-api.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    test_api(image_path)
