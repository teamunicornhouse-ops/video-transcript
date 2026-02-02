#!/bin/bash

# 크로노X 스크립트 변환기 설치 도우미
# 이 스크립트는 앱을 Applications 폴더에 복사하고 실행 권한을 설정합니다

echo "======================================="
echo "  크로노X 스크립트 변환기 설치 도우미  "
echo "======================================="
echo ""

# 스크립트 실행 위치 확인
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_NAME="크로노X 스크립트 변환기.app"

# DMG 마운트 위치에서 앱 찾기
if [ -d "$SCRIPT_DIR/$APP_NAME" ]; then
    APP_PATH="$SCRIPT_DIR/$APP_NAME"
elif [ -d "/Volumes/크로노X 스크립트 변환기/$APP_NAME" ]; then
    APP_PATH="/Volumes/크로노X 스크립트 변환기/$APP_NAME"
else
    echo "❌ 앱을 찾을 수 없습니다."
    echo "DMG 파일을 먼저 마운트해주세요."
    exit 1
fi

echo "📱 앱 발견: $APP_PATH"
echo ""

# 1. Applications 폴더에 복사
echo "1️⃣  Applications 폴더에 앱 복사 중..."
cp -R "$APP_PATH" "/Applications/"

if [ $? -ne 0 ]; then
    echo "❌ 복사 실패. 관리자 권한이 필요할 수 있습니다."
    exit 1
fi

# 2. 실행 권한 설정
echo "2️⃣  실행 권한 설정 중..."
xattr -cr "/Applications/$APP_NAME"
codesign --deep --force --sign - "/Applications/$APP_NAME"

# 3. 완료 메시지
echo ""
echo "✅ 설치가 완료되었습니다!"
echo ""
echo "실행 방법:"
echo "1. Launchpad 또는 Applications 폴더에서"
echo "   '크로노X 스크립트 변환기' 찾기"
echo "2. 처음 실행시 우클릭 > 열기 선택"
echo ""
echo "======================================="
echo "설치가 완료되었습니다. 이 창을 닫아주세요."
echo "======================================="

# 5초 후 자동 종료
sleep 5