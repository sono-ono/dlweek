import gradio as gr
import recognition_api
import mlmodel
import chatmodel

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

def sg_pol_recog(file):
    resp_code, accuracy, name = recognition_api.test_api(file)
    return resp_code, accuracy, name 
    
def deepfake(file):
    if file.name.endswith((".jpg", ".jpeg", ".png")):
        step1 = mlmodel.image(file)
    elif file.name.endswith((".mp4", ".mov", ".avi")):
        step1 = mlmodel.video(file)
    else:
        return f"Unsupported file type: {file.name}"

    hc = False
    output = ""
    print(step1[0]["confidences"][0])
    prob = step1[0]["confidences"][0]["confidence"]
    if prob > 0.8:
        hc = True

    match step1[0]["label"]:
        case "Fake":
            if hc:
                output = "There is a high likelihood of this media being AI-generated. The probability is " + str(prob) + ". "
            resp_code, accuracy, name = sg_pol_recog(file)
            print(resp_code, accuracy, name)     
            output += chatmodel.reason(reasoning(False, name, prob), file)
        case "Real":
            if hc:
                output = "This is probably real! The probability is " + str(prob) + ". "
            resp_code, accuracy, name = sg_pol_recog(file)
            print(resp_code, accuracy, name)
            output += chatmodel.reason(reasoning(True, name, prob), file)
        case "No face detected!":
            output = "There doesn't appear to be a face in the source media..."

    return output
                

def process_input(file):
    if file:  
        output = deepfake(file)
    else:
        output = "Please provide a file for analysis."
    return output

interface = gr.Interface(
    fn=process_input,
    inputs=[
        gr.UploadButton(label="Upload Image or Video", file_types=["image", "video"])
    ],
    outputs=gr.Textbox(label="Result"),
    live=False,
    title="Deepfake Analysis",
    description="Upload an image/video for deepfake detection."
)

# Launch the interface
interface.launch()