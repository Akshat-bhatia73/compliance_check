from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
import json
import openai
import os
from pydantic import BaseModel, HttpUrl
import requests

# Loading the environment variables
load_dotenv()

app = FastAPI(title="Compliance Checker API")

# Initializing the OpenAI client
client = openai.OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key= os.getenv("FIREWORKS_API_KEY"),
)

# Defining the schema for the structured output we require
json_schema = {
    "type": "object",
    "properties": {
        "violations": {
            "type": "array",
            "description": "All the violations found in the webpage. If no violations are present, return an empty array.",
            "items": {
                "type": "object",
                "properties": {
                    "policy_section": {
                        "type": "string",
                        "description": "The specific section of the policy that was violated"
                    },
                    "violation_description": {
                        "type": "string",
                        "description": "Detailed description of the violation"
                    },
                    "example": {
                        "type": "string",
                        "description": "An example from the webpage content illustrating the issue"
                    },
                    "recommended_fix": {
                        "type": "string",
                        "description": "Suggested solution to address the violation"
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "The severity level of the violation"
                    }
                },
                "required": ["policy_section", "violation_description", "recommended_fix", "severity", "example"]
            }
        },
        "total_violations": {
            "type": "integer",
            "description": "Total number of violations found"
        },
        "summary": {
            "type": "string",
            "description": "A high-level summary of the compliance check results."
        }
    },
    "required": ["violations", "total_violations", "summary"]
}

# Request parameters
class WebpageRequest(BaseModel):
    url: HttpUrl
    policy_url: HttpUrl

def extract_webpage_content(url: str) -> str:
    # Extracting the main content from a webpage
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Removing the script and style elements to cleanup the website text
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text(separator=' ', strip=True)
        
        # Applying basic text cleaning
        lines = (line.strip() for line in text.splitlines())
        # Cleaning any excessive white spaces in the split lines
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching page: {str(e)}")

def analyze_compliance(content: str, policy_content: str) -> dict:
    # Analyzing the compliance of the web page
    try:
        chat_completion = client.chat.completions.create(
            model="accounts/fireworks/models/mixtral-8x7b-instruct",
            response_format={"type": "json_object", "schema": json_schema},
            messages=[
                {
                    "role": "system",
                    "content": "You are a compliance checker that analyzes webpage content against compliance policies. Provide detailed violations in a structured format."
                },
                {
                    "role": "user",
                    "content": f"""
                        Analyze this webpage content against the compliance policy.
                            
                        COMPLIANCE POLICY:
                        {policy_content}
                            
                        WEBPAGE CONTENT:
                        {content}
                    """
                },
            ],
            temperature=0.2
        )
        
        return json.loads(chat_completion.choices[0].message.content) # Returning the json response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing: {str(e)}")
    
@app.post("/check-compliance")
async def check_compliance(request: WebpageRequest):
    # Returning a structured JSON response after analyzing the page against compliance policy
    try:
        # Extracting content from both URLs
        webpage_content = extract_webpage_content(str(request.url))
        policy_content = extract_webpage_content(str(request.policy_url))
        
        # Analyzing compliance
        compliance_result = analyze_compliance(webpage_content, policy_content)
        
        return {
            "url_analyzed": request.url,
            "checked_against": request.policy_url,
            "compliance_result": compliance_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)