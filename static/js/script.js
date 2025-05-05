// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const questionForm = document.getElementById('questionForm');
const questionInput = document.getElementById('questionInput');
const processInfo = document.getElementById('processInfo');
const exampleQuestions = document.querySelectorAll('.example-question');

// Random thought-provoking questions about Jewish texts and Chassidic philosophy
const randomQuestions = [
    "How does the concept of tzimtzum (divine contraction) relate to human relationships?",
    "What is the deeper meaning of 'descent for the sake of ascent' in Chassidic thought?",
    "How does the Tanya explain the relationship between the animal soul and divine soul?",
    "What insights does Chassidic philosophy offer on the meaning of suffering?",
    "How does the concept of דירה בתחתונים (dwelling in the lower realms) manifest in daily life?",
    "What is the significance of the number 10 in Kabbalistic thought?",
    "How does the Baal Shem Tov's teaching on divine providence apply to modern life?",
    "What does it mean that 'the whole earth is full of His glory' according to Chassidic texts?",
    "How does Chassidic thought understand the relationship between faith and intellect?",
    "What does the Tanya teach about overcoming negative thoughts and emotions?",
    "How does the concept of אין סוף (Ein Sof - Infinite Light) relate to our finite reality?",
    "What is the meaning of true joy according to Chassidic philosophy?",
    "How can we understand the concept of מסירות נפש (self-sacrifice) in modern times?",
    "What is the Chassidic interpretation of 'love your neighbor as yourself'?",
    "How does the Alter Rebbe explain the purpose of creation?"
];

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    questionForm.addEventListener('submit', handleSubmit);
    exampleQuestions.forEach(question => {
        question.addEventListener('click', (e) => {
            e.preventDefault();
            const questionText = e.target.textContent;
            questionInput.value = questionText;
            handleSubmit(e, questionText);
        });
    });
    
    // Add event listener for random question button if it exists
    const randomQuestionBtn = document.getElementById('randomQuestionBtn');
    if (randomQuestionBtn) {
        randomQuestionBtn.addEventListener('click', generateRandomQuestion);
    }
});

// Generate and use a random question
function generateRandomQuestion(e) {
    if (e) e.preventDefault();
    
    // Select a random question from the array
    const randomIndex = Math.floor(Math.random() * randomQuestions.length);
    const randomQuestion = randomQuestions[randomIndex];
    
    // Fill the input field with the random question
    questionInput.value = randomQuestion;
    
    // Optionally, could auto-submit the question
    // handleSubmit(new Event('submit'), randomQuestion);
    
    // Focus on the input so the user can see the question and decide to submit
    questionInput.focus();
}

// Handle form submission
async function handleSubmit(e, exampleQuestion = null) {
    e.preventDefault();
    const question = exampleQuestion || questionInput.value.trim();
    
    if (question === '') return;
    
    // Add user message to chat
    addMessage('user', question);
    
    // Clear input field
    questionInput.value = '';
    
    // Show loading indicator
    const loadingIndicator = addLoadingIndicator();
    
    try {
        // Update process info
        updateProcessInfo({ status: 'Processing your question...' });
        
        // Send request to backend
        const response = await fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'same-origin',
            mode: 'cors',
            body: JSON.stringify({ question }),
        });
        
        // Check the content type to avoid JSON parse errors
        const contentType = response.headers.get('content-type');
        
        // Handle error response
        if (!response.ok) {
            let errorMessage = 'Something went wrong';
            
            if (contentType && contentType.includes('application/json')) {
                // It's JSON, safe to parse
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } else {
                // Not JSON, probably HTML error page
                const text = await response.text();
                console.error('Non-JSON error response:', text);
                
                // Check if it's an HTML response
                if (text.includes('<html') || text.includes('<!DOCTYPE')) {
                    errorMessage = 'Server error: The server returned an HTML error page instead of JSON';
                } else {
                    errorMessage = `Server error: ${response.status} ${response.statusText}`;
                }
            }
            
            throw new Error(errorMessage);
        }
        
        // Safely parse response data
        let data;
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            throw new Error('Server did not return JSON data');
        }
        
        // Remove loading indicator
        loadingIndicator.remove();
        
        // Add bot message
        addMessage('bot', data.answer);
        
        // Update process info with details
        updateProcessInfo({
            status: 'Completed',
            selectedSource: data.selected_source,
            sourceExplanation: data.source_explanation,
            totalTokens: data.total_tokens
        });
        
    } catch (error) {
        // Remove loading indicator
        loadingIndicator.remove();
        
        // Show error message
        addMessage('system', `Error: ${error.message}`);
        
        // Update process info with error
        updateProcessInfo({
            status: 'Error',
            error: error.message
        });
        
        console.error('Error:', error);
    }
}

// Add message to chat
function addMessage(type, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // Process content for Hebrew text
    content = processHebrewText(content);
    
    // Render markdown and citations
    messageContent.innerHTML = formatContent(content);
    
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageDiv;
}

// Process Hebrew text in content
function processHebrewText(content) {
    // Look for Hebrew text patterns (assume they're already properly formatted)
    // This regex looks for Hebrew characters
    const hebrewRegex = /[\u0590-\u05FF\u200f\uFB1D-\uFB4F]+/g;
    
    // Wrap Hebrew text in span with lang attribute
    return content.replace(hebrewRegex, match => {
        return `<span lang="he">${match}</span>`;
    });
}

// Format content with markdown and citations
function formatContent(content) {
    // Replace line breaks with <br>
    content = content.replace(/\n/g, '<br>');
    
    // Format bold text
    content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Format italic text
    content = content.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Format citations (Source: [text], [chapter])
    content = content.replace(/\(Source: (.*?)\)/g, '<span class="citation">(Source: $1)</span>');
    
    return content;
}

// Add loading indicator
function addLoadingIndicator() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot loading';
    
    loadingDiv.innerHTML = `
        <span>Thinking</span>
        <div class="dots">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
    `;
    
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return loadingDiv;
}

// Update process info
function updateProcessInfo(info) {
    let html = '';
    
    if (info.status === 'Processing your question...') {
        html = `<p>${info.status}</p>`;
    } else if (info.status === 'Completed') {
        html = `
            <div class="info-item">
                <strong>Selected Source:</strong> ${info.selectedSource}
            </div>
            <div class="info-item">
                <strong>Selection Reason:</strong> 
                <div>${formatContent(info.sourceExplanation)}</div>
            </div>
            <div class="info-item">
                <strong>Tokens Used:</strong> ${info.totalTokens.toLocaleString()} / ${(250000).toLocaleString()}
            </div>
        `;
    } else if (info.status === 'Error') {
        html = `
            <div class="info-item">
                <strong>Error:</strong> 
                <div class="error">${info.error}</div>
            </div>
        `;
    }
    
    processInfo.querySelector('.info-content').innerHTML = html;
} 