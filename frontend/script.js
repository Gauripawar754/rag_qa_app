
function show(el, cls, msg) {
  el.className = 'status-box ' + cls + ' visible';
  el.textContent = msg;
}
function hide(el) {
  el.className = 'status-box';
  el.textContent = '';
}

let documentId = null;


const fileInput    = document.getElementById('fileInput');
const fileSelected = document.getElementById('fileSelected');
const uploadBtn    = document.getElementById('uploadBtn');
const clearBtn     = document.getElementById('clearBtn');
const uploadStatus = document.getElementById('uploadStatus');
const dropzone     = document.getElementById('dropzone');

const questionInput = document.getElementById('questionInput');
const askBtn        = document.getElementById('askBtn');
const spinner       = document.getElementById('spinner');
const qaStatus      = document.getElementById('qaStatus');
const answerBlock   = document.getElementById('answerBlock');
const answerText    = document.getElementById('answerText');
const chunksRow     = document.getElementById('chunksRow');


fileInput.addEventListener('change', () => {
  const f = fileInput.files[0];
  if (f) {
    fileSelected.textContent = '✔ ' + f.name;
    fileSelected.style.display = 'block';
    uploadBtn.disabled = false;
    hide(uploadStatus);
  }
});


dropzone.addEventListener('dragover', e => {
  e.preventDefault();
  dropzone.classList.add('dragging');
});

dropzone.addEventListener('dragleave', () => {
  dropzone.classList.remove('dragging');
});

dropzone.addEventListener('drop', e => {
  e.preventDefault();
  dropzone.classList.remove('dragging');

  const f = e.dataTransfer.files[0];

  if (f && f.name.endsWith('.txt')) {
    fileInput.files = e.dataTransfer.files;
    fileSelected.textContent = '✔ ' + f.name;
    fileSelected.style.display = 'block';
    uploadBtn.disabled = false;
    hide(uploadStatus);
  } else {
    show(uploadStatus, 'error', '✕ Only .txt files allowed');
  }
});


clearBtn.addEventListener('click', () => {
  fileInput.value = '';
  fileSelected.style.display = 'none';
  fileSelected.textContent = '';

  uploadBtn.disabled = true;
  askBtn.disabled = true;

  documentId = null;

  hide(uploadStatus);
  hide(qaStatus);

  answerBlock.classList.remove('visible');
  answerText.textContent = '';

  chunksRow.innerHTML = '<span class="chunks-label">Source chunks:</span>';
});


uploadBtn.addEventListener('click', async () => {
  const f = fileInput.files[0];

  if (!f) return;

  if (!f.name.endsWith('.txt')) {
    show(uploadStatus, 'error', '✕ Only .txt files allowed');
    return;
  }

  const formData = new FormData();
  formData.append("file", f);

  show(uploadStatus, '', '⏳ Uploading...');

  try {
    const res = await fetch(`${API_URL}/upload`, {
      method: "POST",
      body: formData
    });

    const data = await res.json();

    if (!res.ok) throw new Error(data.detail);

    documentId = data.document_id;

    show(
      uploadStatus,
      'success',
      `✔ ${data.filename} indexed (${data.total_chunks} chunks)`
    );

    askBtn.disabled = false;

  } catch (err) {
    show(uploadStatus, 'error', '✕ ' + err.message);
  }
});


function resetAnswer() {
  answerBlock.classList.remove('visible');
  answerText.textContent = '';
  hide(qaStatus);
  spinner.classList.remove('visible');

  chunksRow.innerHTML = '<span class="chunks-label">Source chunks:</span>';
}


askBtn.addEventListener('click', async () => {
  const question = questionInput.value.trim();

  if (!question) {
    show(qaStatus, 'error', '✕ Enter a question');
    return;
  }

  if (!documentId) {
    show(qaStatus, 'error', '✕ Upload document first');
    return;
  }

  resetAnswer();
  spinner.classList.add('visible');
  askBtn.disabled = true;

  const API_URL = "https://rag-qa-backend.onrender.com";

  try {
    const res = await fetch(`${API_URL}/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        document_id: documentId,
        question: question
      })
    });

    const data = await res.json();

    if (!res.ok) throw new Error(data.detail);

    spinner.classList.remove('visible');

    answerText.textContent = data.answer;

    chunksRow.innerHTML = '<span class="chunks-label">Source chunks:</span>';

    data.sources.forEach((s, i) => {
      const tag = document.createElement('span');
      tag.className = 'chunk-tag';
      tag.textContent = `#${i + 1}`;
      tag.title = s.content; 
      chunksRow.appendChild(tag);
    });

    answerBlock.classList.add('visible');
    askBtn.disabled = false;

  } catch (err) {
    spinner.classList.remove('visible');
    show(qaStatus, 'error', '✕ ' + err.message);
    askBtn.disabled = false;
  }
});


questionInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
    askBtn.click();
  }
});

