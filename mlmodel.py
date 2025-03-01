import dotenv
from gradio_client import Client, handle_file
import time
import signal
from functools import wraps
import threading
import cv2
import os
import tempfile
import uuid
import numpy as np

# Sample output = ({'label': 'No face detected!', 
# 'confidences': [{'label': 'No face detected!', 'confidence': 1.0}]}, None)

class TimeoutError(Exception):
    pass

def timeout(seconds=30):
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

def image(file):
    print(f"[DEBUG] mlmodel.image function called with file: {file}")
    try:
        print("[DEBUG] Loading environment variables")
        config = dotenv.dotenv_values("env")
        HF_token = config["hf_access_token"]
        print(f"[DEBUG] HF_token retrieved: {HF_token[:5]}...")  # Print first few chars for security
        
        print("[DEBUG] Creating Client for deepfakedetection")
        client = Client("dlweekproj/deepfakedetection", hf_token=HF_token)
        
        print("[DEBUG] Handling file for prediction")
        handled_file = handle_file(file)
        print(f"[DEBUG] File handled, type: {type(handled_file)}")
        
        print("[DEBUG] Calling predict with image")
        result = client.predict(
                inp=handled_file,
                model="Self-Blended Consistency Learning",
                api_name="/predict_image",
        )
        print(f"[DEBUG] Prediction result received: {result}")
        return result
    except Exception as e:
        print(f"[DEBUG] Exception in mlmodel.image: {str(e)}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        raise  # Re-raise the exception after logging

@timeout(60)  # Set a 60-second timeout for video processing
def video(file):
    print(f"[DEBUG] mlmodel.video function called with file: {file}")
    try:
        print("[DEBUG] Loading environment variables")
        config = dotenv.dotenv_values("env")
        HF_token = config["hf_access_token"]
        print(f"[DEBUG] HF_token retrieved: {HF_token[:5]}...")  # Print first few chars for security
        
        print("[DEBUG] Creating Client for deepfakedetection")
        client = Client("dlweekproj/deepfakedetection", hf_token=HF_token)
        
        print("[DEBUG] Handling file for prediction")
        handled_file = handle_file(file)
        print(f"[DEBUG] File handled, type: {type(handled_file)}")
        
        print("[DEBUG] Calling predict with video")
        result = client.predict(
            inp={"video":handled_file},
            model="Self-Blended Consistency Learning",
            api_name="/predict_video"
        )
        print(f"[DEBUG] Prediction result received: {result}")
        return result
    except Exception as e:
        print(f"[DEBUG] Exception in mlmodel.video: {str(e)}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        raise  # Re-raise the exception after logging

def extract_frames(video_path, max_frames=5):
    """Extract frames from a video file and save them as temporary images."""
    print(f"[DEBUG] Extracting frames from video: {video_path}")
    try:
        # Open the video file
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            print(f"[ERROR] Could not open video file: {video_path}")
            return []
            
        # Get video properties
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video.get(cv2.CAP_PROP_FPS)
        duration = frame_count / fps if fps > 0 else 0
        
        print(f"[DEBUG] Video properties: frames={frame_count}, fps={fps}, duration={duration}s")
        
        # Calculate frame intervals
        if frame_count <= max_frames:
            intervals = list(range(frame_count))
        else:
            intervals = [int(i * frame_count / max_frames) for i in range(max_frames)]
        
        print(f"[DEBUG] Frame intervals: {intervals}")
        
        # Extract frames
        frame_paths = []
        temp_dir = tempfile.gettempdir()
        
        for i, frame_idx in enumerate(intervals):
            # Set the frame position
            video.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            
            # Read the frame
            ret, frame = video.read()
            if not ret:
                print(f"[ERROR] Could not read frame {frame_idx}")
                continue
                
            # Save the frame as a temporary file
            frame_path = os.path.join(temp_dir, f"frame_{uuid.uuid4()}.jpg")
            cv2.imwrite(frame_path, frame)
            frame_paths.append(frame_path)
            print(f"[DEBUG] Extracted frame {i+1}/{len(intervals)}: {frame_path}")
        
        # Release the video
        video.release()
        
        return frame_paths
    except Exception as e:
        print(f"[ERROR] Exception in extract_frames: {str(e)}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        return []

@timeout(120)  # Set a 120-second timeout for frame-by-frame video processing
def video_by_frames(file, max_frames=5):
    """Process video by extracting frames and analyzing each with the image model."""
    print(f"[DEBUG] Processing video by frames: {file}")
    try:
        # Extract frames from the video
        frame_paths = extract_frames(file, max_frames)
        if not frame_paths:
            print("[ERROR] No frames could be extracted from the video")
            return {'label': 'Error: No frames could be extracted', 'confidences': []}
        
        # Process each frame with the image model
        results = []
        for i, frame_path in enumerate(frame_paths):
            try:
                print(f"[DEBUG] Processing frame {i+1}/{len(frame_paths)}")
                frame_result = image(frame_path)
                results.append(frame_result)
                
                # Clean up temporary file
                try:
                    os.remove(frame_path)
                except Exception as e:
                    print(f"[WARNING] Could not remove temporary file {frame_path}: {str(e)}")
            except Exception as e:
                print(f"[ERROR] Error processing frame {i+1}: {str(e)}")
        
        # Analyze the results
        return combine_frame_results(results)
    except Exception as e:
        print(f"[ERROR] Exception in video_by_frames: {str(e)}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        return {'label': f'Error: {str(e)}', 'confidences': []}

def combine_frame_results(results):
    """Combine results from multiple frames with a weighted approach."""
    print(f"[DEBUG] Combining results from {len(results)} frames")
    
    if not results:
        return {'label': 'Error: No results to combine', 'confidences': []}
    
    # Filter out frames with no face detected
    valid_results = []
    for result in results:
        if isinstance(result, tuple) and len(result) > 0 and isinstance(result[0], dict):
            label = result[0].get('label', '')
            if label != 'No face detected!':
                valid_results.append(result)
    
    print(f"[DEBUG] Found {len(valid_results)} frames with faces detected")
    
    if not valid_results:
        return {'label': 'No face detected in any frame', 'confidences': [{'label': 'No face detected!', 'confidence': 1.0}]}
    
    # Extract labels and confidences
    fake_count = 0
    real_count = 0
    fake_confidence_sum = 0
    real_confidence_sum = 0
    
    for result in valid_results:
        label = result[0].get('label', '')
        confidences = result[0].get('confidences', [])
        
        if 'fake' in label.lower():
            fake_count += 1
            # Find the fake confidence
            for conf in confidences:
                if 'fake' in str(conf.get('label', '')).lower():
                    fake_confidence_sum += conf.get('confidence', 0)
                    break
        else:
            real_count += 1
            # Find the real confidence
            for conf in confidences:
                if 'real' in str(conf.get('label', '')).lower():
                    real_confidence_sum += conf.get('confidence', 0)
                    break
    
    # Calculate weighted decision
    if fake_count > real_count:
        fake_avg_confidence = fake_confidence_sum / fake_count if fake_count > 0 else 0
        label = 'Fake'
        confidence = fake_avg_confidence
    else:
        real_avg_confidence = real_confidence_sum / real_count if real_count > 0 else 0
        label = 'Real'
        confidence = real_avg_confidence
    
    # Create a combined result
    combined_result = {
        'label': label,
        'confidences': [
            {'label': 'Fake', 'confidence': fake_confidence_sum / fake_count if fake_count > 0 else 0},
            {'label': 'Real', 'confidence': real_confidence_sum / real_count if real_count > 0 else 0}
        ],
        'frame_analysis': {
            'total_frames': len(results),
            'frames_with_faces': len(valid_results),
            'fake_frames': fake_count,
            'real_frames': real_count
        }
    }
    
    print(f"[DEBUG] Combined result: {combined_result}")
    return combined_result