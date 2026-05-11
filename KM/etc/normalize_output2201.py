"""
output2201 포맷을 monthly_batch 포맷에 맞게 통일하는 스크립트.

작업 내용:
  1. 02_모형별_점수결과.csv  → monthly_scores_all_2201.csv (한글 컬럼, 모형명 통일)
  2. 월별_통합집계.csv       → od_combined_2201.csv       (start_arv_place_type 한글화)
  3. 월별_요약.csv           → monthly_summary_2201.csv   (컬럼명 통일)
"""

import pandas as pd
from pathlib import Path

SRC  = Path(r"C:\Users\sun94\Downloads\commute_stress_파이프라인\commute_stress_파이프라인\project2022\output2201")
DEST = Path(r"C:\Users\sun94\Downloads\commute_stress_파이프라인\commute_stress_파이프라인\project2022\monthly_batch_2201")
DEST.mkdir(exist_ok=True)

# ── 1. 02_모형별_점수결과 → monthly_scores_all_2201 ──────────────────────────

COL_RENAME = {
    "gu":           "자치구코드",
    "total_pop":    "총이동인구수",
    "avg_time":     "평균이동시간",
    "total_time":   "총이동시간",
    "pop_norm":     "유입인구_norm",
    "avg_norm":     "평균이동시간_norm",
    "total_norm":   "총이동시간_norm",
    "stress_score": "출퇴근스트레스점수",
    "model":        "모형",
    "w_pop":        "가중치_유입인구",
    "w_avg":        "가중치_평균이동시간",
    "w_total":      "가중치_총이동시간",
}
MODEL_RENAME = {
    "critic":     "CRITIC기반",
    "pca":        "PCA기반",
    "literature": "문헌기반",
}

df_scores = pd.read_csv(SRC / "02_모형별_점수결과.csv", encoding="utf-8-sig")
df_scores = df_scores.rename(columns=COL_RENAME)
df_scores["모형"] = df_scores["모형"].map(MODEL_RENAME)
df_scores.insert(0, "연도", 2022)
df_scores.insert(1, "월",   1)

out1 = DEST / "monthly_scores_all_2201.csv"
df_scores.to_csv(out1, index=False, encoding="utf-8-sig")
print(f"[OK] monthly_scores_all_2201.csv  ({len(df_scores)}행)")
print("  컬럼:", list(df_scores.columns))

# ── 2. 월별_통합집계 → od_combined_2201 ─────────────────────────────────────
#    start_arv_place_type: H=집, W=직장, E=기타
#    HW=출근, WH=퇴근, HE=집→기타, EH=기타→집

PLACE_KO = {"H": "집", "W": "직장", "E": "기타"}

def decode_place_type(code: str) -> tuple[str, str, str]:
    """'HW' → ('집', '직장', '집→직장')"""
    s, d = PLACE_KO[code[0]], PLACE_KO[code[1]]
    return s, d, f"{s}→{d}"

df_od = pd.read_csv(SRC / "월별_통합집계.csv", encoding="utf-8-sig")

decoded = df_od["start_arv_place_type"].apply(decode_place_type)
df_od["출발_장소유형"] = [x[0] for x in decoded]
df_od["도착_장소유형"] = [x[1] for x in decoded]
df_od["이동유형"]     = [x[2] for x in decoded]
df_od = df_od.drop(columns=["start_arv_place_type"])

# 연월 → 연도/월 분리
df_od[["연도", "월"]] = df_od["연월"].str.split("-", expand=True).astype(int)
df_od = df_od.drop(columns=["연월"])

# 컬럼 순서 정리
df_od = df_od[["연도", "월", "출발_자치구코드", "도착_자치구코드",
               "출발_장소유형", "도착_장소유형", "이동유형",
               "총이동인구수", "인구가중평균이동시간"]]

out2 = DEST / "od_combined_2201.csv"
df_od.to_csv(out2, index=False, encoding="utf-8-sig")
print(f"\n[OK] od_combined_2201.csv  ({len(df_od)}행)")
print("  컬럼:", list(df_od.columns))
print("  이동유형 종류:", sorted(df_od["이동유형"].unique()))

# ── 3. 월별_요약 → monthly_summary_2201 ──────────────────────────────────────

df_summary = pd.read_csv(SRC / "월별_요약.csv", encoding="utf-8-sig")
df_summary = df_summary.rename(columns={"연월": "연월", "월총이동인구수": "월총이동인구수"})
df_summary.insert(0, "연도", 2022)
df_summary.insert(1, "월",   1)

out3 = DEST / "monthly_summary_2201.csv"
df_summary.to_csv(out3, index=False, encoding="utf-8-sig")
print(f"\n[OK] monthly_summary_2201.csv  ({len(df_summary)}행)")

print(f"\n저장 위치: {DEST}")
print("\n※ monthly_batch_2205 이후에는 od_combined(OD+이동유형) 파일이 없습니다.")
print("   원본 OUTPUT.csv 파일이 있으면 동일한 형식으로 생성 가능합니다.")
