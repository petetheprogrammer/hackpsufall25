// Tutor chat

let currentSubject, currentGrade, currentLocale;

function openTutor() {
    document.getElementById('tutor-bubble').classList.remove('hidden');
    // Assume from nav or something
    currentSubject = document.querySelector('.nav-center span')?.textContent.toLowerCase().includes('math') ? 'math' : 'english';
    currentGrade = parseInt(document.querySelector('.nav-center span:last-child')?.textContent.split(' ')[1]) || 1;
    currentLocale = document.documentElement.lang;
}

function closeTutor() {
    document.getElementById('tutor-bubble').classList.add('hidden');
}

function sendTutorMessage() {
    const input = document.getElementById('tutor-input');
    const message = input.value.trim();
    if (!message) return;
    addMessage('user', message);
    input.value = '';

    fetch('/api/tutor/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({
            message: message,
            subject: currentSubject,
            grade: currentGrade,
            locale: currentLocale,
        }),
    }).then(r => r.json()).then(data => {
        addMessage('lumi', data.reply);
        if (data.source === 'rules') {
            document.getElementById('tutor-badge').classList.remove('hidden');
        }
    });
}

function addMessage(sender, text) {
    const container = document.getElementById('tutor-messages');
    const msg = document.createElement('div');
    msg.className = `message ${sender}`;
    msg.textContent = text;
    container.appendChild(msg);
    container.scrollTop = container.scrollHeight;
}

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
           document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='))?.split('=')[1];
}