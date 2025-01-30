import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from geopy.distance import geodesic

STORE_LAT, STORE_LON = 19.075887, 72.877911

def generate_circle(radius_km, center_lat, center_lon, num_points=100):
    circle_lats, circle_lons = [], []
    for angle in np.linspace(0, 360, num_points):
        new_point = geodesic(kilometers=radius_km).destination((center_lat, center_lon), angle)
        circle_lats.append(new_point.latitude)
        circle_lons.append(new_point.longitude)
    return circle_lats, circle_lons

circle_7_5_lat, circle_7_5_lon = generate_circle(15, STORE_LAT, STORE_LON)
circle_10_lat, circle_10_lon = generate_circle(20, STORE_LAT, STORE_LON)
#START1
FILE_PATH = "SmartRoute Optimizer.xlsx"
SHEET_NAME = "Shipments_Data"
df = pd.read_excel(FILE_PATH, sheet_name="Shipments_Data")
df2 = pd.read_excel(FILE_PATH, sheet_name="Vehicle_Information")
num3 = int(df2["Number"][0])
num4e = int(df2["Number"][1])
#END1
REQUIRED_COLUMNS = ["Shipment ID", "Latitude", "Longitude", "Delivery Timeslot"]
if not all(col in df.columns for col in REQUIRED_COLUMNS):
    raise ValueError("Missing required columns in the Excel file.")

def haversine_distance(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6372.0 
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

df["Dist"] = df.apply(lambda row: haversine_distance(STORE_LAT, STORE_LON, row["Latitude"], row["Longitude"]), axis=1)

df = df.sort_values(by="Dist")
#START2
count3 = 0
count4e = 0
count4 = 0
for index, row in df.iterrows():
    if row["Dist"] <= 15:
        if num3 > 0:
            count3 = count3 + 1
            if count3 == 5:
                df2["Number"][0] = df2["Number"][0] - 1
                count3 = 0
            
        elif num4e > 0:
            count4e = count4e + 1
            if count4e == 8:
                df2["Number"][1] = df2["Number"][1] - 1
                count4e = 0
        
        else:
            count4 = count4 + 1
            if count4 == 25:
                count4 = 0
    
    elif row["Dist"] <= 20 and row["Dist"] > 15:
        if num4e > 0:
            count4e = count4e + 1
            if count4e == 8:
                df2["Number"][1] = df2["Number"][1] - 1
                count4e = 0
        
        else:
            count4 = count4 + 1
            if count4 == 25:
                count4 = 0
            
    else:
        count4 = count4 + 1
        if count4 == 25:
            count4 = 0
#END2
OUTPUT_FILE = "shipment_distances.xlsx"
df.to_excel(OUTPUT_FILE, index=False)
print(f"Results saved to {OUTPUT_FILE}")

plt.figure(figsize=(8, 8))
plt.scatter(df["Longitude"], df["Latitude"], color='blue', label="Shipments", alpha=0.6)
plt.scatter(STORE_LON, STORE_LAT, color='red', marker="*", s=200, label="Store")
plt.plot(circle_7_5_lon, circle_7_5_lat, 'g-', label="15 km Radius")
plt.plot(circle_10_lon, circle_10_lat, 'orange', label="20 km Radius")

plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Shipments & Delivery Range")
plt.legend()
plt.grid()
plt.show()