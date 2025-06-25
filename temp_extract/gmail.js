// Gmail UI logic

document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.includes('/gmail/inbox')) {
        feather.replace();
    }
    if (window.location.pathname.includes('/gmail/message')) {
        feather.replace();
    }
    if (window.location.pathname.includes('/gmail/compose')) {
        feather.replace();
    }
});

function refreshInbox() {
    window.location.reload();
}

function analyzeEmailAjax(emailText, callback) {
    fetch('/gmail/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email_text: emailText })
    })
    .then(r => r.json())
    .then(data => {
        if (callback) callback(data);
    });
}

function suggestEmailAjax(emailText, context, language, tone, callback) {
    fetch('/gmail/api/suggest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email_text: emailText, context: context, language: language, tone: tone })
    })
    .then(r => r.json())
    .then(data => {
        if (callback) callback(data);
    });
} 