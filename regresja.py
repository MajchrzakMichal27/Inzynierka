import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
import warnings

# Wyłączenie komunikatów o nazwach cech
warnings.filterwarnings("ignore", category=UserWarning)

# ==========================================
# 1. KONFIGURACJA I MAPOWANIA
# ==========================================

powierzchnie_fok = {
    'F30': 30, 'F48': 48, 'F60': 60, 'G87': 87,
    'G87 ': 87, 'G100': 100, 'S': 200, '-': 0
}
powierzchnie_grot = {
    'G': 70, 'G1': 56, 'G2': 42, 'G3': 28, '-': 0
}

WIND_MAP = {
    "N": 0, "NNE": 22.5, "NE": 45, "ENE": 67.5,
    "E": 90, "ESE": 112.5, "SE": 135, "SSE": 157.5,
    "S": 180, "SSW": 202.5, "SW": 225, "WSW": 247.5,
    "W": 270, "WNW": 292.5, "NW": 315, "NNW": 337.5
}

# ==========================================
# 2. PRZYGOTOWANIE I TRENOWANIE MODELI
# ==========================================

# Wczytanie danych z Twojego pliku
df = pd.read_excel("Dziennik2024_wynik.xlsx")
df['powierzchnia_fok'] = df['fok'].map(powierzchnie_fok).fillna(0)
df['powierzchnia_grot'] = df['grot'].map(powierzchnie_grot).fillna(42)

# Cechy wejściowe (X) i cel (y)
X = df[["sila_wiatru", "kat_roznicy", "powierzchnia_fok", "powierzchnia_grot"]].values
y = df["sog"].values

# MODEL A: REGRESJA WIELOMIANOWA
poly_transformer = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly_transformer.fit_transform(X)
model_poly = LinearRegression()
model_poly.fit(X_poly, y)

# MODEL B: LASY LOSOWE (RANDOM FOREST)
model_rf = RandomForestRegressor(n_estimators=100, random_state=42)
model_rf.fit(X, y)


# ==========================================
# 3. FUNKCJE POMOCNICZE
# ==========================================

def parsuj_kierunek(wejscie):
    wejscie = str(wejscie).upper().strip()
    if wejscie in WIND_MAP:
        return WIND_MAP[wejscie]
    try:
        return float(wejscie) % 360
    except ValueError:
        return None


def oblicz_kat_natarcia(kurs, wiatr):
    roznica = abs(kurs - wiatr) % 360
    if roznica > 180:
        roznica = 360 - roznica
    return roznica


def przewidz_sog(v_wiatr, kat, fok, grot, typ_modelu):
    p_fok = powierzchnie_fok.get(fok, 0)
    p_grot = powierzchnie_grot.get(grot, 42)
    X_input = np.array([[v_wiatr, kat, p_fok, p_grot]])

    if typ_modelu == 'poly':
        # Przewidywanie regresją wielomianową
        X_poly_input = poly_transformer.transform(X_input)
        pred = model_poly.predict(X_poly_input)[0]
    else:
        # Przewidywanie lasem losowym
        pred = model_rf.predict(X_input)[0]

    # Kara dla spinakera (S) przy kursach ostrych
    if fok == 'S' and kat < 160:
        pred *= 0.5

    return max(0, pred)


def pobierz_ranking(v_wiatr, kat, typ_modelu):
    # Pobieramy unikalne pary żagli z Twoich danych historycznych
    kombinacje = df[['fok', 'grot']].drop_duplicates()
    kombinacje = kombinacje[(kombinacje['fok'] != '-') & (kombinacje['grot'] != '-')]

    lista_wynikowa = []
    for _, row in kombinacje.iterrows():
        f, g = row['fok'], row['grot']
        sog = przewidz_sog(v_wiatr, kat, f, g, typ_modelu)
        lista_wynikowa.append({'zestaw': f"{f} + {g}", 'sog': sog})

    # Sortowanie od najszybszego
    return sorted(lista_wynikowa, key=lambda x: x['sog'], reverse=True)


# ==========================================
# 4. INTERFEJS I WYŚWIETLANIE
# ==========================================

print("=== SYSTEM REKOMENDACJI: PORÓWNANIE MODELI ===")
print(f"R² Regresja Wielomianowa: {r2_score(y, model_poly.predict(X_poly)):.4f}")
print(f"R² Las Losowy (RF):      {r2_score(y, model_rf.predict(X)):.4f}")

while True:
    try:
        print("\n" + "=" * 70)
        sw_in = input("Siła wiatru [B]: ")
        if sw_in.lower() == 'q': break

        kw_in = input("Kierunek wiatru (np. NW, 315): ")
        kj_in = input("Kurs jachtu (np. S, 180): ")

        kw = parsuj_kierunek(kw_in)
        kj = parsuj_kierunek(kj_in)

        if kw is None or kj is None:
            print("❌ Błąd formatu kierunku!")
            continue

        v_wiatr = float(sw_in)
        kat_natarcia = oblicz_kat_natarcia(kj, kw)

        print(f"\n[INFO] Obliczony kąt wiatru: {kat_natarcia:.1f}°")

        # Pobieramy dwa niezależne rankingi
        ranking_poly = pobierz_ranking(v_wiatr, kat_natarcia, 'poly')
        ranking_rf = pobierz_ranking(v_wiatr, kat_natarcia, 'rf')

        # Wyświetlanie w czytelnej tabeli
        print("\n" + f"{'POZ.':<4} | {'REGRESJA WIELOMIANOWA':<28} | {'LAS LOSOWY (RF)':<28}")
        print("-" * 70)

        for i in range(10):  # Pokazujemy TOP 5 dla obu metod
            p = ranking_poly[i]
            r = ranking_rf[i]

            txt_p = f"{p['zestaw']:15s} ({p['sog']:.2f} w.)"
            txt_r = f"{r['zestaw']:15s} ({r['sog']:.2f} w.)"

            print(f"{i + 1:<4} | {txt_p:<28} | {txt_r:<28}")

    except ValueError:
        print("❌ Wprowadź poprawną liczbę dla siły wiatru!")
    except Exception as e:
        print(f"❌ Błąd: {e}")
