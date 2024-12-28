from lxml import etree
import geopandas as gpd
from shapely.geometry import Point, Polygon

def load_kml(kml_path: str) -> gpd.GeoDataFrame:
    """
    Carga puntos (cajas NAP) y polígonos (zonas urbanas) desde un archivo KML.
    :param kml_path: Ruta del archivo KML.
    :return: Tuple de GeoDataFrames (puntos, poligonos)
    """
    with open(kml_path, "rb") as file:
        content = file.read()
    parser = etree.XMLParser(ns_clean=True, recover=True)
    tree = etree.fromstring(content, parser)
    namespaces = {"kml": "http://www.opengis.net/kml/2.2"}

    points = []
    polygons = []
    
    for placemark in tree.xpath("//kml:Placemark", namespaces=namespaces):
        # Extraer coordenadas de puntos
        coords = placemark.xpath(".//kml:Point/kml:coordinates", namespaces=namespaces)
        for coord in coords:
            lon, lat, *_ = map(float, coord.text.strip().split(","))
            points.append((lon, lat))
        # Extraer coordenadas de poligonos
        poly_coords = placemark.xpath(".//kml:Polygon//kml:coordinates", namespaces=namespaces)
        for poly in poly_coords:
            if(poly != None):
                coord_list = [tuple(map(float, c.split(",")[:2])) for c in poly.text.strip().split()]
                polygons.append(Polygon(coord_list))
    gdf_points = gpd.GeoDataFrame(geometry=[Point(lon, lat) for lon, lat in points], crs="EPSG:4326")
    gdf_polygons = gpd.GeoDataFrame(geometry=polygons, crs="EPSG:4326")
    # gdf_polygons = gdf_polygons[gdf_polygons.is_valid]
    return gdf_points, gdf_polygons