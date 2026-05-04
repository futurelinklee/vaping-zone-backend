#!/bin/bash
# GitHub 자동 푸시 스크립트

echo "🚀 GitHub 자동 배포 시작..."

# Git 설정
git config user.name "VapingZone Bot"
git config user.email "bot@vapingzone.com"

# 최종 커밋
git add -A
git commit -m "Deploy: v2.1 완전 배포 - 카테고리, Cloudflare 연동" || echo "No changes to commit"

# 원격 저장소 URL 표시
echo ""
echo "📋 배포 정보:"
echo "Repository: https://github.com/futurelinklee/vaping-zone-backend"
echo "Branch: main"
echo ""
echo "✅ 코드 준비 완료!"
echo ""
echo "⚠️  GitHub 푸시를 위해 다음 명령어를 실행하세요:"
echo ""
echo "cd /home/user/vaping_review_system"
echo "git push https://YOUR_GITHUB_TOKEN@github.com/futurelinklee/vaping-zone-backend.git main --force"
echo ""
echo "또는 GitHub Desktop/웹 UI를 사용하여 업로드하세요."
