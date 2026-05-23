let selectedFile = null;

const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const previewBox = document.getElementById('previewBox');
const previewImg = document.getElementById('previewImg');
const fileName = document.getElementById('fileName');
const solveBtn = document.getElementById('solveBtn');
const loading = document.getElementById('loading');
const loadingStep = document.getElementById('loadingStep');
const errorBox = document.getElementById('errorBox');
const resultSection = document.getElementById('resultSection');

uploadZone.addEventListener('click', () => fileInput.click());

uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('dragover');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) handleFile(file);
});

fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) handleFile(fileInput.files[0]);
});

function handleFile(file) {
    selectedFile = file;
    fileName.textContent = file.name;

    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
        previewBox.style.display = 'block';
    };
    reader.readAsDataURL(file);

    solveBtn.disabled = false;
    hideResults();
}

solveBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    solveBtn.disabled = true;
    loading.style.display = 'block';
    errorBox.style.display = 'none';
    resultSection.style.display = 'none';

    const steps = [
        'Extracting text from image...',
        'Searching verified database...',
        'Generating explanation...'
    ];
    let stepIdx = 0;
    const stepInterval = setInterval(() => {
        stepIdx = (stepIdx + 1) % steps.length;
        loadingStep.textContent = steps[stepIdx];
    }, 1500);

    try {
        const formData = new FormData();
        formData.append('image', selectedFile);

        const response = await fetch('/solve', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        clearInterval(stepInterval);
        loading.style.display = 'none';

        if (data.error) {
            showError(data.error);
            return;
        }

        showResult(data);

    } catch (err) {
        clearInterval(stepInterval);
        loading.style.display = 'none';
        showError('Connection error. Make sure the server is running.');
    }

    solveBtn.disabled = false;
});

function showResult(data) {
    const methodBadge = document.getElementById('methodBadge');

    if (data.method === 'database') {
        methodBadge.innerHTML = `
            <div class="method-badge db">
                <span class="dot"></span>
                VERIFIED DATABASE MATCH · ${data.source.replace(/_/g, ' ')}
                · ${data.confidence} CONFIDENCE
            </div>
            <div class="confidence-msg">${data.confidence_msg}</div>`;
    } else {
        methodBadge.innerHTML = `
            <div class="method-badge ai">
                <span class="dot"></span>
                AI GENERATED · ${data.source}
            </div>
            <div class="confidence-msg warning">${data.confidence_msg}</div>`;
    }

    document.getElementById('questionText').textContent = data.question;

    const answerHighlight = document.getElementById('answerHighlight');
    const optionNum = document.getElementById('optionNum');

    if (data.answer && data.answer.includes('Correct Option:')) {
        const opt = data.answer.replace('Correct Option:', '').trim();
        optionNum.textContent = opt;
        answerHighlight.style.display = 'flex';
    } else {
        answerHighlight.style.display = 'none';
    }

    document.getElementById('explanationText').textContent = data.explanation;
    document.getElementById('sourceText').textContent = `SOURCE: ${data.source}`;

    if (data.similarity > 0) {
        document.getElementById('similarityText').textContent =
            `SIMILARITY: ${(data.similarity * 100).toFixed(1)}%`;
    } else {
        document.getElementById('similarityText').textContent = 'LLM FALLBACK';
    }

    resultSection.style.display = 'block';
}

function showError(msg) {
    errorBox.textContent = '⚠ ' + msg;
    errorBox.style.display = 'block';
    solveBtn.disabled = false;
}

function hideResults() {
    resultSection.style.display = 'none';
    errorBox.style.display = 'none';
}

function resetUI() {
    selectedFile = null;
    fileInput.value = '';
    previewBox.style.display = 'none';
    previewImg.src = '';
    solveBtn.disabled = true;
    hideResults();
    loading.style.display = 'none';
}