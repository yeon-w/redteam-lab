"""
results.csv 를 읽어서 카테고리별 / 방어모드별 성공률 표를 출력한다.
9회차 최종 보고서의 "총 N개 중 M개 성공 -> 방어 적용 후 M'개 성공" 표를
그대로 뽑아내는 용도.
"""
import csv
from collections import defaultdict


def main():
    stats = defaultdict(lambda: {"total": 0, "success": 0})
    with open("results.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["defense_mode"], row["category"])
            stats[key]["total"] += 1
            if row["success"].strip().lower() == "true":
                stats[key]["success"] += 1

    print(f"{'방어모드':8} {'공격유형':20} {'시도':>5} {'성공':>5} {'성공률':>8}")
    print("-" * 55)
    for (defense_mode, category), s in sorted(stats.items()):
        rate = s["success"] / s["total"] * 100 if s["total"] else 0
        print(f"{defense_mode:8} {category:20} {s['total']:>5} {s['success']:>5} {rate:>7.1f}%")

    # 전체 합계 (defense_mode 별)
    print("-" * 55)
    totals = defaultdict(lambda: {"total": 0, "success": 0})
    for (defense_mode, _category), s in stats.items():
        totals[defense_mode]["total"] += s["total"]
        totals[defense_mode]["success"] += s["success"]
    for defense_mode, s in sorted(totals.items()):
        rate = s["success"] / s["total"] * 100 if s["total"] else 0
        print(f"[{defense_mode:3}] 전체: {s['total']}개 중 {s['success']}개 성공 ({rate:.1f}%)")


if __name__ == "__main__":
    main()
