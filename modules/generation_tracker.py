import json
import os
import uuid
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from modules.site_generator import generate_site
from modules.ai_content import generate_ai_content

class GenerationTracker:
    """Manages multiple simultaneous website generations with status tracking"""
    
    def __init__(self, storage_file: str = "generation_status.json"):
        self.storage_file = storage_file
        self.lock = threading.Lock()
        self._ensure_storage_file()
    
    def _ensure_storage_file(self):
        """Ensure the storage file exists with proper structure"""
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w') as f:
                json.dump({"generations": {}}, f, indent=2)
    
    def _load_data(self) -> Dict:
        """Load generation data from JSON file"""
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"generations": {}}
    
    def _save_data(self, data: Dict):
        """Save generation data to JSON file"""
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def start_generation(self, business_data: Dict, template_name: str, api_keys: List[str]) -> str:
        """
        Start a new generation process and return the generation ID
        
        Args:
            business_data: Business information for site generation
            template_name: Selected template name
            api_keys: List of available API keys
            
        Returns:
            str: Unique generation ID
        """
        generation_id = str(uuid.uuid4())
        
        with self.lock:
            data = self._load_data()
            data["generations"][generation_id] = {
                "id": generation_id,
                "status": "queued",
                "progress": 0,
                "business_name": business_data.get('business', {}).get('name', 'Unknown Business'),
                "template": template_name,
                "created_at": datetime.now().isoformat(),
                "started_at": None,
                "completed_at": None,
                "error": None,
                "version": None,
                "preview_url": None,
                "business_data": business_data
            }
            self._save_data(data)
        
        # Start generation in background thread
        thread = threading.Thread(
            target=self._process_generation,
            args=(generation_id, business_data, template_name, api_keys),
            daemon=True
        )
        thread.start()
        
        return generation_id
    
    def _process_generation(self, generation_id: str, business_data: Dict, template_name: str, api_keys: List[str]):
        """
        Process the actual generation in background
        
        Args:
            generation_id: Unique generation ID
            business_data: Business information
            template_name: Selected template
            api_keys: Available API keys
        """
        try:
            # Update status to generating
            self._update_status(generation_id, "generating", 10, "Starting generation...")
            
            # Generate AI content with progress updates
            self._update_status(generation_id, "generating", 20, "Generating AI content...")
            
            # Create a progress callback for AI content generation
            def ai_progress_callback(progress, message):
                # Map AI progress (0-100) to our range (20-70)
                mapped_progress = 20 + int((progress / 100) * 50)
                self._update_status(generation_id, "generating", mapped_progress, message)
            
            ai_content = generate_ai_content(
                business_data, 
                template_name=template_name, 
                api_key=api_keys[0],
                progress_callback=ai_progress_callback
            )
            
            # Generate site
            self._update_status(generation_id, "generating", 75, "Building website...")
            output_version = generate_site(business_data, template_name=template_name, ai_content=ai_content)
            
            # Final steps
            self._update_status(generation_id, "generating", 90, "Finalizing...")
            
            # Mark as completed
            preview_url = f'/preview/{output_version}'
            self._update_status(
                generation_id, 
                "completed", 
                100, 
                "Generation completed successfully",
                version=output_version,
                preview_url=preview_url
            )
            
        except Exception as e:
            # Mark as failed
            self._update_status(
                generation_id, 
                "failed", 
                0, 
                f"Generation failed: {str(e)}"
            )
    
    def _update_status(self, generation_id: str, status: str, progress: int, message: str = None, **kwargs):
        """
        Update generation status
        
        Args:
            generation_id: Generation ID to update
            status: New status (queued, generating, completed, failed)
            progress: Progress percentage (0-100)
            message: Optional status message
            **kwargs: Additional fields to update
        """
        with self.lock:
            data = self._load_data()
            if generation_id in data["generations"]:
                generation = data["generations"][generation_id]
                generation["status"] = status
                generation["progress"] = progress
                generation["updated_at"] = datetime.now().isoformat()
                
                if message:
                    generation["message"] = message
                
                if status == "generating" and generation["started_at"] is None:
                    generation["started_at"] = datetime.now().isoformat()
                elif status in ["completed", "failed"]:
                    generation["completed_at"] = datetime.now().isoformat()
                
                # Update additional fields
                for key, value in kwargs.items():
                    generation[key] = value
                
                self._save_data(data)
    
    def get_generation_status(self, generation_id: str) -> Optional[Dict]:
        """
        Get status of a specific generation
        
        Args:
            generation_id: Generation ID to check
            
        Returns:
            Dict: Generation status or None if not found
        """
        data = self._load_data()
        return data["generations"].get(generation_id)
    
    def get_all_generations(self) -> List[Dict]:
        """
        Get all generations sorted by creation date (newest first)
        
        Returns:
            List[Dict]: List of all generations
        """
        data = self._load_data()
        generations = list(data["generations"].values())
        
        # Sort by created_at (newest first)
        generations.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return generations
    
    def get_active_generations(self) -> List[Dict]:
        """
        Get all active (queued or generating) generations
        
        Returns:
            List[Dict]: List of active generations
        """
        generations = self.get_all_generations()
        return [g for g in generations if g["status"] in ["queued", "generating"]]
    
    def delete_generation(self, generation_id: str) -> bool:
        """
        Delete a generation record
        
        Args:
            generation_id: Generation ID to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        with self.lock:
            data = self._load_data()
            if generation_id in data["generations"]:
                del data["generations"][generation_id]
                self._save_data(data)
                return True
            return False
    
    def cleanup_old_generations(self, max_age_days: int = 30):
        """
        Clean up generations older than specified days
        
        Args:
            max_age_days: Maximum age in days to keep
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        with self.lock:
            data = self._load_data()
            to_delete = []
            
            for gen_id, generation in data["generations"].items():
                try:
                    created_at = datetime.fromisoformat(generation["created_at"])
                    if created_at < cutoff_date and generation["status"] in ["completed", "failed"]:
                        to_delete.append(gen_id)
                except (ValueError, KeyError):
                    continue
            
            for gen_id in to_delete:
                del data["generations"][gen_id]
            
            if to_delete:
                self._save_data(data)

# Global tracker instance
tracker = GenerationTracker()