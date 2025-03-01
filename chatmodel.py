from google import genai
import dotenv
import time 
import threading
from functools import wraps

class TimeoutError(Exception):
    pass

def timeout(seconds=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = [TimeoutError('Function call timed out')]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    result[0] = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(seconds)
            
            if isinstance(result[0], Exception):
                raise result[0]
            return result[0]
        return wrapper
    return decorator

@timeout(90)  # Set a 90-second timeout for the entire reasoning process
def reason(prompt, file_path):
    print(f"[DEBUG] chatmodel.reason called with file_path: {file_path}")
    print(f"[DEBUG] Prompt: {prompt}")
    try:
        print("[DEBUG] Loading environment variables")
        config = dotenv.dotenv_values("env")
        print("[DEBUG] Creating genai client")
        client = genai.Client(api_key=config["gemini_token"])
        
        print(f"[DEBUG] Uploading file: {file_path}")
        media_file = client.files.upload(file=file_path)
        print(f"[DEBUG] File uploaded, state: {media_file.state.name}")

        print("[DEBUG] Waiting for file processing")
        # Add a timeout for the file processing wait loop
        max_wait_time = 30  # seconds
        start_time = time.time()
        while media_file.state.name == "PROCESSING":
            print('.', end='')
            time.sleep(1)
            
            # Check if we've exceeded the maximum wait time
            if time.time() - start_time > max_wait_time:
                print("\n[DEBUG] File processing timeout exceeded")
                raise TimeoutError("File processing took too long")
                
            media_file = client.files.get(name=media_file.name)
        print(f"\n[DEBUG] File processing complete, state: {media_file.state.name}")
        
        print("[DEBUG] Generating content with Gemini")
        response = client.models.generate_content(
            model = "gemini-1.5-pro",
            contents = [
                media_file,
                prompt
            ]
        )
        print(f"[DEBUG] Response received, length: {len(response.text)}")
        
        return response.text
    except TimeoutError as e:
        print(f"[DEBUG] Timeout in chatmodel.reason: {str(e)}")
        return f"Analysis timed out: {str(e)}. The media may be too complex to analyze."
    except Exception as e:
        print(f"[DEBUG] Exception in chatmodel.reason: {str(e)}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        return f"Error in analysis: {str(e)}"

# test
# print(reason("Summarise this video", "pics/world.mp4"))