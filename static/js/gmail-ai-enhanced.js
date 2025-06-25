/**
 * Enhanced Gmail AI JavaScript Integration
 * Provides advanced AI features for Gmail interface
 */

// Gmail AI Assistant - Integrated with unified FAB
class GmailAIAssistant {
    constructor() {
        this.currentLanguage = document.documentElement.lang || 'en';
        this.currentTone = 'professional';
        this.isProcessing = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadUserPreferences();
    }

    setupEventListeners() {
        // AI analysis buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-ai-action]')) {
                e.preventDefault();
                this.handleAIAction(e.target.dataset.aiAction, e.target);
            }
        });

        // Tone selector
        document.addEventListener('click', (e) => {
            if (e.target.matches('.tone-btn')) {
                this.setTone(e.target.dataset.tone);
            }
        });

        // Auto-analyze on compose
        const bodyField = document.getElementById('body');
        if (bodyField) {
            let timeout;
            bodyField.addEventListener('input', () => {
                clearTimeout(timeout);
                timeout = setTimeout(() => this.autoAnalyze(), 2000);
            });
        }
    }

    async handleAIAction(action, button) {
        if (this.isProcessing) return;

        this.isProcessing = true;
        this.showLoading(button, true);

        try {
            switch (action) {
                case 'analyze':
                    await this.analyzeEmail();
                    break;
                case 'suggest':
                    await this.suggestResponse();
                    break;
                case 'templates':
                    await this.loadTemplates();
                    break;
                case 'entities':
                    await this.extractEntities();
                    break;
                case 'translate':
                    await this.translateContent();
                    break;
            }
        } catch (error) {
            this.showError('AI operation failed', error.message);
        } finally {
            this.isProcessing = false;
            this.showLoading(button, false);
        }
    }

    async analyzeEmail() {
        const emailText = this.getEmailContent();
        if (!emailText.trim()) {
            this.showWarning('Please enter email content first');
            return;
        }

        const response = await fetch('/gmail/ai/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email_text: emailText,
                language: this.currentLanguage
            })
        });

        const data = await response.json();
        if (data.success) {
            this.displayAnalysis(data.analysis);
        } else {
            throw new Error(data.error || 'Analysis failed');
        }
    }

    async suggestResponse() {
        const emailText = this.getEmailContent();
        const context = this.getEmailContext();

        const response = await fetch('/gmail/ai/suggest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email_text: emailText,
                context: context,
                language: this.currentLanguage,
                tone: this.currentTone
            })
        });

        const data = await response.json();
        if (data.success) {
            this.displaySuggestion(data.suggestion);
        } else {
            throw new Error(data.error || 'Suggestion failed');
        }
    }

    async loadTemplates() {
        const emailText = this.getEmailContent();

        const response = await fetch('/gmail/ai/templates', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email_text: emailText,
                language: this.currentLanguage
            })
        });

        const data = await response.json();
        if (data.success) {
            this.displayTemplates(data.templates);
        } else {
            throw new Error(data.error || 'Template loading failed');
        }
    }

    async extractEntities() {
        const emailText = this.getFullEmailContent();

        const response = await fetch('/gmail/ai/extract-entities', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email_text: emailText })
        });

        const data = await response.json();
        if (data.success) {
            this.displayEntities(data.entities);
        } else {
            throw new Error(data.error || 'Entity extraction failed');
        }
    }

    displayAnalysis(analysis) {
        const container = this.getResultsContainer();
        container.innerHTML = `
            <div class="ai-result-box analysis">
                <h6><i data-feather="brain"></i> Email Analysis</h6>
                <div class="analysis-grid">
                    <div class="analysis-item">
                        <span class="label">Sentiment:</span>
                        <span class="value sentiment-${analysis.sentiment}">${this.capitalize(analysis.sentiment)}</span>
                    </div>
                    <div class="analysis-item">
                        <span class="label">Intent:</span>
                        <span class="value">${this.capitalize(analysis.intent)}</span>
                    </div>
                    <div class="analysis-item">
                        <span class="label">Urgency:</span>
                        <span class="value urgency-${analysis.urgency}">${this.capitalize(analysis.urgency)}</span>
                    </div>
                    <div class="analysis-item">
                        <span class="label">Confidence:</span>
                        <span class="value">${Math.round(analysis.confidence_score * 100)}%</span>
                    </div>
                </div>
                ${this.renderKeyInfo(analysis.key_info)}
                ${this.renderActionItems(analysis.action_items)}
            </div>
        `;
        this.refreshIcons();
    }

    displaySuggestion(suggestion) {
        const container = this.getResultsContainer();
        container.innerHTML = `
            <div class="ai-result-box suggestion">
                <h6><i data-feather="zap"></i> AI Suggestion</h6>
                <div class="suggestion-content">
                    <div class="suggestion-subject">
                        <strong>Subject:</strong>
                        <div class="suggestion-text">${suggestion.subject || 'No suggestion'}</div>
                    </div>
                    <div class="suggestion-body">
                        <strong>Response:</strong>
                        <div class="suggestion-text">${suggestion.response}</div>
                    </div>
                </div>
                <div class="suggestion-actions">
                    <button class="btn btn-success btn-sm" onclick="gmailAI.applySuggestion('${this.escapeHtml(suggestion.subject)}', \`${this.escapeHtml(suggestion.response)}\`)">
                        <i data-feather="check"></i> Apply
                    </button>
                    <button class="btn btn-outline-secondary btn-sm" onclick="gmailAI.provideFeedback('helpful')">
                        <i data-feather="thumbs-up"></i> Helpful
                    </button>
                    <button class="btn btn-outline-secondary btn-sm" onclick="gmailAI.provideFeedback('not_helpful')">
                        <i data-feather="thumbs-down"></i> Not Helpful
                    </button>
                </div>
            </div>
        `;
        this.refreshIcons();
    }

    displayTemplates(templates) {
        const container = this.getResultsContainer();
        
        if (!templates.templates || templates.templates.length === 0) {
            container.innerHTML = `
                <div class="ai-result-box info">
                    <p>No suitable templates found for this content.</p>
                </div>
            `;
            return;
        }

        let html = `
            <div class="ai-result-box templates">
                <h6><i data-feather="file-text"></i> Smart Templates</h6>
                <div class="templates-grid">
        `;

        templates.templates.forEach((template, index) => {
            html += `
                <div class="template-card" onclick="gmailAI.selectTemplate(${index})">
                    <div class="template-name">${template.name}</div>
                    <div class="template-use-case">${template.use_case}</div>
                    <div class="template-meta">
                        <span class="badge bg-light text-dark">${template.tone}</span>
                        <span class="badge bg-info">${template.category}</span>
                    </div>
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;

        container.innerHTML = html;
        window.currentTemplates = templates.templates;
    }

    displayEntities(entities) {
        const container = this.getResultsContainer();
        
        let html = `
            <div class="ai-result-box entities">
                <h6><i data-feather="link"></i> Business Entities</h6>
        `;

        if (entities.potential_customers && entities.potential_customers.length > 0) {
            html += `
                <div class="entity-section">
                    <strong>Potential Customers:</strong>
                    <div class="entity-list">
            `;
            entities.potential_customers.forEach(customer => {
                html += `
                    <div class="entity-item">
                        <div class="entity-name">${customer.name}</div>
                        <div class="entity-context">${customer.context}</div>
                        <div class="entity-confidence">${Math.round(customer.confidence * 100)}% confidence</div>
                    </div>
                `;
            });
            html += `</div></div>`;
        }

        if (entities.suggested_actions && entities.suggested_actions.length > 0) {
            html += `
                <div class="entity-section">
                    <strong>Suggested Actions:</strong>
                    <ul class="action-list">
            `;
            entities.suggested_actions.forEach(action => {
                html += `<li>${action}</li>`;
            });
            html += `</ul></div>`;
        }

        html += `</div>`;
        container.innerHTML = html;
    }

    applySuggestion(subject, response) {
        if (subject && subject !== 'No suggestion') {
            const subjectField = document.getElementById('subject');
            if (subjectField) subjectField.value = subject;
        }

        if (response) {
            const bodyField = document.getElementById('body');
            if (bodyField) bodyField.value = response;
        }

        this.showSuccess('Suggestion applied successfully');
    }

    selectTemplate(index) {
        if (!window.currentTemplates || !window.currentTemplates[index]) return;

        const template = window.currentTemplates[index];
        
        if (confirm(`Apply template: ${template.name}?`)) {
            const subjectField = document.getElementById('subject');
            const bodyField = document.getElementById('body');
            
            if (subjectField) subjectField.value = template.subject;
            if (bodyField) bodyField.value = template.body;
            
            this.showSuccess('Template applied');
        }
    }

    setTone(tone) {
        this.currentTone = tone;
        document.querySelectorAll('.tone-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tone === tone);
        });
    }

    getEmailContent() {
        const bodyField = document.getElementById('body');
        return bodyField ? bodyField.value : '';
    }

    getEmailContext() {
        const subjectField = document.getElementById('subject');
        const toField = document.getElementById('to');
        
        let context = '';
        if (subjectField) context += `Subject: ${subjectField.value}\n`;
        if (toField) context += `To: ${toField.value}\n`;
        
        return context;
    }

    getFullEmailContent() {
        const context = this.getEmailContext();
        const body = this.getEmailContent();
        return context + '\n' + body;
    }

    getResultsContainer() {
        let container = document.getElementById('ai-results');
        if (!container) {
            container = document.createElement('div');
            container.id = 'ai-results';
            document.body.appendChild(container);
        }
        return container;
    }

    showLoading(button, show) {
        if (button) {
            if (show) {
                button.disabled = true;
                button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
            } else {
                button.disabled = false;
                // Restore original content - in real implementation, store original content
                this.refreshIcons();
            }
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showWarning(message) {
        this.showNotification(message, 'warning');
    }

    showError(title, message) {
        this.showNotification(`${title}: ${message}`, 'danger');
    }

    showNotification(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alert.innerHTML = `
            <i data-feather="${type === 'success' ? 'check-circle' : type === 'warning' ? 'alert-triangle' : 'alert-circle'}" class="me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alert);
        this.refreshIcons();

        setTimeout(() => {
            if (alert.parentElement) {
                alert.remove();
            }
        }, 5000);
    }

    renderKeyInfo(keyInfo) {
        if (!keyInfo || Object.keys(keyInfo).length === 0) return '';
        
        let html = '<div class="key-info"><strong>Key Information:</strong><ul>';
        Object.entries(keyInfo).forEach(([key, value]) => {
            if (Array.isArray(value) && value.length > 0) {
                html += `<li><strong>${this.capitalize(key)}:</strong> ${value.join(', ')}</li>`;
            } else if (value) {
                html += `<li><strong>${this.capitalize(key)}:</strong> ${value}</li>`;
            }
        });
        html += '</ul></div>';
        return html;
    }

    renderActionItems(actionItems) {
        if (!actionItems || actionItems.length === 0) return '';
        
        let html = '<div class="action-items"><strong>Action Items:</strong><ul>';
        actionItems.forEach(item => {
            html += `<li>${item}</li>`;
        });
        html += '</ul></div>';
        return html;
    }

    capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    refreshIcons() {
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }

    loadUserPreferences() {
        // Load user preferences from localStorage or API
        const savedTone = localStorage.getItem('gmail-ai-tone');
        if (savedTone) {
            this.setTone(savedTone);
        }
    }

    async autoAnalyze() {
        // Auto-analyze email content when user stops typing
        const content = this.getEmailContent();
        if (content.length > 100) { // Only analyze substantial content
            try {
                await this.analyzeEmail();
            } catch (error) {
                console.log('Auto-analysis skipped:', error.message);
            }
        }
    }

    async provideFeedback(feedback) {
        // Implementation for user feedback
        console.log('Feedback provided:', feedback);
        this.showSuccess('Feedback recorded. Thank you!');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.includes('/gmail/')) {
        if (!window.gmailAI) {
            window.gmailAI = new GmailAIAssistant();
        }
    }
});

// CSS for AI features
const aiStyles = `
<style>
.ai-result-box {
    background: white;
    border: 1px solid #e3f2fd;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.analysis-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 0.5rem;
    margin: 0.5rem 0;
}

.analysis-item {
    display: flex;
    flex-direction: column;
    padding: 0.5rem;
    background: #f8f9fa;
    border-radius: 4px;
}

.analysis-item .label {
    font-size: 0.8rem;
    color: #6c757d;
    font-weight: 500;
}

.analysis-item .value {
    font-weight: bold;
    margin-top: 0.25rem;
}

.sentiment-positive { color: #28a745; }
.sentiment-negative { color: #dc3545; }
.sentiment-neutral { color: #6c757d; }

.urgency-high, .urgency-urgent { color: #dc3545; }
.urgency-medium { color: #fd7e14; }
.urgency-low { color: #28a745; }

.suggestion-content {
    margin: 0.5rem 0;
}

.suggestion-subject, .suggestion-body {
    margin-bottom: 0.75rem;
}

.suggestion-text {
    background: #f8f9fa;
    padding: 0.5rem;
    border-radius: 4px;
    margin-top: 0.25rem;
    border-left: 3px solid #007bff;
}

.suggestion-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
}

.templates-grid {
    display: grid;
    gap: 0.5rem;
    margin: 0.5rem 0;
}

.template-card {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 0.75rem;
    cursor: pointer;
    transition: all 0.2s ease;
}

.template-card:hover {
    background: #e3f2fd;
    border-color: #2196f3;
    transform: translateY(-1px);
}

.template-name {
    font-weight: bold;
    margin-bottom: 0.25rem;
}

.template-use-case {
    font-size: 0.875rem;
    color: #6c757d;
    margin-bottom: 0.5rem;
}

.template-meta {
    display: flex;
    gap: 0.25rem;
}

.entity-section {
    margin: 0.75rem 0;
}

.entity-list {
    margin: 0.5rem 0;
}

.entity-item {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    padding: 0.5rem;
    margin: 0.25rem 0;
}

.entity-name {
    font-weight: bold;
}

.entity-context {
    font-size: 0.875rem;
    color: #6c757d;
}

.entity-confidence {
    font-size: 0.75rem;
    color: #007bff;
}

.action-list {
    margin: 0.5rem 0;
}

.action-list li {
    margin: 0.25rem 0;
    font-size: 0.875rem;
}

.key-info, .action-items {
    margin: 0.75rem 0;
    padding: 0.5rem;
    background: #f8f9fa;
    border-radius: 4px;
}

.key-info ul, .action-items ul {
    margin: 0.25rem 0 0 0;
    padding-left: 1.5rem;
}

.tone-btn {
    padding: 0.25rem 0.75rem;
    border: 1px solid #dee2e6;
    border-radius: 15px;
    background: white;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.875rem;
}

.tone-btn.active {
    background: #007bff;
    color: white;
    border-color: #007bff;
}

.tone-btn:hover:not(.active) {
    background: #f8f9fa;
    border-color: #adb5bd;
}
</style>
`;

// Inject styles
document.head.insertAdjacentHTML('beforeend', aiStyles);