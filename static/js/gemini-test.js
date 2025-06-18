// Gemini API Testing JavaScript
function testGeminiAPI() {
    const apiKey = document.getElementById('gemini_api_key').value;
    const testButton = document.querySelector('[onclick="testGeminiAPI()"]');
    const originalText = testButton.innerHTML;
    
    if (!apiKey || apiKey === '••••••••••••••••') {
        alert('Please enter a valid Gemini API key first');
        return;
    }
    
    // Show loading state
    testButton.innerHTML = '<i data-feather="loader" class="me-1"></i> Testing...';
    testButton.disabled = true;
    
    fetch('/settings/test-gemini', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ api_key: apiKey })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success message
            const alert = document.createElement('div');
            alert.className = 'alert alert-success alert-dismissible fade show mt-2';
            alert.innerHTML = `
                <i data-feather="check-circle" class="me-2"></i>
                <strong>Success!</strong> ${data.message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            testButton.parentNode.appendChild(alert);
            feather.replace();
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 5000);
        } else {
            // Show error message
            const alert = document.createElement('div');
            alert.className = 'alert alert-danger alert-dismissible fade show mt-2';
            alert.innerHTML = `
                <i data-feather="x-circle" class="me-2"></i>
                <strong>Error:</strong> ${data.error}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            testButton.parentNode.appendChild(alert);
            feather.replace();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show mt-2';
        alert.innerHTML = `
            <i data-feather="x-circle" class="me-2"></i>
            <strong>Network Error:</strong> Unable to test API connection
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        testButton.parentNode.appendChild(alert);
        feather.replace();
    })
    .finally(() => {
        // Restore button state
        testButton.innerHTML = originalText;
        testButton.disabled = false;
        feather.replace();
    });
}

function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    const icon = field.nextElementSibling.querySelector('i');
    
    if (field.type === 'password') {
        field.type = 'text';
        icon.setAttribute('data-feather', 'eye-off');
    } else {
        field.type = 'password';
        icon.setAttribute('data-feather', 'eye');
    }
    feather.replace();
}