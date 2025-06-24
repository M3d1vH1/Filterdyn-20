/**
 * AI-Enhanced Dictation System
 * Uses OpenAI to process natural language speech into structured task data
 */

class AIDictationManager extends DictationManager {
    constructor() {
        super();
        this.useAI = true;
        this.supportedLanguages = ['en-US', 'el-GR']; // English and Greek
        this.currentLanguage = 'en-US';
        this.updateButtonForAI();
    }

    updateButtonForAI() {
        if (this.floatingButton) {
            const tooltip = this.floatingButton.querySelector('.dictation-tooltip');
            if (tooltip) {
                tooltip.textContent = 'AI Voice Input';
            }
            
            // Add AI indicator
            const content = this.floatingButton.querySelector('.dictation-btn-content');
            if (content && !content.querySelector('.ai-indicator')) {
                const aiIndicator = document.createElement('div');
                aiIndicator.className = 'ai-indicator';
                aiIndicator.innerHTML = '<span style="font-size: 10px; position: absolute; top: -5px; right: -5px; background: #007bff; color: white; border-radius: 50%; width: 16px; height: 16px; display: flex; align-items: center; justify-content: center; font-weight: bold;">AI</span>';
                content.appendChild(aiIndicator);
            }
        }
    }

    async handleResult(event) {
        const transcript = event.results[0][0].transcript;
        console.log('AI Dictation - Raw transcript:', transcript);
        
        this.showNotification('Processing with AI...', 'info');
        
        try {
            if (this.currentField) {
                // Simple field input - just insert text
                if (this.currentField.value) {
                    this.currentField.value += ' ' + transcript;
                } else {
                    this.currentField.value = transcript;
                }
                this.currentField.dispatchEvent(new Event('input', { bubbles: true }));
                this.showSuccess('Text inserted successfully');
            } else {
                // AI task parsing
                await this.parseWithAI(transcript);
            }
        } catch (error) {
            console.error('AI processing error:', error);
            this.showError('AI processing failed. Using basic parsing...');
            // Fallback to basic parsing
            this.parseTaskDictation(transcript);
        }
        
        this.stopListening();
    }

    async parseWithAI(transcript) {
        const taskData = await this.extractTaskDataWithAI(transcript);
        
        if (!taskData) {
            this.showError('Could not extract task information from speech');
            return;
        }

        let fieldsUpdated = 0;

        // Fill form fields
        if (taskData.title) {
            const titleField = document.getElementById('title');
            if (titleField) {
                titleField.value = taskData.title;
                titleField.dispatchEvent(new Event('input', { bubbles: true }));
                fieldsUpdated++;
            }
        }

        if (taskData.description) {
            const descField = document.getElementById('description');
            if (descField) {
                descField.value = taskData.description;
                descField.dispatchEvent(new Event('input', { bubbles: true }));
                fieldsUpdated++;
            }
        }

        if (taskData.priority) {
            const priorityField = document.getElementById('priority');
            if (priorityField) {
                priorityField.value = taskData.priority.toLowerCase();
                priorityField.dispatchEvent(new Event('change', { bubbles: true }));
                fieldsUpdated++;
            }
        }

        if (taskData.assignee) {
            const assigneeField = document.getElementById('assigned_to');
            if (assigneeField) {
                // Try to find matching user in select options
                const options = assigneeField.querySelectorAll('option');
                let found = false;
                
                for (let option of options) {
                    if (option.text.toLowerCase().includes(taskData.assignee.toLowerCase())) {
                        assigneeField.value = option.value;
                        assigneeField.dispatchEvent(new Event('change', { bubbles: true }));
                        found = true;
                        fieldsUpdated++;
                        break;
                    }
                }
                
                if (!found) {
                    this.showNotification(`Note: Could not find user "${taskData.assignee}" in assignee list`, 'info');
                }
            }
        }

        if (taskData.dueDate) {
            const dueDateField = document.getElementById('due_date');
            if (dueDateField) {
                // Convert to datetime-local format
                const date = new Date(taskData.dueDate);
                if (!isNaN(date.getTime())) {
                    const localDateTime = new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
                    dueDateField.value = localDateTime;
                    dueDateField.dispatchEvent(new Event('change', { bubbles: true }));
                    fieldsUpdated++;
                }
            }
        }

        if (fieldsUpdated > 0) {
            this.showSuccess(`AI extracted task data successfully! Updated ${fieldsUpdated} fields.`);
        } else {
            this.showError('AI processed the request but could not fill any form fields');
        }
    }

    async extractTaskDataWithAI(transcript) {
        const prompt = `Extract task information from this natural language input. The input may be in English or Greek. Return a JSON object with the following fields (use null for missing data):

{
  "title": "brief task title",
  "description": "detailed description", 
  "priority": "low|medium|high|urgent",
  "assignee": "person's name if mentioned",
  "dueDate": "ISO date string if mentioned (relative dates like 'tomorrow', 'next week' should be converted to actual dates)"
}

Input: "${transcript}"

Guidelines:
- Infer priority from urgency words (urgent, ASAP, επείγον = urgent; important, σπουδαίο = high)
- Convert Greek terms (τίτλος, περιγραφή, προτεραιότητα) appropriately
- For relative dates: tomorrow/αύριο = +1 day, next week/επόμενη εβδομάδα = +7 days, etc.
- Keep titles concise (max 50 chars)
- If someone says "assign to me" or similar, use "current user"

Respond only with valid JSON.`;

        try {
            const response = await fetch('/api/ai-extract-task', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    prompt: prompt,
                    transcript: transcript,
                    language: this.detectLanguage(transcript)
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(`Gemini API Error ${response.status}: ${errorData.error || response.statusText}`);
            }

            const result = await response.json();
            return result.taskData;
        } catch (error) {
            console.error('Gemini AI API error:', error);
            throw error;
        }
    }

    detectLanguage(text) {
        // Simple language detection
        const greekChars = /[α-ωΑ-Ω]/;
        return greekChars.test(text) ? 'el-GR' : 'en-US';
    }

    getCSRFToken() {
        const token = document.querySelector('meta[name=csrf-token]');
        return token ? token.getAttribute('content') : '';
    }

    startListening() {
        if (!this.recognition || this.isListening) return;

        // Set language based on detected language preference
        const lang = this.detectBrowserLanguage();
        this.recognition.lang = lang;
        this.currentLanguage = lang;

        this.isListening = true;
        this.updateButtonState();
        
        // Show enhanced status
        const status = document.getElementById('dictation-status');
        if (status) {
            status.innerHTML = `<i data-feather="mic" style="width: 14px; height: 14px;"></i> Listening... (Gemini AI - ${lang === 'el-GR' ? 'Ελληνικά' : 'English'})`;
            status.style.display = 'block';
        }

        try {
            this.recognition.start();
        } catch (error) {
            console.error('Error starting recognition:', error);
            this.stopListening();
            this.showError('Could not start voice recognition');
        }
    }

    detectBrowserLanguage() {
        const userLang = navigator.language || navigator.userLanguage;
        if (userLang.startsWith('el')) {
            return 'el-GR';
        }
        return 'en-US';
    }

    showNotification(message, type = 'info') {
        // Enhanced notifications with Gemini AI context
        const alert = document.createElement('div');
        const bgColor = type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info';
        const icon = type === 'error' ? 'alert-circle' : type === 'success' ? 'check-circle' : 'cpu';
        
        alert.className = `alert alert-${bgColor} alert-dismissible fade show position-fixed`;
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 320px; border-left: 4px solid #4285f4;';
        alert.innerHTML = `
            <div class="d-flex align-items-center">
                <i data-feather="${icon}" class="me-2"></i>
                <div class="flex-grow-1">
                    <small class="text-muted d-block">Gemini AI Dictation</small>
                    ${message}
                </div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alert);
        
        if (typeof feather !== 'undefined') {
            feather.replace();
        }

        setTimeout(() => {
            if (alert.parentElement) {
                alert.remove();
            }
        }, type === 'error' ? 6000 : 4000);
    }
}

// Enhanced initialization with AI check
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Dictation system loading...');
    
    // Check if AI is available
    fetch('/api/check-ai-availability')
        .then(response => response.json())
        .then(data => {
            if (data.available && !window.dictationManager) {
                console.log('Creating AI-enhanced DictationManager...');
                window.dictationManager = new AIDictationManager();
                console.log('AI DictationManager created successfully');
            } else if (!window.dictationManager) {
                console.log('AI not available, using basic DictationManager...');
                window.dictationManager = new DictationManager();
            }
        })
        .catch(error => {
            console.log('AI check failed, using basic DictationManager...', error);
            if (!window.dictationManager) {
                window.dictationManager = new DictationManager();
            }
        });
});

// Export for global access
window.AIDictationManager = AIDictationManager;