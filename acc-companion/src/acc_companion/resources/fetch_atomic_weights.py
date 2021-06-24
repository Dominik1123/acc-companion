"""Fetch the atomic weights from the ciaaw.org database and save a JSON dictionary,
   mapping symbols to atomic weights per nucleon in MeV.
"""

import ast
import json
from pathlib import Path
import re

import pandas as pd
from scipy.constants import physical_constants


URL = 'https://ciaaw.org/atomic-weights.htm'


def parse_atomic_weight(s):
    if s == '—':
        return None
    s = re.sub(r'\s', '', s)
    s = re.sub(r'\(\d+\)', '', s)
    v = ast.literal_eval(s)
    if isinstance(v, float):
        return v
    elif isinstance(v, list):
        assert len(v) == 2
        return (v[0] + v[1]) / 2
    else:
        assert False, type(v)


df = pd.read_html(URL)[0].iloc[:-1]
z_per_symbol = {
    s: int(z)
    for s, z in df.set_index('Symbol')['Z'].to_dict().items()
}
weight_per_symbol = {
    s: parse_atomic_weight(w)
    for s, w in df.set_index('Symbol')['Standard Atomic Weight'].to_dict().items()
}
data = {
    symbol: (
        weight
        * physical_constants['atomic mass constant energy equivalent in MeV'][0]
        / (2 * z_per_symbol[symbol])
    )
    for symbol, weight in weight_per_symbol.items()
    if weight is not None
}
data['H'] *= 2  # correct for wrong division by 2 above

save_path = Path(__file__).with_name('atomic_weights.json')
with open(save_path, 'w') as fh:
    json.dump(data, fh, indent=2)
