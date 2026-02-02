const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

exports.default = async function(context) {
  console.log('🔐 빌드 후 처리 시작...');

  // DMG 파일들에 대해서만 처리
  const dmgFiles = context.artifactPaths.filter(p => p.endsWith('.dmg'));

  for (const dmgPath of dmgFiles) {
    console.log(`📦 DMG 처리 중: ${dmgPath}`);

    try {
      // DMG 마운트
      const mountOutput = execSync(`hdiutil attach "${dmgPath}" -nobrowse`, { encoding: 'utf8' });
      const mountPoint = mountOutput.split('\t').pop().trim();

      // 마운트된 앱 찾기
      const appName = '크로노X 스크립트 변환기.app';
      const appPath = path.join(mountPoint, appName);

      if (fs.existsSync(appPath)) {
        // xattr 제거 및 ad-hoc 서명
        execSync(`xattr -cr "${appPath}"`, { stdio: 'inherit' });
        execSync(`codesign --deep --force --sign - "${appPath}"`, { stdio: 'inherit' });
        console.log('✅ 앱 서명 완료!');
      }

      // DMG 언마운트
      execSync(`hdiutil detach "${mountPoint}" -force`, { stdio: 'inherit' });

    } catch (error) {
      console.error('⚠️ DMG 처리 중 오류:', error.message);
    }
  }
};