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

def get_immediate_subfolders(directory):
    """Get immediate subfolders of a directory."""
    return [f for f in os.listdir(directory) 
            if os.path.isdir(os.path.join(directory, f))]

def analyze_folder(folder_path):
    """Analyze a specific folder and return token statistics."""
    total_files = 0
    total_words = 0
    total_size_mb = 0
    
    # Get all text files in this folder and subfolders
    all_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                all_files.append(file_path)
    
    # Process files
    for file_path in all_files:
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        total_size_mb += file_size_mb
        
        # Count words
        word_count = count_words_in_file(file_path)
        total_words += word_count
        total_files += 1
    
    # Calculate estimated tokens (using 1 token ≈ 0.75 words approximation)
    estimated_tokens = int(total_words * 1.33)
    
    return {
        'files': total_files,
        'words': total_words,
        'size_mb': total_size_mb,
        'tokens': estimated_tokens
    }

def main():
    chabad_dir = "txt/Chasidut/Chabad"
    
    if not os.path.exists(chabad_dir):
        print(f"Directory '{chabad_dir}' not found!")
        return
    
    print("ANALYZING CHABAD SUBFOLDERS")
    print("===========================")
    
    # Get all immediate subfolders
    subfolders = get_immediate_subfolders(chabad_dir)
    
    if not subfolders:
        print("No subfolders found within Chabad directory.")
        return
    
    print(f"Found {len(subfolders)} subfolders within Chabad.")
    
    # Analyze each subfolder
    results = []
    grand_total_tokens = 0
    
    for subfolder in tqdm(sorted(subfolders), desc="Analyzing subfolders"):
        subfolder_path = os.path.join(chabad_dir, subfolder)
        print(f"\nAnalyzing: {subfolder}")
        
        stats = analyze_folder(subfolder_path)
        stats['subfolder'] = subfolder
        results.append(stats)
        
        grand_total_tokens += stats['tokens']
    
    # Analyze Chabad root directory (files directly in Chabad folder, not in subfolders)
    print("\nAnalyzing files directly in Chabad folder (not in subfolders)")
    root_files = [os.path.join(chabad_dir, f) for f in os.listdir(chabad_dir) 
                 if os.path.isfile(os.path.join(chabad_dir, f)) and f.endswith('.txt')]
    
    if root_files:
        root_stats = {
            'subfolder': '[Root Chabad folder]',
            'files': 0,
            'words': 0,
            'size_mb': 0,
            'tokens': 0
        }
        
        for file_path in root_files:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            root_stats['size_mb'] += file_size_mb
            
            word_count = count_words_in_file(file_path)
            root_stats['words'] += word_count
            root_stats['files'] += 1
        
        root_stats['tokens'] = int(root_stats['words'] * 1.33)
        results.append(root_stats)
        grand_total_tokens += root_stats['tokens']
    
    # Print results
    print("\nRESULTS BY SUBFOLDER:")
    print("-" * 80)
    print(f"{'Subfolder':<30} | {'Files':<8} | {'Size (MB)':<12} | {'Words':<15} | {'Tokens':<15}")
    print("-" * 80)
    
    # Sort by token count (descending)
    results.sort(key=lambda x: x['tokens'], reverse=True)
    
    for result in results:
        print(f"{result['subfolder']:<30} | {result['files']:<8} | {result['size_mb']:<12.2f} | {result['words']:<15,} | {result['tokens']:<15,}")
    
    print("-" * 80)
    print(f"TOTAL CHABAD TOKENS: {grand_total_tokens:,}")

if __name__ == "__main__":
    main() 