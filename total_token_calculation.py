import os
import re

def count_words_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Split the content by whitespace and count
            words = re.findall(r'\S+', content)
            return len(words)
    except UnicodeDecodeError:
        # Try with a different encoding if UTF-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()
                words = re.findall(r'\S+', content)
                return len(words)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return 0
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0

def analyze_directory(directory_path):
    all_folders = []
    folder_tokens = 0
    text_files = []
    total_files = 0
    total_words = 0
    
    print(f"Starting comprehensive analysis of {directory_path}...")
    
    # Walk through all directories recursively
    for root, dirs, files in os.walk(directory_path):
        # Process folder names
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
        
        # Process text files
        txt_files_in_dir = [f for f in files if f.endswith('.txt')]
        for txt_file in txt_files_in_dir:
            file_path = os.path.join(root, txt_file)
            rel_file_path = os.path.relpath(file_path, directory_path)
            text_files.append(rel_file_path)
            
            # Count words in file
            word_count = count_words_in_file(file_path)
            total_words += word_count
            
            total_files += 1
            if total_files % 100 == 0:
                print(f"Processed {total_files} files...")
    
    # Calculate estimated tokens for text content
    content_tokens = int(total_words * 1.33)  # Using the 0.75 words per token approximation
    
    return {
        'folder_count': len(all_folders),
        'folder_tokens': folder_tokens,
        'file_count': total_files,
        'word_count': total_words,
        'content_tokens': content_tokens,
        'total_tokens': folder_tokens + content_tokens
    }

if __name__ == "__main__":
    txt_directory = "txt"
    
    if not os.path.exists(txt_directory):
        print(f"Directory '{txt_directory}' not found!")
        exit(1)
    
    results = analyze_directory(txt_directory)
    
    print("\n=== FINAL RESULTS ===")
    print(f"Total subfolders: {results['folder_count']}")
    print(f"Total text files: {results['file_count']}")
    print(f"Total words in text files: {results['word_count']}")
    print("\nTOKEN ESTIMATION:")
    print(f"Tokens from folder names: {results['folder_tokens']}")
    print(f"Tokens from text content: {results['content_tokens']}")
    print(f"GRAND TOTAL TOKENS: {results['total_tokens']}") 