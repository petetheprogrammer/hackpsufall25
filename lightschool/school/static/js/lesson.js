// Lesson viewer

let currentCardIndex = 0;
let cards = [];

function initLesson(unit) {
    cards = unit.cards;
    renderCard();
    updateProgress();
}

function renderCard() {
    const container = document.getElementById('card-container');
    const card = cards[currentCardIndex];
    let html = '';
    if (card.title) {
        html += `<h2>${card.title}</h2>`;
    }
    if (card.type === 'text') {
        html += `<p>${card.body}</p>`;
    } else if (card.type === 'image') {
        html += `<img src="${card.src}" alt="${card.caption}" style="max-width:100%;"><p>${card.caption}</p>`;
    } else if (card.type === 'example') {
        html += `<p style="font-size:1.5rem;">${card.body}</p>`;
    }
    container.innerHTML = html;
    updateButtons();
}

function updateButtons() {
    document.getElementById('prev-btn').disabled = currentCardIndex === 0;
    document.getElementById('next-btn').style.display = currentCardIndex < cards.length - 1 ? 'inline' : 'none';
    document.getElementById('quiz-btn').style.display = currentCardIndex === cards.length - 1 ? 'inline' : 'none';
}

function prevCard() {
    if (currentCardIndex > 0) {
        currentCardIndex--;
        renderCard();
        updateProgress();
    }
}

function nextCard() {
    if (currentCardIndex < cards.length - 1) {
        currentCardIndex++;
        renderCard();
        updateProgress();
    }
}

function updateProgress() {
    const progress = ((currentCardIndex + 1) / cards.length) * 100;
    document.getElementById('progress-fill').style.width = `${progress}%`;
}

function goToQuiz() {
    // Assume URL pattern
    const url = window.location.href.replace('/lesson/', '/quiz/');
    window.location.href = url;
}