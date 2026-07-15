#!/usr/bin/env bash
set -uo pipefail

APP_URL="http://localhost:8000"
OLLAMA_URL="http://localhost:11435"
FAIL=0

echo "1. App health check:"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/health")
if [ "$STATUS" = "200" ]; then
  echo "ok (200)"
else
  echo "FAIL (got $STATUS)"
  FAIL=1
fi

echo "2. Checking backend is reachable or not"
if curl -sf "$OLLAMA_URL/api/tags" > /dev/null; then
  echo "ok"
else
  echo "FAIL"
  FAIL=1
fi

echo "3.End to end inference:"
RESPONSE=$(curl -s -X POST "$APP_URL/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is John 3:16 about?"}')
if echo "$RESPONSE" | grep -qi '"answer"'; then
  echo "ok-received response from model"
else
  echo "FAIL - no answer"
  echo "$RESPONSE"
  FAIL=1
fi

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "ALL CHECKS HAVE BEEN PASSED!"
  exit 0
else
  echo "SOME CHECKS FAILED."
  exit 1
fi
