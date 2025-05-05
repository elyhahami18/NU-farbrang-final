import os
import google.generativeai as genai
import tiktoken
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up the API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("No API key found. Please set GEMINI_API_KEY in your .env file")
genai.configure(api_key=api_key)

# Base directory for all text files
BASE_DIR = "txt/Chasidut/Chabad"

# Available text options
TEXT_OPTIONS = ["Tanya", "Torah Ohr", "The Gate of Unity", "Derekh Mitzvotekha/Hebrew", "Likkutei Torah"]

# Maximum tokens to include in context window
MAX_TOKENS = 250000

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set debug mode
app.debug = True

def count_tokens(text):
    """Count the number of tokens in a text string using tiktoken."""
    try:
        encoder = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
        return len(encoder.encode(text))
    except:
        # Fallback: estimate tokens as words/0.75 (rough approximation)
        return len(text.split()) // 0.75

def select_files_with_gemini(subfolder, question):
    """Ask Gemini to select the most relevant subfolders or files for the question."""
    full_path = os.path.join(BASE_DIR, subfolder)
    
    # Get all available subfolders and files
    all_files = []
    try:
        for root, dirs, files in os.walk(full_path):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, full_path)
                    all_files.append(rel_path)
    except Exception as e:
        app.logger.error(f"Error walking directory {full_path}: {str(e)}")
        # Return empty list with error reason
        return [], f"Error accessing files in {subfolder}: {str(e)}"
    
    # If there are no files or just a few, return all of them
    if len(all_files) <= 3:
        return all_files, f"Selected all available files ({len(all_files)} found)"
    
    # Otherwise, ask Gemini to select the most relevant ones
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
        
        prompt = f"""
        Based on the following question about Jewish texts or Chassidus:
        
        Question: {question}
        
        Which of these files from {subfolder} would be most relevant to answer this question?
        Available files:
        {', '.join(all_files)}
        
        Please select the most relevant files (up to 5) and list them one per line.
        Only output the filenames, nothing else.
        """
        
        # Set safety settings to be more permissive
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
        ]
        
        response = model.generate_content(prompt, safety_settings=safety_settings)
        selected_files = [file.strip() for file in response.text.strip().split('\n') if file.strip() in all_files]
        
        # If Gemini doesn't select any valid files, return a few default ones
        if not selected_files and all_files:
            selected_files = all_files[:min(3, len(all_files))]
            reason = "Gemini did not select specific files; using default selection of first few files"
        else:
            reason = f"Selected {len(selected_files)} most relevant files based on your question"
            
    except Exception as e:
        app.logger.error(f"Error in Gemini selection for {subfolder}: {str(e)}")
        # On error, select a few default files
        selected_files = all_files[:min(3, len(all_files))]
        reason = f"Error in AI selection: {str(e)}. Using default selection of first few files."
    
    return selected_files, reason

def get_texts_from_subfolder(subfolder, question):
    """Get text content from files in the specified subfolder, staying under token limit."""
    text_content = []
    total_tokens = 0
    
    # Construct the full path
    full_path = os.path.join(BASE_DIR, subfolder)
    
    # Special case for Likkutei Torah
    if subfolder == "Likkutei Torah":
        file_path = os.path.join(BASE_DIR, "Likkutei Torah/Hebrew/Kehot Publication Society.txt")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tokens = count_tokens(content)
                
                # If the file is too large, take the first part
                if tokens > MAX_TOKENS:
                    # Estimate how much of the text we can include
                    ratio = MAX_TOKENS / tokens
                    # Take slightly less to be safe
                    safe_ratio = ratio * 0.9
                    truncated_content = content[:int(len(content) * safe_ratio)]
                    text_content.append({
                        "title": os.path.basename(file_path) + " (truncated)",
                        "content": truncated_content
                    })
                    total_tokens = count_tokens(truncated_content)
                else:
                    text_content.append({
                        "title": os.path.basename(file_path),
                        "content": content
                    })
                    total_tokens = tokens
            return text_content, "Used main Likkutei Torah text file", total_tokens
    
    # For all other subfolders, get selected txt files
    selected_files, selection_reason = select_files_with_gemini(subfolder, question)
    
    for rel_file_path in selected_files:
        file_path = os.path.join(full_path, rel_file_path)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tokens = count_tokens(content)
                    
                    # Check if adding this file would exceed the token limit
                    if total_tokens + tokens > MAX_TOKENS:
                        # If this is the first file and it's too large, truncate it
                        if not text_content:
                            remaining_tokens = MAX_TOKENS
                            ratio = remaining_tokens / tokens
                            safe_ratio = ratio * 0.9
                            truncated_content = content[:int(len(content) * safe_ratio)]
                            text_content.append({
                                "title": rel_file_path + " (truncated)",
                                "content": truncated_content
                            })
                            total_tokens += count_tokens(truncated_content)
                        # Otherwise skip this file
                        continue
                    
                    text_content.append({
                        "title": rel_file_path,
                        "content": content
                    })
                    total_tokens += tokens
                    
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
    
    return text_content, selection_reason, total_tokens

def select_relevant_text(question):
    """Use Gemini to select the most relevant text source for the question."""
    model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
    
    try:
        prompt = f"""
        Based on the following question about Jewish texts or Chassidus, determine which source would be most relevant.
        
        Question: {question}
        
        Please analyze this question and select ONE of the following options as the most relevant source:
        {', '.join(TEXT_OPTIONS)}
        
        First, explain your reasoning for why this source would be most relevant to the question.
        Then, provide ONLY the name of your selected source on the final line, exactly as written in the list above.
        """
        
        # Set safety settings to be more permissive
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
        ]
        
        response = model.generate_content(prompt, safety_settings=safety_settings)
        
        # Extract the last line which should contain just the source name
        lines = response.text.strip().split('\n')
        selected_source = lines[-1].strip()
        
        # Verify that the response is one of our valid options
        found_match = False
        for option in TEXT_OPTIONS:
            if option in selected_source:
                selected_source = option
                found_match = True
                break
                
        # If not found, default to first option and print warning
        if not found_match:
            app.logger.warning(f"Could not determine selected source. Full response: {response.text}")
            selected_source = TEXT_OPTIONS[0]
            explanation = f"Defaulting to {selected_source} because the AI couldn't determine the best source. Your question might be general or applicable to multiple texts."
        else:
            explanation = '\n'.join(lines[:-1])
        
        return selected_source, explanation
        
    except Exception as e:
        app.logger.error(f"Error in select_relevant_text: {str(e)}")
        # Default to first option on error
        return TEXT_OPTIONS[0], f"Using {TEXT_OPTIONS[0]} as default due to an error in source selection."

def answer_question_with_context(question, selected_source, text_content):
    """Get answer from Gemini with the context of selected texts."""
    model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
    
    # Prepare context with all the text files
    context = f"Selected source: {selected_source}\n\n"
    
    for text in text_content:
        context += f"--- BEGIN: {text['title']} ---\n"
        context += text['content']
        context += f"\n--- END: {text['title']} ---\n\n"
    
    prompt = f"""
    Question about Jewish texts/Chassidus: {question}
    
    Context (relevant texts from {selected_source}):
    
    {context}
    
    Based on the above texts, please answer the question in detail. Follow these requirements carefully:

    AXIOM: You MUST NOT use the provided text if it isn't relevant to the question. In such cases, answer using only your base knowledge of Jewish texts and Chassidic philosophy.
    
    1. CITATIONS: For EVERY claim or concept you mention from the provided texts, include a specific citation in the format (Source: [text title], [chapter/verse/section]). Do not make claims without proper citations.
    
    2. HEBREW TEXT: You should include key phrases and terms in hebrew. When including Hebrew terms or phrases:
       - CRITICAL: Display Hebrew in its CORRECT format: פנים ואחוריים (NOT panim v'Achor)
       - Always place the Hebrew text FIRST, then its transliteration and English translation in parentheses
       - Format as: [Hebrew] ([transliteration] - [English translation])
       - Example: פנים ואחוריים (Panim v'Achor - Face and Back)
    
    3. STRUCTURE: Structure your answer with clear paragraphs, proper citations, and a brief conclusion summarizing the key points.
    
    4. ACCURACY: If the provided texts do not contain sufficient information to answer the question, clearly state this rather than making up information.
    """
    
    try:
        # Set safety settings to be more permissive
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
        ]
        
        # Use generation config to try to avoid pattern errors
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        response = model.generate_content(
            prompt, 
            safety_settings=safety_settings,
            generation_config=generation_config
        )
        
        return response.text
        
    except Exception as e:
        app.logger.error(f"Error in Gemini answer generation: {str(e)}")
        error_msg = str(e)
        if "string did not match the expected pattern" in error_msg:
            return "I'm having trouble formulating a response to this question. Please try rephrasing it or asking about a different aspect of the topic."
        else:
            return f"I encountered an error while processing your question: {error_msg}. Please try again with a different question."

@app.route('/')
def index():
    # Example questions
    example_questions = [
        "What is the concept of Tzimtzum in Chabad philosophy?",
        "Explain the difference between Chochma and Bina according to the Tanya.",
        "How does the Alter Rebbe explain the concept of אחדות ה׳ (Unity of God)?",
        "What is the significance of the four worlds in Kabbalah?",
        "Explain the concept of ביטול (self-nullification) in Chassidic thought."
    ]
    return render_template('index.html', example_questions=example_questions)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question', '')
    
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    try:
        # Step 1: Select the most relevant text source
        selected_source, explanation = select_relevant_text(question)
        
        # Step 2: Get relevant texts from the selected source
        text_content, selection_reason, total_tokens = get_texts_from_subfolder(selected_source, question)
        
        if not text_content:
            return jsonify({
                "error": f"No text files found in {os.path.join(BASE_DIR, selected_source)}. Please check the directory structure."
            }), 500
        
        # Step 3: Get the answer from Gemini with the context
        try:
            answer = answer_question_with_context(question, selected_source, text_content)
            
            return jsonify({
                "answer": answer,
                "selected_source": selected_source,
                "source_explanation": explanation,
                "selection_reason": selection_reason,
                "file_count": len(text_content),
                "total_tokens": total_tokens
            })
        except Exception as e:
            # Handle Gemini API errors
            error_msg = str(e)
            if "string did not match the expected pattern" in error_msg:
                return jsonify({"error": "The Gemini AI model couldn't properly format its response. Please try rephrasing your question."}), 500
            else:
                return jsonify({"error": f"Error from AI model: {error_msg}"}), 500
                
    except Exception as e:
        # Catch all other errors
        app.logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080))) 