from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

def reason(prompt):
    client = genai.Client()
    model_id = "gemini-2.0-flash"

    google_search_tool = Tool(
        google_search = GoogleSearch()
    )

    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        )
    )
    output = []
    for each in response.candidates[0].content.parts:
        output.append(each)

    output.append(response.candidates[0].grounding_metadata.search_entry_point.rendered_content)
    return output
