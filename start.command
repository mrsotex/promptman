#!/bin/bash
# PromptMan 로컬 서버 실행 스크립트
# 이 파일을 더블클릭하면 브라우저에서 자동으로 열립니다.

cd "$(dirname "$0")"

PORT=8742

# 포트가 이미 사용 중이면 종료
lsof -ti:$PORT | xargs kill -9 2>/dev/null

# Python으로 로컬 서버 시작
echo "PromptMan 서버 시작 중... (http://localhost:$PORT)"
python3 server.py &
SERVER_PID=$!

# 서버 준비될 때까지 잠깐 대기
sleep 0.5

# 브라우저에서 열기
open "http://localhost:$PORT"

echo "브라우저에서 열렸습니다."
echo "종료하려면 이 창을 닫으세요."

# 이 창이 닫히면 서버도 종료
trap "kill $SERVER_PID 2>/dev/null" EXIT
wait $SERVER_PID
