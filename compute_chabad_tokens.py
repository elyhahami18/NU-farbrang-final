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

def analyze_chabad():
    """Analyze the Chabad subfolder within Chassidut."""
    directory_path = "txt/Chasidut/Chabad"
    
    if not os.path.exists(directory_path):
        print(f"Directory '{directory_path}' not found!")
        return None
    
    print(f"\nAnalyzing Chabad texts within Chassidut...")
    
    total_files = 0
    total_words = 0
    total_size_mb = 0
    
    # Get all text files first
    all_files = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                all_files.append(file_path)
    
    # Process files with progress bar
    for file_path in tqdm(all_files, desc="Processing files"):
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        total_size_mb += file_size_mb
        
        # Count words
        word_count = count_words_in_file(file_path)
        total_words += word_count
        total_files += 1
    
    # Calculate estimated tokens (using 1 token ≈ 0.75 words approximation)
    estimated_tokens = int(total_words * 1.33)
    
    return {
        'subfolder': 'Chabad',
        'files': total_files,
        'words': total_words,
        'size_mb': total_size_mb,
        'tokens': estimated_tokens
    }

def main():
    print("COMPUTING TOKENS FOR CHABAD TEXTS")
    print("=================================")
    
    result = analyze_chabad()
    
    if result:
        # Print results
        print("\nRESULTS:")
        print("-" * 80)
        print(f"Subfolder: {result['subfolder']} (within Chassidut)")
        print(f"Total files: {result['files']}")
        print(f"Total size: {result['size_mb']:.2f} MB")
        print(f"Total words: {result['words']:,}")
        print(f"Estimated tokens: {result['tokens']:,}")
        print("-" * 80)
    else:
        print("Analysis could not be completed.")

if __name__ == "__main__":
    main() 