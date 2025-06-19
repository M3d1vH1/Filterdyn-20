// Filterdyn Operations Suite - Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide flash messages
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Confirm delete actions
    document.querySelectorAll('[data-confirm-delete]').forEach(function(element) {
        element.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
                return false;
            }
        });
    });

    // Auto-resize textareas
    document.querySelectorAll('textarea[data-auto-resize]').forEach(function(textarea) {
        function resize() {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        }
        textarea.addEventListener('input', resize);
        resize();
    });

    // Initialize date pickers
    initializeDatePickers();
    
    // Initialize quote/order item management
    initializeItemManagement();
    
    // Initialize product search
    initializeProductSearch();
    
    // Initialize form validation
    initializeFormValidation();
});

// Date picker initialization
function initializeDatePickers() {
    var dateInputs = document.querySelectorAll('input[type="date"], input[type="datetime-local"]');
    dateInputs.forEach(function(input) {
        // Add calendar icon
        var wrapper = document.createElement('div');
        wrapper.className = 'input-group';
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);
        
        var iconSpan = document.createElement('span');
        iconSpan.className = 'input-group-text';
        iconSpan.innerHTML = '<i data-feather="calendar"></i>';
        wrapper.appendChild(iconSpan);
    });
}

// Quote/Order item management
function initializeItemManagement() {
    var addItemBtn = document.getElementById('add-item-btn');
    var itemsContainer = document.getElementById('items-container');
    
    if (addItemBtn && itemsContainer) {
        addItemBtn.addEventListener('click', function() {
            showAddItemModal();
        });
        
        // Handle item deletion
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('delete-item-btn')) {
                var itemId = e.target.dataset.itemId;
                deleteItem(itemId);
            }
        });
    }
}

// Product search functionality
function initializeProductSearch() {
    var productSearch = document.getElementById('product-search');
    var productResults = document.getElementById('product-results');
    
    if (productSearch && productResults) {
        var searchTimeout;
        
        productSearch.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            var query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(function() {
                    searchProducts(query);
                }, 300);
            } else {
                productResults.innerHTML = '';
                productResults.style.display = 'none';
            }
        });
        
        // Hide results when clicking outside
        document.addEventListener('click', function(e) {
            if (!productSearch.contains(e.target) && !productResults.contains(e.target)) {
                productResults.style.display = 'none';
            }
        });
    }
}

// Search products via API
function searchProducts(query) {
    fetch('/api/products/search?q=' + encodeURIComponent(query))
        .then(response => response.json())
        .then(products => {
            var resultsHtml = '';
            
            if (products.length === 0) {
                resultsHtml = '<div class="dropdown-item-text text-muted">No products found</div>';
            } else {
                products.forEach(function(product) {
                    resultsHtml += `
                        <a href="#" class="dropdown-item product-result" 
                           data-product-id="${product.id}"
                           data-product-code="${product.code}"
                           data-product-name="${product.name}"
                           data-product-price="${product.price}"
                           data-product-unit="${product.unit}">
                            <strong>${product.code}</strong> - ${product.name}
                            <br><small class="text-muted">€${product.price} / ${product.unit}</small>
                        </a>
                    `;
                });
            }
            
            var productResults = document.getElementById('product-results');
            productResults.innerHTML = resultsHtml;
            productResults.style.display = 'block';
            
            // Handle product selection
            document.querySelectorAll('.product-result').forEach(function(element) {
                element.addEventListener('click', function(e) {
                    e.preventDefault();
                    selectProduct(this);
                });
            });
        })
        .catch(error => {
            console.error('Error searching products:', error);
        });
}

// Select product from search results
function selectProduct(element) {
    var modal = document.getElementById('addItemModal');
    var form = modal.querySelector('form');
    
    form.querySelector('#product_id').value = element.dataset.productId;
    form.querySelector('#description').value = element.dataset.productName;
    form.querySelector('#unit_price').value = element.dataset.productPrice;
    form.querySelector('#quantity').focus();
    
    document.getElementById('product-search').value = '';
    document.getElementById('product-results').style.display = 'none';
}

// Show add item modal
function showAddItemModal() {
    var modal = new bootstrap.Modal(document.getElementById('addItemModal'));
    modal.show();
    
    // Reset form
    var form = document.getElementById('add-item-form');
    form.reset();
    
    // Focus on description field
    setTimeout(function() {
        document.getElementById('description').focus();
    }, 300);
}

// Add item to quote/order
function addItem(formData) {
    var quoteId = document.querySelector('[data-quote-id]')?.dataset.quoteId;
    var orderId = document.querySelector('[data-order-id]')?.dataset.orderId;
    
    var url = quoteId ? `/api/quote-items/${quoteId}` : `/api/order-items/${orderId}`;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload(); // Reload to update totals
        } else {
            alert('Error adding item');
        }
    })
    .catch(error => {
        console.error('Error adding item:', error);
        alert('Error adding item');
    });
}

// Delete item
function deleteItem(itemId) {
    if (!confirm('Are you sure you want to delete this item?')) {
        return;
    }
    
    fetch(`/api/quote-items/${itemId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload(); // Reload to update totals
        } else {
            alert('Error deleting item');
        }
    })
    .catch(error => {
        console.error('Error deleting item:', error);
        alert('Error deleting item');
    });
}

// Form validation
function initializeFormValidation() {
    var forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

// Calculate line total for item forms
function calculateLineTotal() {
    var quantity = parseFloat(document.getElementById('quantity').value) || 0;
    var unitPrice = parseFloat(document.getElementById('unit_price').value) || 0;
    var lineTotal = quantity * unitPrice;
    
    var lineTotalField = document.getElementById('line_total');
    if (lineTotalField) {
        lineTotalField.value = lineTotal.toFixed(2);
    }
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(new Date(date));
}

// Initialize Feather icons when content is loaded
function initializeFeatherIcons() {
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
}

// Call after DOM content loaded
document.addEventListener('DOMContentLoaded', initializeFeatherIcons);

// Also call after AJAX content updates
function refreshFeatherIcons() {
    setTimeout(initializeFeatherIcons, 100);
}

// === Voice Task Creation Feature ===
let recognition, isRecording = false;
let lastVoiceResult = null;

function openVoiceTaskModal() {
    document.getElementById('voiceTranscription').value = '';
    document.getElementById('voiceTaskError').classList.add('d-none');
    document.getElementById('processVoiceBtn').disabled = true;
    document.getElementById('startVoiceBtn').classList.remove('d-none');
    document.getElementById('stopVoiceBtn').classList.add('d-none');
    new bootstrap.Modal(document.getElementById('voiceTaskModal')).show();
}

function startVoiceRecognition() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        showVoiceTaskError('Your browser does not support speech recognition.');
        return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = document.documentElement.lang || 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    isRecording = true;
    document.getElementById('startVoiceBtn').classList.add('d-none');
    document.getElementById('stopVoiceBtn').classList.remove('d-none');
    document.getElementById('voiceTranscription').value = '';
    document.getElementById('processVoiceBtn').disabled = true;
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('voiceTranscription').value = transcript;
        document.getElementById('processVoiceBtn').disabled = false;
    };
    recognition.onerror = function(event) {
        showVoiceTaskError('Speech recognition error: ' + event.error);
        stopVoiceRecognition();
    };
    recognition.onend = function() {
        isRecording = false;
        document.getElementById('startVoiceBtn').classList.remove('d-none');
        document.getElementById('stopVoiceBtn').classList.add('d-none');
    };
    recognition.start();
}

function stopVoiceRecognition() {
    if (recognition && isRecording) {
        recognition.stop();
    }
    isRecording = false;
    document.getElementById('startVoiceBtn').classList.remove('d-none');
    document.getElementById('stopVoiceBtn').classList.add('d-none');
}

function showVoiceTaskError(msg) {
    const errDiv = document.getElementById('voiceTaskError');
    errDiv.textContent = msg;
    errDiv.classList.remove('d-none');
}

function processVoiceTask() {
    const text = document.getElementById('voiceTranscription').value.trim();
    if (!text) {
        showVoiceTaskError('No transcription available.');
        return;
    }
    document.getElementById('processVoiceBtn').disabled = true;
    fetch('/ai/process_voice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text, language: document.documentElement.lang.startsWith('el') ? 'el' : 'en' })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error || data.type !== 'TASK') {
            showVoiceTaskError(data.error || 'Could not extract a task from your command.');
            document.getElementById('processVoiceBtn').disabled = false;
            return;
        }
        lastVoiceResult = data;
        fillReviewTaskModal(data.data);
        bootstrap.Modal.getInstance(document.getElementById('voiceTaskModal')).hide();
        new bootstrap.Modal(document.getElementById('reviewTaskModal')).show();
    })
    .catch(err => {
        showVoiceTaskError('Error processing voice: ' + err);
        document.getElementById('processVoiceBtn').disabled = false;
    });
}

function fillReviewTaskModal(taskData) {
    document.getElementById('taskTitle').value = taskData.title || '';
    document.getElementById('taskDescription').value = taskData.description || '';
    document.getElementById('taskPriority').value = taskData.priority || 'medium';
    document.getElementById('taskDueDate').value = taskData.due_date || '';
    document.getElementById('taskCategory').value = taskData.category || 'general';
    document.getElementById('reviewTaskError').classList.add('d-none');
}

function confirmVoiceTask() {
    const form = document.getElementById('reviewTaskForm');
    const data = {
        type: 'TASK',
        data: {
            title: form.title.value,
            description: form.description.value,
            priority: form.priority.value,
            due_date: form.due_date.value,
            category: form.category.value
        }
    };
    document.getElementById('confirmTaskBtn').disabled = true;
    fetch('/ai/create_entity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {
        if (result.error) {
            showReviewTaskError(result.error);
            document.getElementById('confirmTaskBtn').disabled = false;
            return;
        }
        bootstrap.Modal.getInstance(document.getElementById('reviewTaskModal')).hide();
        alert('Task created successfully!');
        location.reload();
    })
    .catch(err => {
        showReviewTaskError('Error creating task: ' + err);
        document.getElementById('confirmTaskBtn').disabled = false;
    });
}

function showReviewTaskError(msg) {
    const errDiv = document.getElementById('reviewTaskError');
    errDiv.textContent = msg;
    errDiv.classList.remove('d-none');
}

// Export functions for use in templates
window.FilterdynApp = {
    calculateLineTotal: calculateLineTotal,
    formatCurrency: formatCurrency,
    formatDate: formatDate,
    refreshFeatherIcons: refreshFeatherIcons,
    openVoiceTaskModal: openVoiceTaskModal,
    startVoiceRecognition: startVoiceRecognition,
    stopVoiceRecognition: stopVoiceRecognition,
    processVoiceTask: processVoiceTask,
    confirmVoiceTask: confirmVoiceTask
};
