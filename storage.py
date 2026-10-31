
import pandas as pd
from pathlib import Path

CSV_FILE = Path("feedback.csv")

COLUMNS = ["comment", "rating", "label"]


def load_feedback():
    if CSV_FILE.exists():
        return pd.read_csv(CSV_FILE)

    return pd.DataFrame(columns=COLUMNS)


def save_feedback(comment, rating, label):
    df = load_feedback()

    new_feedback = pd.DataFrame([{
        "comment": comment,
        "rating": rating,
        "label": label
    }])

    df = pd.concat(
        [df, new_feedback],
        ignore_index=True
    )

    df.to_csv(CSV_FILE, index=False)
