import re, math, random
from rapidfuzz import fuzz
from sqlalchemy.orm import Session
from app.models.address_db import AddressDB
from app.models.enums import AMLAccuracyEnum


def normalize_text(s: str) -> str:
    """Lowercase, Umlaute auflösen, Satzzeichen entfernen – für Fuzzy-Matching."""
    if not s:
        return ""
    s = s.lower()
    s = s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = re.sub(r"[^\w\s]", "", s)
    return s.strip()


def normalize_hn(hn: str) -> str:
    """Hausnummern: Uppercase, keine Leerzeichen."""
    if not hn:
        return ""
    return re.sub(r"\s+", "", hn.upper())


def fuzzy_best(value: str, candidates: list[str], min_score: int = 70) -> tuple[str | None, int]:
    """Bester Fuzzy-Match für value in candidates (token_sort_ratio)."""
    best_match, best_score = None, 0
    for candidate in candidates:
        score = fuzz.token_sort_ratio(value, candidate)
        if score > best_score:
            best_score, best_match = score, candidate
    return (best_match, best_score) if best_score >= min_score else (None, best_score)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """GPS-Distanz zweier Punkte in km."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def find_addresses_within_radius(lat: float, lon: float, radius_km: float, db: Session) -> list[AddressDB]:
    """DB-Adressen im GPS-Radius. Erst grobe Box (schnell), dann exakte Distanz."""
    delta_lat = radius_km / 111.0
    delta_lon = radius_km / (111.0 * math.cos(math.radians(lat)))
    candidates = db.query(AddressDB).filter(
        AddressDB.lat.between(lat - delta_lat, lat + delta_lat),
        AddressDB.lon.between(lon - delta_lon, lon + delta_lon),
    ).all()
    return [a for a in candidates if haversine_km(lat, lon, a.lat, a.lon) <= radius_km]


def find_address_adaptive(city, street, housenumber, db: Session, min_score: int = 75) -> list[AddressDB]:
    """Mehrstufige Adresssuche gegen DB: Stadt → Straße → Hausnummer (Fuzzy)."""
    city_norm = normalize_text(city or "")
    street_norm = normalize_text(street or "")
    hn_norm = normalize_hn(housenumber or "")

    all_cities = [r[0] for r in db.query(AddressDB.city_norm).distinct().all()]
    best_city, _ = fuzzy_best(city_norm, all_cities, min_score)
    if not best_city:
        return []

    city_addrs = db.query(AddressDB).filter(AddressDB.city_norm == best_city).all()
    city_streets = list({a.street_norm for a in city_addrs})
    best_street, _ = fuzzy_best(street_norm, city_streets, min_score)
    if not best_street:
        return []

    street_addrs = [a for a in city_addrs if a.street_norm == best_street]
    if hn_norm:
        hn_candidates = [a.hn_norm for a in street_addrs if a.hn_norm]
        best_hn, _ = fuzzy_best(hn_norm, hn_candidates, 80)
        if best_hn:
            matched = [a for a in street_addrs if a.hn_norm == best_hn]
            if matched:
                return matched
    return street_addrs


def blur_gps(lat: float, lon: float, min_km: float, max_km: float) -> tuple[float, float]:
    """Verschiebt GPS um zufällige Distanz/Richtung (AML-Simulation)."""
    distance_km = random.uniform(min_km, max_km)
    angle = random.uniform(0, 2 * math.pi)
    delta_lat = (distance_km / 111.0) * math.cos(angle)
    delta_lon = (distance_km / (111.0 * math.cos(math.radians(lat)))) * math.sin(angle)
    return lat + delta_lat, lon + delta_lon


def simulate_aml(lat: float, lon: float) -> tuple[float, float, AMLAccuracyEnum]:
    """Simuliert Handy-Ortung mit zufälliger Genauigkeit. Vom Router (B5) genutzt."""
    r = random.random()
    if r < 0.35:
        acc, (la, lo) = AMLAccuracyEnum.HIGH_ACCURACY, blur_gps(lat, lon, 0, 0.05)
    elif r < 0.70:
        acc, (la, lo) = AMLAccuracyEnum.MEDIUM_ACCURACY, blur_gps(lat, lon, 0, 0.15)
    elif r < 0.90:
        acc, (la, lo) = AMLAccuracyEnum.LOW_ACCURACY, blur_gps(lat, lon, 0, 0.5)
    else:
        acc, (la, lo) = AMLAccuracyEnum.VERY_LOW_ACCURACY, blur_gps(lat, lon, 0.5, 5.0)
    return la, lo, acc