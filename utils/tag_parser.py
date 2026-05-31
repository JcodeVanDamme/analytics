import re
import numpy as np
import pandas as pd

def parse_tags(tags):

    # ----------------------------
    # handle null / empty safely
    # ----------------------------
    if tags is None:
        return []

    if isinstance(tags, float):  # NaN case
        return []

    if isinstance(tags, (np.ndarray, pd.Series)):
        if len(tags) == 0:
            return []
        # if already structured
        return list(tags)

    # if it's a dict
    if isinstance(tags, dict):
        return list(tags.items())

    # if it's already a list
    if isinstance(tags, list):
        return tags

    # if it's string encoded
    if isinstance(tags, str):
        cleaned = tags.replace("\r", "").strip()

        matches = re.findall(r'"([^"]+)"\s*:\s*(\d+)', cleaned)
        if matches:
            return [(k, int(v)) for k, v in matches]

        return []

    return []