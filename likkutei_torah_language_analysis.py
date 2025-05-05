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

def is_english_file(file_path):
    """Check if a file is in English by path or by analyzing content."""
    # Check path for language indicator
    if 'English' in file_path:
        return True
    
    # If no language in path, check content (simplified)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(1000)  # Read first 1000 chars
            # Check for Hebrew characters (simplified)
            hebrew_chars = re.findall(r'[\u0590-\u05FF\uFB1D-\uFB4F]', content)
            english_chars = re.findall(r'[a-zA-Z]', content)
            
            # If more Hebrew than English, consider it Hebrew
            return len(english_chars) > len(hebrew_chars)
    except:
        # Default to assuming English on error
        return True

def analyze_by_language(folder_path):
    """Analyze a folder by language (English vs Hebrew)."""
    english_stats = {'files': 0, 'words': 0, 'size_mb': 0}
    hebrew_stats = {'files': 0, 'words': 0, 'size_mb': 0}
    
    # Get all text files in the folder and subfolders
    all_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                all_files.append(file_path)
    
    # Process each file
    for file_path in tqdm(all_files, desc="Processing files"):
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        word_count = count_words_in_file(file_path)
        
        # Determine language and update stats
        if is_english_file(file_path):
            english_stats['files'] += 1
            english_stats['words'] += word_count
            english_stats['size_mb'] += file_size_mb
            print(f"English: {file_path}")
        else:
            hebrew_stats['files'] += 1
            hebrew_stats['words'] += word_count
            hebrew_stats['size_mb'] += file_size_mb
            print(f"Hebrew: {file_path}")
    
    # Calculate token estimates
    english_stats['tokens'] = int(english_stats['words'] * 1.33)
    hebrew_stats['tokens'] = int(hebrew_stats['words'] * 1.33)
    
    return english_stats, hebrew_stats

def main():
    likkutei_torah_dir = "txt/Chasidut/Chabad/Likkutei Torah"
    
    if not os.path.exists(likkutei_torah_dir):
        print(f"Directory '{likkutei_torah_dir}' not found!")
        # Try alternative spelling
        likkutei_torah_dir = "txt/Chasidut/Chabad/Likutei Torah"
        if not os.path.exists(likkutei_torah_dir):
            print(f"Alternative directory '{likkutei_torah_dir}' also not found!")
            return
    
    print(f"ANALYZING {likkutei_torah_dir} BY LANGUAGE")
    print("=" * 80)
    
    english_stats, hebrew_stats = analyze_by_language(likkutei_torah_dir)
    
    # Print results
    print("\nRESULTS BY LANGUAGE:")
    print("-" * 80)
    print(f"Language  | Files    | Size (MB)    | Words           | Tokens")
    print("-" * 80)
    print(f"English   | {english_stats['files']:<8} | {english_stats['size_mb']:<12.2f} | {english_stats['words']:<15,} | {english_stats['tokens']:<,}")
    print(f"Hebrew    | {hebrew_stats['files']:<8} | {hebrew_stats['size_mb']:<12.2f} | {hebrew_stats['words']:<15,} | {hebrew_stats['tokens']:<,}")
    print("-" * 80)
    total_tokens = english_stats['tokens'] + hebrew_stats['tokens']
    print(f"TOTAL TOKENS: {total_tokens:,}")

if __name__ == "__main__":
    main() 