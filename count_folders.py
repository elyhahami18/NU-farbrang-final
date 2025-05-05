import os

def count_all_folders(directory_path):
    all_folders = []
    folder_tokens = 0
    
    # Walk through all directories recursively
    for root, dirs, files in os.walk(directory_path):
        # Skip the root directory itself
        if root != directory_path:
            # Get the relative path from the root directory
            rel_path = os.path.relpath(root, directory_path)
            all_folders.append(rel_path)
            
            # Calculate tokens for the folder name (just the last part)
            folder_name = os.path.basename(root)
            words = folder_name.split()
            word_count = len(words) if words else 1
            tokens = int(word_count * 1.33)
            folder_tokens += tokens
    
    return all_folders, folder_tokens

if __name__ == "__main__":
    txt_directory = "txt"
    
    if not os.path.exists(txt_directory):
        print(f"Directory '{txt_directory}' not found!")
        exit(1)
    
    all_folders, token_count = count_all_folders(txt_directory)
    
    print(f"\nTotal number of subfolders in txt directory: {len(all_folders)}")
    print(f"Estimated token count of all folder names: {token_count}")
    
    # Print first 20 folders and last 20 folders as sample
    print("\nSample of folder paths (first 20):")
    for folder in sorted(all_folders)[:20]:
        print(f"- {folder}")
    
    if len(all_folders) > 40:
        print("\n... (many more folders) ...")
        
    print("\nSample of folder paths (last 20):")
    for folder in sorted(all_folders)[-20:]:
        print(f"- {folder}") 