import geopandas as gpd

from .config import GEODATA_FILE
from .coords_finder import normalize_teryt
from shapely import Point

class PointValidator:
    _dataframe = None

    @classmethod
    def _load_data(cls):
        if cls._dataframe is None:
            gdf = gpd.read_file(GEODATA_FILE)
            gdf['JPT_KOD_JE'] = gdf['JPT_KOD_JE'].str[:-1].apply(normalize_teryt)
            gdf = gdf.to_crs('EPSG:2180')
            gdf = gdf.set_index('JPT_KOD_JE', drop=True)
            cls._dataframe = gdf
            

    @classmethod
    def validate_point(cls, teryt, point) -> bool:
        """Checks whether points lies in municipality"""
        cls._load_data()
        gdf = cls._dataframe.copy()
        if teryt not in gdf.index:
            return False

        row = gdf.loc[teryt]

        return row.geometry.covers(point)

    @classmethod
    def get_centroid(cls, teryt) -> bool:
        """Returns centroid of the municipality"""
        cls._load_data()
        gdf = cls._dataframe.copy()
        if teryt not in gdf.index:
            return None
        return gdf.loc[teryt].geometry.centroid
    
    @classmethod
    def inverse_coords(cls, point: Point) -> Point:
        x = point.x
        y = point.y
        return Point(y,x)
