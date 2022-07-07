"""Fetch the atomic weights from the ciaaw.org database and save a JSON dictionary,
   mapping symbols to atomic weights per nucleon in MeV.
"""

from collections import defaultdict
import json
from pathlib import Path
import re
from urllib.error import HTTPError

import pandas as pd
from scipy.constants import physical_constants


URL = 'https://ciaaw.org'
AMU_MEV = physical_constants['atomic mass constant energy equivalent in MeV'][0]
AVAILABLE = '\u2714'
NOT_AVAILABLE = '\u2718'


def parse_atomic_weight(s):
    s = re.sub(r'\s', '', s)
    m = re.fullmatch(r'([1-9][0-9]*(?:[.][0-9]+)?)\((?:exact|[0-9])\)', s)
    return float(m.group(1))


def parse_isotope(s):
    s = re.sub(r'\s', '', s)
    m = re.fullmatch('([1-9][0-9]*)([A-Z][a-z]*)', s)
    return m.group(2), int(m.group(1))


data = defaultdict(dict)
for element in pd.read_html(f'{URL}/atomic-weights.htm')[0]['Element']:
    print(f'{element}', end=' ', flush=True)
    try:
        df, = pd.read_html(f'{URL}/{element}.htm')
    except HTTPError as err:
        if err.code != 404:
            raise
        print(NOT_AVAILABLE)
    else:
        for __, (isotope, atomic_mass) in df.loc[:,['Isotope', 'Atomic mass (Da)']].iterrows():
            element, number_of_nucleons = parse_isotope(isotope)
            data[element][number_of_nucleons] = AMU_MEV * parse_atomic_weight(atomic_mass) / number_of_nucleons
        print(AVAILABLE)

save_path = Path(__file__).with_name('atomic_weights_in_MeV.json')
with open(save_path, 'w') as fh:
    json.dump(dict(data), fh, indent=2)
