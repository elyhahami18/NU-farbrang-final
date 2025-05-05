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

def count_words_in_directory(directory_path):
    total_words = 0
    total_files = 0
    file_counts = {}
    
    print(f"Scanning directory: {directory_path}")
    
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                word_count = count_words_in_file(file_path)
                
                relative_path = os.path.relpath(file_path, directory_path)
                file_counts[relative_path] = word_count
                
                total_words += word_count
                total_files += 1
                
                if total_files % 100 == 0:
                    print(f"Processed {total_files} files so far...")
    
    return total_words, total_files, file_counts

if __name__ == "__main__":
    txt_directory = "txt"
    
    if not os.path.exists(txt_directory):
        print(f"Directory '{txt_directory}' not found!")
        exit(1)
    
    total_words, total_files, file_counts = count_words_in_directory(txt_directory)
    
    # Sort files by word count to see the largest files
    sorted_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
    
    print("\n=== RESULTS ===")
    print(f"Total number of words across all text files: {total_words}")
    print(f"Total number of text files processed: {total_files}")
    
    # Print the top 10 largest files by word count
    if sorted_files:
        print("\nTop 10 largest files by word count:")
        for file_path, count in sorted_files[:10]:
            print(f"{file_path}: {count} words")
    
    # Estimate tokens (rough approximation - 1 token ≈ 0.75 words)
    estimated_tokens = int(total_words * 1.33)
    print(f"\nEstimated number of tokens (approx): {estimated_tokens}") 