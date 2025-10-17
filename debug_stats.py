#!/usr/bin/env python3
"""
Debug script to examine AI-generated content structure for stats data
"""

import json
import os
import sys
from modules.site_generator import _extract_content_value

def debug_stats_content():
    """Debug the stats content generation and processing"""
    
    print("🔍 [DEBUG] Starting stats content debugging...")
    
    # Check if there's any cached AI content
    output_dir = "f:/local-seo/output/1"
    
    # Look for any temporary or debug files
    for root, dirs, files in os.walk("f:/local-seo"):
        for file in files:
            if 'ai_content' in file.lower() or 'debug' in file.lower():
                print(f"   📄 Found potential debug file: {os.path.join(root, file)}")
    
    # Test the _extract_content_value function with different input types
    print("\n🧪 [DEBUG] Testing _extract_content_value function...")
    
    # Test case 1: Normal dict structure
    test_stats_1 = [
        {"value": "15+", "title": "Years Experience", "description": "Serving Blacktown residents"},
        {"value": "1000+", "title": "Jobs Completed", "description": "Successful projects in area"},
        {"value": "500+", "title": "Happy Customers", "description": "Satisfied Blacktown clients"}
    ]
    
    print(f"   Test 1 - Normal array: {_extract_content_value(test_stats_1)}")
    
    # Test case 2: Single-key dict (common AI response format)
    test_stats_2 = {
        "stats": [
            {"value": "15+", "title": "Years Experience", "description": "Serving Blacktown residents"},
            {"value": "1000+", "title": "Jobs Completed", "description": "Successful projects in area"}
        ]
    }
    
    print(f"   Test 2 - Single-key dict: {_extract_content_value(test_stats_2)}")
    
    # Test case 3: String that looks like Python dict (problematic case)
    test_stats_3 = "[{'value': '15+', 'title': 'Years Experience', 'description': 'Serving Blacktown residents'}]"
    
    print(f"   Test 3 - String dict: {_extract_content_value(test_stats_3)}")
    
    # Test case 4: Malformed JSON
    test_stats_4 = "{'value': '15+', 'title': 'Years Experience', 'description': 'Serving Blacktown residents'}"
    
    print(f"   Test 4 - Malformed JSON: {_extract_content_value(test_stats_4)}")
    
    print("\n📊 [DEBUG] Checking generated HTML files for stats patterns...")
    
    # Check the actual generated files
    html_files = [
        "plumber-in-blacktown.html",
        "plumber-in-penrith.html", 
        "plumber-in-liverpool.html"
    ]
    
    for html_file in html_files:
        file_path = os.path.join(output_dir, html_file)
        if os.path.exists(file_path):
            print(f"\n   📄 Analyzing {html_file}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for stats section
            if 'id="local-stats"' in content:
                # Extract the stats section
                start = content.find('<section id="local-stats"')
                end = content.find('</section>', start) + 10
                stats_section = content[start:end]
                
                # Count empty title/description fields
                empty_titles = stats_section.count('<h4 class="font-semibold text-gray-900 mb-2"></h4>')
                empty_descriptions = stats_section.count('<p class="text-sm text-gray-600"></p>')
                filled_values = stats_section.count('text-4xl font-bold text-primary-green mb-2">') - stats_section.count('text-4xl font-bold text-primary-green mb-2"></div>')
                
                print(f"      📊 Stats found: {filled_values} values, {empty_titles} empty titles, {empty_descriptions} empty descriptions")
                
                # Look for any stat.title or stat.description patterns
                if 'stat.title' in stats_section or 'stat.description' in stats_section:
                    print(f"      ⚠️  Found unprocessed template variables in {html_file}")
                    
    print("\n🔍 [DEBUG] Stats debugging complete!")

if __name__ == "__main__":
    debug_stats_content()