import os

def analyze_directory(directory_path):
    all_folders = []
    folder_tokens = 0
    text_files = []
    total_file_count = 0
    
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
        
        # Count text files in this directory
        txt_files = [os.path.join(rel_path, f) for f in files if f.endswith('.txt')] if root != directory_path else [f for f in files if f.endswith('.txt')]
        text_files.extend(txt_files)
        total_file_count += len(txt_files)
    
    return all_folders, folder_tokens, text_files, total_file_count

if __name__ == "__main__":
    txt_directory = "txt"
    
    if not os.path.exists(txt_directory):
        print(f"Directory '{txt_directory}' not found!")
        exit(1)
    
    all_folders, folder_tokens, text_files, total_file_count = analyze_directory(txt_directory)
    
    print(f"\nTotal number of subfolders in txt directory: {len(all_folders)}")
    print(f"Total number of text files: {total_file_count}")
    print(f"Estimated token count of all folder names: {folder_tokens}")
    
    # Print first 10 folders as sample
    print("\nSample of folder paths (first 10):")
    for folder in sorted(all_folders)[:10]:
        print(f"- {folder}")
    
    if len(all_folders) > 20:
        print("\n... (many more folders) ...")
    
    # Print first 10 text files as sample
    print("\nSample of text files (first 10):")
    for file in sorted(text_files)[:10]:
        print(f"- {file}")
    
    if len(text_files) > 20:
        print("\n... (many more text files) ...") 