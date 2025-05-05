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

def is_hebrew_file(file_path):
    """Check if a file is in Hebrew by path or by analyzing content."""
    # Check path for language indicator
    if 'Hebrew' in file_path:
        return True
    if 'English' in file_path:
        return False
    
    # If no language in path, check content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(2000)  # Read first 2000 chars for better sample
            # Check for Hebrew characters
            hebrew_chars = re.findall(r'[\u0590-\u05FF\uFB1D-\uFB4F]', content)
            english_chars = re.findall(r'[a-zA-Z]', content)
            
            # If more Hebrew than English, consider it Hebrew
            return len(hebrew_chars) > len(english_chars)
    except:
        # Default to assuming not Hebrew on error
        return False

def analyze_hebrew_texts(folder_path):
    """Analyze only Hebrew texts in the folder with detailed breakdown."""
    hebrew_files = []
    total_words = 0
    total_size_mb = 0
    file_stats = []
    
    # Get all text files in the folder and subfolders
    print("Finding Hebrew text files...")
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                if is_hebrew_file(file_path):
                    hebrew_files.append(file_path)
    
    print(f"Found {len(hebrew_files)} Hebrew text files.")
    
    # Process each Hebrew file
    for file_path in tqdm(hebrew_files, desc="Analyzing Hebrew files"):
        relative_path = os.path.relpath(file_path, folder_path)
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        word_count = count_words_in_file(file_path)
        token_count = int(word_count * 1.33)
        
        # Add to totals
        total_words += word_count
        total_size_mb += file_size_mb
        
        # Store individual file stats
        file_stats.append({
            'path': relative_path,
            'size_mb': file_size_mb,
            'words': word_count,
            'tokens': token_count
        })
    
    # Calculate total tokens
    total_tokens = int(total_words * 1.33)
    
    return {
        'files': len(hebrew_files),
        'words': total_words,
        'size_mb': total_size_mb,
        'tokens': total_tokens,
        'file_details': file_stats
    }

def main():
    likkutei_torah_dir = "txt/Chasidut/Chabad/Likkutei Torah"
    
    if not os.path.exists(likkutei_torah_dir):
        print(f"Directory '{likkutei_torah_dir}' not found!")
        # Try alternative spelling
        likkutei_torah_dir = "txt/Chasidut/Chabad/Likutei Torah"
        if not os.path.exists(likkutei_torah_dir):
            print(f"Alternative directory '{likkutei_torah_dir}' also not found!")
            return
    
    print(f"ANALYZING HEBREW TEXTS IN {likkutei_torah_dir}")
    print("=" * 80)
    
    stats = analyze_hebrew_texts(likkutei_torah_dir)
    
    # Print summary results
    print("\nHEBREW TEXT SUMMARY:")
    print("-" * 80)
    print(f"Total Hebrew files: {stats['files']}")
    print(f"Total size: {stats['size_mb']:.2f} MB")
    print(f"Total words: {stats['words']:,}")
    print(f"Total tokens: {stats['tokens']:,}")
    print("-" * 80)
    
    # Print file details
    print("\nDETAILED FILE BREAKDOWN:")
    print("-" * 80)
    print(f"{'File Path':<50} | {'Size (MB)':<12} | {'Words':<12} | {'Tokens':<12}")
    print("-" * 80)
    
    # Sort by token count (descending)
    sorted_files = sorted(stats['file_details'], key=lambda x: x['tokens'], reverse=True)
    
    for file_stat in sorted_files:
        print(f"{file_stat['path'][:50]:<50} | {file_stat['size_mb']:<12.2f} | {file_stat['words']:<12,} | {file_stat['tokens']:<12,}")

if __name__ == "__main__":
    main() 