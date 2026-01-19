import os
import json
import time
from datetime import datetime
from execution.generate_image import generate_image_from_prompt

class CampaignManager:
    def __init__(self, campaign_file="current_campaign.json"):
        self.campaign_file = campaign_file
        self.queue = self.load_queue()
        self.cleanup_stuck_jobs() # Auto-recover on startup

    def cleanup_stuck_jobs(self):
        """Resets any jobs stuck in 'running' state back to 'pending' on startup."""
        modified = False
        for job in self.queue:
            if job["status"] == "running":
                print(f"⚠️ Resetting stuck job '{job['name']}' to pending.")
                job["status"] = "pending"
                modified = True
        if modified:
            self.save_queue()

    def load_queue(self):
        if os.path.exists(self.campaign_file):
            try:
                with open(self.campaign_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_queue(self):
        with open(self.campaign_file, 'w') as f:
            json.dump(self.queue, f, indent=4)

    def add_job(self, name, description, prompt_data, settings, output_folder, 
                char_path=None, outfit_path=None, vibe_path=None):
        
        job = {
            "id": f"job_{int(time.time())}_{len(self.queue)}",
            "name": name,
            "description": description,
            "status": "pending", # pending, running, completed, failed
            "created_at": str(datetime.now()),
            "data": {
                "prompt_data": prompt_data,
                "settings": settings, # e.g. repeat count
                "paths": {
                    "output_folder": output_folder,
                    "char_path": char_path,
                    "outfit_path": outfit_path,
                    "vibe_path": vibe_path
                }
            },
            "results": []
        }
        self.queue.append(job)
        self.save_queue()
        return job

    def clear_queue(self):
        self.queue = []
        self.save_queue()
        
    def remove_job(self, index):
        if 0 <= index < len(self.queue):
            self.queue.pop(index)
            self.save_queue()

    def get_pending_count(self):
        return len([j for j in self.queue if j["status"] == "pending"])

    def get_next_pending_job(self):
        """Finds and reserves the next pending job."""
        for i, job in enumerate(self.queue):
            if job["status"] == "pending":
                job["status"] = "running"
                self.save_queue()
                return job
        return None

    def process_job(self, job):
        """Runs the generation logic for a specific job."""
        print(f"🚀 Processing Job: {job['name']}")
        
        # Extract Data
        p_data = job["data"]["prompt_data"]
        paths = job["data"]["paths"]
        repeats = job["data"]["settings"].get("batch_count", 1)
        
        job_results = []
        
        try:
            # Run the loop
            for r in range(repeats):
                print(f"   ... Batch {r+1}/{repeats}")
                
                # Call the generator
                result = generate_image_from_prompt(
                    p_data, 
                    output_folder=paths["output_folder"],
                    reference_image_path=paths["char_path"],
                    outfit_path=paths["outfit_path"],
                    vibe_path=paths["vibe_path"]
                )
                job_results.append(result)
                
            # Mark complete
            job["status"] = "completed"
            job["results"] = job_results
            job["completed_at"] = str(datetime.now())
            self.save_queue()
            return job
            
        except Exception as e:
            job["status"] = "failed"
            job["error"] = str(e)
            self.save_queue()
            return job
