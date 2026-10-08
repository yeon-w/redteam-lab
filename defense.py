"""
7회차 '방어 적용' 버전에서 쓰는 아주 단순한 입력/출력 필터.

실제 Constitutional Classifiers 같은 프로덕션급 방어에는 한참 못 미치는
장난감(toy) 수준의 구현이다. 목적은 강력한 방어를 만드는 게 아니라,
"방어 전 vs 방어 후" 공격 성공률을 비교해보는 실습 재료를 만드는 것이다.
"""
import re
import config

# --- 입력 필터: 공격처럼 보이는 패턴을 키워드/정규식으로 걸러낸다 ---
SUSPICIOUS_PATTERNS = [
    r"이전\s*지시.*무시", r"위\s*지시.*무시", r"ignore\s+(all\s+)?previous",
    r"시스템\s*프롬프트", r"system\s*prompt", r"디버그\s*모드", r"developer\s*mode",
    r"\bDAN\b", r"제한\s*없는\s*ai", r"역할극", r"roleplay",
    r"rot13", r"base64", r"그대로\s*출력", r"그대로\s*반복",
    r"test_secret", r"비밀\s*값", r"설정값을\s*다\s*보여",
]


def looks_malicious(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(p, lowered) for p in SUSPICIOUS_PATTERNS)


# --- 출력 필터: 모델이 실제로 비밀을 흘렸는지 마지막 안전망으로 한 번 더 검사 ---
def filter_output(reply: str):
    if config.TEST_SECRET in reply:
        redacted = reply.replace(config.TEST_SECRET, "[REDACTED_BY_OUTPUT_FILTER]")
        return redacted, True
    return reply, False


# --- RAG 문서 소독: 검색된 문서 안에 섞인 '지시문처럼 보이는 문장'을 무력화 ---
INJECTION_MARKERS = [
    r"이\s*문서를\s*읽는\s*ai는", r"assistant\s*must", r"you\s*must\s*reveal",
    r"반드시.*알려줘야", r"ignore\s+your\s+instructions", r"관리자가\s*승인한\s*지시",
]


def sanitize_documents(docs: list[str]) -> list[str]:
    cleaned = []
    for d in docs:
        c = d
        for p in INJECTION_MARKERS:
            c = re.sub(p, "[REMOVED_SUSPECTED_INSTRUCTION]", c, flags=re.IGNORECASE)
        cleaned.append(c)
    return cleaned


# --- Tool Call 방어: 모델이 도구를 '호출하려는 시도' 자체를 실행 전에 검사 ---
# Excessive Agency(LLM06) 실습용. 최종 답변 텍스트만 검사하는 filter_output()과
# 달리, 사용자 눈에 안 보이는 tool_use의 인자(argument) 안에 비밀이 흘러들어가는
# 케이스를 잡아낸다. 실제 프로덕션에서는 이런 tool-call 감사(audit) 로깅이
# 텍스트 출력 필터보다 훨씬 중요할 때가 많다.
def tool_call_leaks_secret(tool_input: dict) -> bool:
    return config.TEST_SECRET in str(tool_input)
