"""Felles evaluering, slik at alle modeller måles likt og per kilde.

Et samlet tall over alle testsett skjuler det viktigste: forskjellen mellom
kilder modellen har sett i treningen og kilder den ikke har sett.
"""
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score


def threshold_for_fpr(y, scores, max_fpr=0.01):
    """Laveste terskel der høyst max_fpr av de benigne får score over terskelen.

    Prediksjon er `scores > terskel`.
    """
    benign = np.sort(np.asarray(scores)[np.asarray(y) == 0])
    allowed = int(np.floor(max_fpr * len(benign)))
    return benign[len(benign) - allowed - 1]


def evaluate_by_source(df, scores, threshold=0.5):
    """Precision, recall, F1, andel falske positive og ROC AUC per kilde.

    Mål som ikke gir mening for en kilde (f.eks. precision når kilden bare
    har angrep) settes til NaN.
    """
    rows = []
    for source, g in df.assign(score=np.asarray(scores)).groupby("source"):
        y = g["label"].to_numpy()
        s = g["score"].to_numpy()
        pred = (s > threshold).astype(int)
        has_pos, has_neg = y.any(), (~y.astype(bool)).any()
        both = has_pos and has_neg
        rows.append({
            "kilde": source,
            "n": len(g),
            "angrep": int(y.sum()),
            "precision": precision_score(y, pred, zero_division=np.nan) if both else np.nan,
            "recall": recall_score(y, pred) if has_pos else np.nan,
            "f1": f1_score(y, pred) if both else np.nan,
            "fpr": pred[y == 0].mean() if has_neg else np.nan,
            "roc_auc": roc_auc_score(y, s) if both else np.nan,
        })
    return pd.DataFrame(rows).set_index("kilde").round(3)
