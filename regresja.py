import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score

# Wczytanie danych
df = pd.read_excel("Dziennik2024_wynik.xlsx")

print("=== SYSTEM REKOMENDACJI ŻAGLI ===")

# Mapowanie żagli na powierzchnie
powierzchnie_fok = {'F30': 30, 'F48': 48, 'F60': 60, 'G87': 87, 'G87 ': 87, 'G100': 100, 'S': 200, '-': 0}
powierzchnie_grot = {'G': 70, 'G1': 56, 'G2': 42, 'G3': 28, '-': 0}

# Dodajemy powierzchnie do danych
df['powierzchnia_fok'] = df['fok'].map(powierzchnie_fok).fillna(0)
df['powierzchnia_grot'] = df['grot'].map(powierzchnie_grot).fillna(42)

# Oblicz funkcję dla każdego wiersza (dla treningu modelu)
kat = df["kat_roznicy"].values
df['funkcja'] = (4 / 360) * (3 ** (kat / 15)) + (37 / 40)

# Przygotowanie danych - TERAZ z funkcją jako 5. zmienna
X = df[["sila_wiatru", "kat_roznicy", "powierzchnia_fok", "powierzchnia_grot", "funkcja"]].values
y = df["sog"].values

print(f"Dane: {X.shape[0]} obserwacji, {X.shape[1]} zmiennych")

# Model regresji wielomianowej
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)

model = LinearRegression()
model.fit(X_poly, y)

print(f"Liczba cech po transformacji wielomianowej: {X_poly.shape[1]}")


def oblicz_funkcje(kat_roznicy):
    """Oblicza wartość funkcji dla podanego kąta"""
    return (4 / 360) * (3 ** (kat_roznicy / 15)) + (37 / 40)


def przewidz(sila_wiatru, kat_roznicy, fok, grot):
    pow_fok = powierzchnie_fok.get(fok, 0)
    pow_grot = powierzchnie_grot.get(grot, 42)

    # Oblicz funkcję dla konkretnego kąta
    funkcja_wartosc = oblicz_funkcje(kat_roznicy)

    # Tworzymy wektor z 5 zmiennymi
    X_test = np.array([[sila_wiatru, kat_roznicy, pow_fok, pow_grot, funkcja_wartosc]])
    X_test_poly = poly.transform(X_test)

    predkosc = model.predict(X_test_poly)[0]

    if kat_roznicy < 120 and fok == 'S':
        predkosc = 1

    return predkosc


# Funkcja do znajdowania unikalnych kombinacji żagli z danych
def znajdz_unikalne_kombinacje_zagli(df):
    kombinacje = df[['fok', 'grot']].drop_duplicates()
    kombinacje = kombinacje[(kombinacje['fok'] != '-') & (kombinacje['grot'] != '-')]
    return kombinacje.to_dict('records')


# Główna funkcja rekomendacji
def rekomenduj_zagle(sila_wiatru, kat_roznicy, pokaz_wszystkie=False, top_n=5):
    print(f"\n{'=' * 60}")
    print(f"REKOMENDACJE ŻAGLI DLA:")
    print(f"Siła wiatru: {sila_wiatru} ")
    print(f"Kąt względem wiatru: {kat_roznicy}°")
    print(f"{'=' * 60}")

    # Oblicz funkcję dla tego konkretnego kąta
    funkcja_wartosc = oblicz_funkcje(kat_roznicy)
    print(f"Wartość funkcji dla kąta {kat_roznicy}°: {funkcja_wartosc:.4f}")

    # Znajdź wszystkie unikalne kombinacje żagli z danych historycznych
    kombinacje = znajdz_unikalne_kombinacje_zagli(df)

    results = []

    for komb in kombinacje:
        fok = komb['fok']
        grot = komb['grot']

        # Przewidywana prędkość
        predkosc = przewidz(sila_wiatru, kat_roznicy, fok, grot)

        # Dodajemy informacje o powierzchni
        pow_fok = powierzchnie_fok[fok]
        pow_grot = powierzchnie_grot[grot]
        calkowita_pow = pow_fok + pow_grot

        results.append({
            'fok': fok,
            'grot': grot,
            'predkosc': predkosc,
            'pow_fok': pow_fok,
            'pow_grot': pow_grot,
            'calkowita_pow': calkowita_pow
        })

    # Sortuj od najszybszej do najwolniejszej
    results.sort(key=lambda x: x['predkosc'], reverse=True)

    if pokaz_wszystkie:
        print(f"\nWSZYSTKIE KOMBINACJE ({len(results)}):")
        for i, res in enumerate(results, 1):
            print(f"{i:2d}. {res['fok']:4s} + {res['grot']:3s} -> {res['predkosc']:.3f}  "
                  f"(pow: {res['calkowita_pow']:3d}m²)")
    else:
        print(f"\nTOP {top_n} NAJLEPSZYCH KOMBINACJI:")
        for i, res in enumerate(results[:top_n], 1):
            print(f"{i}. {res['fok']} + {res['grot']} -> {res['predkosc']:.3f}  "
                  f"(powierzchnia: {res['calkowita_pow']}m²)")

            # Dodajemy krótką analizę dla top kombinacji
            if i == 1:
                print(f"   🏆 NAJLEPSZY WYBÓR!")
            elif res['predkosc'] > results[0]['predkosc'] * 0.95:
                print(f"   💡 BARDZO DOBRY WYBÓR (prawie tak dobry jak najlepszy)")

    # Dodatkowa analiza
    najlepszy = results[0]
    print(f"\nNajszybsza kombinacja: {najlepszy['fok']} + {najlepszy['grot']} -> {najlepszy['predkosc']:.3f} ")

    return results


# Test systemu rekomendacji
print("\n" + "=" * 80)
print("TEST SYSTEMU REKOMENDACJI ŻAGLI")
print("=" * 80)

# Przykładowe scenariusze
scenariusze = [
    (8, 50),
]

for wiatr, kat in scenariusze:
    rekomenduj_zagle(wiatr, kat, pokaz_wszystkie=False, top_n=3)
    print("\n" + "-" * 60)

# Możliwość ręcznego testowania
print("\n🎯 TESTUJ SWOJE WARUNKI:")
while True:
    try:
        print("\nPodaj warunki (lub 'q' aby zakończyć):")
        wiatr = input("Siła wiatru: ")
        if wiatr.lower() == 'q':
            break
        kat = input("Kąt względem wiatru [°]: ")
        if kat.lower() == 'q':
            break

        wiatr = float(wiatr)
        kat = float(kat)

        pokaz_wszystkie = input("Pokazać wszystkie kombinacje? (t/n): ").lower() == 't'

        if pokaz_wszystkie:
            rekomenduj_zagle(wiatr, kat, pokaz_wszystkie=True)
        else:
            top_n = int(input("Ile top kombinacji pokazać? "))
            rekomenduj_zagle(wiatr, kat, pokaz_wszystkie=False, top_n=top_n)
    except ValueError:
        print("Błąd! Wprowadź poprawne wartości.")
    except KeyboardInterrupt:
        print("\nZakończono program.")
        break