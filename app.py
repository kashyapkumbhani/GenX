import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, send_file
from dotenv import load_dotenv
from modules.site_generator import generate_site
from modules.data_manager import save_business_data, get_business_data, get_history, delete_site_version, create_site_zip
from modules.ai_content import generate_ai_content, discover_templates

# Load environment variables
load_dotenv()

# Initialize Flask application
app = Flask(__name__, 
            static_folder='static',
            template_folder='dashboard')

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['OUTPUT_DIR'] = os.path.join(os.path.dirname(__file__), 'output')
app.config['TEMPLATE_DIR'] = os.path.join(os.path.dirname(__file__), 'templates', 'business')
app.config['GEMINI_API_KEYS'] = [
    os.getenv('GEMINI_API_KEY_1'),
    os.getenv('GEMINI_API_KEY_2'),
    os.getenv('GEMINI_API_KEY_3'),
    os.getenv('GEMINI_API_KEY_4')
]

# Routes
@app.route('/')
def dashboard():
    """Dashboard home page with multi-step form"""
    # Discover available templates dynamically
    template_base_dir = os.path.join(os.path.dirname(__file__), 'templates')
    available_templates = discover_templates(template_base_dir)
    return render_template('index.html', dashboard_path='dashboard', templates=available_templates)

@app.route('/history')
def history():
    """View previously generated websites"""
    history_data = get_history()
    return render_template('history.html', history=history_data, dashboard_path='dashboard')

@app.route('/settings')
def settings():
    """API key management page"""
    api_keys = app.config['GEMINI_API_KEYS']
    return render_template('settings.html', api_keys=api_keys, dashboard_path='dashboard')

@app.route('/submit_business_data', methods=['POST'])
def submit_business_data():
    """Handle form submission and trigger site generation"""
    data = request.json
    
    # Get selected template from form data
    selected_template = data.get('template', 'business')  # Default to 'business' if not specified
    
    # Save business data
    save_business_data(data)
    
    # Generate AI content
    ai_content = generate_ai_content(data, template_name=selected_template, api_key=app.config['GEMINI_API_KEYS'][0])
    
    # Generate site
    output_version = generate_site(data, template_name=selected_template, ai_content=ai_content)
    
    return jsonify({
        'status': 'success',
        'message': 'Site generated successfully!',
        'version': output_version,
        'preview_url': f'/preview/{output_version}'
    })

@app.route('/preview/<int:version>')
def preview(version):
    """Preview generated site"""
    return redirect(f'/output/{version}/index.html')

# Serve generated sites
@app.route('/output/<path:path>')
def serve_output(path):
    return send_from_directory('output', path)

@app.route('/delete_version/<int:version>', methods=['POST'])
def delete_version(version):
    """Delete a specific site version"""
    success = delete_site_version(version)
    if success:
        return jsonify({'status': 'success', 'message': f'Version {version} deleted successfully'})
    else:
        return jsonify({'status': 'error', 'message': f'Failed to delete version {version}'}), 500

@app.route('/download_version/<int:version>')
def download_version(version):
    """Download a specific site version as zip"""
    zip_path = create_site_zip(version)
    if zip_path and os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True, download_name=f'site_v{version}.zip')
    else:
        return jsonify({'status': 'error', 'message': f'Failed to create zip for version {version}'}), 500

@app.route('/get_api_keys', methods=['GET'])
def get_api_keys():
    """Get current API keys for the settings page"""
    try:
        api_keys = []
        
        # Check for primary GEMINI_API_KEY first
        if os.environ.get('GEMINI_API_KEY'):
            api_keys.append(os.environ.get('GEMINI_API_KEY'))
        
        # Then check for numbered keys
        i = 1
        while True:
            key_name = f'GEMINI_API_KEY_{i}'
            if os.environ.get(key_name):
                api_keys.append(os.environ.get(key_name))
                i += 1
            else:
                break
        
        return jsonify({
            'success': True,
            'api_keys': api_keys
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/test_api_key', methods=['POST'])
def test_api_key():
    """Test if an API key is valid"""
    try:
        import requests
        
        data = request.get_json()
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return jsonify({
                'valid': False,
                'error': 'API key is required'
            }), 400
        
        # Test the API key by making a simple request to Gemini API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": "Hello, this is a test message."
                        }
                    ]
                }
            ]
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Make the test request with a timeout
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return jsonify({
                'valid': True,
                'message': 'API key is valid'
            })
        elif response.status_code == 400:
            return jsonify({
                'valid': False,
                'error': 'Invalid API key or request format'
            })
        elif response.status_code == 403:
            return jsonify({
                'valid': False,
                'error': 'API key access denied'
            })
        elif response.status_code == 429:
            return jsonify({
                'valid': False,
                'error': 'Rate limit exceeded - API key may be valid but overused'
            })
        else:
            return jsonify({
                'valid': False,
                'error': f'API returned status {response.status_code}'
            })
        
    except requests.exceptions.Timeout:
        return jsonify({
            'valid': False,
            'error': 'Request timeout - please try again'
        }), 400
    except requests.exceptions.RequestException as e:
        return jsonify({
            'valid': False,
            'error': f'Network error: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': str(e)
        }), 400

@app.route('/save_api_keys', methods=['POST'])
def save_api_keys():
    """Save API keys to environment file"""
    try:
        data = request.get_json()
        api_keys = data.get('api_keys', [])
        
        if not api_keys:
            return jsonify({
                'success': False,
                'error': 'At least one API key is required'
            }), 400
        
        # Read current .env file
        env_path = '.env'
        env_vars = {}
        
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key] = value
        
        # Remove existing GEMINI_API_KEY entries
        keys_to_remove = [key for key in env_vars.keys() if key.startswith('GEMINI_API_KEY')]
        for key in keys_to_remove:
            del env_vars[key]
        
        # Add new API keys
        for i, api_key in enumerate(api_keys):
            if api_key.strip():
                if i == 0:
                    env_vars['GEMINI_API_KEY'] = api_key.strip()
                else:
                    env_vars[f'GEMINI_API_KEY_{i+1}'] = api_key.strip()
        
        # Write back to .env file
        with open(env_path, 'w') as f:
            for key, value in env_vars.items():
                f.write(f'{key}={value}\n')
        
        # Update current environment
        for key in keys_to_remove:
            if key in os.environ:
                del os.environ[key]
        
        for key, value in env_vars.items():
            if key.startswith('GEMINI_API_KEY'):
                os.environ[key] = value
        
        # Update the config
        app.config['GEMINI_API_KEYS'] = [value for key, value in env_vars.items() if key.startswith('GEMINI_API_KEY') and value]
        
        return jsonify({
            'success': True,
            'message': f'Successfully saved {len(api_keys)} API key(s)'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate_services', methods=['POST'])
def generate_services():
    """Generate additional services using AI based on business category and primary service"""
    try:
        from modules.ai_content import get_random_api_key
        import requests
        
        data = request.get_json()
        business_category = data.get('businessCategory', '').strip()
        primary_keyword = data.get('primaryKeyword', '').strip()
        quantity = data.get('quantity', 8)  # Default to 8 if not provided
        
        if not business_category or not primary_keyword:
            return jsonify({
                'success': False,
                'error': 'Business category and primary keyword are required'
            }), 400
        
        # Validate quantity
        try:
            quantity = int(quantity)
            if quantity < 1 or quantity > 50:
                quantity = 8  # Default to 8 if invalid
        except (ValueError, TypeError):
            quantity = 8
        
        # Get API key
        api_key = get_random_api_key()
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'No valid API keys available'
            }), 400
        
        # Create AI prompt for services
        prompt = f"""Generate exactly {quantity} additional services for a {business_category} business whose primary service is "{primary_keyword}".

Requirements:
- Generate exactly {quantity} services, no more, no less
- Services should be related to {business_category} industry
- Include both basic and specialized services
- Make them specific and actionable
- Return as comma-separated values only
- No explanations or additional text
- Keep each service name concise (2-4 words)

Example format: Service 1, Service 2, Service 3, etc."""

        # Make API request
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                generated_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Clean up the response
                services = [service.strip() for service in generated_text.split(',')]
                services = [service for service in services if service and len(service) > 2]
                
                return jsonify({
                    'success': True,
                    'services': ', '.join(services)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'No content generated'
                }), 400
        else:
            return jsonify({
                'success': False,
                'error': f'API request failed with status {response.status_code}'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate_cities', methods=['POST'])
def generate_cities():
    """Generate service areas (cities) using AI based on business location"""
    try:
        from modules.ai_content import get_random_api_key
        import requests
        
        data = request.get_json()
        city = data.get('city', '').strip()
        state = data.get('state', '').strip()
        business_category = data.get('businessCategory', '').strip()
        quantity = data.get('quantity', 10)  # Default to 10 if not provided
        
        if not city or not state:
            return jsonify({
                'success': False,
                'error': 'City and state are required'
            }), 400
        
        # Validate quantity
        try:
            quantity = int(quantity)
            if quantity < 1 or quantity > 50:
                quantity = 10  # Default to 10 if invalid
        except (ValueError, TypeError):
            quantity = 10
        
        # Get API key
        api_key = get_random_api_key()
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'No valid API keys available'
            }), 400
        
        # Create AI prompt for cities
        prompt = f"""Generate exactly {quantity} cities and towns near {city}, {state} where a {business_category} business would typically provide services.

Requirements:
- Generate exactly {quantity} cities/areas, no more, no less
- Include {city} as the first city
- Focus on nearby cities, suburbs, and towns within reasonable service distance
- Include both larger cities and smaller communities
- Make them realistic locations in {state}
- Return as comma-separated values only
- No explanations or additional text
- Keep names concise and accurate

Example format: City 1, City 2, City 3, etc."""

        # Make API request
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                generated_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Clean up the response
                cities = [city.strip() for city in generated_text.split(',')]
                cities = [city for city in cities if city and len(city) > 1]
                
                return jsonify({
                    'success': True,
                    'cities': ', '.join(cities)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'No content generated'
                }), 400
        else:
            return jsonify({
                'success': False,
                'error': f'API request failed with status {response.status_code}'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)