import geopandas as gpd
from sklearn.neighbors import NearestNeighbors
import numpy as np
import pandas as pd

def main():
    df = pd.read_csv('../data/geocoded_polling_districts.csv')
    df['geometry'] = df['geometry'].astype(str)
    df['geometry'] = gpd.GeoSeries.from_wkt(df['geometry'])
    gdf = gpd.GeoDataFrame(df, crs='EPSG:2180')

    df_psl = pd.read_csv('../data/psl.csv')
    df_psl['geometry'] = df_psl['geometry'].astype(str)
    df_psl['geometry'] = gpd.GeoSeries.from_wkt(df_psl['geometry'])
    gdf_psl = gpd.GeoDataFrame(df_psl, crs='EPSG:2180')

    gdf_psl['psl_pct'] = gdf_psl['psl'].astype(int) / gdf_psl['total_votes'].astype(int)
    psl_votes = knn_pct_interpolate(gdf, gdf_psl, 4)
    df['psl'] = round(psl_votes * df['total_votes'] / (1-psl_votes))
    df['total_votes'] += df['psl']

    print(df['psl'])
    results = df.select_dtypes(include="number").sum(axis=0)
    results = results[3:]
    results /= results['total_votes']
    print(results*100)
    df = df.drop(columns='address_id')
    for col in df.columns[3:]:
        df[col] = df[col].astype(int)
    df.to_csv('../data/final.csv', index=False)

def knn_pct_interpolate(gdf: gpd.GeoDataFrame, gdf_psl: gpd.GeoDataFrame, k=4):
    curr_coords = np.array([
        [p.centroid.x, p.centroid.y] 
        for p in gdf.to_crs('EPSG:3857').geometry
    ])
    hist_coords = np.array([
        [p.centroid.x, p.centroid.y] 
        for p in gdf_psl.to_crs('EPSG:3857').geometry
    ])

    nbrs = NearestNeighbors(n_neighbors=k).fit(hist_coords)
    _, indices = nbrs.kneighbors(curr_coords)

    interpolated_pct = np.array([gdf_psl['psl_pct'].iloc[idx].mean() for idx in indices])
    return pd.Series(interpolated_pct, index=gdf.index)

if __name__ == "__main__":
    main()
