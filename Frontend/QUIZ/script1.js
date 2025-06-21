document.addEventListener('DOMContentLoaded', function() {
    async function generateQuestions(questionType, topic, examType) {
        const response = await fetch('http://localhost:8000/generate-questions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ questionType, topic, examType })
        });
        const data = await response.json();
        return data.questions;
    }

    const form = document.getElementById('quiz-setup-form');
    const questionsContainer = document.getElementById('questions-container');
    const questionsList = document.getElementById('questions-list');
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        questionsList.innerHTML = '<p>Loading questions...</p>';
        questionsContainer.style.display = 'block';
        const questionType = document.getElementById('question-type').value;
        const topic = document.getElementById('topic').value;
        const examType = document.getElementById('exam-type').value;
        const questions = await generateQuestions(questionType, topic, examType);
        let html = '';
        questions.forEach((q, idx) => {
            html += `<div class="question-card"><p class="question-text">${idx+1}. ${q.question}</p>`;
            if (q.options) {
                html += '<ul class="options-list">';
                q.options.forEach((opt, i) => {
                    html += `<li>${String.fromCharCode(65+i)}. ${opt}</li>`;
                });
                html += '</ul>';
            }
            if (q.answer) {
                html += `<details><summary>Show Answer</summary><p>${q.answer}</p></details>`;
            }
            html += '</div>';
        });
        questionsList.innerHTML = html;
    });
});
