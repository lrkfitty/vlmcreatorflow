import os
import shutil

def cleanup():
    base_dir = "/Users/tylarkin/Desktop/AI Cnntent Creator workflow/output/users"
    protected_users = ["TyTheGuyTTG", "admin"]
    folders_to_clean = ["characters", "outfits", "vibes", "relations"]
    
    if not os.path.exists(base_dir):
        print(f"Directory not found: {base_dir}")
        return

    users = os.listdir(base_dir)
    for user in users:
        user_path = os.path.join(base_dir, user)
        if not os.path.isdir(user_path):
            continue
            
        if user in protected_users:
            print(f"Skipping protected user: {user}")
            continue
            
        print(f"Cleaning assets for user: {user}")
        for folder in folders_to_clean:
            folder_path = os.path.join(user_path, folder)
            if os.path.exists(folder_path):
                # Remove all files in the folder but keep the folder
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print(f'Failed to delete {file_path}. Reason: {e}')
                print(f"  - Cleaned {folder}")

if __name__ == "__main__":
    cleanup()
