#!/bin/bash

# Ad-hoc 서명 스크립트 - Apple Developer 계정 없이 앱 서명
# 이 방법으로 Gatekeeper 경고를 줄일 수 있습니다

APP_PATH="$1"

if [ -z "$APP_PATH" ]; then
    echo "사용법: ./sign-app.sh /path/to/app.app"
    exit 1
fi

echo "🔐 앱 서명 시작: $APP_PATH"

# 기존 서명 제거
echo "기존 서명 제거 중..."
xattr -cr "$APP_PATH"

# Ad-hoc 서명 (--deep: 모든 번들 내용물 서명, --force: 기존 서명 덮어쓰기)
echo "Ad-hoc 서명 적용 중..."
codesign --deep --force --sign - "$APP_PATH"

# 서명 검증
echo "서명 검증 중..."
codesign --verify --verbose "$APP_PATH"

if [ $? -eq 0 ]; then
    echo "✅ 서명 완료! 앱이 정상적으로 서명되었습니다."
else
    echo "❌ 서명 실패. 다시 시도해주세요."
    exit 1
fi

echo "🎉 완료! 이제 앱을 더 쉽게 실행할 수 있습니다."