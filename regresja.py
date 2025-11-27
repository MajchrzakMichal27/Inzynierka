import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Wczytanie danych
df = pd.read_excel("Dziennik2024_wynik.xlsx")

print("=== REGRESJA WIELOMIANOWA Z 4 ZMIENNYMI ===")

# Mapowanie żagli na powierzchnie
powierzchnie_fok = {'F30': 30, 'F48': 48, 'F60': 60, 'G87': 87, 'G100': 100, 'S': 200, '-': 0}
powierzchnie_grot = {'G': 70, 'G1': 56, 'G2': 42, 'G3': 28, '-': 0}

# Dodajemy powierzchnie do danych
df['powierzchnia_fok'] = df['fok'].map(powierzchnie_fok).fillna(0)
df['powierzchnia_grot'] = df['grot'].map(powierzchnie_grot).fillna(42)

# Przygotowanie danych - 4 zmienne
X = df[["sila_wiatru", "kat_roznicy", "powierzchnia_fok", "powierzchnia_grot"]].values
y = df["sog"].values

print(f"Dane: {X.shape[0]} obserwacji, {X.shape[1]} zmiennych")

# Model regresji wielomianowej
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)

model = LinearRegression()
model.fit(X_poly, y)
y_pred = model.predict(X_poly)

# Metryki
mse = mean_squared_error(y, y_pred)
r2 = r2_score(y, y_pred)

print(f"\nWYNIK MODELU:")
print(f"R²: {r2:.3f}")
print(f"MSE: {mse:.3f}")

# Najważniejsze współczynniki
feature_names = poly.get_feature_names_out(['wiatr', 'kat', 'fok', 'grot'])
print(f"\nNAJWAŻNIEJSZE WSPÓŁCZYNNIKI:")
for name, coef in zip(feature_names, model.coef_):
    if abs(coef) > 0.01:
        print(f"  {name}: {coef:.4f}")


# Prosta funkcja przewidywania
def przewidz(sila_wiatru, kat_roznicy, fok, grot):
    pow_fok = powierzchnie_fok.get(fok, 0)
    pow_grot = powierzchnie_grot.get(grot, 42)

    X_test = np.array([[sila_wiatru, kat_roznicy, pow_fok, pow_grot]])
    X_test_poly = poly.transform(X_test)

    return model.predict(X_test_poly)[0]


# Test
print(f"\nPRZYKŁADY PRZEWIDYWAŃ:")

przyklady = [
    (8, 50, 'G87', 'G1'),
    (4, 170, 'F48', 'G3'),
    (4, 170, 'S', 'G2'),
    (4, 170, 'S', 'G1'),
    (7, 45, 'G87', 'G1'),
    (7, 45, 'F48', 'G1'),
    (7, 45, 'F30', 'G3')
]

for i, (wiatr, kat, fok, grot) in enumerate(przyklady, 1):
    pred = przewidz(wiatr, kat, fok, grot)
    print(f"{i}. sila_wiatru: {wiatr}, kat_roznicy: {kat}, fok: {fok}, grot: {grot} -> {pred:.3f}")