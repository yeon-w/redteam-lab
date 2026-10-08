"""
아주 단순한 키워드 기반 '검색'. 진짜 임베딩/벡터DB는 4회차에서 확장하면 된다.

documents/ 폴더의 .txt 파일들을 읽어서 질문과 겹치는 단어가 가장 많은
문서를 돌려준다. documents/notice_poisoned.txt 에는 일부러
Indirect Prompt Injection 페이로드를 숨겨 놨다.
"""
import os
import glob

DOC_DIR = os.path.join(os.path.dirname(__file__), "documents")


def _load_docs():
    docs = {}
    for path in glob.glob(os.path.join(DOC_DIR, "*.txt")):
        with open(path, encoding="utf-8") as f:
            docs[os.path.basename(path)] = f.read()
    return docs


def retrieve(query: str, top_k: int = 2) -> list[str]:
    docs = _load_docs()
    q_words = set(query.replace(",", " ").split())
    scored = []
    for name, content in docs.items():
        overlap = len(q_words & set(content.replace(",", " ").split()))
        scored.append((overlap, name, content))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [f"[{name}]\n{content}" for _, name, content in scored[:top_k]]
