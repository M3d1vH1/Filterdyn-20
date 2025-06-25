/**
 * Global Dictation System
 * Provides speech recognition capabilities across the application
 */

class DictationManager {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.currentField = null;
        this.floatingButton = null;
        this.init();
    }

    init() {
        this.initializeSpeechRecognition();
        this.createFloatingButton();
        this.setupEventListeners();
    }

    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            
            this.recognition.onresult = (event) => this.handleResult(event);
            this.recognition.onerror = (event) => this.handleError(event);
            this.recognition.onend = () => this.stopListening();
            
            return true;
        }
        return false;
    }

    createFloatingButton() {
        // Only create if not already exists
        if (document.getElementById('floating-dictation-btn')) {
            console.log('Floating dictation button already exists');
            return;
        }

        console.log('Creating floating dictation button...');
        this.floatingButton = document.createElement('div');
        this.floatingButton.id = 'floating-dictation-btn';
        this.floatingButton.className = 'floating-dictation-btn';
        this.floatingButton.innerHTML = `
            <div class="dictation-btn-content">
                <i data-feather="mic" class="dictation-icon"></i>
                <i data-feather="mic-off" class="dictation-icon-off" style="display: none;"></i>
                <span class="dictation-tooltip">Voice Input</span>
            </div>
        `;

        // Add CSS styles
        const style = document.createElement('style');
        style.textContent = `
            .floating-dictation-btn {
                position: fixed;
                bottom: 20px;
                left: 20px;
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, #28a745, #20c997);
                border-radius: 50%;
                box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
                cursor: pointer;
                z-index: 1000;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .floating-dictation-btn:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 16px rgba(40, 167, 69, 0.4);
            }

            .floating-dictation-btn.listening {
                background: linear-gradient(135deg, #dc3545, #fd7e14);
                animation: dictation-pulse 1.5s infinite;
            }

            .dictation-btn-content {
                position: relative;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .dictation-tooltip {
                position: absolute;
                right: 70px;
                top: 50%;
                transform: translateY(-50%);
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                white-space: nowrap;
                opacity: 0;
                pointer-events: none;
                transition: opacity 0.3s ease;
            }

            .floating-dictation-btn:hover .dictation-tooltip {
                opacity: 1;
            }

            @keyframes dictation-pulse {
                0% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.7; transform: scale(1.05); }
                100% { opacity: 1; transform: scale(1); }
            }

            .dictation-status {
                position: fixed;
                bottom: 90px;
                left: 20px;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 10px 15px;
                border-radius: 20px;
                font-size: 14px;
                z-index: 1001;
                display: none;
                animation: dictation-pulse 1.5s infinite;
            }

            @media (max-width: 768px) {
                .floating-dictation-btn {
                    width: 50px;
                    height: 50px;
                    bottom: 15px;
                    left: 15px;
                }
                
                .dictation-tooltip {
                    display: none;
                }
            }
        `;
        document.head.appendChild(style);

        // Create status indicator
        const statusDiv = document.createElement('div');
        statusDiv.id = 'dictation-status';
        statusDiv.className = 'dictation-status';
        statusDiv.innerHTML = '<i data-feather="mic" style="width: 14px; height: 14px;"></i> Listening...';

        document.body.appendChild(this.floatingButton);
        document.body.appendChild(statusDiv);

        // Refresh feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }

    setupEventListeners() {
        if (this.floatingButton) {
            this.floatingButton.addEventListener('click', () => this.toggleDictation());
        }

        // Auto-detect focused input fields
        document.addEventListener('focusin', (e) => {
            if (e.target.matches('input[type="text"], textarea, input[type="search"]')) {
                this.currentField = e.target;
            }
        });

        document.addEventListener('focusout', (e) => {
            if (e.target === this.currentField) {
                setTimeout(() => {
                    if (document.activeElement !== this.currentField) {
                        this.currentField = null;
                    }
                }, 100);
            }
        });
    }

    toggleDictation() {
        if (!this.recognition) {
            this.showError('Speech recognition not supported in this browser');
            return;
        }

        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    startListening() {
        if (!this.recognition || this.isListening) return;

        this.isListening = true;
        this.updateButtonState();
        
        // Show status
        const status = document.getElementById('dictation-status');
        if (status) {
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

    stopListening() {
        if (!this.recognition) return;

        this.isListening = false;
        this.updateButtonState();

        // Hide status
        const status = document.getElementById('dictation-status');
        if (status) {
            status.style.display = 'none';
        }

        try {
            this.recognition.stop();
        } catch (error) {
            // Ignore errors when stopping
        }
    }

    handleResult(event) {
        const transcript = event.results[0][0].transcript;
        
        if (this.currentField) {
            // Insert into focused field
            if (this.currentField.value) {
                this.currentField.value += ' ' + transcript;
            } else {
                this.currentField.value = transcript;
            }
            this.currentField.dispatchEvent(new Event('input', { bubbles: true }));
            this.showSuccess('Text inserted successfully');
        } else {
            // Check if we're on a task creation page or can find suitable fields
            const isTaskPage = window.location.pathname.includes('/tasks/create') || 
                             document.getElementById('title') || 
                             document.getElementById('description');
            
            if (isTaskPage) {
                this.parseTaskDictation(transcript);
            } else {
                // Try to find a suitable input field automatically
                const possibleFields = document.querySelectorAll('input[type="text"], input[type="search"], textarea');
                if (possibleFields.length > 0) {
                    // Use the first visible input field
                    for (let field of possibleFields) {
                        if (field.offsetParent !== null && !field.disabled && !field.readonly) {
                            field.value = transcript;
                            field.dispatchEvent(new Event('input', { bubbles: true }));
                            this.showSuccess('Text inserted into ' + (field.placeholder || 'input field'));
                            this.stopListening();
                            return;
                        }
                    }
                }
                this.showError('No suitable input field found. Please click on a text field first, or use this on a task creation page.');
            }
        }
        
        this.stopListening();
    }

    parseTaskDictation(transcript) {
        const text = transcript.toLowerCase();
        let parsed = false;

        // Extract title
        const titleMatch = text.match(/title[:\s]+(.+?)(?:\s+description|\s+priority|\s+assign|\s*$)/i);
        if (titleMatch) {
            const titleField = document.getElementById('title');
            if (titleField) {
                titleField.value = this.capitalizeFirst(titleMatch[1].trim());
                titleField.dispatchEvent(new Event('input', { bubbles: true }));
                parsed = true;
            }
        }

        // Extract description
        const descMatch = text.match(/description[:\s]+(.+?)(?:\s+priority|\s+assign|\s*$)/i);
        if (descMatch) {
            const descField = document.getElementById('description');
            if (descField) {
                descField.value = this.capitalizeFirst(descMatch[1].trim());
                descField.dispatchEvent(new Event('input', { bubbles: true }));
                parsed = true;
            }
        }

        // Extract priority
        const priorityMatch = text.match(/priority[:\s]+(low|medium|high|urgent)/i);
        if (priorityMatch) {
            const priorityField = document.getElementById('priority');
            if (priorityField) {
                priorityField.value = priorityMatch[1].toLowerCase();
                priorityField.dispatchEvent(new Event('change', { bubbles: true }));
                parsed = true;
            }
        }

        // Extract assignee (try multiple patterns)
        const assigneeMatch = text.match(/assign(?:\s+to)?[:\s]+(.+?)(?:\s+title|\s+description|\s+priority|\s*$)/i) ||
                             text.match(/assigned?\s+to[:\s]+(.+?)(?:\s+title|\s+description|\s+priority|\s*$)/i);
        if (assigneeMatch) {
            const assigneeField = document.getElementById('assigned_to');
            if (assigneeField) {
                // If it's a select field, try to find matching option
                const assigneeName = assigneeMatch[1].trim();
                const options = assigneeField.querySelectorAll('option');
                let found = false;
                
                for (let option of options) {
                    if (option.text.toLowerCase().includes(assigneeName.toLowerCase())) {
                        assigneeField.value = option.value;
                        assigneeField.dispatchEvent(new Event('change', { bubbles: true }));
                        found = true;
                        break;
                    }
                }
                
                if (found) {
                    parsed = true;
                } else {
                    this.showError(`Could not find user "${assigneeName}" in assignee list`);
                }
            }
        }

        if (parsed) {
            this.showSuccess('Task details filled from voice input!');
        } else {
            this.showError('Could not parse task information. Try: "Title: [task name], Description: [details], Priority: [low/medium/high/urgent], Assign to: [username]"');
        }
    }

    handleError(event) {
        console.error('Speech recognition error:', event.error);
        this.stopListening();
        
        let message = 'Voice recognition error';
        switch (event.error) {
            case 'network':
                message = 'Network error. Check your connection.';
                break;
            case 'not-allowed':
                message = 'Microphone access denied. Please allow microphone access.';
                break;
            case 'no-speech':
                message = 'No speech detected. Try speaking again.';
                break;
            default:
                message = 'Voice recognition error. Please try again.';
        }
        
        this.showError(message);
    }

    updateButtonState() {
        if (!this.floatingButton) return;

        const button = this.floatingButton;
        const micIcon = button.querySelector('.dictation-icon');
        const micOffIcon = button.querySelector('.dictation-icon-off');
        const tooltip = button.querySelector('.dictation-tooltip');

        if (this.isListening) {
            button.classList.add('listening');
            micIcon.style.display = 'none';
            micOffIcon.style.display = 'inline';
            tooltip.textContent = 'Stop Listening';
        } else {
            button.classList.remove('listening');
            micIcon.style.display = 'inline';
            micOffIcon.style.display = 'none';
            tooltip.textContent = 'Voice Input';
        }

        // Refresh feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }

    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showNotification(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show position-fixed`;
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alert.innerHTML = `
            <i data-feather="${type === 'error' ? 'alert-circle' : 'check-circle'}" class="me-2"></i>
            ${message}
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
        }, type === 'error' ? 5000 : 3000);
    }
}

// Initialize dictation manager when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dictation system loading...');
    
    // Only initialize if not already done
    if (!window.dictationManager) {
        console.log('Creating new DictationManager...');
        window.dictationManager = new DictationManager();
        console.log('DictationManager created successfully');
    } else {
        console.log('DictationManager already exists');
    }
});
});

// Export for global access
window.DictationManager = DictationManager;