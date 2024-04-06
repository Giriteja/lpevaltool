from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import streamlit as st
from openai import OpenAI
import openai
import requests
import PyPDF2
from PIL import Image

client = OpenAI(
  api_key='',  # this is also the default, it can be omitted
)

chatgpt_url = "https://api.openai.com/v1/chat/completions"

chatgpt_headers = {
    "content-type": "application/json",
    "Authorization":"Bearer {}".format('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')}

# Replace with your Form Recognizer endpoint and key
endpoint = "https://fixityai.cognitiveservices.azure.com/"
key = "0f74022fa8674eee9ecf38fbe0e31e24"


uploaded_pdf = st.file_uploader("Upload a PDF file", type="pdf")

def Analyize_answers(topic,url,headers,data):
    
    # Define the payload for the chat model
    messages = [
        {"role": "system", "content": """You are a teacher who evaluates students answers and give marks and Feedback on the given data.Ignore Spelling Mistakes.

	
	Give the output that should contain Question,overall score, and following metrics:

1)Accuracy: Determine the correctness of the information provided in the response. Are the facts and concepts presented accurate?

2)Relevance: Assess whether the student's response directly addresses the question asked. Is the information provided relevant to the topic being discussed?

3)Depth of Understanding: Evaluate the depth of the student's understanding of the topic. Does the response demonstrate a deep understanding of the concepts, theories, and principles involved?

4)Completeness: Consider whether the response covers all aspects of the question comprehensively. Are all relevant points addressed, or are there significant omissions?

5)Clarity of Expression: Evaluate the clarity and coherence of the student's writing. Is the response well-organized and easy to follow? Are ideas expressed clearly and concisely?

6)Use of Examples: Assess whether the student provides relevant examples to support their arguments or explanations. Do the examples enhance understanding and illustrate key points effectively?

7)Critical Thinking: Analyze the student's ability to critically evaluate and analyze information. Does the response demonstrate critical thinking skills, such as the ability to analyze, evaluate, and synthesize information?

8)Originality: Consider whether the student offers original insights or perspectives on the topic. Does the response demonstrate creativity or independent thinking?

9)Integration of Sources: If applicable, evaluate the student's ability to integrate information from multiple sources (e.g., textbooks, articles, lectures) into their response. Are sources properly cited and integrated into the discussion?

10)Argumentation and Logic: Assess the strength of the student's arguments and the logical coherence of their reasoning. Are arguments well-supported with evidence and logical reasoning?

11)Grammar and Mechanics: Consider the student's use of grammar, punctuation, and spelling. Are there any grammatical errors or typos that affect the clarity of the response?

12)Overall Quality: Provide an overall assessment of the quality of the student's response. Consider all of the above metrics in conjunction to determine the overall effectiveness of the response.

Make sure to provide all metrics.If not applicable ignore the specific metric by saying N/A. ensuring to include a newline character at the end to properly format your result.Display both Question and Answer written.

	

"""},
        {"role": "user", "content": data}
    ]

    chatgpt_payload = {
        "model": "gpt-4-1106-preview",
        "messages": messages,
        "temperature": 1.3,
        "top_p": 1,
	#"response_format": {"type": "json_object"},
        "stop": ["###"]
    }

    # Make the request to OpenAI's API
    response = requests.post(url, json=chatgpt_payload, headers=headers)
    response_json = response.json()

    # Extract data from the API's response
    #st.write(response_json)
    output = response_json['choices'][0]['message']['content']
    return output

def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in bounding_box])

def analyze_read():
    # Path to your local PDF file
    print(
uploaded_pdf)
    pdf_path = uploaded_pdf.name

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    
    with open(pdf_path, "rb") as f:
        poller = document_analysis_client.begin_analyze_document("prebuilt-read", f)
        result = poller.result()

    print("Document contains content: ", result.content)
    
    for idx, style in enumerate(result.styles):
        print(
            "Document contains {} content".format(
                "handwritten" if style.is_handwritten else "no handwritten"
            )
        )

    print("----------------------------------------")
    lp=Analyize_answers(result.content,chatgpt_url,chatgpt_headers,result.content)
    st.write(lp)



def read_pdf_file(file_path):
    with open(file_path, "rb") as f:
        pdf_bytes = f.read()
        st.write(pdf_bytes, format="pdf")


if __name__ == "__main__":
	if(uploaded_pdf):
		analyze_read()

		# Open the image file
		image = Image.open("metrics.png")

		# Display the image
		st.image(image, caption="Optional caption here", use_column_width=True)
