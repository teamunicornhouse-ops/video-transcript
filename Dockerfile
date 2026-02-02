# Python 3.11 기반 이미지
FROM python:3.11-slim

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    g++ \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 먼저 복사하여 캐싱 활용
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# whisper-ctranslate2 설치
RUN pip install --no-cache-dir whisper-ctranslate2

# Whisper 모델 다운로드 (base 모델 - 더 작고 빠름)
RUN python -c "from whisper_ctranslate2 import WhisperModel; WhisperModel('base')"

# 앱 파일들 복사
COPY . .

# Railway는 PORT 환경변수를 자동으로 설정
EXPOSE ${PORT:-8080}

# 앱 실행
CMD ["python", "app.py"]