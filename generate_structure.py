import os

# Folders to ignore to keep the diagram clean
IGNORE_DIRS = {
    'node_modules', 'venv', '.git', '__pycache__', 
    '.pytest_cache', 'postgres_data', 'dist', 'build', '.idea', '.vscode'
}

def generate_tree(dir_path, prefix=""):
    # Get all files and folders in the current directory
    try:
        items = os.listdir(dir_path)
    except PermissionError:
        return

    # Sort: Directories first, then files
    items.sort(key=lambda x: (not os.path.isdir(os.path.join(dir_path, x)), x.lower()))

    # Filter out ignored items
    items = [i for i in items if i not in IGNORE_DIRS]

    total_items = len(items)
    
    for index, item in enumerate(items):
        path = os.path.join(dir_path, item)
        is_last = index == (total_items - 1)
        
        # specific graphic for the branch
        connector = "└── " if is_last else "├── "
        
        print(f"{prefix}{connector}{item}")
        
        if os.path.isdir(path):
            # If it's a folder, recurse into it
            extension = "    " if is_last else "│   "
            generate_tree(path, prefix + extension)

if __name__ == "__main__":
    root_dir = "."
    print(f"AlertBot/")
    generate_tree(root_dir)