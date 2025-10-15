import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from skimage.color.rgb_colors import lightblue, blue

#oryginalny plik excel
df = pd.read_excel("../Inzynierka/Dziennik2024.xlsx")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("ł", "l").str.replace("ó", "o")

#print("Dostępne kolumny:", df.columns.tolist())

wind_map = {
    "N": 0, "NNE": 22.5, "NE": 45, "ENE": 67.5,
    "E": 90, "ESE": 112.5, "SE": 135, "SSE": 157.5,
    "S": 180, "SSW": 202.5, "SW": 225, "WSW": 247.5,
    "W": 270, "WNW": 292.5, "NW": 315, "NNW": 337.5
}

#Klasyfikacja kierunków
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

#biegunowy wykres prędkości
def show_speed(df,
               speed_col='sog',
               angle_col='kat_roznicy',
               bins=18,
               figsize=(8,8),
               save_path=None,
               rmax=None):
    """
    Rysuje wykres biegunowy prędkości względem kąta do wiatru.
    - df: pandas.DataFrame (Wczytaj dane z pliku już z kątem róznicy)
    - speed_col: nazwa kolumny z prędkością (domyślnie 'sog - sail over ground')
    - angle_col: nazwa kolumny z kątem różnicy ('kat_roznicy')
    - group_col: (opcjonalnie) nazwa kolumny z grupami (np. 'nastawa'), żeby porównać serie
    - bins: liczba przedziałów do liczenia średniej (na 0..180°)
    - figsize: rozmiar wykresu
    - save_path: -> scieżka zapsiu
    - rmax: max osi radialnej (jeśli None -> autodopasowanie)
    """

    # Sprawdzenie kolumn
    for col in [speed_col, angle_col]:
        if col not in df.columns:
            raise ValueError(f"Brakuje kolumny: {col}")

    # Kopia i konwersja typów
    df2 = df.copy()
    df2[speed_col] = pd.to_numeric(df2[speed_col], errors='coerce')
    df2 = df2.dropna(subset=[speed_col, angle_col])

    # Normalizacja kąta 0–180°
    df2['angle360'] = df2[angle_col] % 360
    df2['angle'] = df2['angle360'].where(df2['angle360'] <= 180, 360 - df2['angle360'])
    df2['angle_rad'] = np.deg2rad(df2['angle'])

    # Tworzenie figury polarnej
    fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)

    # Zakres radialny
    if rmax is None:
        rmax = df2[speed_col].max() * 1.1
    ax.set_ylim(0, rmax)

    # Etykiety kątowe
    thetas = [0, 30, 45, 60, 90, 120, 135, 150, 180]
    ax.set_thetagrids(thetas, labels=[f"{t}°" for t in thetas])

    # Punkty pomiarowe (symetrycznie)
    ax.scatter(df2['angle_rad'], df2[speed_col], s=18, alpha=0.6, color='skyblue', label='pomiary')
    ax.scatter(-df2['angle_rad'], df2[speed_col], s=18, alpha=0.6, color='skyblue')

    #średnie prędkości w przedziałach kątowych
    bin_edges = np.linspace(0, 180, bins + 1)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    inds = np.digitize(df2['angle'].values, bin_edges) - 1

    mean_speeds = []
    for j in range(len(bin_centers)):
        vals = df2[speed_col].values[inds == j]
        mean_speeds.append(np.nan if len(vals) == 0 else np.nanmean(vals))
    mean_speeds = np.array(mean_speeds)
    valid = ~np.isnan(mean_speeds)

    # Krzywa średniej
    if valid.any():
        x = np.deg2rad(bin_centers[valid])
        y = mean_speeds[valid]
        ax.plot(x, y, linewidth=2.5, color='navy', label='średnia')
        ax.plot(-x, y, linewidth=2.5, color='navy')

    # Opisy i legenda
    ax.set_title("Wykres biegunowy prędkości jachtu względem kąta do wiatru", va='bottom')
    ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.05))

    #zapis wykresu
    if save_path:
        fig.savefig(save_path, bbox_inches='tight', dpi=150)

    plt.show()
    return fig, ax

def group_by(df):
    help = df.groupby(["kurs_typ", "sila_wiatru"])["sog"].idxmax()
    df_grouped = df.loc[help,["kurs_typ", "sila_wiatru", "sog", "grot", "fok"]]
    return df_grouped

#zapis danego kursu do pliku
df[["kurs_typ", "hals"]] = df.apply(
    lambda row: pd.Series(classify_course(row["wiatr"], row["cog"])),
    axis=1
)

#zapis kata miedzy kursem a wiatrm do pliku
df["kat_roznicy"] = df.apply(
    lambda row: abs((float(row["cog"]) - wind_map.get(str(row["wiatr"]).strip().upper(), 0)) % 360)
    if pd.notna(row["wiatr"]) and pd.notna(row["cog"]) else None,
    axis=1
)

#zapis excela z dodanymi danymi
out_path = "../Inzynierka/Dziennik2024_wynik.xlsx"
df.to_excel(out_path, index=False)

#odczyt pliku z dodanymi danymi i rysowanie wykresu
df_wynik = pd.read_excel(out_path)
#show_speed(df, save_path="../Inzynierka/wykres_prędkości.png",rmax=12,figsize=(10,8))

test = group_by(df_wynik)
print(test)






