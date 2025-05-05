import os
import re
from tqdm import tqdm

def count_words_in_file(file_path):
    """Count words in a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Split by whitespace and count
            words = re.findall(r'\S+', content)
            return len(words)
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
                words = re.findall(r'\S+', content)
                return len(words)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return 0
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0

def analyze_folder(folder_name):
    """Analyze a specific folder and return token statistics."""
    directory_path = f"txt/{folder_name}"
    
    if not os.path.exists(directory_path):
        print(f"Directory '{directory_path}' not found!")
        return None
    
    print(f"\nAnalyzing {folder_name} folder...")
    
    total_files = 0
    total_words = 0
    total_size_mb = 0
    
    # Process files recursively
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                total_size_mb += file_size_mb
                
                # Count words
                word_count = count_words_in_file(file_path)
                total_words += word_count
                total_files += 1
                
                if total_files % 500 == 0:
                    print(f"Processed {total_files} files so far...")
    
    # Calculate estimated tokens (using 1 token ≈ 0.75 words approximation)
    estimated_tokens = int(total_words * 1.33)
    
    return {
        'folder': folder_name,
        'files': total_files,
        'words': total_words,
        'size_mb': total_size_mb,
        'tokens': estimated_tokens
    }

def main():
    folders_to_analyze = ['Chasidut', 'Talmud', 'Tanakh']
    results = []
    
    print("COMPUTING TOKENS BY FOLDER")
    print("==========================")
    
    for folder in folders_to_analyze:
        result = analyze_folder(folder)
        if result:
            results.append(result)
    
    # Print results
    print("\nRESULTS:")
    print("-" * 80)
    print(f"{'Folder':<10} | {'Files':<10} | {'Size (MB)':<12} | {'Words':<15} | {'Tokens':<15}")
    print("-" * 80)
    
    total_tokens = 0
    for result in results:
        print(f"{result['folder']:<10} | {result['files']:<10} | {result['size_mb']:<12.2f} | {result['words']:<15,} | {result['tokens']:<15,}")
        total_tokens += result['tokens']
    
    print("-" * 80)
    print(f"TOTAL TOKENS: {total_tokens:,}")

if __name__ == "__main__":
    main() 