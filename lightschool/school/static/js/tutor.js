// Tutor chat

let currentSubject, currentGrade, currentLocale;

function openTutor() {
    document.getElementById('tutor-bubble').classList.remove('hidden');
    // Get current subject and grade
    const navSpans = document.querySelectorAll('.nav-center span');
    if (navSpans.length >= 2) {
        const subjectSpan = navSpans[0].textContent.toLowerCase();
        currentSubject = subjectSpan.includes('math') ? 'math' : 'english';
        const gradeText = navSpans[1].textContent;
        const gradeMatch = gradeText.match(/\d+/);
        currentGrade = gradeMatch ? parseInt(gradeMatch[0]) : 1;
    } else {
        currentSubject = 'math';  // default
        currentGrade = 1;  // default
    }
    currentLocale = document.documentElement.lang || 'en';
    console.log('Tutor initialized with:', { currentSubject, currentGrade, currentLocale });
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
    
    // Make sure we have the required values
    if (!currentSubject || !currentGrade || !currentLocale) {
        console.log('Reinitializing tutor values...');
        openTutor();  // Try to get values again
    }
    
    // Log what we're about to send
    console.log('Sending tutor request:', {
        message,
        subject: currentSubject,
        grade: currentGrade,
        locale: currentLocale
    });

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
    }).then(r => {
        if (!r.ok) throw new Error('Network response was not ok');
        return r.json();
    }).then(data => {
        addMessage('lumi', data.reply);
        if (data.source === 'rules') {
            document.getElementById('tutor-badge').classList.remove('hidden');
        }
    }).catch(error => {
        console.error('Tutor error:', error);
        // Try to get more specific error message
        error.response?.json().then(data => {
            console.error('Server error:', data);
            addMessage('lumi', `Error: ${data.error || 'Unknown server error'}`);
        }).catch(() => {
            addMessage('lumi', 'Sorry, I\'m having trouble right now. Try again later!');
        });
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