import os

# Mimic logic in app.py
user_root = os.path.join("output", "users", "TyTheGuyTTG")
print(f"Scanning: {user_root}")
print(f"Exists: {os.path.exists(user_root)}")

my_images = []
for root, dirs, files in os.walk(user_root):
    print(f"Walking: {root}")
    for file in files:
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
             my_images.append(os.path.join(root, file))

print(f"Found {len(my_images)} images:")
for img in my_images:
    print(f" - {img}")
