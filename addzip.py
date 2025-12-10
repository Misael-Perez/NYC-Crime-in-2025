from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point




crimedata= pd.read_csv("crime_data.csv")
gdf= gpd.GeoDataFrame( 
                      crimedata,
                      geometry=gpd.points_from_xy(crimedata["Longitude"], crimedata["Latitude"]),
                      crs="EPSG:4326"
                      )

shapes= gpd.read_file("Modified Zip Code Tabulation Areas (MODZCTA)_20251203 2/geo_export_2338bbb2-c8d8-44b4-bb68-b258e07eb6f5.shp")
shapes= shapes.to_crs("EPSG:4326")

newdata_withzip = gpd.sjoin(gdf, shapes, how="left", predicate="within")
newdata_withzip = newdata_withzip.rename(columns={"zcta": "ZIP"})

print(newdata_withzip.columns)
newdata_withzip= newdata_withzip.drop(["geometry",'index_right','modzcta','label','pop_est'], axis=1)
newdata_withzip.to_csv("crimedata_with_zip.csv", index=False)

