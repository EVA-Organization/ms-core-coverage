import geopandas as gpd
from shapely.geometry import Point
from utils import load_kml

# Carga inicial del archivo KML
gdf_points, gdf_polygons = load_kml("data/map.kml")

def get_zone_type(point: Point) -> str:
    """
    Determina si una coordenada está dentro de un polígono (zona urbana o rural).
    :param point: Coordenada a evaluar.
    :return: 'urban' si está dentro de un polígono, 'rural' en caso contrario.
    """
    # Crear un GeoDataFrame con el punto y el CRS
    point_gdf = gpd.GeoDataFrame(geometry=[point], crs="EPSG:4326")
    if gdf_polygons.contains(point_gdf.geometry.iloc[0]).any():
        return "urban"
    return "rural"

def check_coverage(latitude: float, longitude: float) -> bool:
    """
    Verifica si una coordenada está dentro del radio de alguna caja NAP.
    :param latitude: Latitud del punto a verificar.
    :param longitude: Longitud del punto a verificar.
    :return: True si está en cobertura, False en caso contrario.
    """
    # Crear el punto del usuario
    user_point = Point(longitude, latitude)
    user_point_gdf = gpd.GeoDataFrame(geometry=[user_point], crs="EPSG:4326").to_crs(epsg=3857)
    
    # Reproyectar las cajas NAP al mismo CRS
    gdf_points_3857 = gdf_points.to_crs(epsg=3857)

    coverage_found = False
    for _, nap_row in gdf_points_3857.iterrows():
        # Determinar si la caja NAP está en zona urbana o rural
        nap_geometry_latlon = gpd.GeoSeries([nap_row.geometry], crs="EPSG:3857").to_crs(epsg=4326).iloc[0]
        zone_type = get_zone_type(nap_geometry_latlon)  # No intentamos reproyectar aquí
        buffer_distance = 150 if zone_type == "urban" else 200

        # Crear buffer alrededor de la caja NAP
        buffer = nap_row.geometry.buffer(buffer_distance)
        if buffer.contains(user_point_gdf.geometry.iloc[0]):
            print(f"nap_row.geometry: {nap_geometry_latlon}")
            print(f"buffer_distance: {buffer_distance}")
            print(f"zone_type: {zone_type}")
            coverage_found = True
            break

    return coverage_found