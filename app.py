from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import tempfile
import json
import subprocess

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# 임시 파일 저장 경로
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

# 지원하는 파일 확장자
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'mp3', 'wav', 'm4a', 'flac'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': '파일이 없습니다'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '파일이 선택되지 않았습니다'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': '지원하지 않는 파일 형식입니다'}), 400

        # 임시 파일로 저장
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(temp_path)

        # 파일 정보 반환
        file_info = {
            'filename': file.filename,
            'path': temp_path,
            'size': os.path.getsize(temp_path)
        }

        return jsonify(file_info)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        data = request.json
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다'}), 400

        url = data.get('url')
        language = data.get('language', 'ko')
        model_size = data.get('model', 'base')

        if not url:
            return jsonify({'error': 'URL이 필요합니다'}), 400

        # URL 유효성 간단 체크
        if not url.startswith(('http://', 'https://')):
            return jsonify({'error': '올바른 URL 형식이 아닙니다'}), 400

        # yt-dlp로 비디오 다운로드
        import yt_dlp

        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'downloaded_video.%(ext)s')
        final_path = None
        video_info = {}

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_info['title'] = info.get('title', 'Unknown')
                video_info['duration'] = info.get('duration', 0)
                video_info['uploader'] = info.get('uploader', 'Unknown')

                # 다운로드된 파일 찾기
                for ext in ['mp3', 'mp4', 'webm', 'm4a', 'wav']:
                    test_path = os.path.join(app.config['UPLOAD_FOLDER'], f'downloaded_video.{ext}')
                    if os.path.exists(test_path):
                        final_path = test_path
                        break
        except yt_dlp.utils.DownloadError as e:
            return jsonify({'error': f'지원하지 않는 URL 또는 비디오를 찾을 수 없습니다: {str(e)}'}), 400
        except Exception as e:
            return jsonify({'error': f'비디오 다운로드 중 오류 발생: {str(e)}'}), 400

        if not final_path or not os.path.exists(final_path):
            return jsonify({'error': '비디오 파일을 다운로드할 수 없습니다'}), 400

        file_path = final_path

        # Check if whisper is available
        try:
            # Try to use whisper-ctranslate2 if available
            import shutil
            if not shutil.which('whisper-ctranslate2'):
                # Fallback message when whisper is not available
                return jsonify({
                    'error': '음성 변환 서비스가 현재 사용 불가능합니다. Railway 배포 환경에서는 whisper 패키지 설치 문제로 인해 변환 기능이 제한됩니다.',
                    'info': '로컬 환경에서는 정상 작동합니다.'
                }), 503

            output_dir = os.path.dirname(file_path)

            # 모델 크기 매핑 - 정확도를 위해 더 큰 모델 사용
            model_map = {
                'tiny': 'small',  # tiny 요청시 small 사용
                'base': 'medium',  # base 요청시 medium 사용
                'small': 'large-v2',  # small 요청시 large-v2 사용
                'medium': 'large-v3',  # medium 요청시 large-v3 사용
                'large': 'large-v3'  # large 요청시 large-v3 사용
            }

            model = model_map.get(model_size, 'large-v3')  # 기본값을 large-v3으로 설정하여 최고 정확도

            cmd = [
                'whisper-ctranslate2',
                file_path,
                '--model', model,
                '--output_dir', output_dir,
                '--output_format', 'all',
                '--vad_filter', 'True',
                '--vad_threshold', '0.3',
                '--vad_min_speech_duration_ms', '100',
                '--vad_min_silence_duration_ms', '500',
                '--word_timestamps', 'True',
                '--beam_size', '5',
                '--best_of', '5',
                '--temperature', '0',
                '--condition_on_previous_text', 'True',
                '--initial_prompt', '정확한 한국어 자막을 생성합니다.'
            ]

            # 언어가 auto가 아니면 추가
            if language != 'auto':
                cmd.extend(['--language', language])

            # 실행
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # 실시간 진행상황 스트리밍 (간단한 버전)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                # 에러 메시지 정리
                error_msg = stderr.strip() if stderr else 'Unknown error'
                if 'CUDA' in error_msg or 'GPU' in error_msg:
                    error_msg = 'GPU 처리 실패, CPU 모드로 재시도 필요'
                elif 'memory' in error_msg.lower():
                    error_msg = '메모리 부족: 더 작은 모델 크기를 선택해주세요'
                return jsonify({'error': f'변환 실패: {error_msg}'}), 500

        except Exception as e:
            return jsonify({
                'error': '음성 변환 서비스를 사용할 수 없습니다',
                'details': str(e)
            }), 503

        # 결과 파일 읽기
        base_name = 'downloaded_video'  # yt-dlp로 다운로드한 파일명

        results = {}

        # TXT 파일 먼저 확인
        txt_path = os.path.join(output_dir, f"{base_name}.txt")
        if os.path.exists(txt_path):
            with open(txt_path, 'r', encoding='utf-8') as f:
                results['txt'] = f.read()

        # SRT 파일
        srt_path = os.path.join(output_dir, f"{base_name}.srt")
        if os.path.exists(srt_path):
            with open(srt_path, 'r', encoding='utf-8') as f:
                results['srt'] = f.read()

        # VTT 파일
        vtt_path = os.path.join(output_dir, f"{base_name}.vtt")
        if os.path.exists(vtt_path):
            with open(vtt_path, 'r', encoding='utf-8') as f:
                results['vtt'] = f.read()

        # JSON 파일에서 언어와 길이 정보 추출
        json_path = os.path.join(output_dir, f"{base_name}.json")
        language_display = '한국어'
        duration = 0

        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                results['json'] = json_data

                # 언어 정보 추출
                if 'language' in json_data:
                    lang_map = {
                        'ko': '한국어',
                        'en': '영어',
                        'ja': '일본어',
                        'zh': '중국어'
                    }
                    language_display = lang_map.get(json_data['language'], json_data['language'])

                # 길이 정보 추출
                if 'duration' in json_data:
                    duration = json_data['duration']

        # yt-dlp에서 추출한 비디오 정보 사용
        title = video_info.get('title', url[:50])
        if not duration and 'duration' in video_info:
            duration = video_info['duration']

        return jsonify({
            'success': True,
            'results': results,
            'language': language_display,
            'duration': duration,
            'title': title
        })

    except Exception as e:
        # 디버그 정보 로깅 (프로덕션에서는 제거)
        app.logger.error(f"Transcribe error: {str(e)}")
        return jsonify({'error': f'서버 오류: {str(e)}'}), 500
    finally:
        # 임시 파일 정리
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

@app.route('/download/<format>', methods=['POST'])
def download(format):
    try:
        data = request.json
        content = data.get('content', '')
        filename = data.get('filename', 'transcript')

        # 파일 생성
        if format == 'srt':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.srt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        elif format == 'vtt':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.vtt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        elif format == 'txt':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            return jsonify({'error': '지원하지 않는 형식'}), 400

        return send_from_directory(
            os.path.dirname(file_path),
            os.path.basename(file_path),
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    # 개발 서버 실행 (프로덕션에서는 debug=False로 변경)
    app.run(host='0.0.0.0', port=8080, debug=False)