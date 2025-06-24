/**
 * Gmail Interface JavaScript
 * Handles email management, AI features, and user interactions
 */

class GmailInterface {
    constructor() {
        this.currentAccountId = null;
        this.currentFilter = 'all';
        this.currentPage = 1;
        this.selectedThreadId = null;
        this.searchTimeout = null;
        this.autoSyncInterval = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadInitialData();
        this.startAutoSync();
        
        // Initialize Feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }
    
    bindEvents() {
        // Account selector
        $('#account-selector').on('change', (e) => {
            this.currentAccountId = parseInt(e.target.value);
            this.loadThreads();
        });
        
        // Filter buttons
        $('.gmail-filters .list-group-item').on('click', (e) => {
            e.preventDefault();
            const filter = $(e.currentTarget).data('filter');
            this.setFilter(filter);
        });
        
        // Sync button
        $('#sync-emails').on('click', () => {
            this.syncEmails();
        });
        
        // Search
        $('#search-input').on('input', (e) => {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.searchEmails(e.target.value);
            }, 500);
        });
        
        $('#search-btn').on('click', () => {
            const query = $('#search-input').val();
            this.searchEmails(query);
        });
        
        // Detail panel controls
        $('#close-detail').on('click', () => {
            this.closeDetailPanel();
        });
        
        $('#reply-btn').on('click', () => {
            this.composeReply();
        });
        
        $('#forward-btn').on('click', () => {
            this.composeForward();
        });
        
        // Associate customer
        $('#associate-customer').on('click', () => {
            this.showAssociateCustomerModal();
        });
        
        $('#confirm-associate').on('click', () => {
            this.associateCustomer();
        });
        
        // AI suggestions
        $('#ai-suggest').on('click', () => {
            this.showAISuggestions();
        });
        
        // Quick actions
        $('#mark-all-read').on('click', () => {
            this.markAllRead();
        });
        
        $('#archive-selected').on('click', () => {
            this.archiveSelected();
        });
        
        // Create task from email
        $('#create-task').on('click', () => {
            this.createTaskFromEmail();
        });
    }
    
    loadInitialData() {
        // Get first account ID
        const firstOption = $('#account-selector option:first');
        if (firstOption.length) {
            this.currentAccountId = parseInt(firstOption.val());
            this.loadThreads();
            this.loadCustomers();
        }
    }
    
    async loadThreads() {
        if (!this.currentAccountId) return;
        
        this.showLoading();
        
        try {
            const response = await fetch(`/gmail/api/threads/${this.currentAccountId}?page=${this.currentPage}`);
            const data = await response.json();
            
            if (data.success) {
                this.renderThreads(data.threads);
                this.renderPagination(data.pagination);
                this.updateCounts(data.threads);
            } else {
                this.showError('Failed to load emails');
            }
        } catch (error) {
            console.error('Error loading threads:', error);
            this.showError('Network error loading emails');
        }
        
        this.hideLoading();
    }
    
    renderThreads(threads) {
        const container = $('#email-threads');
        container.empty();
        
        if (threads.length === 0) {
            this.showEmptyState();
            return;
        }
        
        threads.forEach(thread => {
            if (this.shouldShowThread(thread)) {
                const threadElement = this.createThreadElement(thread);
                container.append(threadElement);
            }
        });
        
        // Bind click events to threads
        $('.email-thread').on('click', (e) => {
            const threadId = parseInt($(e.currentTarget).data('thread-id'));
            this.selectThread(threadId);
        });
        
        this.hideEmptyState();
        
        // Update Feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }
    
    createThreadElement(thread) {
        const isUnread = thread.has_unread;
        const sentimentColor = thread.sentiment === 'positive' ? 'positive' : 
                              thread.sentiment === 'negative' ? 'negative' : 'neutral';
        
        const categoryClass = thread.category ? thread.category.replace('_', '-') : 'general';
        
        return $(`
            <div class="email-thread ${isUnread ? 'unread' : ''}" data-thread-id="${thread.id}">
                <div class="email-thread-header">
                    <div class="email-sender">${this.escapeHtml(thread.participants[0] || 'Unknown')}</div>
                    <div class="email-date">${this.formatDate(thread.last_message_date)}</div>
                </div>
                <div class="email-subject">${this.escapeHtml(thread.subject || '(No Subject)')}</div>
                <div class="email-preview">${this.escapeHtml(thread.preview || '')}</div>
                <div class="email-meta">
                    ${thread.category ? `<span class="email-category ${categoryClass}">${thread.category.replace('_', ' ')}</span>` : ''}
                    <span class="badge bg-light text-dark">${thread.message_count}</span>
                    ${thread.customer_id ? '<i data-feather="user" class="text-success" title="Associated with customer"></i>' : ''}
                    ${thread.is_important ? '<i data-feather="star" class="text-warning" title="Important"></i>' : ''}
                    <div class="email-sentiment ${sentimentColor}" title="Sentiment: ${thread.sentiment || 'neutral'}"></div>
                </div>
            </div>
        `);
    }
    
    shouldShowThread(thread) {
        switch (this.currentFilter) {
            case 'unread':
                return thread.has_unread;
            case 'important':
                return thread.is_important;
            case 'customer_inquiry':
            case 'quote_request':
            case 'technical_support':
                return thread.category === this.currentFilter;
            case 'all':
            default:
                return true;
        }
    }
    
    async selectThread(threadId) {
        // Update UI
        $('.email-thread').removeClass('selected');
        $(`.email-thread[data-thread-id="${threadId}"]`).addClass('selected');
        
        this.selectedThreadId = threadId;
        
        // Load thread messages
        try {
            const response = await fetch(`/gmail/api/thread/${threadId}/messages`);
            const data = await response.json();
            
            if (data.success) {
                this.renderThreadMessages(data.thread, data.messages);
                this.showDetailPanel();
            } else {
                this.showError('Failed to load thread messages');
            }
        } catch (error) {
            console.error('Error loading thread messages:', error);
            this.showError('Network error loading messages');
        }
    }
    
    renderThreadMessages(thread, messages) {
        const container = $('#email-messages');
        container.empty();
        
        // Thread info
        const threadInfo = $(`
            <div class="thread-info mb-3">
                <h5>${this.escapeHtml(thread.subject || '(No Subject)')}</h5>
                <div class="thread-meta">
                    <span class="badge bg-secondary">${messages.length} messages</span>
                    ${thread.customer_id ? '<span class="badge bg-success">Customer Associated</span>' : ''}
                    ${thread.quote_id ? '<span class="badge bg-info">Quote Associated</span>' : ''}
                    ${thread.order_id ? '<span class="badge bg-warning">Order Associated</span>' : ''}
                </div>
            </div>
        `);
        container.append(threadInfo);
        
        // Messages
        messages.forEach(message => {
            const messageElement = this.createMessageElement(message);
            container.append(messageElement);
        });
        
        // Update Feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }
    
    createMessageElement(message) {
        const hasAttachments = message.attachments && message.attachments.length > 0;
        
        let aiAnalysis = '';
        if (message.ai_category || message.ai_sentiment || message.ai_summary) {
            aiAnalysis = `
                <div class="ai-analysis">
                    <h6><i data-feather="zap" style="width: 16px; height: 16px;"></i> AI Analysis</h6>
                    <div class="ai-tags">
                        ${message.ai_category ? `<span class="ai-tag">${message.ai_category}</span>` : ''}
                        ${message.ai_sentiment ? `<span class="ai-tag">${message.ai_sentiment}</span>` : ''}
                    </div>
                    ${message.ai_summary ? `<div class="ai-summary">${this.escapeHtml(message.ai_summary)}</div>` : ''}
                </div>
            `;
        }
        
        return $(`
            <div class="email-message" data-message-id="${message.id}">
                <div class="email-message-header">
                    <div class="email-message-sender">${this.escapeHtml(message.sender)}</div>
                    <div class="email-message-meta">
                        <span>To: ${this.escapeHtml(message.recipient)}</span>
                        <span>${this.formatDateTime(message.received_date)}</span>
                    </div>
                </div>
                ${aiAnalysis}
                <div class="email-message-body">
                    ${message.body_html || this.escapeHtml(message.body_text || '').replace(/\n/g, '<br>')}
                </div>
                ${hasAttachments ? this.renderAttachments(message.attachments) : ''}
            </div>
        `);
    }
    
    renderAttachments(attachments) {
        const attachmentList = attachments.map(att => 
            `<a href="/gmail/api/attachment/${att.id}" class="email-attachment" target="_blank">
                <i data-feather="paperclip" style="width: 14px; height: 14px;" class="me-1"></i>
                ${this.escapeHtml(att.filename)} (${this.formatFileSize(att.size)})
            </a>`
        ).join('');
        
        return `
            <div class="email-attachments-list">
                <strong>Attachments:</strong><br>
                ${attachmentList}
            </div>
        `;
    }
    
    async syncEmails() {
        if (!this.currentAccountId) return;
        
        const syncBtn = $('#sync-emails');
        const originalHtml = syncBtn.html();
        
        syncBtn.prop('disabled', true).html('<i data-feather="refresh-cw" class="me-1 spinning"></i> Syncing...');
        
        try {
            const response = await fetch(`/gmail/api/sync/${this.currentAccountId}`);
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess(`Synced ${data.synced_count} new emails`);
                this.loadThreads(); // Reload threads
            } else {
                this.showError(`Sync failed: ${data.error}`);
            }
        } catch (error) {
            console.error('Sync error:', error);
            this.showError('Network error during sync');
        }
        
        syncBtn.prop('disabled', false).html(originalHtml);
        
        // Update Feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }
    
    async searchEmails(query) {
        if (!query.trim()) {
            this.loadThreads();
            return;
        }
        
        if (!this.currentAccountId) return;
        
        try {
            const response = await fetch(`/gmail/api/search/${this.currentAccountId}?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.success) {
                this.renderSearchResults(data.results);
            } else {
                this.showError('Search failed');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Network error during search');
        }
    }
    
    renderSearchResults(results) {
        const container = $('#email-threads');
        container.empty();
        
        if (results.length === 0) {
            container.append('<div class="text-center py-4 text-muted">No results found</div>');
            return;
        }
        
        results.forEach(result => {
            const resultElement = $(`
                <div class="email-thread" data-thread-id="${result.thread_id}">
                    <div class="email-thread-header">
                        <div class="email-sender">${this.escapeHtml(result.sender)}</div>
                        <div class="email-date">${this.formatDate(result.received_date)}</div>
                    </div>
                    <div class="email-subject">${this.escapeHtml(result.subject || '(No Subject)')}</div>
                    <div class="email-preview">${this.escapeHtml(result.preview)}</div>
                </div>
            `);
            container.append(resultElement);
        });
        
        // Bind click events
        $('.email-thread').on('click', (e) => {
            const threadId = parseInt($(e.currentTarget).data('thread-id'));
            this.selectThread(threadId);
        });
    }
    
    setFilter(filter) {
        this.currentFilter = filter;
        this.currentPage = 1;
        
        // Update UI
        $('.gmail-filters .list-group-item').removeClass('active');
        $(`.gmail-filters .list-group-item[data-filter="${filter}"]`).addClass('active');
        
        this.loadThreads();
    }
    
    async showAssociateCustomerModal() {
        if (!this.selectedThreadId) return;
        
        // Load customers if not already loaded
        await this.loadCustomers();
        
        $('#associateCustomerModal').modal('show');
    }
    
    async loadCustomers() {
        try {
            const response = await fetch('/api/customers');
            const data = await response.json();
            
            if (data.success) {
                const select = $('#customer-select');
                select.empty().append('<option value="">Choose a customer...</option>');
                
                data.customers.forEach(customer => {
                    select.append(`<option value="${customer.id}">${this.escapeHtml(customer.name)}</option>`);
                });
            }
        } catch (error) {
            console.error('Error loading customers:', error);
        }
    }
    
    async associateCustomer() {
        const customerId = $('#customer-select').val();
        if (!customerId || !this.selectedThreadId) return;
        
        try {
            const response = await fetch('/gmail/api/associate-customer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    thread_id: this.selectedThreadId,
                    customer_id: parseInt(customerId)
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Customer associated successfully');
                $('#associateCustomerModal').modal('hide');
                this.loadThreads(); // Refresh thread list
            } else {
                this.showError('Failed to associate customer');
            }
        } catch (error) {
            console.error('Error associating customer:', error);
            this.showError('Network error');
        }
    }
    
    async showAISuggestions() {
        if (!this.selectedThreadId) return;
        
        // Get the latest message in the thread
        const latestMessage = $('#email-messages .email-message:last');
        const messageId = latestMessage.data('message-id');
        
        if (!messageId) return;
        
        const modal = $('#aiSuggestionsModal');
        const content = $('#ai-suggestions-content');
        
        content.html('<div class="text-center"><div class="spinner-border" role="status"></div><div class="mt-2">Generating AI suggestions...</div></div>');
        modal.modal('show');
        
        try {
            const response = await fetch('/gmail/api/ai/suggest-response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message_id: messageId
                })
            });
            
            const data = await response.json();
            
            if (data.success && data.suggestions) {
                this.renderAISuggestions(data.suggestions);
            } else {
                content.html(`<div class="alert alert-warning">
                    <i data-feather="alert-triangle" class="me-2"></i>
                    ${data.fallback || 'No suggestions available'}
                </div>`);
            }
        } catch (error) {
            console.error('Error getting AI suggestions:', error);
            content.html('<div class="alert alert-danger">Error generating suggestions</div>');
        }
        
        // Update Feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }
    
    renderAISuggestions(suggestions) {
        const content = $('#ai-suggestions-content');
        content.empty();
        
        suggestions.forEach((suggestion, index) => {
            const suggestionElement = $(`
                <div class="card mb-3">
                    <div class="card-header">
                        <h6 class="mb-0">${suggestion.type.charAt(0).toUpperCase() + suggestion.type.slice(1)} Response</h6>
                    </div>
                    <div class="card-body">
                        <textarea class="form-control" rows="8" readonly>${suggestion.content}</textarea>
                        <div class="mt-2">
                            <button class="btn btn-primary btn-sm use-suggestion-btn" data-content="${this.escapeHtml(suggestion.content)}">
                                Use This Response
                            </button>
                            <button class="btn btn-outline-secondary btn-sm copy-suggestion-btn" data-content="${this.escapeHtml(suggestion.content)}">
                                Copy to Clipboard
                            </button>
                        </div>
                    </div>
                </div>
            `);
            content.append(suggestionElement);
        });
        
        // Bind events
        $('.use-suggestion-btn').on('click', (e) => {
            const content = $(e.target).data('content');
            this.useSuggestion(content);
        });
        
        $('.copy-suggestion-btn').on('click', (e) => {
            const content = $(e.target).data('content');
            this.copyToClipboard(content);
        });
    }
    
    useSuggestion(content) {
        // Open compose window with suggestion
        const composeUrl = `/gmail/compose?reply_to=${this.selectedThreadId}&suggestion=${encodeURIComponent(content)}`;
        window.open(composeUrl, '_blank');
        $('#aiSuggestionsModal').modal('hide');
    }
    
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showSuccess('Copied to clipboard');
        }).catch(err => {
            console.error('Error copying to clipboard:', err);
            this.showError('Failed to copy to clipboard');
        });
    }
    
    composeReply() {
        if (this.selectedThreadId) {
            const url = `/gmail/compose?reply_to=${this.selectedThreadId}`;
            window.open(url, '_blank');
        }
    }
    
    composeForward() {
        if (this.selectedThreadId) {
            const url = `/gmail/compose?forward=${this.selectedThreadId}`;
            window.open(url, '_blank');
        }
    }
    
    createTaskFromEmail() {
        if (!this.selectedThreadId) return;
        
        // Get thread subject for task title
        const subject = $('.thread-info h5').text();
        const url = `/tasks/create?from_email=${this.selectedThreadId}&title=${encodeURIComponent(subject)}`;
        window.open(url, '_blank');
    }
    
    async markAllRead() {
        // Implementation for marking all emails as read
        this.showInfo('Mark all read functionality would be implemented here');
    }
    
    async archiveSelected() {
        // Implementation for archiving selected emails
        this.showInfo('Archive selected functionality would be implemented here');
    }
    
    updateCounts(threads) {
        let unreadCount = 0;
        let importantCount = 0;
        let inquiryCount = 0;
        let quoteCount = 0;
        let supportCount = 0;
        
        threads.forEach(thread => {
            if (thread.has_unread) unreadCount++;
            if (thread.is_important) importantCount++;
            if (thread.category === 'customer_inquiry') inquiryCount++;
            if (thread.category === 'quote_request') quoteCount++;
            if (thread.category === 'technical_support') supportCount++;
        });
        
        $('#unread-count').text(unreadCount);
        $('#unread-filter-count').text(unreadCount);
        $('#all-count').text(threads.length);
        $('#important-count').text(importantCount);
        $('#inquiry-count').text(inquiryCount);
        $('#quote-count').text(quoteCount);
        $('#support-count').text(supportCount);
    }
    
    renderPagination(pagination) {
        const container = $('#pagination-container');
        container.empty();
        
        if (pagination.pages <= 1) return;
        
        const paginationElement = $(`
            <nav aria-label="Email pagination">
                <ul class="pagination">
                    <li class="page-item ${!pagination.has_prev ? 'disabled' : ''}">
                        <a class="page-link" href="#" data-page="${pagination.page - 1}">Previous</a>
                    </li>
                </ul>
            </nav>
        `);
        
        const pageList = paginationElement.find('.pagination');
        
        // Add page numbers
        const startPage = Math.max(1, pagination.page - 2);
        const endPage = Math.min(pagination.pages, pagination.page + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            const pageItem = $(`
                <li class="page-item ${i === pagination.page ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `);
            pageList.append(pageItem);
        }
        
        // Next button
        pageList.append(`
            <li class="page-item ${!pagination.has_next ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${pagination.page + 1}">Next</a>
            </li>
        `);
        
        container.append(paginationElement);
        
        // Bind pagination events
        $('.page-link').on('click', (e) => {
            e.preventDefault();
            const page = parseInt($(e.target).data('page'));
            if (page && page !== this.currentPage) {
                this.currentPage = page;
                this.loadThreads();
            }
        });
    }
    
    showDetailPanel() {
        $('#email-detail').removeClass('d-none');
    }
    
    closeDetailPanel() {
        $('#email-detail').addClass('d-none');
        $('.email-thread').removeClass('selected');
        this.selectedThreadId = null;
    }
    
    showLoading() {
        $('#loading-state').show();
        $('#empty-state').hide();
        $('#email-threads').hide();
    }
    
    hideLoading() {
        $('#loading-state').hide();
        $('#email-threads').show();
    }
    
    showEmptyState() {
        $('#empty-state').removeClass('d-none').show();
        $('#email-threads').hide();
    }
    
    hideEmptyState() {
        $('#empty-state').addClass('d-none').hide();
        $('#email-threads').show();
    }
    
    startAutoSync() {
        // Auto-sync every 5 minutes
        this.autoSyncInterval = setInterval(() => {
            if (this.currentAccountId) {
                this.syncEmails();
            }
        }, 5 * 60 * 1000);
    }
    
    // Utility functions
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        const now = new Date();
        
        if (date.toDateString() === now.toDateString()) {
            return date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        } else {
            return date.toLocaleDateString();
        }
    }
    
    formatDateTime(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleString();
    }
    
    formatFileSize(bytes) {
        if (!bytes) return '0 B';
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }
    
    showSuccess(message) {
        this.showToast(message, 'success');
    }
    
    showError(message) {
        this.showToast(message, 'error');
    }
    
    showInfo(message) {
        this.showToast(message, 'info');
    }
    
    showToast(message, type) {
        // Use existing toast system or create a simple one
        const toastClass = type === 'success' ? 'alert-success' : 
                          type === 'error' ? 'alert-danger' : 'alert-info';
        
        const toast = $(`
            <div class="alert ${toastClass} alert-dismissible fade show position-fixed" 
                 style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);
        
        $('body').append(toast);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            toast.alert('close');
        }, 5000);
    }
}

// Initialize Gmail interface when DOM is ready
$(document).ready(() => {
    window.gmailInterface = new GmailInterface();
});

// Add CSS for spinning animation
const style = document.createElement('style');
style.textContent = `
    .spinning {
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);