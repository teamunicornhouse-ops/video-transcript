# 🎬 실시간 비디오 스크립트 변환기

비디오의 실제 음성을 AI로 정확하게 텍스트로 변환하는 프로그램입니다.

## ✨ 주요 기능

- **🎙️ 실제 음성 추출**: YouTube, Instagram, TikTok 등의 비디오에서 실제 오디오 추출
- **🤖 AI 음성 인식**: OpenAI Whisper를 사용한 정확한 음성-텍스트 변환
- **🌐 자동 언어 감지**: 한국어, 영어, 일본어, 중국어 등 모든 언어 자동 감지
- **📝 가독성 높은 포맷팅**: 문단 구분과 타임스탬프 기반 구조화
- **📋 복사/붙여넣기**: URL 입력과 스크립트 출력 모두 복사 가능
- **💾 다운로드 기능**: 텍스트 파일로 저장
- **🔗 공유 기능**: 앱을 다른 사람과 링크로 공유
- **🚀 캐싱 시스템**: 한 번 변환한 비디오는 빠르게 재사용

## 📋 설치 방법

### 1. 필수 요구사항
- Python 3.8 이상
- ffmpeg (오디오 처리용)
- 4GB 이상의 RAM (Whisper AI 모델용)

### 2. 자동 설치 (권장)

```bash
# 1. 프로젝트 디렉토리로 이동
cd video-transcript-app

# 2. 설치 스크립트 실행
./setup.sh
```

### 3. 수동 설치

```bash
# 1. 가상환경 생성
python3 -m venv venv

# 2. 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows

# 3. 패키지 설치
pip install -r requirements.txt

# 4. ffmpeg 설치
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# https://ffmpeg.org/download.html 에서 다운로드
```

## 🚀 실행 방법

### 1. 서버 시작

```bash
# 가상환경 활성화
source venv/bin/activate

# 서버 실행
python server.py
```

서버가 http://localhost:5000 에서 실행됩니다.

### 2. 웹 인터페이스 열기

브라우저에서 `index.html` 파일을 열거나:
```bash
open index.html  # macOS
# 또는
python -m http.server 8080  # 로컬 웹서버로 실행
```

## 💡 사용 방법

1. **서버 시작**: 터미널에서 `python server.py` 실행
2. **웹페이지 열기**: `index.html`을 브라우저에서 열기
3. **URL 입력**: YouTube, Instagram Reels, TikTok 등의 비디오 URL 입력
4. **변환 클릭**: "실제 음성 변환" 버튼 클릭
5. **결과 확인**: AI가 추출한 실제 스크립트 확인
6. **복사/저장**: 스크립트를 복사하거나 파일로 다운로드

## 🎯 지원 플랫폼

- YouTube (일반 동영상, Shorts)
- Instagram (Reels, IGTV)
- TikTok
- Twitter/X
- Facebook
- 기타 yt-dlp가 지원하는 모든 플랫폼

## ⚙️ 고급 설정

### Whisper 모델 변경

`server.py`에서 모델 크기 변경 가능:

```python
# 현재 설정 (균형잡힌 성능)
model = whisper.load_model("base")

# 다른 옵션들
model = whisper.load_model("tiny")    # 빠르지만 정확도 낮음
model = whisper.load_model("small")   # 조금 더 정확
model = whisper.load_model("medium")  # 높은 정확도
model = whisper.load_model("large")   # 최고 정확도 (느림, 높은 메모리 필요)
```

### 포트 변경

`server.py` 마지막 줄에서 포트 변경:

```python
app.run(host='0.0.0.0', port=5000)  # 원하는 포트로 변경
```

## 🐛 문제 해결

### "서버 연결 실패" 에러
- 서버가 실행 중인지 확인 (`python server.py`)
- 방화벽이 5000번 포트를 차단하지 않는지 확인

### "ffmpeg not found" 에러
- ffmpeg 설치 확인: `ffmpeg -version`
- PATH에 ffmpeg 추가되었는지 확인

### 메모리 부족 에러
- 더 작은 Whisper 모델 사용 ("tiny" 또는 "small")
- 시스템 메모리 확인 (최소 4GB 권장)

## 📝 라이선스

MIT License

## 🤝 기여하기

버그 리포트, 기능 제안, Pull Request 모두 환영합니다!