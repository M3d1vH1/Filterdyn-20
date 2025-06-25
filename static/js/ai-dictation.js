/**
 * AI-Enhanced Dictation Manager for Filterdyn Operations Suite
 * Enhanced voice input with Gemini AI integration for natural language task creation
 */

class AIDictationManager {
    constructor() {
        this.isListening = false;
        this.recognition = null;
        this.currentField = null;
        this.lastTranscript = '';
        
        this.setupSpeechRecognition();
        console.log('AI-Enhanced Dictation Manager initialized');
    }

    setupSpeechRecognition() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.warn('Speech recognition not supported in this browser');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.maxAlternatives = 1;
        this.recognition.lang = this.detectLanguage();

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript.trim();
            this.lastTranscript = transcript;
            console.log('AI Speech Recognition Result:', transcript);
            this.processTranscript(transcript);
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.stopListening();
            this.showError('Voice recognition error: ' + event.error);
        };

        this.recognition.onend = () => {
            console.log('Speech recognition ended');
            this.stopListening();
        };
    }

    async processTranscript(transcript) {
        console.log('AI Dictation - Raw transcript:', transcript);
        
        this.showNotification('Processing with AI...', 'info');
        
        try {
            if (this.currentField) {
                if (this.currentField.value) {
                    this.currentField.value += ' ' + transcript;
                } else {
                    this.currentField.value = transcript;
                }
                this.currentField.dispatchEvent(new Event('input', { bubbles: true }));
                this.showSuccess('Text inserted successfully');
            } else {
                const isTaskPage = window.location.pathname.includes('/tasks/create') || 
                                 document.getElementById('title') || 
                                 document.getElementById('description');
                
                if (isTaskPage) {
                    await this.parseWithAI(transcript);
                } else {
                    const possibleFields = document.querySelectorAll('input[type="text"], input[type="search"], textarea');
                    if (possibleFields.length > 0) {
                        for (let field of possibleFields) {
                            if (field.offsetParent !== null && !field.disabled && !field.readonly) {
                                field.value = transcript;
                                field.dispatchEvent(new Event('input', { bubbles: true }));
                                this.showSuccess('Text inserted into ' + (field.placeholder || 'input field'));
                                return;
                            }
                        }
                    }
                    this.showNotification('Voice input: ' + transcript, 'info');
                }
            }
        } catch (error) {
            console.error('AI processing error:', error);
            this.showError('AI processing failed. Using basic parsing...');
            this.parseTaskDictation(transcript);
        }
        
        this.stopListening();
    }

    async parseWithAI(transcript) {
        console.log('parseWithAI called with transcript:', transcript);
        
        try {
            const taskData = await this.extractTaskDataWithAI(transcript);
            console.log('AI extracted task data:', taskData);
            
            if (!taskData) {
                this.showError('Could not extract task information from speech');
                return;
            }
            
            this.fillFormWithTaskData(taskData);
            this.showSuccess('Task information extracted and filled successfully');
        } catch (error) {
            console.error('Error parsing task with AI:', error);
            this.showError('Failed to parse task information');
        }
    }

    fillFormWithTaskData(taskData) {
        console.log('Filling form with task data:', taskData);
        
        if (taskData.title) {
            const titleField = document.getElementById('title');
            if (titleField) {
                titleField.value = taskData.title;
                titleField.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
        
        if (taskData.description) {
            const descriptionField = document.getElementById('description');
            if (descriptionField) {
                descriptionField.value = taskData.description;
                descriptionField.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
        
        if (taskData.priority) {
            const priorityField = document.getElementById('priority');
            if (priorityField) {
                priorityField.value = taskData.priority;
                priorityField.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
        
        if (taskData.category) {
            const categoryField = document.getElementById('category');
            if (categoryField) {
                categoryField.value = taskData.category;
                categoryField.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
        
        if (taskData.assigned_to) {
            const assignedField = document.getElementById('assigned_to');
            if (assignedField) {
                assignedField.value = taskData.assigned_to;
                assignedField.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
        
        if (taskData.due_date) {
            const dueDateField = document.getElementById('due_date');
            if (dueDateField) {
                dueDateField.value = taskData.due_date;
                dueDateField.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
        
        console.log('Form fields populated with AI-extracted data');
    }

    async extractTaskDataWithAI(transcript) {
        console.log('Extracting task data with AI from transcript:', transcript);
        
        const prompt = `
You are an AI assistant that extracts task information from spoken natural language.

Extract the following information from this spoken text: "${transcript}"

Return a JSON object with these fields (use null for missing information):
- title: Brief task title (max 50 chars)
- description: Detailed description 
- priority: "low", "medium", "high", or "urgent"
- category: "follow_up", "service_reminder", or "general"
- assigned_to: User name or "current user" if not specified
- due_date: ISO date format YYYY-MM-DD if mentioned

Guidelines:
- Extract the main action/task as the title
- Include context and details in description
- Infer priority from urgency words (urgent, asap, important, etc.)
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
                    transcript: transcript,
                    prompt: prompt
                })
            });
            
            if (!response.ok) {
                throw new Error(`API request failed: ${response.status}`);
            }
            
            const data = await response.json();
            return data.task_data || null;
        } catch (error) {
            console.error('Error extracting task data:', error);
            return null;
        }
    }

    parseTaskDictation(transcript) {
        console.log('Basic task parsing for:', transcript);
        
        const result = {
            title: transcript.substring(0, 50),
            description: transcript,
            priority: 'medium',
            category: 'general'
        };
        
        if (/urgent|asap|immediately|critical/i.test(transcript)) {
            result.priority = 'urgent';
        } else if (/important|high|priority/i.test(transcript)) {
            result.priority = 'high';
        } else if (/low|later|whenever/i.test(transcript)) {
            result.priority = 'low';
        }
        
        return result;
    }

    detectLanguage(text) {
        if (!text) return this.detectBrowserLanguage();
        
        const greekChars = /[\u0370-\u03FF\u1F00-\u1FFF]/;
        return greekChars.test(text) ? 'el-GR' : 'en-US';
    }

    getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }

    startListening() {
        if (!this.recognition || this.isListening) return;

        this.currentField = document.activeElement;
        if (this.currentField && this.currentField.tagName !== 'INPUT' && this.currentField.tagName !== 'TEXTAREA') {
            this.currentField = null;
        }

        this.isListening = true;
        this.recognition.lang = this.detectLanguage();
        
        const status = document.getElementById('voice-status');
        if (status) {
            const lang = this.recognition.lang;
            const context = this.currentField ? 'Field Input' : 'Auto-detect Mode';
            
            status.innerHTML = `<i data-feather="mic" style="width: 14px; height: 14px;"></i> Listening... (${context} - ${lang === 'el-GR' ? 'Ελληνικά' : 'English'})`;
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

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    stopListening() {
        this.isListening = false;
        
        const status = document.getElementById('voice-status');
        if (status) {
            status.style.display = 'none';
        }
        
        if (this.recognition) {
            this.recognition.stop();
        }
    }

    toggleDictation() {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Dictation system loading...');
    
    fetch('/api/check-ai-availability')
        .then(response => response.json())
        .then(data => {
            console.log('AI availability check result:', data);
            if (data.available) {
                console.log('Creating AI-enhanced DictationManager...');
                window.dictationManager = new AIDictationManager();
                console.log('AI DictationManager created successfully');
            } else if (!window.dictationManager) {
                console.log('AI not available, using basic DictationManager...');
                window.dictationManager = new AIDictationManager();
            }
        })
        .catch(error => {
            console.log('AI check failed, using basic DictationManager...', error);
            if (!window.dictationManager) {
                window.dictationManager = new AIDictationManager();
            }
        });
});

window.AIDictationManager = AIDictationManager;