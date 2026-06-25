# app/simulation/location/matching_rich.py
import re
import math
import pandas as pd
from rapidfuzz import process, fuzz

from app.models.address import Address, AddressType, SourceEnum
from app.simulation.location.address_data import get_addresses_df


# ---------------------------------------------------------------------------
# Normalisierung & Fuzzy-Helfer
# ---------------------------------------------------------------------------
def normalize_text(s) -> str:
    """Lowercase, Umlaute, Satzzeichen raus, 'straße'->'strasse' – für Fuzzy-Matching."""
    if pd.isna(s):
        return ""
    s = str(s).strip().lower()
    s = s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = re.sub(r"[.,]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("straße", "strasse")
    s = re.sub(r"\bstr\.\b", "strasse", s)
    return s


def normalize_hn(hn) -> str:
    """Hausnummer: Uppercase, keine Leerzeichen ('12 a' -> '12A')."""
    if pd.isna(hn):
        return ""
    return re.sub(r"\s+", "", str(hn).strip().upper())


def fuzzy_best(value: str, candidates: list[str], min_score: int):
    """Bester Treffer via token_sort_ratio, nur wenn Score >= min_score."""
    m = process.extractOne(value, candidates, scorer=fuzz.token_sort_ratio)
    if m and m[1] >= min_score:
        return m[0], m[1]          # (gematchter Wert, Score 0..100)
    return None


def _clean(value):
    """pandas/NumPy-Fehlwerte (NaN) -> None."""
    if value is None:
        return None
    if isinstance(value, (list, dict, tuple, set)):
        return value
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2))
    R = 6371.0088
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


# ---------------------------------------------------------------------------
# Adaptive Adresssuche gegen den DataFrame
# ---------------------------------------------------------------------------
def find_address_adaptive(
    address: Address,
    city_schedule=(92, 88, 85, 82, 78, 75, 72),
    street_schedule=(92, 90, 88, 85, 82, 80, 78, 75),
    min_rows=1,
    max_rows=25,
    require_same_city_for_street=True,
    min_street_len_for_fuzzy=4,
) -> list[Address]:
    """Mehrstufig: exakt -> City-Fuzzy -> exakte Straße in City -> Street-Fuzzy in City
    -> Contains-Fallback -> optional globales Street-Fuzzy.
    Die zurückgegebenen DB-Adressen erben confidence/type des LLM-Kandidaten und
    tragen die Match-Scores in fuzzy_mode."""
    df = get_addresses_df()

    c_in = normalize_text(address.city)
    s_in = normalize_text(address.street)
    hn_in = normalize_hn(address.housenumber)

    def to_addresses(matches: pd.DataFrame, fuzzy_mode: dict) -> list[Address]:
        out = []
        for _, row in matches.head(max_rows).iterrows():
            out.append(Address(
                osm_id=_clean(row.get("osm_id")),
                city=_clean(row.get("city")),
                street=_clean(row.get("street")),
                housenumber=_clean(row.get("housenumber")),
                postcode=_clean(row.get("postcode")),
                lat=_clean(row.get("lat")),          # lat/lon direkt aus DB – fürs Scoring
                lon=_clean(row.get("lon")),
                type=address.type,
                confidence=address.confidence,       # FIX: Confidence des LLM-Kandidaten übernehmen
                source=SourceEnum.ADDRESS_DATABASE,
                fuzzy_mode=fuzzy_mode.copy(),         # enthält city_score / street_score
            ))
        return out

    # 0) exakt (Stadt + Straße + Hausnummer)
    exact = df.loc[(df["city_norm"] == c_in) & (df["street_norm"] == s_in) & (df["hn_norm"] == hn_in)]
    if len(exact) >= min_rows:
        return to_addresses(exact, {"mode": "exact", "city_score": 100, "street_score": 100})

    # 1) City-Fuzzy (adaptiv absteigende Schwellen)
    city_candidates = df["city_norm"].dropna().unique().tolist()
    city_best, city_score = None, None
    for cs in city_schedule:
        m = fuzzy_best(c_in, city_candidates, cs)
        if m:
            city_best, city_score = m
            break
    scope = df if not city_best else df[df["city_norm"] == city_best]

    # 2) exakte Straße + Hausnummer innerhalb der gefundenen Stadt
    exact_street = scope.loc[(scope["street_norm"] == s_in) & (scope["hn_norm"] == hn_in)]
    if len(exact_street) >= min_rows:
        return to_addresses(exact_street, {"mode": "city_exact_street", "city_score": city_score, "street_score": 100})

    # 3) Street-Fuzzy innerhalb der Stadt
    street_candidates = scope["street_norm"].dropna().unique().tolist()
    if len(s_in) >= min_street_len_for_fuzzy:
        for ss in street_schedule:
            m = fuzzy_best(s_in, street_candidates, ss)
            if m:
                street_best, street_score = m
                hits = scope.loc[(scope["street_norm"] == street_best) & (scope["hn_norm"] == hn_in)]
                if len(hits) >= min_rows:
                    return to_addresses(hits, {"mode": "city_fuzzy_street", "city_score": city_score, "street_score": street_score})

    # 4) Contains-Fallback (Anfang des Straßennamens)
    seed = s_in[:max(3, len(s_in) // 2)]
    fallback = scope.loc[
        (scope["hn_norm"] == hn_in) & (scope["street_norm"].str.contains(re.escape(seed), na=False))
    ]
    if len(fallback) > 0:
        return to_addresses(fallback, {"mode": "contains_fallback", "city_score": city_score, "street_score": None})

    # 5) optional: globales Street-Fuzzy (über Stadtgrenzen hinweg)
    if not require_same_city_for_street and len(s_in) >= min_street_len_for_fuzzy:
        global_streets = df["street_norm"].dropna().unique().tolist()
        for ss in street_schedule:
            m = fuzzy_best(s_in, global_streets, ss)
            if m:
                street_best, street_score = m
                hits = df.loc[(df["street_norm"] == street_best) & (df["hn_norm"] == hn_in)]
                if len(hits) >= min_rows:
                    return to_addresses(hits, {"mode": "global_fuzzy_street", "city_score": None, "street_score": street_score})

    return []


# ---------------------------------------------------------------------------
# Listen verarbeiten + Distanzen
# ---------------------------------------------------------------------------
def _flatten(address_list) -> list[Address]:
    """find_address_adaptive liefert pro Kandidat eine Liste -> alles flach machen."""
    result = []
    def rec(item):
        if item is None:
            return
        if isinstance(item, (list, tuple)):
            for el in item:
                rec(el)
        else:
            result.append(item)
    rec(address_list)
    return result


def get_distances(address_list: list[Address], aml_lat, aml_lon) -> list[Address]:
    """Setzt gps_distance je Kandidat (Haversine zur AML-Position; None wenn AML fehlt)."""
    for a in address_list:
        if aml_lat and aml_lon and a.lat is not None and a.lon is not None:
            a.gps_distance = haversine_km(aml_lat, aml_lon, a.lat, a.lon)
        else:
            a.gps_distance = None
    return address_list


def get_addresses_from_db(candidate_list: list[Address], aml_lat=None, aml_lon=None) -> list[Address]:
    """Weg A: pro LLM-Kandidat DB-Match -> flach -> Distanzen -> nach Distanz sortiert."""
    matched = [find_address_adaptive(a) for a in candidate_list]
    matched = _flatten(matched)
    matched = get_distances(matched, aml_lat, aml_lon)
    matched.sort(key=lambda a: float("inf") if a.gps_distance is None else a.gps_distance)
    return matched