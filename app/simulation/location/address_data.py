import pandas as pd
from functools import lru_cache

CSV_PATH = "addresses/saarland_addresses_norm.csv"

@lru_cache(maxsize=1)
def get_addresses_df() -> pd.DataFrame:
    """Adress-CSV einmalig laden (Norm-Spalten city_norm/street_norm/hn_norm sind enthalten)."""
    return pd.read_csv(CSV_PATH)