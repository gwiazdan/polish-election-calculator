import geopandas as gpd

from .config import GEODATA_FILE


class PointValidator:
    _dataframe = None

    @classmethod
    def _load_data(cls):
        if cls._dataframe is None:
            gdf = gpd.read_file(GEODATA_FILE)
            gdf['JPT_KOD_JE'] = gdf['JPT_KOD_JE'].str[:-1]
            cls._dataframe = gdf
            

    @classmethod
    def validate_point(cls, teryt, point) -> bool:
        """Checks whether points lies in municipality"""
        cls._load_data()
        gdf = cls._dataframe.set_index("JPT_KOD_JE").copy()
        if teryt not in gdf.index:
            return False

        row = gdf.loc[teryt]

        return row.geometry.contains(point)

    @classmethod
    def get_centroid(cls, teryt) -> bool:
        """Returns centroid of the municipality"""
        cls._load_data()
        gdf = cls._dataframe.set_index("JPT_KOD_JE").copy()
        if teryt not in gdf.index:
            return None
        return gdf.loc[teryt].geometry.centroid
