#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
import tempfile
import json
import subprocess
import yt_dlp

class VideoTranscriptApp:
    def __init__(self, root):
        self.root = root
        self.root.title("크로노X 스크립트 변환기")
        self.root.geometry("1000x750")

        # 모던한 색상 팔레트
        self.colors = {
            'bg': '#1a1a1a',           # 다크 배경
            'card': '#2d2d2d',         # 카드 배경
            'accent': '#6366f1',       # 인디고 액센트
            'accent_hover': '#818cf8', # 밝은 인디고
            'success': '#10b981',      # 에메랄드
            'text': '#f3f4f6',         # 밝은 텍스트
            'text_secondary': '#9ca3af', # 보조 텍스트
            'border': '#374151'        # 테두리
        }

        # 스타일 설정
        self.root.configure(bg=self.colors['bg'])

        style = ttk.Style()
        style.theme_use('clam')

        # 탭 스타일
        style.configure('TNotebook', background=self.colors['bg'], borderwidth=0)
        style.configure('TNotebook.Tab',
                       background=self.colors['card'],
                       foreground=self.colors['text'],
                       padding=[20, 12],
                       font=('SF Pro Display', 11))
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['accent'])],
                 foreground=[('selected', 'white')])

        # 프로그레스바 스타일
        style.configure("TProgressbar",
                       background=self.colors['accent'],
                       troughcolor=self.colors['card'],
                       borderwidth=0,
                       lightcolor=self.colors['accent'],
                       darkcolor=self.colors['accent'])

        # 메인 프레임
        main_frame = tk.Frame(root, bg=self.colors['bg'], padx=30, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 제목 섹션
        title_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        title_frame.pack(fill=tk.X, pady=(0, 25))

        title_label = tk.Label(title_frame,
                              text="크로노X 스크립트 변환기",
                              font=('SF Pro Display', 28, 'bold'),
                              bg=self.colors['bg'],
                              fg=self.colors['text'])
        title_label.pack(side=tk.LEFT)

        subtitle_label = tk.Label(title_frame,
                                 text="YouTube 비디오를 텍스트로 변환",
                                 font=('SF Pro Display', 12),
                                 bg=self.colors['bg'],
                                 fg=self.colors['text_secondary'])
        subtitle_label.pack(side=tk.LEFT, padx=(15, 0))

        # URL 입력 카드
        url_card = tk.Frame(main_frame, bg=self.colors['card'], highlightbackground=self.colors['border'], highlightthickness=1)
        url_card.pack(fill=tk.X, pady=(0, 20))

        url_inner = tk.Frame(url_card, bg=self.colors['card'], padx=20, pady=15)
        url_inner.pack(fill=tk.X)

        tk.Label(url_inner, text="YouTube URL",
                font=('SF Pro Display', 11, 'bold'),
                bg=self.colors['card'],
                fg=self.colors['text']).pack(anchor='w', pady=(0, 8))

        self.url_entry = tk.Entry(url_inner,
                                 font=('SF Pro Display', 12),
                                 bg=self.colors['bg'],
                                 fg=self.colors['text'],
                                 insertbackground=self.colors['text'],
                                 highlightthickness=1,
                                 highlightbackground=self.colors['border'],
                                 highlightcolor=self.colors['accent'],
                                 relief='flat')
        self.url_entry.pack(fill=tk.X, ipady=8)

        # 설정 카드
        settings_card = tk.Frame(main_frame, bg=self.colors['card'], highlightbackground=self.colors['border'], highlightthickness=1)
        settings_card.pack(fill=tk.X, pady=(0, 20))

        settings_inner = tk.Frame(settings_card, bg=self.colors['card'], padx=20, pady=15)
        settings_inner.pack(fill=tk.BOTH)

        # 설정 그리드
        settings_grid = tk.Frame(settings_inner, bg=self.colors['card'])
        settings_grid.pack(fill=tk.X)

        # 언어 선택
        lang_frame = tk.Frame(settings_grid, bg=self.colors['card'])
        lang_frame.pack(side=tk.LEFT, padx=(0, 30))

        tk.Label(lang_frame, text="언어",
                font=('SF Pro Display', 11, 'bold'),
                bg=self.colors['card'],
                fg=self.colors['text']).pack(anchor='w', pady=(0, 5))

        self.language_var = tk.StringVar(value='ko')
        language_combo = ttk.Combobox(lang_frame,
                                     textvariable=self.language_var,
                                     values=['ko', 'en', 'ja', 'zh', 'auto'],
                                     width=15,
                                     state='readonly',
                                     font=('SF Pro Display', 11))
        language_combo.pack()

        # 모델 선택
        model_frame = tk.Frame(settings_grid, bg=self.colors['card'])
        model_frame.pack(side=tk.LEFT, padx=(0, 30))

        tk.Label(model_frame, text="모델 크기",
                font=('SF Pro Display', 11, 'bold'),
                bg=self.colors['card'],
                fg=self.colors['text']).pack(anchor='w', pady=(0, 5))

        self.model_var = tk.StringVar(value='base')
        model_combo = ttk.Combobox(model_frame,
                                  textvariable=self.model_var,
                                  values=['tiny', 'base', 'small', 'medium', 'large'],
                                  width=15,
                                  state='readonly',
                                  font=('SF Pro Display', 11))
        model_combo.pack()

        # 다운로드 버튼
        self.download_btn = tk.Button(settings_grid,
                                     text="변환 시작",
                                     command=self.download_and_transcribe,
                                     bg=self.colors['accent'],
                                     fg='white',
                                     font=('SF Pro Display', 12, 'bold'),
                                     padx=30,
                                     pady=8,
                                     relief='flat',
                                     cursor='hand2',
                                     activebackground=self.colors['accent_hover'])
        self.download_btn.pack(side=tk.RIGHT)

        # 상태 표시
        status_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_label = tk.Label(status_frame,
                                    text="준비됨",
                                    font=('SF Pro Display', 11),
                                    bg=self.colors['bg'],
                                    fg=self.colors['success'])
        self.status_label.pack(side=tk.LEFT)

        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate', style="TProgressbar")
        self.progress_bar.pack(fill=tk.X, pady=(0, 20))

        # 탭 컨테이너
        tab_control = ttk.Notebook(main_frame, style='TNotebook')

        # 텍스트 탭
        self.txt_tab = tk.Frame(tab_control, bg=self.colors['card'])
        tab_control.add(self.txt_tab, text='📝 텍스트')
        self.txt_text = scrolledtext.ScrolledText(self.txt_tab,
                                                  wrap=tk.WORD,
                                                  font=('SF Mono', 12),
                                                  bg=self.colors['bg'],
                                                  fg=self.colors['text'],
                                                  insertbackground=self.colors['text'],
                                                  highlightthickness=0,
                                                  relief='flat',
                                                  padx=15,
                                                  pady=15)
        self.txt_text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # SRT 탭
        self.srt_tab = tk.Frame(tab_control, bg=self.colors['card'])
        tab_control.add(self.srt_tab, text='🎬 SRT 자막')
        self.srt_text = scrolledtext.ScrolledText(self.srt_tab,
                                                  wrap=tk.WORD,
                                                  font=('SF Mono', 12),
                                                  bg=self.colors['bg'],
                                                  fg=self.colors['text'],
                                                  insertbackground=self.colors['text'],
                                                  highlightthickness=0,
                                                  relief='flat',
                                                  padx=15,
                                                  pady=15)
        self.srt_text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # VTT 탭
        self.vtt_tab = tk.Frame(tab_control, bg=self.colors['card'])
        tab_control.add(self.vtt_tab, text='📺 VTT 자막')
        self.vtt_text = scrolledtext.ScrolledText(self.vtt_tab,
                                                  wrap=tk.WORD,
                                                  font=('SF Mono', 12),
                                                  bg=self.colors['bg'],
                                                  fg=self.colors['text'],
                                                  insertbackground=self.colors['text'],
                                                  highlightthickness=0,
                                                  relief='flat',
                                                  padx=15,
                                                  pady=15)
        self.vtt_text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        tab_control.pack(fill=tk.BOTH, expand=True)

        # 저장 버튼 프레임
        save_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        save_frame.pack(fill=tk.X, pady=(20, 0))

        save_buttons = [
            ("텍스트 저장", 'txt'),
            ("SRT 저장", 'srt'),
            ("VTT 저장", 'vtt')
        ]

        for text, format_type in save_buttons:
            btn = tk.Button(save_frame,
                          text=text,
                          command=lambda f=format_type: self.save_file(f),
                          bg=self.colors['card'],
                          fg=self.colors['text'],
                          font=('SF Pro Display', 11, 'bold'),
                          padx=20,
                          pady=8,
                          relief='flat',
                          cursor='hand2',
                          highlightbackground=self.colors['border'],
                          activebackground=self.colors['accent'])
            btn.pack(side=tk.LEFT, padx=(0, 10))

    def download_and_transcribe(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("경고", "URL을 입력해주세요!")
            return

        # 버튼 비활성화
        self.download_btn.config(state='disabled')
        self.progress_bar.start()
        self.status_label.config(text="다운로드 중...", fg='#f39c12')

        # 별도 스레드에서 실행
        thread = threading.Thread(target=self._process_video, args=(url,))
        thread.start()

    def _process_video(self, url):
        try:
            # 임시 디렉토리
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, 'downloaded_video.%(ext)s')

            # yt-dlp로 다운로드
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

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.root.after(0, lambda: self.status_label.config(text="비디오 다운로드 중..."))
                info = ydl.extract_info(url, download=True)
                video_title = info.get('title', 'Unknown')

            # 다운로드된 파일 찾기
            audio_file = None
            for ext in ['mp3', 'mp4', 'webm', 'm4a', 'wav']:
                test_path = os.path.join(temp_dir, f'downloaded_video.{ext}')
                if os.path.exists(test_path):
                    audio_file = test_path
                    break

            if not audio_file:
                raise Exception("오디오 파일을 찾을 수 없습니다")

            # whisper 실행
            self.root.after(0, lambda: self.status_label.config(text="음성 변환 중... (시간이 걸릴 수 있습니다)"))

            language = self.language_var.get()
            model = self.model_var.get()

            # 모델 크기 매핑
            model_map = {
                'tiny': 'small',
                'base': 'medium',
                'small': 'large-v2',
                'medium': 'large-v3',
                'large': 'large-v3'
            }
            model = model_map.get(model, 'large-v3')

            # whisper-ctranslate2 명령 실행
            import shutil
            if shutil.which('whisper-ctranslate2'):
                cmd = [
                    'whisper-ctranslate2',
                    audio_file,
                    '--model', model,
                    '--output_dir', temp_dir,
                    '--output_format', 'all',
                    '--vad_filter', 'True',
                    '--word_timestamps', 'True',
                ]

                if language != 'auto':
                    cmd.extend(['--language', language])

                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate()

                if process.returncode != 0:
                    raise Exception(f"변환 실패: {stderr}")

                # 결과 파일 읽기
                base_name = 'downloaded_video'

                # 텍스트 파일
                txt_path = os.path.join(temp_dir, f"{base_name}.txt")
                if os.path.exists(txt_path):
                    with open(txt_path, 'r', encoding='utf-8') as f:
                        txt_content = f.read()
                        self.root.after(0, lambda: self.txt_text.delete(1.0, tk.END))
                        self.root.after(0, lambda: self.txt_text.insert(1.0, txt_content))

                # SRT 파일
                srt_path = os.path.join(temp_dir, f"{base_name}.srt")
                if os.path.exists(srt_path):
                    with open(srt_path, 'r', encoding='utf-8') as f:
                        srt_content = f.read()
                        self.root.after(0, lambda: self.srt_text.delete(1.0, tk.END))
                        self.root.after(0, lambda: self.srt_text.insert(1.0, srt_content))

                # VTT 파일
                vtt_path = os.path.join(temp_dir, f"{base_name}.vtt")
                if os.path.exists(vtt_path):
                    with open(vtt_path, 'r', encoding='utf-8') as f:
                        vtt_content = f.read()
                        self.root.after(0, lambda: self.vtt_text.delete(1.0, tk.END))
                        self.root.after(0, lambda: self.vtt_text.insert(1.0, vtt_content))

                self.root.after(0, lambda: self.status_label.config(text=f"✅ 변환 완료: {video_title}", fg='#27ae60'))
            else:
                raise Exception("whisper-ctranslate2가 설치되어 있지 않습니다.\n터미널에서 'pip install whisper-ctranslate2'를 실행해주세요.")

            # 임시 파일 정리
            if audio_file and os.path.exists(audio_file):
                os.remove(audio_file)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("오류", str(e)))
            self.root.after(0, lambda: self.status_label.config(text="오류 발생", fg='#e74c3c'))
        finally:
            self.root.after(0, lambda: self.download_btn.config(state='normal'))
            self.root.after(0, lambda: self.progress_bar.stop())

    def save_file(self, format_type):
        if format_type == 'txt':
            content = self.txt_text.get(1.0, tk.END)
            default_ext = '.txt'
            filetypes = [("텍스트 파일", "*.txt")]
        elif format_type == 'srt':
            content = self.srt_text.get(1.0, tk.END)
            default_ext = '.srt'
            filetypes = [("SRT 자막", "*.srt")]
        else:  # vtt
            content = self.vtt_text.get(1.0, tk.END)
            default_ext = '.vtt'
            filetypes = [("VTT 자막", "*.vtt")]

        if content.strip():
            file_path = filedialog.asksaveasfilename(
                defaultextension=default_ext,
                filetypes=filetypes,
                title=f"{format_type.upper()} 파일 저장"
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("성공", f"파일이 저장되었습니다:\n{file_path}")
        else:
            messagebox.showwarning("경고", "저장할 내용이 없습니다!")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoTranscriptApp(root)
    root.mainloop()