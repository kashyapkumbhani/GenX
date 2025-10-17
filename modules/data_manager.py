import json
import os
import shutil
import zipfile
from datetime import datetime

def save_business_data(data):
    """
    Save business data to JSON file
    
    Args:
        data (dict): Business data to save
        
    Returns:
        bool: Success status
    """
    data['timestamp'] = datetime.now().isoformat()
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.dirname(__file__)), exist_ok=True)
    
    # Save to file
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'business_data.json'), 'w') as f:
        json.dump(data, f, indent=2)
    
    return True

def get_business_data():
    """
    Get business data from JSON file
    
    Returns:
        dict: Business data or empty dict if file not found
    """
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'business_data.json'), 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def get_history():
    """
    Get history of generated sites
    
    Returns:
        list: List of version information dictionaries
    """
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
                
                # Try to load business data for this version
                business_name = "Unknown Business"
                website_url = "N/A"
                
                business_data_path = os.path.join(version_dir, 'business_data.json')
                if os.path.exists(business_data_path):
                    try:
                        with open(business_data_path, 'r') as f:
                            business_data = json.load(f)
                            business_name = business_data.get('business', {}).get('name', 'Unknown Business')
                            website_url = business_data.get('business', {}).get('website', 'N/A')
                    except (json.JSONDecodeError, KeyError):
                        pass
                
                versions.append({
                    'version': version_num,
                    'timestamp': datetime.fromtimestamp(timestamp).isoformat(),
                    'path': f'/output/{version_num}/index.html',
                    'business_name': business_name,
                    'website_url': website_url
                })
            except ValueError:
                continue
    
    return sorted(versions, key=lambda x: x['version'], reverse=True)

def delete_site_version(version):
    """
    Delete a specific site version from the output directory
    
    Args:
        version (int): Version number to delete
        
    Returns:
        bool: Success status
    """
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
    version_dir = os.path.join(output_dir, str(version))
    
    if os.path.exists(version_dir):
        try:
            shutil.rmtree(version_dir)
            return True
        except Exception as e:
            print(f"Error deleting version {version}: {e}")
            return False
    return False

def create_site_zip(version):
    """
    Create a zip file of a specific site version
    
    Args:
        version (int): Version number to zip
        
    Returns:
        str: Path to the created zip file, or None if failed
    """
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
    version_dir = os.path.join(output_dir, str(version))
    
    if not os.path.exists(version_dir):
        return None
    
    zip_path = os.path.join(output_dir, f'site_v{version}.zip')
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(version_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, version_dir)
                    zipf.write(file_path, arcname)
        return zip_path
    except Exception as e:
        print(f"Error creating zip for version {version}: {e}")
        return None