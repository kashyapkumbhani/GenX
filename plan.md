# Local Business Site Generator Plan

This document outlines the plan to create a local business site generator using Flask and pre-defined HTML templates.

## Priorities
- [x] 1. Project Setup
- [x] 2. HTML Templates
- [x] 2.1 Template Schemas
- [x] 3. Flask Application Setup
- [x] 4. Python Script for Site Generation
- [x] 5. Dashboard Implementation
- [x] 6. Data Management
- [ ] 7. Deployment/Serving

## 1. Project Setup
- Create a basic project directory structure.
- Define a data structure (e.g., JSON) to store business details, services, keywords, and areas served.

## 2. HTML Templates
- **Flask Template Structure**:
  - Templates will be organized in the Flask application's `templates` directory
  - Business site templates will remain in the `template/template-a` directory
- **`index.html`**: A template for the main business homepage.
  - Uses Jinja2 syntax for dynamic content insertion
  - Include placeholders for dynamic content such as business name, description, services, primary keywords, etc.
- **`location.html`**: A template for individual location pages.
  - Uses Jinja2 syntax for dynamic content insertion
  - Include placeholders for dynamic content such as business name, location-specific details, services, and keywords.
- **Dashboard Templates**:
  - `dashboard/index.html`: Main dashboard with multi-step form
  - `dashboard/history.html`: Page to view previously generated websites
  - `dashboard/settings.html`: Page to manage API keys
  - `components/sidebar.html`: Reusable sidebar navigation component
  - `components/form_steps.html`: Reusable multi-step form components

## 2.1 Template Schemas
- Each business site template (e.g., `index.html`, `location.html`) will have a corresponding JSON schema file (e.g., `index.json`, `location.json`) located in the same template directory (e.g., `/Users/anushri509/11ty/pyt-local/template/template-a`).
- These JSON schema files will define the structure and requirements for the dynamic content that the AI will generate.
- `index.json` and `location.json` will have different schemas and designs to cater to their specific content needs.
- **Jinja2 Integration**: The HTML templates will use Jinja2 syntax for dynamic content insertion. The JSON schema will map directly to Jinja2 variables:
  - Schema fields will correspond to Jinja2 variables (e.g., `{{ serviceHighlights.title }}`)
  - For iterating through arrays: `{% for highlight in serviceHighlights.highlights %} ... {% endfor %}`
  - For conditional content: `{% if serviceHighlights.required %} ... {% endif %}`
- Example schema object for a section:
  ```json
  "serviceHighlights": {
    "required": true,
    "description": "Service highlights section emphasizing local advantages",
    "fields": ["title", "highlights"],
    "prompt": "Create a service highlights section for {business.name} in {location.city}, {location.state}. Include: 1) A compelling section title like 'Why Choose Local Service?', 2) An array of 3 highlight cards, each with a title and description emphasizing local advantages such as neighborhood knowledge, rapid response times, and community trust. Make the content specific to local service benefits in {location.city}.",
    "examples": [
      {
        "title": "Why Choose Local Service?",
        "highlights": [
          {
            "title": "Neighborhood Knowledge",
            "description": "We understand the specific plumbing systems and common issues in your area. Our local expertise means faster diagnosis and more effective solutions."
          },
          {
            "title": "Rapid Response",
            "description": "Being local means we're never far away. Our service vehicles are strategically positioned for the fastest possible response to your plumbing emergencies."
          },
          {
            "title": "Community Trust",
            "description": "We're your neighbors too. Our reputation is built on trust, quality work, and fair pricing. We're invested in maintaining our community relationships."
          }
        ]
      }
    ]
  }
  ```

## 3. Flask Application Setup

### 3.1 Directory Structure
```
/Users/anushri509/11ty/pyt-local/
├── app.py                      # Main Flask application entry point
├── config.py                   # Configuration settings
├── requirements.txt            # Project dependencies
├── .env                        # Environment variables (not in version control)
├── .gitignore                  # Git ignore file
├── static/                     # Static assets
│   ├── css/                    # Stylesheets
│   ├── js/                     # JavaScript files
│   └── images/                 # Image assets
├── templates/                  # Flask application templates
│   ├── dashboard/              # Dashboard templates
│   │   ├── index.html          # Dashboard home page
│   │   ├── history.html        # History page
│   │   └── settings.html       # Settings page
│   └── components/             # Reusable template components
│       ├── sidebar.html        # Sidebar navigation
│       └── form_steps.html     # Multi-step form components
├── template/                   # Business site templates
│   └── template-a/             # Template variant A
│       ├── index.html          # Homepage template
│       ├── index.json          # Homepage schema
│       ├── location.html       # Location page template
│       └── location.json       # Location page schema
├── output/                     # Generated sites (versioned)
│   ├── 1/                      # Version 1
│   └── 2/                      # Version 2
└── modules/                    # Application modules
    ├── site_generator.py       # Site generation logic
    ├── ai_content.py           # AI content generation
    └── data_manager.py         # Data management utilities
```

### 3.2 Flask Application Configuration

#### 3.2.1 Dependencies (requirements.txt)
```
Flask==2.3.3
python-dotenv==1.0.0
Jinja2==3.1.2
requests==2.31.0
jsonschema==4.19.0
Werkzeug==2.3.7
Flask-WTF==1.1.1
```

#### 3.2.2 Environment Variables (.env)
```
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
GEMINI_API_KEY_1=AIzaSyAMCZti3Ndirh2_O_fe42z03ocerkXLlV0
GEMINI_API_KEY_2=AIzaSyCyma9-wQb6BCvzzONNtArKAmiwW_E0HNQ
GEMINI_API_KEY_3=AIzaSyAREOxhnBXNOe70JMtrfiCVTMk9CztnJvg
GEMINI_API_KEY_4=AIzaSyBQeZrkmC40-gXZjPTJbMzyObOsqNpsk1I
SECRET_KEY=your-secret-key-for-flask-sessions
```

#### 3.2.3 Main Application (app.py)
```python
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv
from modules.site_generator import generate_site
from modules.data_manager import save_business_data, get_business_data, get_history
from modules.ai_content import generate_ai_content

# Load environment variables
load_dotenv()

# Initialize Flask application
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['OUTPUT_DIR'] = os.path.join(os.path.dirname(__file__), 'output')
app.config['TEMPLATE_DIR'] = os.path.join(os.path.dirname(__file__), 'template')
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
    return render_template('dashboard/index.html')

@app.route('/history')
def history():
    """View previously generated websites"""
    history_data = get_history()
    return render_template('dashboard/history.html', history=history_data)

@app.route('/settings')
def settings():
    """API key management page"""
    api_keys = app.config['GEMINI_API_KEYS']
    return render_template('dashboard/settings.html', api_keys=api_keys)

@app.route('/submit_business_data', methods=['POST'])
def submit_business_data():
    """Handle form submission and trigger site generation"""
    data = request.json
    
    # Save business data
    save_business_data(data)
    
    # Generate AI content
    ai_content = generate_ai_content(data, app.config['GEMINI_API_KEYS'][0])
    
    # Generate site
    output_version = generate_site(data, ai_content)
    
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
    return app.send_static_file(f'../output/{path}')

if __name__ == '__main__':
    app.run(debug=True)
```

#### 3.2.4 Configuration (config.py)
```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-for-development-only')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
    TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'template')
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

## 4. Python Script for Site Generation
- **Data Loading**: Read business details, services, keywords, and areas served from a structured data file (e.g., `business_data.json`).
- **AI Content Generation**:
  - The JSON schema files (e.g., `index.json`, `location.json`) will be provided to the generative AI model (e.g., Gemini 2.0 Flash).
  - The AI will generate dynamic content based on the provided schema, business details, and keywords, returning the content in the specified JSON format.
  - This AI-generated JSON content will then be used to populate placeholders in the HTML templates to generate the final output pages.
  - **Jinja2 Template Processing**: The script will use Jinja2 to render templates with the AI-generated content:
    ```python
    from jinja2 import Environment, FileSystemLoader
    
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader('template/template-a'))
    
    # Load template
    template = env.get_template('index.html')
    
    # Render template with AI-generated content
    rendered_html = template.render(ai_generated_content)
    
    # Save to output file
    with open('output/1/index.html', 'w') as f:
        f.write(rendered_html)
    ```
  - Use the provided API keys for authentication.
  - Example `curl` command for AI integration:
    ```bash
    curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent" \
      -H 'Content-Type: application/json' \
      -H 'X-goog-api-key: AIzaSyBQeZrkmC40-gXZjPTJbMzyObOsqNpsk1I' \
      -X POST \
      -d '{
        "contents": [
          {
            "parts": [
              {
                "text": "Explain how AI works in a few words"
              }
            ]
          }
        ]
      }'
    ```
  - Provided API Keys:
    - `AIzaSyAMCZti3Ndirh2_O_fe42z03ocerkXLlV0`
    - `AIzaSyCyma9-wQb6BCvzzONNtArKAmiwW_E0HNQ`
    - `AIzaSyAREOxhnBXNOe70JMtrfiCVTMk9CztnJvg`
    - `AIzaSyBQeZrkmC40-gXZjPTJbMzyObOsqNpsk1I`
- **Homepage Generation**:
  - Load `homepage.html` template.
  - Populate the template with data from `business_data.json` and AI-generated content.
  - Save the generated HTML as `index.html` in a versioned output directory (e.g., `output/1/index.html`, `output/2/index.html`).
- **Location Page Generation**:
  - Iterate through the "areas served" data.
  - For each location, load `location_page.html` template.
  - Populate the template with business details, location-specific information, and AI-generated content.
  - Generate a unique filename for each location page (e.g., `[primary-keyword-in-service-area].html`).
  - Save the generated HTML files in the corresponding versioned output directory (e.g., `output/1/plumber-in-texas.html`).

## 5. Dashboard Implementation
- **Dashboard UI**:
  - Create Flask templates for the dashboard interface.
  - **Design**: Implement a beautiful, responsive, and minimal design without gradient colors.
  - **Autofill Button**: Add an "Autofill Form" button to automatically populate the multi-step form for testing purposes.
  - **Sidebar**: Implement a navigation sidebar with links to:
    - Home (multi-step form).
    - History (view previously generated websites).
    - Settings (add and test multiple Gemini API keys).
    - View Generated Site.
  - **Multi-step Form**: On the dashboard home page, create a multi-step form to collect:
    - **Step 1: Business Information**
      - Business Name *
      - Phone Number
      - Email Address
      - Street Address
      - City
      - State
      - ZIP Code
      - Website URL
    - **Step 2: Services and Keywords**
      - Primary Keyword/Service *
      - Additional Services (text box with accept comma separated value)
      - Service Areas (Cities) *(text box with accept comma separated value)
    - **Step 3: Choose Template**
      - Allow selection of a template (e.g., `homepage.html`, `location_page.html` - with future expansion for more templates)
    - **Step 4: Review and Generate**
      - Display an overview of how many pages will be generated.
      - Provide a "Generate" button to trigger site generation.
  - **Form Submission**: Implement JavaScript to handle form submission and send data to the Flask backend.

## 6. Data Management
- **Data Storage**:
  - Store business data in JSON format.
  - Implement functions to read/write business data.
  - Track version history of generated sites.
- **Module Implementation (`modules/data_manager.py`)**:
  ```python
  import json
  import os
  from datetime import datetime
  
  def save_business_data(data):
      """Save business data to JSON file"""
      data['timestamp'] = datetime.now().isoformat()
      
      with open('business_data.json', 'w') as f:
          json.dump(data, f, indent=2)
      
      return True
  
  def get_business_data():
      """Get business data from JSON file"""
      try:
          with open('business_data.json', 'r') as f:
              return json.load(f)
      except FileNotFoundError:
          return {}
  
  def get_history():
      """Get history of generated sites"""
      output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
      
      if not os.path.exists(output_dir):
          return []
      
      versions = []
      for item in os.listdir(output_dir):
          version_dir = os.path.join(output_dir, item)
          if os.path.isdir(version_dir):
              try:
                  version_num = int(item)
                  timestamp = os.path.getmtime(version_dir)
                  versions.append({
                      'version': version_num,
                      'timestamp': datetime.fromtimestamp(timestamp).isoformat(),
                      'path': f'/output/{version_num}/index.html'
                  })
              except ValueError:
                  continue
      
      return sorted(versions, key=lambda x: x['version'], reverse=True)
  ```

## 7. Deployment/Serving
- The entire application should be runnable with a single command:
  ```bash
  python app.py
  ```
- This will start the Flask development server, making the dashboard accessible at `http://localhost:5000/`.
- Generated sites will be available at `http://localhost:5000/output/{version}/index.html`.
- For production deployment:
  1. Set environment variables:
     ```bash
     export FLASK_ENV=production
     ```
  2. Use a production WSGI server:
     ```bash
     pip install gunicorn
     gunicorn app:app
     ```

## 8. Recommended Libraries
- **Flask**: Web framework for the dashboard and API endpoints
- **Jinja2**: Template engine (included with Flask)
- **Requests**: For making API calls to the Gemini AI service
- **jsonschema**: For validating AI-generated content against template schemas
- **python-dotenv**: For secure API key management
- **Flask-WTF**: For form handling and validation (optional)
- **Werkzeug**: WSGI utility library for Flask

## Next Steps
1. Set up the Flask application structure
2. Implement the dashboard templates
3. Create the site generation module
4. Implement the AI content generation module
5. Set up data management utilities
6. Test the complete workflow
7. Document deployment instructions



