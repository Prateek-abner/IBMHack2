import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

class GraniteClient:
    def __init__(self):
        self.api_key = os.getenv('IBM_API_KEY')
        self.project_id = os.getenv('WATSONX_PROJECT_ID')
        self.base_url = os.getenv('WATSONX_URL')
        self.model_id = os.getenv('GRANITE_MODEL')
        self.access_token = None
        self.token_expires_at = 0
    
    def get_access_token(self):
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        url = "https://iam.cloud.ibm.com/identity/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.api_key
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.token_expires_at = time.time() + token_data.get("expires_in", 3600) - 300
            
            return self.access_token
        except Exception as e:
            raise Exception(f"Failed to get access token: {str(e)}")
    
    def generate_test_cases(self, prompt):
        url = f"{self.base_url}/ml/v1/text/generation?version=2023-05-29"
        
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "input": prompt,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 3000,
                "temperature": 0.1,
                "stop_sequences": ["</code>", "---END---"]
            },
            "model_id": self.model_id,
            "project_id": self.project_id
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["results"][0]["generated_text"]
        except Exception as e:
            raise Exception(f"Failed to generate test cases: {str(e)}")
