"""
preprocess_data.py
-------------------
Merges the two source datasets bundled with this project:

  1. labeled_data.csv         (Davidson et al., 2017 - "Automated Hate Speech
                                Detection and the Problem of Offensive Language")
                                24,783 tweets, labeled: 0=hate_speech,
                                1=offensive_language, 2=neither

  2. olid-training-v1_0.tsv   (Zampieri et al., 2019 - OLID / OffensEval,
                                SemEval-2019 Task 6)
                                13,240 tweets, hierarchical labels:
                                subtask_a: NOT / OFF
                                subtask_b: TIN / UNT   (only if OFF)
                                subtask_c: IND / GRP / OTH (only if TIN)

Both source datasets are ENGLISH-ONLY Twitter data. They do NOT contain
Hindi or Hinglish text. This script produces a clean, unified baseline
dataset for the "Indian Social Media" content moderation project. Hindi /
Hinglish support is added later by fine-tuning the same pipeline on
HASOC / HateXplain / L3Cube-HingCorpus data (see docs/07_AI_Model.md,
section "Extending to Hindi & Hinglish").

Unified 3-class label schema
-----------------------------
  SAFE       -> content with no offense / hate
  OFFENSIVE  -> profanity, insults, trolling, harassment (not identity-based)
  HATE       -> targeted, identity-based hate speech (religion, caste, gender,
                ethnicity, sexual orientation, political group, etc.)

Mapping rules
-------------
Davidson (labeled_data.csv):
  class 0 (hate_speech)        -> HATE
  class 1 (offensive_language) -> OFFENSIVE
  class 2 (neither)            -> SAFE

OLID (olid-training-v1_0.tsv):
  subtask_a == NOT                          -> SAFE
  subtask_a == OFF & subtask_b == UNT       -> OFFENSIVE   (untargeted profanity)
  subtask_a == OFF & subtask_b == TIN
        & subtask_c == GRP                  -> HATE        (group/identity target)
        & subtask_c in {IND, OTH}           -> OFFENSIVE   (targeted insult,
                                                             not identity-based)

This is a reasonable, documented approximation -- OLID does not explicitly
label "hate speech", but its own annotation guide defines GRP as "a group of
people considered as a unity due to the same ethnicity, gender, sexual
orientation, political affiliation, religious belief" which is the standard
definition of a hate-speech target. See docs/07_AI_Model.md for the full
justification and known limitations of this mapping.

Output
------
data/processed/
  merged_dataset.csv          full cleaned + unified pool (both sources)
  train.csv (80%)
  val.csv   (10%)
  test.csv  (10%)             stratified by unified label
  olid_official_test.csv      OLID's own SemEval test set (860 tweets) with
                               gold labels reconstructed from labels-level*.csv
                               -- kept OUT of train/val/test as an external
                               generalization check (never trained on).
"""

import re
import html
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
OUT = Path(__file__).resolve().parent.parent / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42


# ----------------------------------------------------------------------
# Text cleaning
# ----------------------------------------------------------------------
def clean_text(text: str) -> str:
    """Light-touch cleaning that preserves signal BERT-family models need
    (case, punctuation, emoji) while stripping noise (urls, RT boilerplate,
    HTML entities, extra whitespace)."""
    if not isinstance(text, str):
        return ""
    text = html.unescape(text)                     # &amp; -> &
    text = re.sub(r"^RT[\s]*[:@]?\S*[\s]*", "", text)  # leading "RT @user:"
    text = re.sub(r"http\S+|www\.\S+", "URL", text)    # normalize links
    text = re.sub(r"@\w+", "@USER", text)              # normalize mentions
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ----------------------------------------------------------------------
# Load + map: Davidson (labeled_data.csv)
# ----------------------------------------------------------------------
def load_davidson() -> pd.DataFrame:
    df = pd.read_csv(RAW / "labeled_data.csv")
    label_map = {0: "HATE", 1: "OFFENSIVE", 2: "SAFE"}
    out = pd.DataFrame({
        "text": df["tweet"].map(clean_text),
        "label": df["class"].map(label_map),
        "source": "davidson",
    })
    return out


# ----------------------------------------------------------------------
# Load + map: OLID training set
# ----------------------------------------------------------------------
def map_olid_row(a, b, c) -> str:
    if a == "NOT":
        return "SAFE"
    if a == "OFF" and b == "UNT":
        return "OFFENSIVE"
    if a == "OFF" and b == "TIN" and c == "GRP":
        return "HATE"
    if a == "OFF" and b == "TIN" and c in ("IND", "OTH"):
        return "OFFENSIVE"
    return None  # incomplete / malformed row -> dropped


def load_olid_training() -> pd.DataFrame:
    df = pd.read_csv(RAW / "olid-training-v1_0.tsv", sep="\t")
    df["label"] = df.apply(
        lambda r: map_olid_row(r["subtask_a"], r["subtask_b"], r["subtask_c"]),
        axis=1,
    )
    df = df.dropna(subset=["label"])
    out = pd.DataFrame({
        "text": df["tweet"].map(clean_text),
        "label": df["label"],
        "source": "olid",
    })
    return out


def load_olid_official_test() -> pd.DataFrame:
    """Reconstruct OLID's held-out SemEval test set (levels a/b/c) with gold
    labels, then apply the same unified mapping. Used ONLY for external
    evaluation, never for training."""
    tweets_a = pd.read_csv(RAW / "testset-levela.tsv", sep="\t")
    labels_a = pd.read_csv(RAW / "labels-levela.csv", names=["id", "subtask_a"])
    labels_b = pd.read_csv(RAW / "labels-levelb.csv", names=["id", "subtask_b"])
    labels_c = pd.read_csv(RAW / "labels-levelc.csv", names=["id", "subtask_c"])

    df = tweets_a.merge(labels_a, on="id", how="left")
    df = df.merge(labels_b, on="id", how="left")
    df = df.merge(labels_c, on="id", how="left")

    df["label"] = df.apply(
        lambda r: map_olid_row(r["subtask_a"], r.get("subtask_b"), r.get("subtask_c")),
        axis=1,
    )
    df = df.dropna(subset=["label"])
    out = pd.DataFrame({
        "text": df["tweet"].map(clean_text),
        "label": df["label"],
        "source": "olid_official_test",
    })
    return out


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    davidson = load_davidson()
    olid = load_olid_training()
    merged = pd.concat([davidson, olid], ignore_index=True)

    before = len(merged)
    merged = merged[merged["text"].str.len() > 0]
    merged = merged.drop_duplicates(subset=["text"])
    after = len(merged)
    print(f"Merged pool: {before} rows -> {after} after cleaning/dedup "
          f"({before - after} removed)")

    print("\nClass distribution (merged pool):")
    print(merged["label"].value_counts())
    print("\nBy source:")
    print(merged.groupby(["source", "label"]).size())

    merged.to_csv(OUT / "merged_dataset.csv", index=False)

    # Stratified 80/10/10 split
    train, temp = train_test_split(
        merged, test_size=0.20, stratify=merged["label"], random_state=RANDOM_SEED
    )
    val, test = train_test_split(
        temp, test_size=0.50, stratify=temp["label"], random_state=RANDOM_SEED
    )

    train.to_csv(OUT / "train.csv", index=False)
    val.to_csv(OUT / "val.csv", index=False)
    test.to_csv(OUT / "test.csv", index=False)

    print(f"\ntrain.csv: {len(train)} rows")
    print(f"val.csv:   {len(val)} rows")
    print(f"test.csv:  {len(test)} rows")

    # External, never-trained-on evaluation set
    official_test = load_olid_official_test()
    official_test.to_csv(OUT / "olid_official_test.csv", index=False)
    print(f"\nolid_official_test.csv (external eval only): {len(official_test)} rows")
    print(official_test["label"].value_counts())


if __name__ == "__main__":
    main()
