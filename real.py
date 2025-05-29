import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Leer la primera columna (Nivel) de data.csv
niveles = []
with open("data.csv", mode="r") as file:
    reader = csv.reader(file)
    next(reader)  # Saltar encabezado
    for row in reader:
        if row and row[0]:
            valor = float(row[0])
            if valor > 0.5:
                niveles.append(valor)

niveles = np.array(niveles)
tiempo = np.arange(len(niveles)) * 0.1  # Cada dato es cada 100 ms

# Guardar en un archivo Excel
df = pd.DataFrame({'Tiempo (s)': tiempo, 'Nivel': niveles})
df.to_excel('nivel_vs_tiempo.xlsx', index=False)

# Graficar con zoom interactivo
plt.figure(figsize=(10, 5))
plt.plot(tiempo, niveles, label="Nivel (>0.1)")
plt.xlabel("Tiempo (s)")
plt.ylabel("Nivel")
plt.title("Nivel vs Tiempo (filtrado)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()