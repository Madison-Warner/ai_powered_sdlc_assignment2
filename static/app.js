// Study Helper Frontend JavaScript

const API_BASE = '/api';

let selectedSubjectId = null;
let selectedSubjectName = '';
let selectedTopicId = null;
let selectedTopicName = '';
let currentQuiz = null;

function updateSelectionBar() {
    const bar = document.getElementById('selection-bar');
    if (!bar) return;
    if (selectedSubjectId) {
        bar.innerHTML = `<strong>Current selection:</strong> Subject: ${selectedSubjectName}${selectedTopicId ? ` → Topic: ${selectedTopicName}` : ''}`;
    } else {
        bar.innerHTML = '<strong>Current selection:</strong> None';
    }
}

function showSection(sectionId) {
    if (sectionId === 'topics' && !selectedSubjectId) {
        alert('Please select a subject first.');
        return;
    }
    if (sectionId === 'flashcards' && !selectedTopicId) {
        alert('Please select a topic first.');
        return;
    }
    if (sectionId === 'materials' && !selectedTopicId) {
        alert('Please select a topic first.');
        return;
    }
    if (sectionId === 'quizzes' && !selectedSubjectId) {
        alert('Please select a subject first.');
        return;
    }

    document.querySelectorAll('.section').forEach(section => section.classList.remove('active'));
    const target = document.getElementById(`${sectionId}-section`);
    if (target) target.classList.add('active');
    updateSelectionBar();
    loadSectionData(sectionId);
}

async function apiRequest(endpoint, method = 'GET', data = null) {
    const config = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
    };

    if (data) {
        config.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, config);
        if (!response.ok) {
            const errorBody = await response.json().catch(() => null);
            const message = errorBody?.error || `HTTP error ${response.status}`;
            throw new Error(message);
        }
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        alert('Error: ' + error.message);
        return null;
    }
}

function selectSubject(id, name) {
    selectedSubjectId = id;
    selectedSubjectName = name;
    selectedTopicId = null;
    selectedTopicName = '';
    updateSelectionBar();
    showSection('topics');
}

function selectTopic(id, name) {
    selectedTopicId = id;
    selectedTopicName = name;
    updateSelectionBar();
    showSection('flashcards');
}

// Subjects functions
async function loadSubjects() {
    const subjects = await apiRequest('/subjects');
    if (!subjects) return;

    const container = document.getElementById('subjects-list');
    container.innerHTML = '';

    subjects.forEach(subject => {
        const item = document.createElement('div');
        item.className = 'item';
        item.innerHTML = `
            <h3>${subject.name}</h3>
            <p>${subject.description}</p>
            <div class="item-actions">
                <button class="btn btn-edit" onclick="selectSubject('${subject.id}', '${subject.name}')">Select</button>
                <button class="btn btn-edit" onclick="editSubject('${subject.id}')">Edit</button>
                <button class="btn btn-delete" onclick="deleteSubject('${subject.id}')">Delete</button>
            </div>
        `;
        container.appendChild(item);
    });
}

async function createSubject() {
    const name = document.getElementById('subject-name').value.trim();
    const description = document.getElementById('subject-description').value.trim();

    if (!name) {
        alert('Subject name is required');
        return;
    }

    const result = await apiRequest('/subjects', 'POST', { name, description });
    if (result) {
        document.getElementById('subject-name').value = '';
        document.getElementById('subject-description').value = '';
        loadSubjects();
        loadSubjectSelects();
    }
}

async function deleteSubject(id) {
    if (!confirm('Are you sure you want to delete this subject?')) return;

    const result = await apiRequest(`/subjects/${id}`, 'DELETE');
    if (result) {
        if (selectedSubjectId === id) {
            selectedSubjectId = null;
            selectedSubjectName = '';
            selectedTopicId = null;
            selectedTopicName = '';
            updateSelectionBar();
        }
        loadSubjects();
        loadSubjectSelects();
        loadTopics();
        loadFlashcards();
        loadMaterials();
    }
}

async function editSubject(id) {
    const subject = await apiRequest(`/subjects/${id}`);
    if (!subject) return;

    const newName = prompt('Enter new subject name:', subject.name);
    const newDescription = prompt('Enter new description:', subject.description);

    if (newName && newName.trim()) {
        const result = await apiRequest(`/subjects/${id}`, 'PUT', {
            name: newName.trim(),
            description: newDescription ? newDescription.trim() : subject.description
        });
        if (result) {
            if (selectedSubjectId === id) {
                selectedSubjectName = result.name;
                updateSelectionBar();
            }
            loadSubjects();
            loadSubjectSelects();
        }
    }
}

// Topics functions
async function loadTopics() {
    const container = document.getElementById('topics-list');
    container.innerHTML = '';

    const endpoint = selectedSubjectId ? `/subjects/${selectedSubjectId}/topics` : '/topics';
    const topics = await apiRequest(endpoint);
    if (!topics) return;

    topics.forEach(topic => {
        const item = document.createElement('div');
        item.className = 'item';
        item.innerHTML = `
            <h3>${topic.name}</h3>
            <p>${topic.description}</p>
            <p class="weak-score">Weak Score: ${topic.weak_score ?? 0}</p>
            <div class="item-actions">
                <button class="btn btn-edit" onclick="selectTopic('${topic.id}', '${topic.name}')">Open</button>
                <button class="btn btn-edit" onclick="editTopic('${topic.id}')">Edit</button>
                <button class="btn btn-delete" onclick="deleteTopic('${topic.id}')">Delete</button>
            </div>
        `;
        container.appendChild(item);
    });
}

async function loadSubjectSelects() {
    const subjects = await apiRequest('/subjects');
    if (!subjects) return;

    const selects = ['topic-subject-select', 'quiz-subject-select'];
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        select.innerHTML = '<option value="">Select Subject</option>';
        subjects.forEach(subject => {
            const option = document.createElement('option');
            option.value = subject.id;
            option.textContent = subject.name;
            if (subject.id === selectedSubjectId) {
                option.selected = true;
            }
            select.appendChild(option);
        });
    });
}

async function createTopic() {
    const subjectId = document.getElementById('topic-subject-select').value || selectedSubjectId;
    const name = document.getElementById('topic-name').value.trim();
    const description = document.getElementById('topic-description').value.trim();

    if (!subjectId || !name) {
        alert('Subject and topic name are required');
        return;
    }

    const result = await apiRequest('/topics', 'POST', { subject_id: subjectId, name, description });
    if (result) {
        document.getElementById('topic-name').value = '';
        document.getElementById('topic-description').value = '';
        loadTopics();
        loadTopicSelects();
    }
}

async function deleteTopic(id) {
    if (!confirm('Are you sure you want to delete this topic?')) return;

    const result = await apiRequest(`/topics/${id}`, 'DELETE');
    if (result) {
        if (selectedTopicId === id) {
            selectedTopicId = null;
            selectedTopicName = '';
            updateSelectionBar();
        }
        loadTopics();
        loadTopicSelects();
        loadFlashcards();
        loadMaterials();
    }
}

async function editTopic(id) {
    const topic = await apiRequest(`/topics/${id}`);
    if (!topic) return;

    const newName = prompt('Enter new topic name:', topic.name);
    const newDescription = prompt('Enter new description:', topic.description);

    if (newName && newName.trim()) {
        const result = await apiRequest(`/topics/${id}`, 'PUT', {
            name: newName.trim(),
            description: newDescription ? newDescription.trim() : topic.description
        });
        if (result) {
            if (selectedTopicId === id) {
                selectedTopicName = result.name;
                updateSelectionBar();
            }
            loadTopics();
            loadTopicSelects();
        }
    }
}

// Flashcards functions
async function loadFlashcards() {
    const container = document.getElementById('flashcards-list');
    container.innerHTML = '';

    if (!selectedTopicId) {
        container.innerHTML = '<p>Please select a topic to view flashcards.</p>';
        return;
    }

    const flashcards = await apiRequest(`/topics/${selectedTopicId}/flashcards`);
    if (!flashcards) return;

    flashcards.forEach(flashcard => {
        const item = document.createElement('div');
        item.className = 'item';
        item.innerHTML = `
            <h3>Q: ${flashcard.question}</h3>
            <p>A: ${flashcard.answer}</p>
            <div class="item-actions">
                <button class="btn btn-edit" onclick="editFlashcard('${flashcard.id}')">Edit</button>
                <button class="btn btn-delete" onclick="deleteFlashcard('${flashcard.id}')">Delete</button>
            </div>
        `;
        container.appendChild(item);
    });
}

async function loadTopicSelects() {
    const subjects = await apiRequest('/subjects');
    if (!subjects) return;

    const topicSelects = ['flashcard-topic-select', 'material-topic-select'];
    const grouped = await Promise.all(subjects.map(async subject => {
        const topics = await apiRequest(`/topics?subject_id=${subject.id}`);
        return { subject, topics };
    }));

    topicSelects.forEach(selectId => {
        const select = document.getElementById(selectId);
        select.innerHTML = '<option value="">Select Topic</option>';
        grouped.forEach(group => {
            if (!group.topics || !group.topics.length) return;
            const optgroup = document.createElement('optgroup');
            optgroup.label = group.subject.name;
            group.topics.forEach(topic => {
                const option = document.createElement('option');
                option.value = topic.id;
                option.textContent = `${topic.name} (Weak: ${topic.weak_score ?? 0})`;
                if (topic.id === selectedTopicId) {
                    option.selected = true;
                }
                optgroup.appendChild(option);
            });
            select.appendChild(optgroup);
        });
    });
}

async function createFlashcard() {
    const topicId = document.getElementById('flashcard-topic-select').value || selectedTopicId;
    const question = document.getElementById('flashcard-question').value.trim();
    const answer = document.getElementById('flashcard-answer').value.trim();

    if (!topicId || !question || !answer) {
        alert('Topic, question, and answer are required');
        return;
    }

    const result = await apiRequest('/flashcards', 'POST', { topic_id: topicId, question, answer });
    if (result) {
        document.getElementById('flashcard-question').value = '';
        document.getElementById('flashcard-answer').value = '';
        if (!selectedTopicId) {
            selectedTopicId = topicId;
            const selectedOption = document.querySelector(`#flashcard-topic-select option[value="${topicId}"]`);
            selectedTopicName = selectedOption ? selectedOption.textContent : selectedTopicName;
            updateSelectionBar();
        }
        loadFlashcards();
    }
}

async function deleteFlashcard(id) {
    if (!confirm('Are you sure you want to delete this flashcard?')) return;

    const result = await apiRequest(`/flashcards/${id}`, 'DELETE');
    if (result) {
        loadFlashcards();
    }
}

async function editFlashcard(id) {
    const flashcard = await apiRequest(`/flashcards/${id}`);
    if (!flashcard) return;

    const newQuestion = prompt('Enter new question:', flashcard.question);
    const newAnswer = prompt('Enter new answer:', flashcard.answer);

    if (newQuestion && newQuestion.trim() && newAnswer && newAnswer.trim()) {
        const result = await apiRequest(`/flashcards/${id}`, 'PUT', {
            question: newQuestion.trim(),
            answer: newAnswer.trim()
        });
        if (result) {
            loadFlashcards();
        }
    }
}

// Study Materials functions
async function loadMaterials() {
    const container = document.getElementById('materials-list');
    container.innerHTML = '';

    if (!selectedTopicId) {
        container.innerHTML = '<p>Please select a topic to view study materials.</p>';
        return;
    }

    const materials = await apiRequest(`/study-materials?topic_id=${selectedTopicId}`);
    if (!materials) return;

    materials.forEach(material => {
        const item = document.createElement('div');
        item.className = 'item';
        item.innerHTML = `
            <h3>${material.filename}</h3>
            <p>${material.content.substring(0, 200)}...</p>
            <div class="item-actions">
                <button class="btn btn-delete" onclick="deleteMaterial('${material.id}')">Delete</button>
            </div>
        `;
        container.appendChild(item);
    });
}

async function uploadMaterial() {
    const topicId = document.getElementById('material-topic-select').value || selectedTopicId;
    const filename = document.getElementById('material-filename').value.trim();
    const content = document.getElementById('material-content').value.trim();

    if (!topicId || !filename || !content) {
        alert('Topic, filename, and content are required');
        return;
    }

    const result = await apiRequest('/study-materials', 'POST', { topic_id: topicId, filename, content });
    if (result) {
        document.getElementById('material-filename').value = '';
        document.getElementById('material-content').value = '';
        if (!selectedTopicId) {
            selectedTopicId = topicId;
            const selectedOption = document.querySelector(`#material-topic-select option[value="${topicId}"]`);
            selectedTopicName = selectedOption ? selectedOption.textContent : selectedTopicName;
            updateSelectionBar();
        }
        loadMaterials();
    }
}

async function deleteMaterial(id) {
    if (!confirm('Are you sure you want to delete this material?')) return;

    const result = await apiRequest(`/study-material/${id}`, 'DELETE');
    if (result) {
        loadMaterials();
    }
}

// Quiz functions
async function generateQuiz() {
    const subjectId = document.getElementById('quiz-subject-select').value || selectedSubjectId;
    if (!subjectId) {
        alert('Please select a subject');
        return;
    }

    const quiz = await apiRequest('/quizzes/generate', 'POST', { subject_id: subjectId });
    if (!quiz) return;

    currentQuiz = quiz;
    displayQuiz(quiz);
}

function displayQuiz(quiz) {
    const container = document.getElementById('quiz-container');
    container.innerHTML = '';

    quiz.questions.forEach((question, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'quiz-question';
        questionDiv.innerHTML = `
            <h4>${index + 1}. ${question.question}</h4>
            <div class="quiz-options">
                ${question.options.map((option, optIndex) => `
                    <label class="quiz-option">
                        <input type="radio" name="q${question.id}" value="${option}" required>
                        ${String.fromCharCode(65 + optIndex)}. ${option}
                    </label>
                `).join('')}
            </div>
        `;
        container.appendChild(questionDiv);
    });

    const submitBtn = document.createElement('div');
    submitBtn.className = 'quiz-actions';
    submitBtn.innerHTML = '<button onclick="submitQuiz()">Submit Quiz</button>';
    container.appendChild(submitBtn);
}

async function submitQuiz() {
    if (!currentQuiz) return;

    const answers = {};
    let allAnswered = true;

    currentQuiz.questions.forEach(question => {
        const selected = document.querySelector(`input[name="q${question.id}"]:checked`);
        if (selected) {
            answers[question.id] = selected.value;
        } else {
            allAnswered = false;
        }
    });

    if (!allAnswered) {
        alert('Please answer all questions');
        return;
    }

    const result = await apiRequest('/quizzes/submit', 'POST', {
        quiz_id: currentQuiz.id,
        answers
    });

    if (result) {
        displayQuizResult(result);
        loadResults();
    }
}

function displayQuizResult(result) {
    const container = document.getElementById('quiz-container');
    container.innerHTML = `
        <div class="item">
            <h3>Quiz Complete!</h3>
            <p>Your Score: ${result.score}%</p>
            <p>Correct Answers: ${result.correct_count}/${result.total_questions}</p>
            <div class="quiz-actions">
                <button onclick="generateQuiz()">Take Another Quiz</button>
            </div>
        </div>
    `;
}

// Results functions
async function loadResults() {
    const results = await apiRequest('/quiz-results');
    if (!results) return;

    const container = document.getElementById('results-list');
    container.innerHTML = '';

    results.forEach(result => {
        const item = document.createElement('div');
        item.className = 'item';
        item.innerHTML = `
            <h3>Score: ${result.score}%</h3>
            <p>Correct: ${result.details.correct_count}/${result.details.total_questions}</p>
            <small>${new Date(result.created_at).toLocaleString()}</small>
        `;
        container.appendChild(item);
    });
}

// Section loading
function loadSectionData(section) {
    switch (section) {
        case 'subjects':
            loadSubjects();
            break;
        case 'topics':
            loadTopics();
            loadSubjectSelects();
            break;
        case 'flashcards':
            loadFlashcards();
            loadTopicSelects();
            break;
        case 'materials':
            loadMaterials();
            loadTopicSelects();
            break;
        case 'quizzes':
            loadSubjectSelects();
            break;
        case 'results':
            loadResults();
            break;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    updateSelectionBar();
    loadSectionData('subjects');
});
