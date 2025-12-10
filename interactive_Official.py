import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import json
import geopandas as gpd
import folium


pd.set_option('display.max_columns', None)
crime_data = pd.read_csv('Full_crimedata_with_zip.csv', dtype={'ZIP': str})
crime_data["ZIP"] = crime_data["ZIP"].astype(str).str.zfill(5)
with open('zip_median.json', 'r') as file:
    zip_median = json.load(file)

#Top crime
crime_type_count =(
    crime_data.groupby(["ZIP","OFNS_DESC"]).size().reset_index(name="crime_type_count")
)

#Each's ZIP's top crime
top_crime_by_ZIP=(
    crime_type_count.sort_values(["ZIP","crime_type_count"],
    ascending=[True,False]).drop_duplicates(subset="ZIP").rename(columns={
        "OFNS_DESC": "Top_crime",
        "crime_type_count": "Top_crime_count"
    })
)
#We will make a toggle for crime type and their counts
pivot_crime_type_count=(
    crime_type_count.pivot(index="ZIP",columns="OFNS_DESC",values="crime_type_count").fillna(0)
)


zcta = gpd.read_file("MODZCTA.geojson")
crime_counts = crime_data.groupby('ZIP').size().reset_index(name='crime_count')
zcta = zcta.merge(crime_counts, left_on="modzcta", right_on="ZIP", how="left")
zcta["crime_count"] = zcta["crime_count"].fillna(0)
zcta["ZIP"] =zcta["modzcta"].astype(str).str.zfill(5)
del zcta[':created_at']
del zcta[':updated_at']

zcta['income'] = zcta['modzcta'].map(zip_median)
#Let's merge our top crime
zcta= zcta.merge(
    top_crime_by_ZIP[["ZIP","Top_crime", "Top_crime_count"]],
    on="ZIP",
    how="left"
)
#Merge the crime type counts
zcta= zcta.merge(
    pivot_crime_type_count,
    on="ZIP",
    how="left"
)
zcta_simplified= zcta.to_crs(epsg=3857)
zcta_simplified["geometry"] = zcta_simplified["geometry"].simplify(
    tolerance=50,
    preserve_topology=True
)

zcta_simplified= zcta_simplified.to_crs(epsg=4326)
    

# Center map on NYC
m = folium.Map(location=[40.7128, -74.0060], zoom_start=11)

# Add choropleth
folium.Choropleth(
    geo_data=zcta_simplified,
    data=zcta_simplified,
    columns=["ZIP", "crime_count"],
    key_on="feature.properties.ZIP",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Crime Count by ZIP",
    name="Total Crimes",
    overlay=True,
    control=True
).add_to(m)

types = [
    "PETIT LARCENY",
    "GRAND LARCENY",
    "ROBBERY",
    "OFFENSES AGAINST THE PERSON",    
    "OFFENSES INVOLVING FRAUD",
    "POSSESSION OF STOLEN PROPERTY",
    "SEX CRIMES",
    "RAPE",                           
    "KIDNAPPING & RELATED OFFENSES",  
    "PETIT LARCENY OF MOTOR VEHICLE", 
    "THEFT-FRAUD",                    
    "UNAUTHORIZED USE OF A VEHICLE",  
]
types_top_10= [
    "PETIT LARCENY",
    "HARRASSMENT 2",
    "ASSAULT 3 & RELATED OFFENSES",
    "GRAND LARCENY",
    "CRIMINAL MISCHIEF & RELATED OF",
    "FELONY ASSAULT",
    "VEHICLE AND TRAFFIC LAWS",
    "MISCELLANEOUS PENAL LAW",
    "DANGEROUS DRUGS",
    "OTHER OFFENSES RELATED TO THEFT"
]

print(zcta_simplified.columns)

for name in types_top_10:
    if name not in zcta_simplified.columns:
        print(f"Not found {name} in zcta")
        continue
    
    specific= zcta_simplified[["ZIP", name]].copy()

    #we will reuse our code
    folium.Choropleth(
    geo_data=zcta_simplified,
    data=specific,
    columns=["ZIP", name],
    key_on="feature.properties.ZIP",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name=f"{name} Count by ZIP",
    name=name,
    overlay=False,
    control=True
    ).add_to(m)
    
 
   
    
    #adding hover option
    
    
    
  
folium.GeoJson(
    zcta_simplified,
    style_function=lambda x: {"fillColor": "transparent", "color": "black", "weight": 0.5},
    highlight_function=lambda feature: {
        "color": "blue",       # outline color when hovered/clicked
        "weight": 3,           # thicker outline
        "fillOpacity": 0.6     # optional: darken fill
    },
    tooltip=folium.GeoJsonTooltip(fields=["ZIP", "crime_count", 'income', "Top_crime", "Top_crime_count"], aliases=["ZIP Code", "2025 Crimes", 'Median Income', "Most Common Crime","Frequency"], localize=False),
    # on_each_feature=lambda _, layer: layer.on('click', lambda e: None)
).add_to(m)


folium.LayerControl(collapsed=False).add_to(m)

m.save("crime_by_zip.html")





