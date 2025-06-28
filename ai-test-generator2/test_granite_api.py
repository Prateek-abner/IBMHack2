import requests
import os
import json

# Set your environment variables
os.environ['IBM_API_KEY'] = 'oS3eRXK2a8wdPcoEYg6XrH0lr60pD1r1cWY0ueh2uYS1'
os.environ['WATSONX_PROJECT_ID'] = '423037e0-7293-43bf-bcb8-0a3bd65f9ef6'
os.environ['WATSONX_URL'] = 'https://us-south.ml.cloud.ibm.com'
os.environ['GRANITE_MODEL'] = 'ibm/granite-3-0-8b-instruct'

def get_access_token(api_key):
    """Get IAM access token"""
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
        print("✅ Successfully obtained access token")
        return token_data["access_token"]
    except requests.exceptions.HTTPError as e:
        print(f"❌ Failed to get access token: {e}")
        print(f"Response: {response.text}")
        return None
    except Exception as e:
        print(f"❌ Error getting access token: {e}")
        return None

def test_granite_api():
    """Test Granite API with text generation"""
    # Get access token
    token = get_access_token(os.environ['IBM_API_KEY'])
    if not token:
        return None
    
    # API endpoint for text generation
    url = f"{os.environ['WATSONX_URL']}/ml/v1/text/generation?version=2023-05-29"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Test prompt
    prompt = """Generate a simple Java JUnit test case for a calculator add method.
    
Requirements:
- Use JUnit 5 annotations
- Test the add method with two integers
- Include proper assertions

Generate the test class:"""
    
    body = {
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 200,
            "temperature": 0.3,
            "top_p": 0.9,
            "repetition_penalty": 1.1
        },
        "model_id": os.environ['GRANITE_MODEL'],
        "project_id": os.environ['WATSONX_PROJECT_ID']
    }
    
    try:
        print("🔄 Making API request to Granite model...")
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Successfully received response from Granite API")
        return result
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    except Exception as e:
        print(f"❌ Error calling Granite API: {e}")
        return None

def run_comprehensive_test():
    """Run comprehensive test of Granite API"""
    print("🤖 Testing IBM Granite API Connection")
    print("=" * 50)
    
    # Test 1: Check environment variables
    print("📋 Step 1: Checking environment variables...")
    required_vars = ['IBM_API_KEY', 'WATSONX_PROJECT_ID', 'WATSONX_URL', 'GRANITE_MODEL']
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {'*' * 10}...{value[-4:] if len(value) > 4 else value}")
        else:
            print(f"❌ {var}: Not set")
            return
    
    # Test 2: Get access token
    print("\n🔑 Step 2: Testing IAM token generation...")
    token = get_access_token(os.environ['IBM_API_KEY'])
    if not token:
        return
    
    # Test 3: Test Granite API
    print("\n🧠 Step 3: Testing Granite model inference...")
    result = test_granite_api()
    
    if result:
        print("\n📄 Generated Response:")
        print("-" * 50)
        generated_text = result.get('results', [{}])[0].get('generated_text', 'No text generated')
        print(generated_text[:500] + "..." if len(generated_text) > 500 else generated_text)
        
        print("\n📊 Response Metadata:")
        print(f"Model ID: {result.get('model_id', 'N/A')}")
        print(f"Created: {result.get('created_at', 'N/A')}")
        
        # Check token usage if available
        if 'results' in result and len(result['results']) > 0:
            first_result = result['results'][0]
            if 'input_token_count' in first_result:
                print(f"Input tokens: {first_result['input_token_count']}")
            if 'generated_token_count' in first_result:
                print(f"Generated tokens: {first_result['generated_token_count']}")
        
        print("\n✅ All tests passed! Granite API is working correctly.")
    else:
        print("\n❌ Granite API test failed.")

# Alternative simple test function
def quick_test():
    """Quick test with minimal output"""
    try:
        token = get_access_token(os.environ['IBM_API_KEY'])
        if not token:
            return False
        
        url = f"{os.environ['WATSONX_URL']}/ml/v1/text/generation?version=2023-05-29"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        body = {
            "input": "Hello, how are you?",
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 50,
                "temperature": 0.3
            },
            "model_id": os.environ['GRANITE_MODEL'],
            "project_id": os.environ['WATSONX_PROJECT_ID']
        }
        
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Quick test passed - Granite API is working!")
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

# Run the tests
if __name__ == "__main__":
    print("Choose test type:")
    print("1. Comprehensive test (detailed)")
    print("2. Quick test (simple)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        run_comprehensive_test()
    elif choice == "2":
        quick_test()
    else:
        print("Running comprehensive test by default...")
        run_comprehensive_test()
