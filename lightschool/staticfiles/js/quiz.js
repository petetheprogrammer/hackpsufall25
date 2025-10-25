// Quiz handler

function initQuiz(unit, subject, grade, locale) {
    const form = document.getElementById('quiz-form');
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        submitQuiz(unit, subject, grade, locale);
    });
}

function submitQuiz(unit, subject, grade, locale) {
    const formData = new FormData(document.getElementById('quiz-form'));
    let correct = 0;
    const explanations = [];
    unit.quiz.forEach(q => {
        const answer = formData.get(`q${q.id}`);
        if (parseInt(answer) === q.answerIndex) {
            correct++;
        }
        explanations.push(`<p><strong>${q.prompt}</strong><br>${q.explanation}</p>`);
    });
    const score = Math.round((correct / unit.quiz.length) * 100);
    document.getElementById('score').textContent = score;
    document.getElementById('explanations').innerHTML = explanations.join('');
    document.getElementById('feedback').style.display = 'block';
    document.getElementById('quiz-form').style.display = 'none';

    // Post progress
    fetch('/api/progress/set/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({
            subject: subject,
            grade: grade,
            unitId: unit.id,
            status: 'completed',
            score: score,
        }),
    });
}

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
           document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='))?.split('=')[1];
}