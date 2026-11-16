import pandas as pd
from sklearn.ensemble import IsolationForest

def analyze_csv(path: str):
    df = pd.read_csv(path)
    numeric = df.select_dtypes(include="number")
    result = {"rows": int(len(df)), "columns": list(df.columns), "missing_values": {k:int(v) for k,v in df.isna().sum().items()}, "numeric_summary": numeric.describe().replace({float('nan'):None}).to_dict() if not numeric.empty else {}, "anomalies": []}
    if len(numeric.columns) and len(df) >= 10:
        clean = numeric.fillna(numeric.median())
        model = IsolationForest(contamination="auto", random_state=42)
        labels = model.fit_predict(clean)
        result["anomalies"] = [{"row": int(i), "values": df.iloc[i].where(pd.notna(df.iloc[i]), None).to_dict()} for i, label in enumerate(labels) if label == -1][:30]
    return result
