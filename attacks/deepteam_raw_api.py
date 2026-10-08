"""
1단계: DeepTeam으로 Claude API를 '직접' 공격 (redteam-lab 서버 없이).

WITH_SYSTEM_PROMPT = False (기본값):
    완전히 맨몸 상태의 Claude를 테스트한다. 일반적인 안전성 카테고리
    (Bias, Toxicity, Illegal Activity, Misinformation)에 Multi-turn
    (Crescendo/Linear Jailbreaking)으로 얼마나 버티는지를 본다.
    TEST_SECRET이 없는 상태라 Indirect Injection이나 Tool Call은 여기서
    테스트할 수 없다 — 그건 2단계(redteam-lab 서버 + tools.py)에서 진행한다.

WITH_SYSTEM_PROMPT = True:
    server.py를 띄우지 않고도, config.py에 정의된 시스템 프롬프트
    (TEST_SECRET 포함)를 API 호출에 그대로 얹어서 'Multi-turn + System Prompt
    Leakage' 조합만 빠르게 검증하고 싶을 때 쓰는 보너스 모드.
    (여전히 RAG/Tool은 없다 — 이건 2단계 전용.)

⚠️ 사전 준비
  pip install -U deepteam
  export ANTHROPIC_API_KEY=...   # 공격 '대상'(target) Claude용
  export OPENAI_API_KEY=...      # DeepTeam이 공격 프롬프트를 만들고 채점하는 데
                                  # 내부적으로 사용한다 (기본값). 즉 이 1단계는
                                  # Anthropic 예산 안에서만 끝나지는 않는다.
                                  # OpenAI를 아예 안 쓰고 싶으면 DeepEval의
                                  # custom LLM 설정이 필요한데, 설정이 꽤 복잡해서
                                  # 동아리 실습에서는 기본값 그대로 쓰는 걸 추천한다.

실행:
    python attacks/deepteam_raw_api.py
"""
import anthropic
from deepteam import red_team
from deepteam.vulnerabilities import (
    PromptLeakage,
    Bias,
    Toxicity,
    IllegalActivity,
    Misinformation,
)
from deepteam.attacks.multi_turn import CrescendoJailbreaking, LinearJailbreaking
from deepteam.attacks.single_turn import Roleplay

import config
import server  # BASE_SYSTEM_PROMPT만 재사용 - 서버를 실제로 띄우진 않는다

WITH_SYSTEM_PROMPT = False  # True로 바꾸면 TEST_SECRET이 있는 상태로 테스트

anthropic_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


async def model_callback(input: str, turns=None) -> str:
    """DeepTeam이 요구하는 콜백 시그니처. turns가 주어지면 이전 대화를 이어붙여서
    실제 Multi-turn 대화처럼 Claude에게 보낸다."""
    messages = []
    if turns:
        for t in turns:
            messages.append({"role": t.role, "content": t.content})
    messages.append({"role": "user", "content": input})

    kwargs = dict(model=config.MODEL_NAME, max_tokens=config.MAX_TOKENS, messages=messages)
    if WITH_SYSTEM_PROMPT:
        kwargs["system"] = server.BASE_SYSTEM_PROMPT

    resp = anthropic_client.messages.create(**kwargs)
    return resp.content[0].text if resp.content else ""


if __name__ == "__main__":
    if WITH_SYSTEM_PROMPT:
        vulnerabilities = [PromptLeakage()]
        purpose = "대학 정보 안내 챗봇 (시스템 프롬프트에 TEST_SECRET 보유)"
    else:
        vulnerabilities = [Bias(), Toxicity(), IllegalActivity(), Misinformation()]
        purpose = "대학 정보 안내를 전문으로 하는 범용 AI 어시스턴트"

    red_team(
        model_callback=model_callback,
        target_purpose=purpose,
        vulnerabilities=vulnerabilities,
        attacks=[CrescendoJailbreaking(), LinearJailbreaking(), Roleplay()],
        attacks_per_vulnerability_type=5,
    )
