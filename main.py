import gradio as gr
import recognition_api
import mlmodel
import chatmodel

def reasoning(falsity, ide):
    return f"""
You are an AI assistant specialized in assessing the authenticity of videos, particularly in the context of deepfakes and AI-generated content. Your task is to analyze the provided information and determine the likelihood of a video being AI-generated or manipulated, as well as any potential malicious intent behind its creation or distribution.
Based on a face recognition tool* the person in the video has been identified as {ide} (search who this is).
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
Reasoning: [Explanation for your assessment, including any specific concerns if applicable)
</assessment>
Remember, it's acceptable to return an unsure result if the evidence is inconclusive. Be thorough in your analysis and clear in your explanations.
"""

def deepfake(file):
    if file.name.endswith((".jpg", ".jpeg", ".png")):
        step1 = mlmodel.image(file)
    elif file.name.endswith((".mp4", ".mov", ".avi")):
        step1 = mlmodel.video(file)
    else:
        return f"Unsupported file type: {file.name}"

    if step1[0]["confidences"][0]["confidence"] > 0.8:
        hc = True

    match step1[0]["label"]:
        case "Fake":
            if hc:
                output = "There is a high likelihood of this media being AI-generated.", step1[0]["confidences"]
            else:
                resp_code, accuracy, name = recognition_api.test_api(file)
                output = chatmodel.reason(reasoning(False, name))
        case "Real":
            if hc:
                output = "This is probably real!", step1[0]["confidences"]
            else:
                resp_code, accuracy, name = recognition_api.test_api(file)
                output = chatmodel.reason(reasoning(True, name), file)
        case "No face detected!":
            output = "There doesn't appear to be a face in the source media..."

    return output
                
        
def analysis(text):
    return f"Text analysis result: The input text is '{text}'."

def process_input(text, file):
    if text:  
        output = analysis(text)
    elif file:  
        output = deepfake(file)
    else:
        output = "Please provide either text or a file."
    return output, gr.Textbox.update(value="")

interface = gr.Interface(
    fn=process_input,
    inputs=[
        gr.Textbox(label="Enter text for analysis", lines=2, placeholder="Type here..."),
        gr.UploadButton(label="Upload Image or Video", file_types=["image", "video"])
    ],
    outputs=gr.Textbox(label="Result"),
    live=False,
    title="Deepfake & Text Analysis",
    description="Upload an image/video for deepfake detection or enter text for analysis."
)

# Launch the interface
interface.launch()