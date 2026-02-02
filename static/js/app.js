let uploadedFile = null;

// DOM 요소들
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeFile = document.getElementById('removeFile');
const settingsSection = document.getElementById('settingsSection');
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const resultSection = document.getElementById('resultSection');
const startTranscribe = document.getElementById('startTranscribe');
const newConversion = document.getElementById('newConversion');

// 파일 업로드 처리
uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// 파일 처리
async function handleFile(file) {
    // 파일 크기 확인 (500MB 제한)
    if (file.size > 500 * 1024 * 1024) {
        alert('파일 크기는 500MB를 초과할 수 없습니다.');
        return;
    }

    // 파일 형식 확인
    const ext = file.name.split('.').pop().toLowerCase();
    const allowedExts = ['mp4', 'avi', 'mov', 'mkv', 'mp3', 'wav', 'm4a', 'flac'];
    if (!allowedExts.includes(ext)) {
        alert('지원하지 않는 파일 형식입니다.');
        return;
    }

    uploadedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);

    uploadArea.style.display = 'none';
    fileInfo.style.display = 'block';
    settingsSection.style.display = 'block';
}

// 파일 제거
removeFile.addEventListener('click', () => {
    uploadedFile = null;
    fileInput.value = '';
    uploadArea.style.display = 'block';
    fileInfo.style.display = 'none';
    settingsSection.style.display = 'none';
});

// 변환 시작
startTranscribe.addEventListener('click', async () => {
    if (!uploadedFile) return;

    // UI 전환
    settingsSection.style.display = 'none';
    progressSection.style.display = 'block';
    resultSection.style.display = 'none';

    try {
        // 1. 파일 업로드
        progressText.textContent = '파일 업로드 중...';
        progressFill.style.width = '20%';

        const formData = new FormData();
        formData.append('file', uploadedFile);

        const uploadResponse = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!uploadResponse.ok) {
            throw new Error('파일 업로드 실패');
        }

        const uploadResult = await uploadResponse.json();

        // 2. 변환 시작
        progressText.textContent = '음성 인식 중... (시간이 걸릴 수 있습니다)';
        progressFill.style.width = '50%';

        const transcribeResponse = await fetch('/transcribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_path: uploadResult.path,
                language: document.getElementById('language').value,
                model: document.getElementById('model').value
            })
        });

        if (!transcribeResponse.ok) {
            throw new Error('변환 실패');
        }

        const result = await transcribeResponse.json();

        // 3. 결과 표시
        progressText.textContent = '완료!';
        progressFill.style.width = '100%';

        setTimeout(() => {
            progressSection.style.display = 'none';
            resultSection.style.display = 'block';

            // 결과 표시
            if (result.results.srt) {
                document.getElementById('srtResult').value = result.results.srt;
            }
            if (result.results.vtt) {
                document.getElementById('vttResult').value = result.results.vtt;
            }
            if (result.results.txt) {
                document.getElementById('txtResult').value = result.results.txt;
            }

            // 다운로드 버튼 설정
            setupDownloadButtons(result.results);
        }, 1000);

    } catch (error) {
        alert('변환 중 오류가 발생했습니다: ' + error.message);
        progressSection.style.display = 'none';
        settingsSection.style.display = 'block';
    }
});

// 새 변환
newConversion.addEventListener('click', () => {
    uploadedFile = null;
    fileInput.value = '';
    uploadArea.style.display = 'block';
    fileInfo.style.display = 'none';
    settingsSection.style.display = 'none';
    progressSection.style.display = 'none';
    resultSection.style.display = 'none';
    progressFill.style.width = '0';
});

// 탭 전환
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        // 모든 탭 비활성화
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));

        // 클릭한 탭 활성화
        tab.classList.add('active');
        const tabId = tab.dataset.tab + '-tab';
        document.getElementById(tabId).classList.add('active');
    });
});

// 다운로드 버튼 설정
function setupDownloadButtons(results) {
    document.querySelectorAll('.btn-download').forEach(btn => {
        btn.addEventListener('click', async () => {
            const format = btn.dataset.format;
            let content = '';

            if (format === 'srt') content = results.srt;
            else if (format === 'vtt') content = results.vtt;
            else if (format === 'txt') content = results.txt;

            if (!content) {
                alert('다운로드할 내용이 없습니다.');
                return;
            }

            // 다운로드 생성
            const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `transcript.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    });
}

// 파일 크기 포맷
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}