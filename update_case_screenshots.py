
import sys, os, re
import pandas as pd

def main(shots_dir, excel_path, out_path=None):
    shots = [f for f in os.listdir(shots_dir) if f.lower().endswith(".png")]
    mapping = {}
    for fn in shots:
        # expect: TIMESTAMP_CaseId.png  => extract CaseId
        m = re.match(r'^\d+_(BaiDuMap_[A-Z0-9]+_\d{3})\.png$', fn)
        if m:
            mapping[m.group(1)] = fn
    if not mapping:
        print("No matching screenshots found.")
        return
    df = pd.read_excel(excel_path, sheet_name="Sheet1")
    if "测试用例编号" not in df.columns or "截图文件名" not in df.columns:
        raise RuntimeError("Excel columns missing.")
    for i,row in df.iterrows():
        cid = row["测试用例编号"]
        if cid in mapping:
            df.at[i, "截图文件名"] = mapping[cid]
    out_path = out_path or excel_path
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Sheet1", index=False)
        # keep empty sheets
        pd.DataFrame().to_excel(writer, sheet_name="Sheet2", index=False)
        pd.DataFrame().to_excel(writer, sheet_name="Sheet3", index=False)
    print(f"Updated Excel saved to: {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python update_case_screenshots.py <screenshots_dir> <excel_path> [out_path]")
        sys.exit(1)
    shots_dir = sys.argv[1]
    excel_path = sys.argv[2]
    out_path = sys.argv[3] if len(sys.argv) > 3 else None
    main(shots_dir, excel_path, out_path)
