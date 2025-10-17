import os
import json
import requests
import random
import time
import glob

def get_random_api_key():
    """
    Get a random API key from available keys in environment
    
    Returns:
        str: Random API key or None if no keys available
    """
    print("🔑 [AI Content] Checking for available API keys...")
    api_keys = []
    for i in range(1, 5):  # Check for GEMINI_API_KEY_1 through GEMINI_API_KEY_4
        key = os.getenv(f'GEMINI_API_KEY_{i}')
        if key:
            api_keys.append(key)
            print(f"   ✓ Found GEMINI_API_KEY_{i}")
        else:
            print(f"   ✗ GEMINI_API_KEY_{i} not found")
    
    if not api_keys:
        print("❌ [AI Content] WARNING: No Gemini API keys found in environment variables")
        print("   📝 [AI Content] AI content generation will be skipped")
        return None
    
    selected_key = random.choice(api_keys)
    print(f"🎲 [AI Content] Selected random API key (ending in ...{selected_key[-8:]})")
    return selected_key

def get_all_api_keys():
    """
    Get all available API keys from environment
    
    Returns:
        list: List of all available API keys
    """
    api_keys = []
    for i in range(1, 5):  # Check for GEMINI_API_KEY_1 through GEMINI_API_KEY_4
        key = os.getenv(f'GEMINI_API_KEY_{i}')
        if key:
            api_keys.append(key)
    return api_keys

def get_api_key_for_location(location_index, total_locations):
    """
    Get API key for specific location using rotation logic
    
    Args:
        location_index (int): Index of current location (0-based)
        total_locations (int): Total number of locations
        
    Returns:
        str: API key for this location or None if no keys available
    """
    api_keys = get_all_api_keys()
    if not api_keys:
        return None
    
    # Use modulo to rotate through available API keys
    key_index = location_index % len(api_keys)
    selected_key = api_keys[key_index]
    
    print(f"🔄 [API Rotation] Location {location_index + 1}/{total_locations} -> API Key {key_index + 1} (ending in ...{selected_key[-8:]})")
    return selected_key

def generate_location_seed(location_data, business_data=None):
    """
    Generate a unique seed for location-based content generation
    
    Args:
        location_data (dict): Location information containing city, state, etc.
        business_data (dict, optional): Business information for additional uniqueness
        
    Returns:
        int: Unique seed for this location
    """
    import hashlib
    
    # Create a unique string from location data
    seed_components = []
    
    # Add location-specific data
    if location_data:
        seed_components.append(location_data.get('city', ''))
        seed_components.append(location_data.get('state', ''))
        seed_components.append(location_data.get('zip_code', ''))
        seed_components.append(location_data.get('area_code', ''))
    
    # Add business data for additional uniqueness
    if business_data:
        seed_components.append(business_data.get('business_name', ''))
        seed_components.append(business_data.get('industry', ''))
    
    # Create hash from combined components
    seed_string = '|'.join(str(component) for component in seed_components if component)
    
    # Generate consistent hash-based seed
    hash_object = hashlib.md5(seed_string.encode())
    # Use first 8 hex chars but ensure it fits in 32-bit signed integer range
    seed = int(hash_object.hexdigest()[:8], 16) % 2147483647  # Modulo to stay within 32-bit signed int range
    
    print(f"🌱 [Seed Generation] Location: {location_data.get('city', 'Unknown')} -> Seed: {seed}")
    return seed

def get_seed_from_env_or_location(location_data=None, business_data=None):
    """
    Get seed from environment variable or generate from location data
    
    Args:
        location_data (dict, optional): Location information
        business_data (dict, optional): Business information
        
    Returns:
        int or None: Seed value or None if no seed should be used
    """
    # Check for environment variable first
    env_seed = os.getenv('AI_CONTENT_SEED')
    if env_seed:
        try:
            seed = int(env_seed)
            print(f"🌱 [Seed] Using environment seed: {seed}")
            return seed
        except ValueError:
            print(f"⚠️ [Seed] Invalid environment seed value: {env_seed}")
    
    # Generate location-based seed if location data is available
    if location_data:
        return generate_location_seed(location_data, business_data)
    
    # No seed if no location data and no env variable
    return None

def discover_templates(template_base_dir):
    """
    Dynamically discover all available templates and their schemas
    
    Args:
        template_base_dir (str): Base templates directory path
        
    Returns:
        dict: Dictionary of discovered templates with their schemas and HTML files
    """
    print(f"\n🔍 [Template Discovery] Scanning template directory: {template_base_dir}")
    
    discovered_templates = {}
    
    # Find all template directories
    if not os.path.exists(template_base_dir):
        print(f"❌ [Template Discovery] Template directory not found: {template_base_dir}")
        return discovered_templates
    
    for template_name in os.listdir(template_base_dir):
        template_dir = os.path.join(template_base_dir, template_name)
        
        if not os.path.isdir(template_dir):
            continue
            
        print(f"\n📁 [Template Discovery] Processing template: {template_name}")
        
        # Find all JSON schema files in this template directory
        json_files = glob.glob(os.path.join(template_dir, '*.json'))
        
        template_schemas = {}
        
        for json_file in json_files:
            schema_name = os.path.splitext(os.path.basename(json_file))[0]
            html_file = os.path.join(template_dir, f"{schema_name}.html")
            
            # Check if corresponding HTML template exists
            if os.path.exists(html_file):
                try:
                    with open(json_file, 'r') as f:
                        schema = json.load(f)
                    
                    template_schemas[schema_name] = {
                        'schema': schema,
                        'schema_file': json_file,
                        'html_file': html_file
                    }
                    print(f"   ✓ Found template pair: {schema_name}.json + {schema_name}.html")
                    
                except Exception as e:
                    print(f"   ❌ Failed to load schema {json_file}: {e}")
            else:
                print(f"   ⚠️  Schema {schema_name}.json found but no matching {schema_name}.html")
        
        if template_schemas:
            discovered_templates[template_name] = template_schemas
            print(f"   🎯 Template '{template_name}' registered with {len(template_schemas)} schema(s)")
        else:
            print(f"   ⚠️  No valid template pairs found in '{template_name}'")
    
    print(f"\n🏆 [Template Discovery] Discovery complete!")
    print(f"   📊 Total templates discovered: {len(discovered_templates)}")
    for template_name, schemas in discovered_templates.items():
        print(f"   📁 {template_name}: {list(schemas.keys())}")
    
    return discovered_templates

def generate_ai_content(business_data, template_name=None, api_key=None, progress_callback=None):
    """
    Generate AI content for any template type using dynamic discovery
    
    Args:
        business_data (dict): Business information
        template_name (str): Name of the template to use (auto-detected if not provided)
        api_key (str, optional): Gemini API key. If not provided, API keys will be rotated for each page
        
    Returns:
        dict: Generated content for all discovered template schemas
    """
    print(f"\n🚀 [AI Content] Starting dynamic AI content generation...")
    print(f"📊 [AI Content] Business: {business_data.get('name', business_data.get('business', {}).get('name', 'Unknown'))}")
    print(f"🎯 [AI Content] Target template: {template_name}")
    print("🔄 [AI Content] Using API key rotation for each page to generate unique content")
    
    # Check if API keys are available
    test_key = get_random_api_key()
    if not test_key:
        print("⚠️  [AI Content] No API keys available - returning empty content")
        return {}
    
    # Discover all available templates
    template_base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    discovered_templates = discover_templates(template_base_dir)
    
    # Check if requested template exists
    if template_name not in discovered_templates:
        available_templates = list(discovered_templates.keys())
        print(f"❌ [AI Content] Template '{template_name}' not found!")
        print(f"   Available templates: {available_templates}")
        raise ValueError(f"Template '{template_name}' not found. Available: {available_templates}")
    
    template_schemas = discovered_templates[template_name]
    print(f"✅ [AI Content] Using template '{template_name}' with {len(template_schemas)} schema(s)")
    
    # Generate content for each schema in the template
    generated_content = {}
    total_schemas = len(template_schemas)
    
    # Process each schema in the template
    for schema_index, (schema_name, schema_info) in enumerate(template_schemas.items(), 1):
        schema = schema_info['schema']
        
        print(f"\n📄 [AI Content] Processing schema: {schema_name} ({schema_index}/{total_schemas})")
        
        # Update progress if callback is provided
        if progress_callback:
            base_progress = int((schema_index - 1) / total_schemas * 100)
            progress_callback(base_progress, f"Processing {schema_name}...")
        
        # Handle location-based schemas (like location.json)
        if schema_name == 'location' and 'service_areas' in business_data:
            print(f"   🌍 [Location Schema] Processing location-based content for {len(business_data['service_areas'])} areas")
            location_content = {}
            total_locations = len(business_data['service_areas'])
            
            for i, area in enumerate(business_data['service_areas'], 1):
                city = area.get('city')
                
                # Create display name based on available data
                location_display = city
                print(f"\n   🏙️  LOCATION {i}/{total_locations}: Starting {city}")
                
                # Update progress for this location
                if progress_callback:
                    location_progress = base_progress + int((i / total_locations) * (100 / total_schemas))
                    progress_callback(location_progress, f"Generating content for {city}...")
                
                # Get API key for this specific location using rotation
                location_api_key = api_key if api_key else get_api_key_for_location(i - 1, total_locations)
                if not location_api_key:
                    print(f"      ⚠️  No API key available for {city} - skipping AI generation")
                    continue
                    
                print(f"      🔑 Using rotated API key for {city} (ending in ...{location_api_key[-8:]})")
                
                # Generate content for this specific location
                area_content = _generate_content_for_schema(
                    schema, 
                    {**business_data, 'location': area},
                    location_api_key
                )
                
                # Store with the expected key format
                area_key = location_display
                location_content[area_key] = area_content
                
                print(f"      ✅ {city} complete! Generated {len(area_content)} sections")
                
                # Add delay between locations (except for the last one)
                if i < len(business_data['service_areas']):
                    print(f"      ⏳ Waiting 3 seconds before next location...")
                    time.sleep(3)
            
            generated_content[schema_name] = location_content
            
        else:
            # Handle regular schemas (like index.json, services.json, about.json, etc.)
            print(f"   📝 [Regular Schema] Generating content for {schema_name}")
            
            # Update progress for regular schema
            if progress_callback:
                schema_progress = base_progress + int(50 / total_schemas)
                progress_callback(schema_progress, f"Generating {schema_name} content...")
            
            schema_api_key = api_key if api_key else get_random_api_key()
            if not schema_api_key:
                print(f"   ⚠️  No API key available for {schema_name} - skipping AI generation")
                continue
                
            print(f"   🔑 Using API key for {schema_name} (ending in ...{schema_api_key[-8:]})")
            
            # For index page, modify business data to exclude service areas from AI context
            if schema_name == 'index':
                # Create a copy of business data without service areas for index page generation
                index_business_data = business_data.copy()
                # Remove service areas from the AI context for index page
                if 'service_areas' in index_business_data:
                    del index_business_data['service_areas']
                print(f"   🏠 [Index Schema] Removed service areas from AI context for main city focus")
                schema_content = _generate_content_for_schema(schema, index_business_data, schema_api_key)
            else:
                schema_content = _generate_content_for_schema(schema, business_data, schema_api_key)
            
            generated_content[schema_name] = schema_content
            
            print(f"   ✅ {schema_name} complete! Generated {len(schema_content)} sections")
            
            # Small delay between schemas
            if len(template_schemas) > 1:
                print("   ⏳ Waiting 2 seconds before next schema...")
                time.sleep(2)
    
    # Final progress update
    if progress_callback:
        progress_callback(100, "AI content generation complete!")
    
    print(f"\n🎉 [AI Content] ALL CONTENT GENERATION COMPLETE!")
    print(f"   📊 Schemas processed: {list(generated_content.keys())}")
    total_sections = sum(len(content) if isinstance(content, dict) else 1 for content in generated_content.values())
    print(f"   📄 Total sections generated: {total_sections}")
    print(f"   🏆 Template '{template_name}' fully processed!")
    
    return generated_content

def _generate_content_for_schema(schema, business_data, api_key):
    """
    Generate content for a complete schema in a single API call
    
    Args:
        schema (dict): JSON schema defining content structure
        business_data (dict): Business information
        api_key (str): Gemini API key
        
    Returns:
        dict: Generated content matching schema
    """
    print("      🔧 [Schema] Processing complete schema for single API call...")
    
    # Skip schema metadata and focus on properties
    if "$schema" in schema and "properties" in schema:
        properties = schema["properties"]
        required_fields = schema.get("required", [])
        
        print(f"      📝 [Schema] Found {len(properties)} total properties, {len(required_fields)} required")
        print(f"      🚀 [Schema] Making SINGLE API call for all {len(required_fields)} fields")
        
        # Build comprehensive prompt for all required fields
        # Map business data structure correctly
        business_info = business_data.get('business', {})
        business_name = business_info.get('name', business_data.get('business_name', 'N/A'))
        primary_service = business_data.get('primary_keyword', business_data.get('primary_service', 'N/A'))
        phone = business_info.get('phone', business_data.get('phone', 'N/A'))
        email = business_info.get('email', business_data.get('email', 'N/A'))
        
        full_prompt = f"""Generate content for a business website based on the following business information:

Business Name: {business_name}
Primary Service: {primary_service}
Phone: {phone}
Email: {email}
"""
        
        # Add location-specific info if available
        if 'location' in business_data:
            location = business_data['location']
            city = location.get('city', 'N/A')
            state = location.get('state')
            
            if state:
                location_display = f"{city}, {state}"
                service_area_display = f"{city}, {state} and surrounding areas"
            else:
                location_display = city
                service_area_display = f"{city} and surrounding areas"
                
            full_prompt += f"""
Location: {location_display}
Service Area: {service_area_display}
"""
        else:
            # Use business data structure for location info
            city = business_info.get('city', 'N/A')
            state = business_info.get('state')
            
            if state:
                location_display = f"{city}, {state}"
                service_area_display = f"{city}, {state} and surrounding areas"
            else:
                location_display = city
                service_area_display = f"{city} and surrounding areas"
                
            full_prompt += f"""
Location: {location_display}
Service Area: {service_area_display}
"""
        
        # Add service areas if available
        if 'service_areas' in business_data and isinstance(business_data['service_areas'], list):
            areas = []
            for area in business_data['service_areas']:
                city = area.get('city', 'Unknown')
                state = area.get('state')
                if state:
                    areas.append(f"{city}, {state}")
                else:
                    areas.append(city)
            full_prompt += f"Service Areas: {', '.join(areas)}\n"
        
        # Add additional services if available
        if 'additional_services' in business_data and isinstance(business_data['additional_services'], list):
            # Handle both string and object formats for additional services
            services = []
            for service in business_data['additional_services']:
                if isinstance(service, dict):
                    services.append(service.get('name', 'Unknown'))
                else:
                    services.append(str(service))
            full_prompt += f"Additional Services: {', '.join(services)}\n"
        
        full_prompt += f"""
Please generate content for the following fields and return ONLY a valid JSON object with these exact keys:

"""
        
        # Add field descriptions to the prompt
        for field_key in required_fields:
            if field_key in properties:
                field_schema = properties[field_key]
                description = field_schema.get('description', '')
                field_type = field_schema.get('type', 'string')
                
                # Replace placeholders in description with actual business data
                for key, value in business_data.items():
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            description = description.replace(f"{{{key}.{subkey}}}", str(subvalue))
                    else:
                        description = description.replace(f"{{{key}}}", str(value))
                
                full_prompt += f"- {field_key} ({field_type}): {description}\n"
                
                # For array fields, include detailed structure and examples
                if field_type == "array" and "items" in field_schema:
                    items_schema = field_schema["items"]
                    if "properties" in items_schema:
                        full_prompt += f"  Structure for each {field_key} item:\n"
                        for prop_key, prop_schema in items_schema["properties"].items():
                            prop_desc = prop_schema.get('description', '')
                            prop_ai_prompt = prop_schema.get('ai_prompt', '')
                            prop_examples = prop_schema.get('examples', [])
                            
                            # Replace placeholders in ai_prompt
                            for key, value in business_data.items():
                                if isinstance(value, dict):
                                    for subkey, subvalue in value.items():
                                        prop_ai_prompt = prop_ai_prompt.replace(f"{{{key}.{subkey}}}", str(subvalue))
                                else:
                                    prop_ai_prompt = prop_ai_prompt.replace(f"{{{key}}}", str(value))
                            
                            full_prompt += f"    - {prop_key}: {prop_desc}\n"
                            if prop_ai_prompt:
                                full_prompt += f"      AI Guidance: {prop_ai_prompt}\n"
                            if prop_examples:
                                full_prompt += f"      Examples: {', '.join(prop_examples)}\n"
                    
                    # Include overall examples for the array
                    if "examples" in field_schema:
                        full_prompt += f"  Complete {field_key} examples:\n"
                        for example in field_schema["examples"][:2]:  # Show first 2 examples
                            full_prompt += f"    {json.dumps(example)}\n"
        
        full_prompt += f"""
Return ONLY a valid JSON object with the exact field names listed above. Do not include any explanatory text before or after the JSON.
"""
        
        print(f"      📏 [Schema] Full prompt prepared (length: {len(full_prompt)})")
        
        # Make single API call for entire schema
        generated_content = _call_gemini_api_full_schema(full_prompt, schema, api_key, business_data)
        
        print(f"      🎉 [Schema] Single API call complete - generated {len(generated_content)} sections")
        return generated_content
    else:
        print("      ⚠️  [Schema] Invalid schema format - missing $schema or properties")
        return {}

def _call_gemini_api_full_schema(prompt, schema, api_key, business_data=None, max_retries=3):
    """
    Call Gemini API for full schema content generation
    
    Args:
        prompt (str): The complete prompt for all schema fields
        schema (dict): The complete JSON schema
        api_key (str): Gemini API key
        business_data (dict, optional): Business data for seed generation
        max_retries (int): Maximum number of retries
        
    Returns:
        dict: Generated content for all schema fields
    """
    print(f"         🌟 [API] Starting Gemini API call for full schema")
    print(f"         🔑 [API] Using API key ending in ...{api_key[-8:]}")
    print(f"         📊 [API] Payload size: {len(prompt)} characters")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    # Generate seed for this content generation
    location_data = business_data.get('location') if business_data else None
    seed = get_seed_from_env_or_location(location_data, business_data)
    
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
    
    # Add seed to generation config if available
    if seed is not None:
        payload["generationConfig"] = {
            "seed": seed
        }
        print(f"         🌱 [API] Added seed to payload: {seed}")
    else:
        print(f"         🌱 [API] No seed specified - using default randomization")
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    for attempt in range(max_retries):
        try:
            print(f"         🚀 [API] Making API call (attempt {attempt + 1}/{max_retries})")
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            print(f"         📡 [API] Response status: {response.status_code}")
            
            if response.status_code == 429:
                print(f"         ⚠️  [API] Rate limit hit! Waiting before retry...")
                # Wait longer for rate limit instead of switching keys to maintain rotation
                wait_time = 5 + (attempt * 2)  # Progressive backoff: 5, 7, 9 seconds
                print(f"         ⏳ [API] Waiting {wait_time} seconds for rate limit...")
                time.sleep(wait_time)
                continue
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"         ✅ [API] Successful response received")
                
                # Extract the generated text
                if 'candidates' in response_data and len(response_data['candidates']) > 0:
                    candidate = response_data['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        generated_text = candidate['content']['parts'][0]['text']
                        print(f"         📝 [API] Generated text length: {len(generated_text)} characters")
                        
                        # Parse JSON response
                        try:
                            print(f"         🔍 [JSON] Attempting to parse JSON response...")
                            # Clean the response - remove any markdown formatting
                            cleaned_text = generated_text.strip()
                            if cleaned_text.startswith('```json'):
                                cleaned_text = cleaned_text[7:]
                            if cleaned_text.endswith('```'):
                                cleaned_text = cleaned_text[:-3]
                            cleaned_text = cleaned_text.strip()
                            
                            parsed_content = json.loads(cleaned_text)
                            print(f"         ✅ [JSON] Successfully parsed JSON with {len(parsed_content)} fields")
                            
                            # Validate that we got all required fields
                            required_fields = schema.get("required", [])
                            missing_fields = [field for field in required_fields if field not in parsed_content]
                            
                            if missing_fields:
                                print(f"         ⚠️  [JSON] Missing required fields: {missing_fields}")
                                # Fill in missing fields with empty values
                                for field in missing_fields:
                                    if field in schema.get("properties", {}):
                                        field_type = schema["properties"][field].get("type", "string")
                                        if field_type == "array":
                                            parsed_content[field] = []
                                        else:
                                            parsed_content[field] = ""
                                print(f"         🔧 [JSON] Added default values for missing fields")
                            
                            return parsed_content
                            
                        except json.JSONDecodeError as e:
                            print(f"         ❌ [JSON] Failed to parse JSON: {str(e)}")
                            print(f"         📄 [JSON] Raw response: {generated_text[:200]}...")
                            
                            # Fallback: create empty structure based on schema
                            fallback_content = {}
                            required_fields = schema.get("required", [])
                            for field in required_fields:
                                if field in schema.get("properties", {}):
                                    field_type = schema["properties"][field].get("type", "string")
                                    if field_type == "array":
                                        fallback_content[field] = []
                                    else:
                                        fallback_content[field] = f"Generated content for {field}"
                            
                            print(f"         🔧 [JSON] Using fallback structure with {len(fallback_content)} fields")
                            return fallback_content
                
                print(f"         ❌ [API] Invalid response structure")
                return {}
            else:
                print(f"         ❌ [API] HTTP error {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"         ❌ [API] Request failed (attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"         ⏳ [API] Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
    
    print(f"         💥 [API] All retry attempts failed")
    
    # Return empty structure based on schema as final fallback
    fallback_content = {}
    required_fields = schema.get("required", [])
    for field in required_fields:
        if field in schema.get("properties", {}):
            field_type = schema["properties"][field].get("type", "string")
            if field_type == "array":
                fallback_content[field] = []
            else:
                fallback_content[field] = f"Content for {field}"
    
    return fallback_content
    """
    Call Gemini API to generate content with retry logic
    
    Args:
        prompt (str): Prompt for content generation
        schema (dict): Schema defining expected response structure
        api_key (str): Gemini API key
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        str: Generated content
    """
    print(f"               🌐 [API] Calling Gemini API (key ending in ...{api_key[-8:]})")
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': api_key
    }
    
    # Include examples if available
    examples = schema.get('examples', [])
    example_text = ""
    if examples:
        example_text = "Here are examples of the expected format:\n" + json.dumps(examples[0], indent=2)
        print(f"               📋 [API] Using example from schema")
    else:
        print(f"               ⚠️  [API] No examples found in schema")
    
    # Build the request payload
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"{prompt}\n\nPlease generate content in the following JSON format. Include all required fields.\n{example_text}"
                    }
                ]
            }
        ]
    }
    
    print(f"               📦 [API] Payload size: {len(json.dumps(payload))} characters")
    
    # For development/testing, you can uncomment the lines below to use mock data
    # if os.getenv('FLASK_ENV') != 'production':
    #     if examples:
    #         return examples[0]
    #     else:
    #         # Return minimal mock data
    #         return "Mock content for testing purposes"

    for attempt in range(max_retries):
        try:
            print(f"               🔄 [API] Attempt {attempt + 1}/{max_retries}")
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            print(f"               ✅ [API] Request successful (status: {response.status_code})")
            
            # Extract text from response
            response_data = response.json()
            content_text = response_data['candidates'][0]['content']['parts'][0]['text']
            
            print(f"               📄 [API] Raw response length: {len(content_text)} characters")
            
            # Try to parse as JSON if it looks like JSON
            try:
                # Clean up the response text (remove markdown code blocks if present)
                cleaned_text = content_text.strip()
                if cleaned_text.startswith('```json'):
                    cleaned_text = cleaned_text[7:]
                    print(f"               🧹 [API] Removed JSON markdown prefix")
                if cleaned_text.endswith('```'):
                    cleaned_text = cleaned_text[:-3]
                    print(f"               🧹 [API] Removed JSON markdown suffix")
                cleaned_text = cleaned_text.strip()
                
                print(f"               🔍 [API] Attempting to parse as JSON...")
                
                # Try to parse as JSON
                parsed_content = json.loads(cleaned_text)
                print(f"               ✅ [API] Successfully parsed JSON")
                
                # If it's a dictionary, we need to extract the actual content
                if isinstance(parsed_content, dict):
                    print(f"               📊 [API] Response is dictionary with {len(parsed_content)} keys")
                    # If it has a single key, return just the value
                    if len(parsed_content) == 1:
                        result = list(parsed_content.values())[0]
                        print(f"               🎯 [API] Extracted single value from dictionary")
                        return result
                    # If it matches the expected schema structure, return the whole dict
                    else:
                        print(f"               📋 [API] Returning full dictionary structure")
                        return parsed_content
                
                print(f"               📝 [API] Returning parsed content as-is")
                return parsed_content
            except json.JSONDecodeError as e:
                print(f"               ⚠️  [API] JSON parsing failed: {e}")
                print(f"               📝 [API] Returning raw text content")
                # If not valid JSON, return the text as is
                return content_text
                
        except requests.exceptions.HTTPError as e:
            print(f"               ❌ [API] HTTP Error: {e}")
            if e.response.status_code == 429:  # Too Many Requests
                if attempt < max_retries - 1:
                    # Immediately try with a different API key without waiting
                    print(f"               🔄 [API] Rate limit hit, switching to different API key immediately...")
                    api_key = get_random_api_key()
                    headers['X-goog-api-key'] = api_key
                    print(f"               🔄 [API] Switched to new API key for retry")
                    continue
                else:
                    print(f"               💥 [API] Max retries reached for rate limiting. Error: {e}")
            else:
                print(f"               💥 [API] HTTP Error: {e}")
                break
        except Exception as e:
            print(f"               💥 [API] Unexpected error: {e}")
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"               ⏳ [API] Retrying in {wait_time:.2f} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            break
    
    # Return example if available, otherwise empty string
    print(f"               🔄 [API] All attempts failed, falling back to example or empty string")
    if examples:
        print(f"               📋 [API] Using fallback example")
        return examples[0]
    print(f"               ❌ [API] No example available, returning empty string")
    return ""