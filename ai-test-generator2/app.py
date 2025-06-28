from flask import Flask, render_template, request, jsonify
from granite_client import GraniteClient
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize Granite client
try:
    granite_client = GraniteClient()
    print("✅ Granite client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Granite client: {e}")
    granite_client = None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        api_code = request.form.get('api_code', '').strip()
        
        if not api_code:
            return render_template('index.html', 
                                 error="Please provide API code to analyze")
        
        if not granite_client:
            return render_template('index.html', 
                                 error="Granite client not initialized. Check your environment variables.")
        
        try:
            # Analyze API structure
            api_analysis = granite_client.analyze_api_structure(api_code)
            
            # Generate test cases
            generated_tests = granite_client.generate_test_cases(api_code)
            
            return render_template('index.html', 
                                 generated_tests=generated_tests,
                                 api_analysis=api_analysis,
                                 api_code=api_code)
        
        except Exception as e:
            error_message = f"Error generating test cases: {str(e)}"
            print(f"❌ {error_message}")
            return render_template('index.html', 
                                 error=error_message,
                                 api_code=api_code)
    
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def api_generate():
    """API endpoint for programmatic access"""
    try:
        data = request.get_json()
        api_code = data.get('api_code', '').strip()
        
        if not api_code:
            return jsonify({'error': 'API code is required'}), 400
        
        if not granite_client:
            return jsonify({'error': 'Granite client not initialized'}), 500
        
        # Analyze and generate
        api_analysis = granite_client.analyze_api_structure(api_code)
        generated_tests = granite_client.generate_test_cases(api_code)
        
        return jsonify({
            'generated_tests': generated_tests,
            'api_analysis': api_analysis,
            'model_used': os.getenv('GRANITE_MODEL'),
            'success': True
        })
    
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'granite_client': granite_client is not None,
        'model': os.getenv('GRANITE_MODEL'),
        'environment': os.getenv('FLASK_ENV', 'production')
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"🚀 Starting AI Test Case Generator")
    print(f"📊 Model: {os.getenv('GRANITE_MODEL')}")
    print(f"🌐 Port: {port}")
    print(f"🔧 Debug: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
