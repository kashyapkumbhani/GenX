import json
import sys
sys.path.append('f:/local-seo')
from modules.ai_content import generate_ai_content

# Load business data
with open('f:/local-seo/business_data.json', 'r') as f:
    business_data = json.load(f)

# Generate content for Cedar Park location specifically
cedar_park_location = None
for area in business_data['service_areas']:
    if area['city'] == 'Cedar Park':
        cedar_park_location = area
        break

if cedar_park_location:
    print('Testing AI generation for Cedar Park:', cedar_park_location)
    
    # Load location schema
    with open('f:/local-seo/templates/Greenz/location.json', 'r') as f:
        schema = json.load(f)
    
    # Test just the testimonials_additional field
    from modules.ai_content import _generate_content_for_schema, get_random_api_key
    
    # Create a minimal schema for just testimonials_additional
    test_schema = {
        '$schema': 'http://json-schema.org/draft-07/schema#',
        'type': 'object',
        'properties': {
            'testimonials_additional': schema['properties']['testimonials_additional']
        },
        'required': ['testimonials_additional']
    }
    
    api_key = get_random_api_key()
    test_data = {**business_data, 'location': cedar_park_location}
    
    result = _generate_content_for_schema(test_schema, test_data, api_key)
    testimonials = result.get('testimonials_additional', [])
    print('Generated testimonials_additional:')
    print(json.dumps(testimonials, indent=2))
    print('Number of testimonials:', len(testimonials))
    for i, t in enumerate(testimonials):
        platform = t.get('platform', 'N/A')
        quote = t.get('quote', '')
        attribution = t.get('attribution', 'N/A')
        print(f'Testimonial {i+1}: platform={platform}, quote_length={len(quote)}, attribution={attribution}')
else:
    print('Cedar Park location not found')