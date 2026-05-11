"""
yearly_combined_YYMM.csv 파일들(월 집계)을 연별로 모아 평균내어
annual_avg_YYYY.csv 로 저장하는 스크립트.
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict

BASE = Path(r"C:\Users\sun94\Downloads\commute_stress_파이프라인\commute_stress_파이프라인")
OUTPUT_DIR = BASE / "annual_avg_output"
OUTPUT_DIR.mkdir(exist_ok=True)

# yearly_combined_YYMM.csv 전부 수집 → 연도별 그룹핑
year_files: dict[str, list[Path]] = defaultdict(list)
for f in BASE.rglob("yearly_combined_*.csv"):
    yymm = f.stem.replace("yearly_combined_", "")   # e.g. "2302"
    year = "20" + yymm[:2]                           # "2023"
    year_files[year].append(f)

NUMERIC_COLS = ["연평균_스트레스점수", "연합계_총이동인구수", "연평균_평균이동시간"]
RENAME_COLS  = {
    "연평균_스트레스점수": "연평균_스트레스점수",   # 분기 대표월 평균 = 연평균 추정
    "연합계_총이동인구수": "월평균_총이동인구수",    # 월 단위 평균; ×12 = 연간 합계 추정
    "연평균_평균이동시간": "연평균_이동시간",        # 중복 제거
}
GROUP_KEYS   = ["연도", "자치구코드", "모형"]

for year, files in sorted(year_files.items()):
    n = len(files)
    dfs = [pd.read_csv(f, encoding="utf-8-sig") for f in sorted(files)]
    combined = pd.concat(dfs, ignore_index=True)

    agg = (
        combined
        .groupby(GROUP_KEYS, as_index=False)[NUMERIC_COLS]
        .mean()
        .rename(columns=RENAME_COLS)
    )
    agg["연도"] = int(year)
    agg["집계월수"] = n

    out_path = OUTPUT_DIR / f"annual_avg_{year}.csv"
    agg.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"{year}: {n}개월 평균 → {out_path.name}  ({len(agg)}행)")

print("\n완료. 저장 위치:", OUTPUT_DIR)
