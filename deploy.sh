#!/bin/bash

# 베이핑존 백엔드 자동 배포 스크립트
# 이 스크립트는 GitHub 푸시 및 Render 배포를 자동화합니다

set -e  # 오류 발생 시 스크립트 중단

echo "🚀 베이핑존 백엔드 v2.1 자동 배포 시작"
echo "============================================"
echo ""

# 현재 디렉토리 확인
if [ ! -f "app.py" ]; then
    echo "❌ 오류: app.py 파일을 찾을 수 없습니다."
    echo "   vaping_review_system 디렉토리에서 실행하세요."
    exit 1
fi

echo "✅ 프로젝트 디렉토리 확인 완료"
echo ""

# Git 설정
echo "📝 Git 설정 중..."
git config user.name "Vaping Zone Deployer"
git config user.email "deploy@vapingzone.com"
echo "✅ Git 설정 완료"
echo ""

# 변경사항 커밋
echo "📦 변경사항 커밋 중..."
git add .
git commit -m "v2.1: 카테고리 기능 추가, Cloudflare Workers 연동 준비" 2>/dev/null || echo "변경사항 없음 또는 이미 커밋됨"
echo "✅ 커밋 완료"
echo ""

# GitHub 원격 저장소 설정 확인
echo "🔗 GitHub 원격 저장소 확인 중..."
if ! git remote get-url origin &>/dev/null; then
    echo "⚠️  원격 저장소가 설정되지 않았습니다."
    echo "   다음 명령어로 설정하세요:"
    echo "   git remote add origin https://github.com/futurelinklee/vaping-zone-backend.git"
    exit 1
fi
echo "✅ 원격 저장소 확인 완료"
echo ""

# GitHub 푸시
echo "📤 GitHub에 푸시 중..."
echo "⚠️  GitHub 인증이 필요합니다."
echo "   사용자명: futurelinklee"
echo "   비밀번호: Personal Access Token (설정 → Developer settings → Personal access tokens)"
echo ""

git push origin main || {
    echo "❌ GitHub 푸시 실패"
    echo ""
    echo "🔧 해결 방법:"
    echo "1. GitHub Personal Access Token 생성:"
    echo "   https://github.com/settings/tokens"
    echo ""
    echo "2. 다음 명령어로 수동 푸시:"
    echo "   git push https://YOUR_TOKEN@github.com/futurelinklee/vaping-zone-backend.git main"
    echo ""
    exit 1
}

echo "✅ GitHub 푸시 완료!"
echo ""

# Render 배포 안내
echo "============================================"
echo "🎉 GitHub 업로드 완료!"
echo ""
echo "📋 다음 단계: Render 배포"
echo "============================================"
echo ""
echo "1. Render 대시보드 접속:"
echo "   https://dashboard.render.com/"
echo ""
echo "2. 'vaping-zone-backend' 서비스 선택"
echo ""
echo "3. 자동 배포 대기 (약 2-3분)"
echo "   또는 'Manual Deploy' 버튼 클릭"
echo ""
echo "4. 배포 완료 후 테스트:"
echo "   curl https://vaping-zone-backend.onrender.com/"
echo ""
echo "============================================"
echo "✅ 배포 스크립트 완료!"
echo "============================================"
