import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Wczytanie danych
df = pd.read_excel("Dziennik2024_wynik.xlsx")

# Wybieramy potrzebne kolumny - teraz 3 czynniki
data = df[["sog", "sila_wiatru", "kat_roznicy"]]

# Przygotowanie danych - X ma teraz 2 kolumny
X = df[["sila_wiatru", "kat_roznicy"]].values
y = df["sog"].values

print("Podgląd danych:")
print(data.head())
print(f"\nLiczba obserwacji: {len(data)}")

# Model regresji liniowej (wielowymiarowej)
model_lin = LinearRegression()
model_lin.fit(X, y)
y_pred_lin = model_lin.predict(X)

# Model regresji wielomianowej (stopień 2) z interakcjami
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)
model_poly = LinearRegression()
model_poly.fit(X_poly, y)
y_pred_poly = model_poly.predict(X_poly)

# Obliczenia metryk
mse_lin = mean_squared_error(y, y_pred_lin)
r2_lin = r2_score(y, y_pred_lin)

mse_poly = mean_squared_error(y, y_pred_poly)
r2_poly = r2_score(y, y_pred_poly)

print("\n=== WYNIKI ===")
print("=== MODEL LINIOWY ===")
print(f"MSE: {mse_lin:.3f}")
print(f"R²: {r2_lin:.3f}")
print(f"Współczynniki: sila_wiatru={model_lin.coef_[0]:.3f}, kat_roznicy={model_lin.coef_[1]:.3f}")
print(f"Intercept: {model_lin.intercept_:.3f}")

print("\n=== MODEL WIELOMIANOWY (stopień 2) ===")
print(f"MSE: {mse_poly:.3f}")
print(f"R²: {r2_poly:.3f}")

# Wyświetlenie nazw cech w modelu wielomianowym
feature_names = poly.get_feature_names_out(['sila_wiatru', 'kat_roznicy'])
print(f"\nCechy w modelu wielomianowym: {feature_names}")
print(f"Współczynniki: {model_poly.coef_}")

# Wizualizacja 3D
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(12, 5))

# Wykres 1: Dane rzeczywiste
ax1 = fig.add_subplot(121, projection='3d')
scatter1 = ax1.scatter(X[:, 0], X[:, 1], y, c=y, cmap='viridis', alpha=0.6)
ax1.set_xlabel('Siła wiatru [B]')
ax1.set_ylabel('Kąt różnicy [°]')
ax1.set_zlabel('Prędkość (SOG) [węzły]')
ax1.set_title('Dane rzeczywiste')
plt.colorbar(scatter1, ax=ax1, label='SOG')

# Wykres 2: Predykcje modelu wielomianowego
ax2 = fig.add_subplot(122, projection='3d')
scatter2 = ax2.scatter(X[:, 0], X[:, 1], y_pred_poly, c=y_pred_poly, cmap='viridis', alpha=0.6)
ax2.set_xlabel('Siła wiatru [B]')
ax2.set_ylabel('Kąt różnicy [°]')
ax2.set_zlabel('Prędkość (SOG) [węzły]')
ax2.set_title('Predykcje modelu wielomianowego')
plt.colorbar(scatter2, ax=ax2, label='SOG')

plt.tight_layout()
plt.show()

# Dodatkowa wizualizacja: zależność SOG od siły wiatru z uwzględnieniem kąta
plt.figure(figsize=(10, 6))
scatter = plt.scatter(X[:, 0], y, c=X[:, 1], cmap='viridis', alpha=0.7)
plt.colorbar(scatter, label='Kąt różnicy [°]')
plt.xlabel('Siła wiatru [B]')
plt.ylabel('Prędkość jachtu (SOG) [węzły]')
plt.title('Zależność prędkości jachtu od siły wiatru i kąta różnicy')
plt.grid(True, alpha=0.3)
plt.show()