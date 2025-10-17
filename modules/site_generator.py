import os
import json
import shutil
import logging
from jinja2 import Environment, FileSystemLoader
from flask import url_for
from modules.ai_content import generate_ai_content, discover_templates

def generate_site(business_data, template_name=None, ai_content=None):
    """
    Generate a site based on any template type using dynamic discovery
    
    Args:
        business_data (dict): Business information
        template_name (str): Name of the template to use (auto-detected if not provided)
        ai_content (dict, optional): Pre-generated AI content
        
    Returns:
        int: Version number of the generated site
    """
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('site_generator')
    
    logger.info(f"Starting dynamic site generation process for template: {template_name}")
    logger.info(f"Data provided: {json.dumps(business_data, indent=2)}")
    
    # Determine output version
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        version = 1
        logger.info(f"Created new output directory: {output_dir}")
    else:
        existing_versions = [int(d) for d in os.listdir(output_dir) 
                            if os.path.isdir(os.path.join(output_dir, d)) and d.isdigit()]
        version = max(existing_versions) + 1 if existing_versions else 1
        logger.info(f"Determined new version: {version}")
    
    # Create version directory
    version_dir = os.path.join(output_dir, str(version))
    os.makedirs(version_dir)
    logger.info(f"Created version directory: {version_dir}")
    
    # Save business data with this version for history tracking
    data_path = os.path.join(version_dir, 'business_data.json')
    with open(data_path, 'w') as f:
        json.dump(business_data, f, indent=2)
    logger.info(f"Saved data to: {data_path}")
    
    # Discover available templates
    template_base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    discovered_templates = discover_templates(template_base_dir)
    
    # If no template specified, use the first available template
    if template_name is None:
        if not discovered_templates:
            raise ValueError("No templates found in templates directory")
        template_name = list(discovered_templates.keys())[0]
        logger.info(f"No template specified, using first available: {template_name}")
    
    # Validate requested template exists
    if template_name not in discovered_templates:
        available_templates = list(discovered_templates.keys())
        logger.error(f"Template '{template_name}' not found! Available: {available_templates}")
        raise ValueError(f"Template '{template_name}' not found. Available: {available_templates}")
    
    template_schemas = discovered_templates[template_name]
    template_dir = os.path.join(template_base_dir, template_name)
    logger.info(f"Using template '{template_name}' with {len(template_schemas)} schema(s): {list(template_schemas.keys())}")
    
    # Set up Jinja2 environment for the specific template
    env = Environment(loader=FileSystemLoader(template_dir))
    logger.info(f"Set up Jinja2 environment with template directory: {template_dir}")
    
    # Add Flask's url_for function to the Jinja2 environment
    env.globals['url_for'] = lambda endpoint, **kwargs: f"/static/{kwargs.get('filename', '')}" if endpoint == 'static' else f"/{endpoint}"
    
    # Load CSS content to include directly in templates
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'css', 'style.css')
    with open(css_path, 'r') as css_file:
        css_content = css_file.read()
    env.globals['css_content'] = css_content
    logger.info(f"Loaded CSS content from: {css_path}")
    
    # Generate AI content if not provided
    if ai_content is None:
        api_key = os.getenv('GEMINI_API_KEY_1')
        logger.info("No AI content provided, generating new content")
        ai_content = generate_ai_content(business_data, template_name, api_key)
        logger.info("AI content generated successfully")
    else:
        logger.info("Using pre-generated AI content")
    
    # Process each schema in the template dynamically
    for schema_name, schema_info in template_schemas.items():
        logger.info(f"Processing schema: {schema_name}")
        
        # Handle location-based schemas (generate multiple pages)
        if schema_name == 'location' and 'service_areas' in business_data:
            logger.info(f"Generating {len(business_data['service_areas'])} location-based pages")
            _generate_location_pages(env, business_data, ai_content, version_dir, template_schemas, logger)
        else:
            # Handle regular schemas (generate single page)
            logger.info(f"Generating single page for schema: {schema_name}")
            _generate_single_page(env, schema_name, schema_info, business_data, ai_content, version_dir, template_schemas, logger)
    
    # Copy static assets if needed
    # TODO: Implement static asset copying
    
    logger.info(f"Site generation completed successfully. Version: {version}")
    return version
def _generate_single_page(env, schema_name, schema_info, business_data, ai_content, version_dir, template_schemas, logger):
    """
    Generate a single page from a schema (like index.json, services.json, about.json)
    
    Args:
        env: Jinja2 environment
        schema_name (str): Name of the schema (e.g., 'index', 'services')
        schema_info (dict): Schema information including HTML template path
        business_data (dict): Business information
        ai_content (dict): Generated AI content
        version_dir (str): Output directory path
        logger: Logger instance
    """
    try:
        # Load the HTML template
        template_filename = os.path.basename(schema_info['html_file'])
        template = env.get_template(template_filename)
        
        # Prepare content data
        page_content = {**business_data}
        
        # Add AI-generated content for this schema
        schema_ai_content = ai_content.get(schema_name, {})
        if schema_ai_content:
            page_content.update(schema_ai_content)
            logger.info(f"Added AI content for {schema_name}: {len(schema_ai_content)} fields")
        else:
            logger.warning(f"No AI content found for {schema_name}, using defaults")
        
        # Add content variable for template access
        page_content['content'] = schema_ai_content
        
        # Clean up AI content using extraction logic
        if page_content['content']:
            for key, value in page_content['content'].items():
                page_content['content'][key] = _extract_content_value(value)
        
        # Add default fallbacks based on schema requirements
        _add_default_content(page_content, schema_name, business_data, template_schemas, logger)
        
        # Determine output filename
        if schema_name == 'index':
            output_filename = 'index.html'
        else:
            output_filename = f'{schema_name}.html'
        
        # Render template
        rendered_content = template.render(page_content)
        
        # Write to file
        output_path = os.path.join(version_dir, output_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered_content)
        
        logger.info(f"Generated {output_filename} from {schema_name} schema")
        
    except Exception as e:
        logger.error(f"Failed to generate page for schema {schema_name}: {e}")
        raise

# Removed hardcoded coordinates - now using AI-generated geo_position from template schemas

def _generate_location_pages(env, business_data, ai_content, version_dir, template_schemas, logger):
    """
    Generate multiple location-based pages from location schema
    
    Args:
        env: Jinja2 environment
        schema_name (str): Name of the schema ('location')
        business_data (dict): Business information
        ai_content (dict): Generated AI content
        version_dir (str): Output directory path
        logger: Logger instance
    """
    try:
        # Load the location template dynamically from schema info
        location_schema_info = template_schemas.get('location', {})
        location_template_file = os.path.basename(location_schema_info.get('html_file', 'location.html'))
        location_template = env.get_template(location_template_file)
        
        for area in business_data['service_areas']:
            logger.info(f"Generating page for location: {area.get('city', '')}, {area.get('state', '')}")
            
            # Create location-specific content with proper structure for Jinja2 templates
            location_data = {
                # Primary keyword for SEO
                'primary_keyword': business_data.get('primary_keyword', ''),
                # Location information - coordinates now come from AI-generated content
                'location': {
                    'city': area.get('city')
                },
                # Include all original business data for backward compatibility
                **business_data,
                # Core business data (override any conflicting keys from business_data)
                'business': {
                    'name': business_data.get('name', business_data.get('business', {}).get('name', '')),
                    'phone': business_data.get('phone', business_data.get('business', {}).get('phone', '')),
                    'email': business_data.get('email', business_data.get('business', {}).get('email', '')),
                    'address': business_data.get('address', business_data.get('business', {}).get('address', '')),
                    'category': business_data.get('category', business_data.get('business', {}).get('category', '')),
                    'website': business_data.get('website', business_data.get('business', {}).get('website', '')),
                    'city': business_data.get('city', business_data.get('business', {}).get('city', '')),
                    'state': business_data.get('state', business_data.get('business', {}).get('state', '')),
                    'service_areas': business_data.get('service_areas', []),
                    'primary_keyword': business_data.get('primary_keyword', '')
                }
            }
            
            # Add AI content for this location if available
            # Match the key format used in AI content generation
            area_key = area.get('city')
            location_ai_content = ai_content.get('location', {}).get(area_key, {})
            if location_ai_content:
                # Clean up AI content and add to location_data
                cleaned_ai_content = {}
                for key, value in location_ai_content.items():
                    cleaned_value = _extract_content_value(value)
                    cleaned_ai_content[key] = cleaned_value
                    
                    # Debug output for stats specifically
                    if key == 'stats':
                        logger.info(f"Processing stats for {area_key}:")
                        logger.info(f"  Raw value type: {type(value)}")
                        logger.info(f"  Raw value: {str(value)[:200]}...")
                        logger.info(f"  Cleaned value type: {type(cleaned_value)}")
                        logger.info(f"  Cleaned value: {str(cleaned_value)[:200]}...")
                        
                location_data['content'] = cleaned_ai_content
                logger.info(f"Found AI content for location: {area_key}")
            else:
                logger.warning(f"No AI content found for location: {area_key}, using defaults")
            
            # Add default content for location pages
            _add_default_location_content(location_data, area, business_data, template_schemas, logger)
            
            # Generate filename based on primary keyword and location
            primary_keyword = business_data.get('primary_keyword', '').lower().replace(' ', '-')
            location_name = area.get('city', '').lower().replace(' ', '-')
            filename = f"{primary_keyword}-in-{location_name}.html"
            
            # Render template
            rendered_location = location_template.render(location_data)
            
            # Write to file
            output_path = os.path.join(version_dir, filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(rendered_location)
            
            logger.info(f"Generated location page: {filename}")
            
    except Exception as e:
        logger.error(f"Failed to generate location pages: {e}")
        raise

def _extract_content_value(content):
    """Extract the actual content value from AI response"""
    if isinstance(content, dict):
        # If it's a single-key dict, return the value
        if len(content) == 1:
            return list(content.values())[0]
        # If it has multiple keys, it might be the expected structure
        return content
    elif isinstance(content, str):
        # Try to parse if it looks like a JSON string
        try:
            if content.strip().startswith('{') and content.strip().endswith('}'):
                parsed = json.loads(content)
                if isinstance(parsed, dict) and len(parsed) == 1:
                    return list(parsed.values())[0]
                return parsed
            # Handle Python-style dictionary strings (common AI output issue)
            elif content.strip().startswith('[') and content.strip().endswith(']'):
                # Try to convert Python dict syntax to JSON
                try:
                    # Replace single quotes with double quotes for JSON compatibility
                    json_str = content.replace("'", '"')
                    parsed = json.loads(json_str)
                    return parsed
                except json.JSONDecodeError:
                    pass
        except json.JSONDecodeError:
            pass
        return content
    elif isinstance(content, list):
        # Handle arrays directly (like stats arrays)
        return content
    return content

def _add_default_content(page_content, schema_name, business_data, template_schemas, logger):
    """Add default content based on schema requirements"""
    if not page_content.get('content'):
        page_content['content'] = {}
    
    # Get the schema for this page type to understand what fields are required
    schema_info = template_schemas.get(schema_name, {})
    schema = schema_info.get('schema', {})
    required_fields = schema.get('required', [])
    schema_properties = schema.get('properties', {})
    
    # Generate default content for each required field based on its schema definition
    for field_name in required_fields:
        if field_name not in page_content['content']:
            field_schema = schema_properties.get(field_name, {})
            default_value = _generate_default_field_value(field_name, field_schema, 
                                                        business_data, schema_name)
            if default_value is not None:
                page_content['content'][field_name] = default_value
    
    logger.info(f"Added default content for {schema_name} schema based on schema requirements")

def _add_default_location_content(location_data, area, business_data, template_schemas, logger):
    """Add default content for location pages based on schema requirements"""
    if not location_data.get('content'):
        location_data['content'] = {}
    
    # Get the location schema to understand what fields are required
    location_schema = template_schemas.get('location', {}).get('schema', {})
    required_fields = location_schema.get('required', [])
    schema_properties = location_schema.get('properties', {})
    
    # Generate default content for each required field based on its schema definition
    for field_name in required_fields:
        if field_name not in location_data['content']:
            field_schema = schema_properties.get(field_name, {})
            default_value = _generate_default_field_value(field_name, field_schema, business_data, 'location', area)
            if default_value is not None:
                location_data['content'][field_name] = default_value
    
    # Log with location info if available
    city = area.get('city', '') if area else ''
    state = area.get('state', '') if area else ''
    location_info = f"{city}, {state}" if city and state else city if city else "location"
    logger.info(f"Added default location content for {location_info} based on schema requirements")

def _generate_default_field_value(field_name, field_schema, business_data, schema_name, area=None):
    """Generate minimal default content based purely on field type and schema information"""
    
    # Get field type from schema
    field_type = field_schema.get('type', 'string')
    
    # Use examples from schema if available and process Jinja2 variables
    examples = field_schema.get('examples', [])
    if examples:
        example_value = examples[0]
        # If the example contains Jinja2 variables, process them
        if isinstance(example_value, str) and '{{' in example_value and '}}' in example_value:
            try:
                # Create a Jinja2 template from the example
                from jinja2 import Template
                template = Template(example_value)
                
                # Create context data for rendering
                context = {
                    'business': business_data.get('business', business_data),
                    'primary_keyword': business_data.get('primary_keyword', ''),
                    'location': area if area else {'city': '', 'state': ''},
                    **business_data
                }
                
                # Render the template with context
                rendered_value = template.render(context)
                return rendered_value
            except Exception as e:
                # If template rendering fails, return the raw example
                return example_value
        return example_value
    
    # Use default from schema if available
    if 'default' in field_schema:
        return field_schema['default']
    
    # Basic type-based defaults
    if field_type == 'array':
        return []
    elif field_type == 'object':
        return {}
    elif field_type == 'boolean':
        return True
    elif field_type == 'number' or field_type == 'integer':
        return 0
    else:
        # For strings, return the field name as a placeholder
        return field_name.replace('_', ' ').title()