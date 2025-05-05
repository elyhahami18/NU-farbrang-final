import os
import google.generativeai as genai
import argparse
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up the API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("No API key found. Please set GEMINI_API_KEY in your .env file")
genai.configure(api_key=api_key)

def load_chassidut_texts(directory_path="txt/Chasidut", limit_mb=100):
    """
    Load text files from the Chassidut directory, with a size limit.
    Returns a dictionary mapping file paths to their contents.
    """
    print(f"Loading Chassidut texts from {directory_path}...")
    chassidut_texts = {}
    total_size_mb = 0
    
    # Walk through all directories recursively
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, "txt")
                
                # Check file size before loading
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                
                # Skip very large files
                if file_size_mb > 20:  # Skip individual files over 20MB
                    print(f"Skipping large file: {relative_path} ({file_size_mb:.2f} MB)")
                    continue
                
                # Stop if we've reached the total size limit
                if total_size_mb + file_size_mb > limit_mb:
                    print(f"Reached size limit of {limit_mb} MB. Stopping.")
                    break
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Only include non-empty files
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

def prepare_context(texts_dict, max_tokens=125000):
    """
    Prepare a context string from the loaded texts, keeping within token limits.
    Returns a formatted string with text titles and content.
    """
    context = "CHASSIDUT TEXTS:\n\n"
    estimated_tokens = 0
    included_texts = 0
    
    # Sort by path to maintain consistent order
    for path, content in sorted(texts_dict.items()):
        # Estimate tokens - approximately 4 characters per token for English
        estimated_text_tokens = len(content) / 4
        
        # Skip if this text would exceed our token limit
        if estimated_tokens + estimated_text_tokens > max_tokens:
            continue
        
        # Add formatted text with title
        text_section = f"### {path} ###\n{content}\n\n"
        context += text_section
        
        estimated_tokens += estimated_text_tokens
        included_texts += 1
    
    print(f"Included {included_texts} texts in context. Estimated tokens: {int(estimated_tokens)}")
    return context

def query_gemini_with_context(prompt, context):
    """
    Query the Gemini model with a user prompt and the Chassidut texts as context.
    """
    # Set up the model
    model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
    
    # Combine context and prompt
    full_prompt = f"{context}\n\nBased on the Chassidut texts above, please answer: {prompt}"
    
    # Generate content
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "This model's maximum context length is" in error_msg:
            return "Error: The context is too large for Gemini. Please try with fewer texts or a shorter query."
        return f"Error: {error_msg}"

def main():
    parser = argparse.ArgumentParser(description='Query Gemini with Chassidut texts as context')
    parser.add_argument('--limit', type=int, default=50, help='Size limit in MB for loading texts (default: 50)')
    args = parser.parse_args()
    
    # Load Chassidut texts
    chassidut_texts = load_chassidut_texts(limit_mb=args.limit)
    
    if not chassidut_texts:
        print("No texts were loaded. Please check the directory path and try again.")
        return
    
    # Prepare context
    context = prepare_context(chassidut_texts)
    
    # Interactive prompt loop
    print("\nCHASSIDUT TEXT QUERY SYSTEM")
    print("==========================")
    print("Enter your questions about Chassidut. Type 'exit' to quit.\n")
    
    while True:
        user_prompt = input("Your question: ")
        if user_prompt.lower() == 'exit':
            break
        
        print("\nQuerying Gemini with your question and Chassidut texts as context...")
        response = query_gemini_with_context(user_prompt, context)
        print("\nRESPONSE:")
        print("---------")
        print(response)
        print("\n" + "-" * 80 + "\n")

if __name__ == "__main__":
    main() 