from PIL import Image
import os

def optimize_images(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('png', 'jpg', 'jpeg')):
                file_path = os.path.join(root, file)
                try:
                    with Image.open(file_path) as img:
                        img = img.convert('RGB')
                        optimized_path = os.path.join(root, f"optimized_{file}")
                        img.save(optimized_path, optimize=True, quality=85)
                        print(f"Optimized: {file_path} -> {optimized_path}")
                except Exception as e:
                    print(f"Error optimizing {file_path}: {e}")

if __name__ == "__main__":
    static_dir = os.path.join(os.path.dirname(__file__), 'static', 'plots')
    optimize_images(static_dir)
