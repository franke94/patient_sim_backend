from app.models.enums import AMLAccuracyEnum
from app.simulation.location.matching_rich import haversine_km
from app.simulation.location.radius import get_radius_candidates, BASE_RADIUS_KM
import pandas as pd
AML_CORRECTION = {
    AMLAccuracyEnum.HIGH_ACCURACY: 1.0, AMLAccuracyEnum.MEDIUM_ACCURACY: 0.9,
    AMLAccuracyEnum.LOW_ACCURACY: 0.7, AMLAccuracyEnum.VERY_LOW_ACCURACY: 0.5,
}

def get_distance_score(distance, acc) -> float:
    """1.0 innerhalb Basisradius, linear bis 0 beim 5-fachen, danach 0."""
    base = BASE_RADIUS_KM.get(acc)
    if distance is None or not base:
        return 0.0
    if distance <= base:
        return 1.0
    if distance >= 5 * base:
        return 0.0
    return (5 * base - distance) / (4 * base)

def get_aml_score(distance, acc) -> float:
    if acc is None or distance is None:
        return 0.0
    return get_distance_score(distance, acc) * AML_CORRECTION.get(acc, 0.5)

def get_on_scene_score(agent_status, agent_conf, human_result=None) -> float:
    if human_result is True:  return 1.0
    if human_result is False: return 0.0
    if agent_status == "yes": return agent_conf or 0.0
    if agent_status == "no":  return 1.0 - (agent_conf or 0.0)
    return 0.5

def _score_candidate(cand, aml_lat, aml_lon, acc, on_scene_score) -> dict:
    fm = cand.get("fuzzy_mode") or {}
    city_score = (fm.get("city_score") or 0) / 100
    street_score = (fm.get("street_score") or 0) / 100
    confidence = cand.get("confidence") or 0.0

    db_fuzzy = city_score * street_score
    aa_score = confidence * db_fuzzy

    dist = (haversine_km(aml_lat, aml_lon, cand["lat"], cand["lon"])
            if aml_lat and aml_lon and cand.get("lat") and cand.get("lon") else None)

    dist_score = get_distance_score(dist, acc)                       # NEU explizit
    correction = AML_CORRECTION.get(acc, 0.5) if acc is not None else 0.0   # NEU explizit
    aml = dist_score * correction                                   # == get_aml_score(dist, acc)
    location = aml * on_scene_score
    aa_distance = location * aa_score
    address_score = aa_distance + aa_score + location

    return {
        **cand, "distance_km": dist,
        # Blattwerte für den Score-Baum:
        "db_fuzzy_city_score": city_score,
        "db_fuzzy_street_score": street_score,
        "distance_score": dist_score,
        "aml_correction_score": correction,
        "aml_radius": BASE_RADIUS_KM.get(acc),
        # bisherige Werte:
        "db_fuzzy_score": db_fuzzy,
        "address_agent_confidence_score": confidence,
        "address_agent_score": aa_score,
        "aml_score": aml,
        "location_score": location,
        "address_agent_distance_score": aa_distance,
        "address_score": address_score,
    }

def score_candidates(*, matched_addresses, aml_lat, aml_lon, aml_accuracy,
                     on_scene_status, on_scene_conf, on_scene_human=None) -> dict:
    """Vereint address_agent-Treffer ∪ Radius-Adressen, scort einheitlich, rankt."""
    on_scene_score = get_on_scene_score(on_scene_status, on_scene_conf, on_scene_human)

    by_osm = {}
    for a in matched_addresses:                       # Weg A (mit fuzzy_mode + confidence)
        if a.get("osm_id") is not None:
            by_osm[a["osm_id"]] = dict(a)

    if aml_lat and aml_lon and aml_accuracy is not None:  # Weg B (Radius)
        for _, row in get_radius_candidates(aml_lat, aml_lon, aml_accuracy).iterrows():
            osm = int(row["osm_id"])
            if osm not in by_osm:
                by_osm[osm] = {
                    "osm_id": osm,
                    "city": str(row["city"]) if pd.notna(row["city"]) else None,
                    "street": str(row["street"]) if pd.notna(row["street"]) else None,
                    "housenumber": str(row["housenumber"]) if pd.notna(row["housenumber"]) else None,
                    "postcode": int(row["postcode"]) if pd.notna(row["postcode"]) else None,
                    "lat": float(row["lat"]),
                    "lon": float(row["lon"]),
                }

    scored = [_score_candidate(c, aml_lat, aml_lon, aml_accuracy, on_scene_score)
              for c in by_osm.values()]
    scored = [s for s in scored if s["address_score"] > 0]
    scored.sort(key=lambda s: s["address_score"], reverse=True)
    return {"on_scene_score": on_scene_score, "candidates": scored}