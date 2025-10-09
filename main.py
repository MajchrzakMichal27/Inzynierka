import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_excel("../Inzynierka/Dziennik2024.xlsx")

df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("ł", "l").str.replace("ó", "o")

#print("Dostępne kolumny:", df.columns.tolist())

wind_map = {
    "N": 0, "NNE": 22.5, "NE": 45, "ENE": 67.5,
    "E": 90, "ESE": 112.5, "SE": 135, "SSE": 157.5,
    "S": 180, "SSW": 202.5, "SW": 225, "WSW": 247.5,
    "W": 270, "WNW": 292.5, "NW": 315, "NNW": 337.5
}


def classify_course(wind_dir, boat_course):
    if pd.isna(wind_dir) or pd.isna(boat_course):
        return None, None

    wind_dir = str(wind_dir).strip().upper()
    wind_deg = wind_map.get(wind_dir, None)
    if wind_deg is None:
        return None, None

    boat_course = float(boat_course)

    diff = (boat_course - wind_deg) % 360
    angle = min(diff, 360 - diff)

    hals = "lewy" if diff <= 180 else "prawy"

    if angle <= 35:
        course_type = "ostry bajdewind"
    elif angle <= 60:
        course_type = "bajdewind"
    elif angle <= 80:
        course_type = "pelny bajdewind"
    elif angle <= 100:
        course_type = "polwiatr"
    elif angle <= 120:
        course_type = "ostry baksztag"
    elif angle <= 150:
        course_type = "baksztag"
    elif angle <= 170:
        course_type = "pelny baksztag"
    else:
        course_type = "fordewind"

    return course_type, hals


def show_speed():

    return None

df[["kurs_typ", "hals"]] = df.apply(
    lambda row: pd.Series(classify_course(row["wiatr"], row["cog"])),
    axis=1
)

df["kat_roznicy"] = df.apply(
    lambda row: abs((float(row["cog"]) - wind_map.get(str(row["wiatr"]).strip().upper(), 0)) % 360)
    if pd.notna(row["wiatr"]) and pd.notna(row["cog"]) else None,
    axis=1
)

out_path = "../Inzynierka/Dziennik2024_wynik.xlsx"
df.to_excel(out_path, index=False)

