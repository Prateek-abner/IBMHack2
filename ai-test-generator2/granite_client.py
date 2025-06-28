import requests
import os
from dotenv import load_dotenv
import time
import json

load_dotenv()

class GraniteClient:
    def __init__(self):
        self.api_key = os.getenv('IBM_API_KEY')
        self.project_id = os.getenv('WATSONX_PROJECT_ID')
        self.watsonx_url = os.getenv('WATSONX_URL')
        self.model_id = os.getenv('GRANITE_MODEL')
        self.access_token = None
        self.token_expires_at = 0
        
        if not all([self.api_key, self.project_id, self.watsonx_url, self.model_id]):
            raise ValueError("Missing required environment variables")
    
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
            self.token_expires_at = time.time() + token_data["expires_in"] - 300
            
            return self.access_token
        except Exception as e:
            raise Exception(f"Failed to get access token: {str(e)}")
    
    def generate_test_cases(self, api_code):
        access_token = self.get_access_token()
        
        prompt = f"""You are an expert QA automation engineer specializing in API testing. Analyze the following API code and generate comprehensive JUnit 5 test cases using RestAssured framework.

API Code to Analyze:
{api_code}

Generate comprehensive test cases that include:

1. Functional Tests: Happy path scenarios for each endpoint
2. Error Handling Tests: Test 400, 401, 404, 500 error responses  
3. Boundary Value Tests: Test edge cases and input limits
4. Input Validation Tests: Test invalid data formats and missing fields
5. Authentication Tests: Test secured endpoints
6. Performance Tests: Basic response time validation

Requirements:
- Use JUnit 5 annotations (@Test, @DisplayName, @BeforeEach)
- Use RestAssured for API calls (given().when().then() pattern)
- Include proper assertions and status code validations
- Add realistic test data and scenarios
- Follow naming convention: test[MethodName][Scenario][ExpectedResult]
- Include setup methods for base configuration

Format as a complete, runnable JUnit 5 test class with all necessary imports.

Generate the complete test class:"""

        url = f"{self.watsonx_url}/ml/v1/text/generation?version=2023-05-29"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        body = {
            "input": prompt,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 3000,
                "temperature": 0.2,
                "top_p": 0.9,
                "repetition_penalty": 1.1,
                "stop_sequences": ["```"]
            },
            "model_id": self.model_id,
            "project_id": self.project_id
        }
        
        try:
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()
            
            result = response.json()
            generated_text = result["results"]["generated_text"]
            
            # Clean up the generated text
            if "```java" in generated_text:
                generated_text = generated_text.split("```")[0]
            elif "```" in generated_text:
                generated_text = generated_text.split("```")[0]
            
            return generated_text.strip()
            
        except Exception as e:
            raise Exception(f"Failed to generate test cases: {str(e)}")
    
    def analyze_api_structure(self, api_code):
        """Analyze API structure to provide better context"""
        endpoints = []
        lines = api_code.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(annotation in line for annotation in ['@GetMapping', '@PostMapping', '@PutMapping', '@DeleteMapping']):
                endpoints.append(line)
        
        return {
            "endpoint_count": len(endpoints),
            "endpoints": endpoints,
            "has_path_variables": "{" in api_code and "}" in api_code,
            "has_request_body": "@RequestBody" in api_code,
            "has_validation": "@Valid" in api_code
        }