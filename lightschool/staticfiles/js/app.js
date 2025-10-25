// General app helpers

function setLang(lang) {
    fetch('/set-lang/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCSRFToken(),
        },
        body: `lang=${lang}`,
    }).then(() => location.reload());
}

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
           document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='))?.split('=')[1];
}

// PWA install
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    // Show install button
    const btn = document.createElement('button');
    btn.textContent = 'Install App';
    btn.onclick = () => {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then(() => deferredPrompt = null);
    };
    document.querySelector('.nav-right').appendChild(btn);
});