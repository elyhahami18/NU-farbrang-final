import os
import google.generativeai as genai
import sys
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up the API key
API_KEY = os.getenv('GEMINI_API_KEY')
if not API_KEY:
    raise ValueError("No API key found. Please set GEMINI_API_KEY in your .env file")
genai.configure(api_key=API_KEY)

# Set up the model
MODEL = 'gemini-2.5-flash-preview-04-17'

def load_chassidut_texts(directory_path="txt/Chasidut", limit_mb=30):
    """Load Chassidut text files with size limits."""
    print(f"Loading Chassidut texts from {directory_path}...")
    chassidut_texts = {}
    total_size_mb = 0
    
    # Get all valid text files
    all_files = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                if file_size_mb <= 10:  # Skip files over 10MB
                    all_files.append((file_path, file_size_mb))
    
    # Sort by size (smallest first)
    all_files.sort(key=lambda x: x[1])
    
    # Process files
    for file_path, file_size_mb in tqdm(all_files, desc="Loading files"):
        # Stop if we've reached the limit
        if total_size_mb + file_size_mb > limit_mb:
            continue
            
        relative_path = os.path.relpath(file_path, "txt")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():
                    chassidut_texts[relative_path] = content
                    total_size_mb += file_size_mb
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                    if content.strip():
                        chassidut_texts[relative_path] = content
                        total_size_mb += file_size_mb
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    print(f"Loaded {len(chassidut_texts)} text files. Total size: {total_size_mb:.2f} MB")
    return chassidut_texts

def prepare_context(texts_dict, max_chars=500000):
    """Prepare context from text files, staying within character limits."""
    context = "CHASSIDUT TEXTS:\n\n"
    total_chars = len(context)
    included_texts = 0
    
    for path, content in sorted(texts_dict.items()):
        # Check if adding this content would exceed the size limit
        text_section = f"### {path} ###\n{content}\n\n"
        if total_chars + len(text_section) > max_chars:
            continue
        
        # Add the content
        context += text_section
        total_chars += len(text_section)
        included_texts += 1
    
    print(f"Included {included_texts} texts in context. Total characters: {total_chars}")
    return context

def query_gemini(prompt, context=None):
    """Query Gemini with optional context."""
    model = genai.GenerativeModel(MODEL)
    
    full_prompt = prompt
    if context:
        full_prompt = f"{context}\n\nBased on the Chassidut texts above, please answer: {prompt}"
    
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "This model's maximum context length is" in error_msg:
            return "Error: Context too large. Try with fewer texts or a shorter query."
        return f"Error: {error_msg}"

def main():
    print("\n=== CHASSIDUT TEXT QUERY SYSTEM ===\n")
    
    # Load texts
    chassidut_texts = load_chassidut_texts()
    
    # Show sample of loaded texts
    print("\nSample of loaded texts:")
    for i, path in enumerate(sorted(chassidut_texts.keys())[:5]):
        print(f"{i+1}. {path}")
    if len(chassidut_texts) > 5:
        print(f"... and {len(chassidut_texts) - 5} more texts")
    
    # Prepare context
    print("\nPreparing context for Gemini...")
    context = prepare_context(chassidut_texts)
    
    # Query loop
    print("\nEnter your questions about Chassidut (or 'exit' to quit):")
    while True:
        prompt = input("\nYour question: ")
        if prompt.lower() in ('exit', 'quit'):
            break
            
        print("\nQuerying Gemini...\n")
        response = query_gemini(prompt, context)
        
        print("\n" + "=" * 80)
        print(response)
        print("=" * 80)

if __name__ == "__main__":
    main() 