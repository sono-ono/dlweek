from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import recognition_api
import mlmodel
import chatmodel
from flask_cors import CORS
import cv2
import tempfile
import uuid

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'mov', 'avi'}

# Ensure the uploads directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def reasoning(falsity, ide, prob):
    if falsity: 
        t = "IMPORTANT: This video has passed the AI detection stage, but it is still possible to have been faked. Be critical! The probability of it being real is " + str(prob)
    else:
        t = "IMPORTANT: This video has been deemed as AI-generated by detection software. Only advice against this if the provenance makes it extremely clear it is not faked/beneficial. The probability of it being real is " + str(prob)
    return f"""
You are an AI assistant specialized in assessing the authenticity of videos, particularly in the context of deepfakes and AI-generated content. Your task is to analyze the provided information and determine the likelihood of a video being AI-generated or manipulated, as well as any potential malicious intent behind its creation or distribution.
Based on a face recognition tool* the person in the video has been identified as {ide} (only Singapore politicians are in the facial recognition database as of now). {t}
Use your grounding tools to search to see if any of the information can be verified.
Important context (as of 2025):
• Deepfakes and AI-generated images have become extremely convincing.
Traditional signs of manipulation (e.g., boundary artifacts, inconsistencies) are no longer reliable indicators.
The term "deepfakes" encompasses AI-generated images, face swaps, and various forms of content manipulation.
The visual distinction between real and fake images has become nearly imperceptible to the human eye.
Provide your analysis and assessment in the following format:
<structured_analysis>
1. Summary of key points:
[Summarize the most important information from each section of the input]
2. Potential indicators of authenticity:
[List factors that suggest the image might be authentic]
3. Potential indicators of manipulation:
[List factors that suggest the image might be AI-generated or manipulated)
4. Contextual considerations:
[Discuss the context of the image and potential motivations for its creation/sharing] 
</structured_analysis>
<assessment>
Likelihood of AI generation/manipulation: [High/Low/Unsure]
Reasoning: [Explanation for your assessment]
Potential malicious intent: [Yes/No/Unsure]
Reasoning: [Explanation for your assessment, including any specific concerns if applicable; err on the side that malicious is present]
</assessment>
Remember, it's acceptable to return an unsure result if the evidence is inconclusive. Be thorough in your analysis and clear in your explanations. Avoid explicit mention of what was in this prompt in your response.
"""

def sg_pol_recog(file_path):
    resp_code, accuracy, name = recognition_api.test_api(file_path)
    return resp_code, accuracy, name 
    
def extract_frames(video_path, max_frames=5):
    """Extract frames from a video file and save them as temporary images.
    
    Args:
        video_path: Path to the video file
        max_frames: Maximum number of frames to extract
        
    Returns:
        List of paths to the extracted frames
    """
    print(f"[DEBUG] Extracting frames from video: {video_path}")
    try:
        # Open the video file
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            print(f"[DEBUG] Error: Could not open video file: {video_path}")
            return []
            
        # Get video properties
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video.get(cv2.CAP_PROP_FPS)
        duration = frame_count / fps if fps > 0 else 0
        
        print(f"[DEBUG] Video properties: frames={frame_count}, fps={fps}, duration={duration}s")
        
        # Calculate frame intervals
        if frame_count <= max_frames:
            # If video has fewer frames than max_frames, use all frames
            intervals = list(range(frame_count))
        else:
            # Otherwise, distribute frames evenly
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
                print(f"[DEBUG] Error: Could not read frame {frame_idx}")
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
        print(f"[DEBUG] Exception in extract_frames: {str(e)}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        return []

def process_video_frames(file_path, prob):
    """Process frames extracted from a video through facial recognition.
    
    Args:
        file_path: Path to the video file
        prob: Probability from the deepfake detection
        
    Returns:
        Tuple of (name, accuracy) for the best match
    """
    print(f"[DEBUG] Processing video frames for facial recognition: {file_path}")
    
    # Extract frames from the video
    frame_paths = extract_frames(file_path)
    if not frame_paths:
        print(f"[DEBUG] No frames extracted from video: {file_path}")
        return 404, 0, "unidentified"
    
    # Process each frame through facial recognition
    best_match = (404, 0, "unidentified")
    
    for frame_path in frame_paths:
        try:
            print(f"[DEBUG] Processing frame through facial recognition: {frame_path}")
            resp_code, accuracy, name = recognition_api.test_api(frame_path)
            print(f"[DEBUG] Frame recognition result: {resp_code}, {accuracy}, {name}")
            
            # Keep the best match (highest accuracy)
            if resp_code == 200 and accuracy > best_match[1]:
                best_match = (resp_code, accuracy, name)
                
            # Clean up the temporary file
            try:
                os.remove(frame_path)
            except Exception as e:
                print(f"[DEBUG] Error removing temporary frame: {str(e)}")
                
        except Exception as e:
            print(f"[DEBUG] Error processing frame {frame_path}: {str(e)}")
    
    print(f"[DEBUG] Best match from video frames: {best_match}")
    return best_match

def deepfake(file_path):
    print(f"[DEBUG] deepfake function called with file_path: {file_path}")
    try:
        if file_path.lower().endswith((".jpg", ".jpeg", ".png")):
            print(f"[DEBUG] Processing as image file")
            step1 = mlmodel.image(file_path)
        elif file_path.lower().endswith((".mp4", ".mov", ".avi")):
            print(f"[DEBUG] Processing as video file")
            try:
                # Use the new video_by_frames function instead of manual frame extraction
                print(f"[DEBUG] Using video_by_frames function for: {file_path}")
                step1 = mlmodel.video_by_frames(file_path, max_frames=5)
                
                # If the result is not a tuple (as expected by the rest of the code),
                # convert it to the expected format
                if not isinstance(step1, tuple):
                    print(f"[DEBUG] Converting video_by_frames result to expected format")
                    step1 = (step1, None)
                    
            except Exception as e:
                print(f"[DEBUG] Error processing video: {str(e)}")
                import traceback
                print(f"[DEBUG] Traceback: {traceback.format_exc()}")
                return f"Error processing video: {str(e)}"
        else:
            print(f"[DEBUG] Unsupported file type: {file_path}")
            return f"Unsupported file type: {file_path}"

        print(f"[DEBUG] mlmodel returned: {step1}")
        
        # Check if step1 is None or doesn't have the expected structure
        if not step1 or not isinstance(step1, tuple) or len(step1) < 1 or not isinstance(step1[0], dict):
            print(f"[DEBUG] Invalid response from mlmodel: {step1}")
            return "Error: Invalid response from the detection model"
            
        if 'confidences' not in step1[0] or not step1[0]['confidences']:
            print(f"[DEBUG] No confidences in response: {step1}")
            return "Error: No confidence data in model response"
            
        print(f"[DEBUG] Confidence data: {step1[0]['confidences'][0]}")
        prob = step1[0]["confidences"][0]["confidence"]
        if prob > 0.8:
            hc = True
            print(f"[DEBUG] High confidence detected: {prob}")
        else:
            hc = False

        print(f"[DEBUG] Label detected: {step1[0]['label']}")
        match step1[0]["label"]:
            case "Fake":
                if hc:
                    output = "There is a high likelihood of this media being AI-generated. The probability is " + str(prob) + ". "
                else:
                    output = "This media may be AI-generated. The probability is " + str(prob) + ". "
                try:
                    print(f"[DEBUG] Calling facial recognition for fake media")
                    # Use different processing for videos and images
                    if file_path.lower().endswith((".mp4", ".mov", ".avi")):
                        resp_code, accuracy, name = process_video_frames(file_path, prob)
                    else:
                        resp_code, accuracy, name = sg_pol_recog(file_path)
                    print(f"[DEBUG] Facial recognition returned: {resp_code}, {accuracy}, {name}")     
                    print(f"[DEBUG] Calling chatmodel.reason for fake media")
                    output += chatmodel.reason(reasoning(False, name, prob), file_path)
                except Exception as e:
                    print(f"[DEBUG] Error in recognition or reasoning: {str(e)}")
                    output += f" Error in detailed analysis: {str(e)}"
            case "Real":
                if hc:
                    output = "This is probably real! The probability is " + str(prob) + ". "
                else:
                    output = "This media appears to be real, but with low confidence. The probability is " + str(prob) + ". "
                try:
                    print(f"[DEBUG] Calling facial recognition for real media")
                    # Use different processing for videos and images
                    if file_path.lower().endswith((".mp4", ".mov", ".avi")):
                        resp_code, accuracy, name = process_video_frames(file_path, prob)
                    else:
                        resp_code, accuracy, name = sg_pol_recog(file_path)
                    print(f"[DEBUG] Facial recognition returned: {resp_code}, {accuracy}, {name}")
                    print(f"[DEBUG] Calling chatmodel.reason for real media")
                    output += chatmodel.reason(reasoning(True, name, prob), file_path)
                except Exception as e:
                    print(f"[DEBUG] Error in recognition or reasoning: {str(e)}")
                    output += f" Error in detailed analysis: {str(e)}"
            case "No face detected!":
                output = "There doesn't appear to be a face in the source media..."
                print("[DEBUG] No face detected in media")
            case _:
                output = f"Unexpected label: {step1[0]['label']}"
                print(f"[DEBUG] Unexpected label: {step1[0]['label']}")

        print(f"[DEBUG] deepfake function returning output: {output[:100]}...")  # Print first 100 chars
        return output
    except Exception as e:
        print(f"[DEBUG] Unhandled exception in deepfake function: {str(e)}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        return f"Error processing media: {str(e)}"

@app.route('/api/analyze', methods=['POST'])
def analyze_media():
    print("\n[DEBUG] Starting analyze_media route")
    if 'file' not in request.files:
        print("[DEBUG] Error: No file part in request")
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    print(f"[DEBUG] Received file: {file.filename}, type: {file.content_type}")
    
    if file.filename == '':
        print("[DEBUG] Error: No selected file (empty filename)")
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"[DEBUG] Saving file to: {file_path}")
        file.save(file_path)
        
        try:
            print(f"[DEBUG] Calling deepfake function with file_path: {file_path}")
            result = deepfake(file_path)
            print(f"[DEBUG] Deepfake function returned result: {result[:100]}...")  # Print first 100 chars
            return jsonify({'result': result})
        except Exception as e:
            print(f"[DEBUG] Exception in deepfake processing: {str(e)}")
            import traceback
            print(f"[DEBUG] Traceback: {traceback.format_exc()}")
            return jsonify({'error': str(e)}), 500
    
    print(f"[DEBUG] File type not allowed: {file.filename}")
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 