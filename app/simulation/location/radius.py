import math
import pandas as pd
from app.simulation.location.address_data import get_addresses_df
from app.simulation.location.matching_rich import haversine_km
from app.models.enums import AMLAccuracyEnum

BASE_RADIUS_KM = {                       # entspricht get_aml_radius im Notebook
    AMLAccuracyEnum.HIGH_ACCURACY: 0.03,
    AMLAccuracyEnum.MEDIUM_ACCURACY: 0.05,
    AMLAccuracyEnum.LOW_ACCURACY: 0.1,
    AMLAccuracyEnum.VERY_LOW_ACCURACY: 0.5,
}

def find_addresses_within_radius(lat, lon, radius_km) -> pd.DataFrame:
    df = get_addresses_df()
    dlat = radius_km / 111.0
    dlon = radius_km / (111.0 * math.cos(math.radians(lat)))
    box = df[(df["lat"].between(lat-dlat, lat+dlat)) & (df["lon"].between(lon-dlon, lon+dlon))].copy()
    box["distance_km"] = box.apply(lambda r: haversine_km(lat, lon, r["lat"], r["lon"]), axis=1)
    return box[box["distance_km"] <= radius_km].sort_values("distance_km")

def get_radius_candidates(aml_lat, aml_lon, acc: AMLAccuracyEnum, radius_factor=5) -> pd.DataFrame:
    """Adressen im 5×-Basisradius (deckt die Distanz-Score-Abklingzone ab)."""
    radius = BASE_RADIUS_KM.get(acc, 0.5) * radius_factor
    return find_addresses_within_radius(aml_lat, aml_lon, radius)