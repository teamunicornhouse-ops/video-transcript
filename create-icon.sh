#!/bin/bash

# 간단한 아이콘 생성 스크립트
# 나중에 디자이너가 만든 아이콘으로 교체하세요

# 임시 PNG 파일 생성 (1024x1024)
cat << 'EOF' > assets/icon_temp.svg
<svg width="1024" height="1024" xmlns="http://www.w3.org/2000/svg">
  <rect width="1024" height="1024" rx="200" fill="url(#grad)"/>
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#6366f1;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#818cf8;stop-opacity:1" />
    </linearGradient>
  </defs>
  <text x="512" y="400" font-family="Arial Black" font-size="200" fill="white" text-anchor="middle">크로노X</text>
  <text x="512" y="650" font-family="Arial" font-size="120" fill="white" text-anchor="middle">스크립트</text>
</svg>
EOF

# SVG를 PNG로 변환 (ImageMagick 필요)
if command -v convert &> /dev/null; then
    convert -background none assets/icon_temp.svg -resize 1024x1024 assets/icon.png

    # ICNS 파일 생성
    mkdir -p assets/icon.iconset
    sips -z 16 16 assets/icon.png --out assets/icon.iconset/icon_16x16.png
    sips -z 32 32 assets/icon.png --out assets/icon.iconset/icon_16x16@2x.png
    sips -z 32 32 assets/icon.png --out assets/icon.iconset/icon_32x32.png
    sips -z 64 64 assets/icon.png --out assets/icon.iconset/icon_32x32@2x.png
    sips -z 128 128 assets/icon.png --out assets/icon.iconset/icon_128x128.png
    sips -z 256 256 assets/icon.png --out assets/icon.iconset/icon_128x128@2x.png
    sips -z 256 256 assets/icon.png --out assets/icon.iconset/icon_256x256.png
    sips -z 512 512 assets/icon.png --out assets/icon.iconset/icon_256x256@2x.png
    sips -z 512 512 assets/icon.png --out assets/icon.iconset/icon_512x512.png
    sips -z 1024 1024 assets/icon.png --out assets/icon.iconset/icon_512x512@2x.png

    iconutil -c icns assets/icon.iconset
    mv icon.icns assets/icon.icns

    # 정리
    rm -rf assets/icon.iconset
    rm assets/icon_temp.svg

    echo "✅ 아이콘 생성 완료!"
else
    echo "⚠️  ImageMagick이 설치되어 있지 않습니다. 기본 아이콘을 사용합니다."
    # 기본 PNG 생성
    touch assets/icon.png
    touch assets/icon.icns
fi