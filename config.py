"""
redteam-lab 설정 파일

- DEFENSE_MODE: False(off) = 방어 미적용(취약 버전), True(on) = 방어 적용 버전
  7회차에서 이 값을 바꿔가며 '같은 공격'을 재실행해서 Before/After를 비교한다.
- API 키는 반드시 환경변수로만 넣는다 (코드/깃허브에 절대 하드코딩 금지).
"""
import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# 2026-09 기준 사용 가능한 모델 ID. 시점에 따라 바뀔 수 있으니
# platform.claude.com/docs/en/about-claude/models/overview 에서 최신값 확인 권장.
MODEL_NAME = os.environ.get("REDTEAM_MODEL", "claude-sonnet-5")

# 방어 스위치. 서버 실행 전에 REDTEAM_DEFENSE=on / off 환경변수로 제어한다.
DEFENSE_MODE = os.environ.get("REDTEAM_DEFENSE", "off").lower() == "on"

# 실습용 가짜 비밀 값. 절대 실제 개인정보 / 실제 비밀번호를 넣지 말 것.
TEST_SECRET = "PROJECT_FLAG_2026_EWHA"

MAX_TOKENS = 800
