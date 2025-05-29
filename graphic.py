import matplotlib.pyplot as plt
import numpy as np

# Definir las funciones
def funcion_1(x):
    return 0.6225 * x

def funcion_2(x):
    return -0.7705 * x + 44.771  # Ajustada para que pase por (32.129, 20)

# Calcular el valor de x donde y = 20 para la primera función
x_interseccion = 32.129  # Resolviendo y = 20
print(f"La primera función alcanza y=20 en x={x_interseccion:.2f}")

# Rango de valores para la primera función
x1 = np.linspace(0, x_interseccion, 100)  # Desde x=0 hasta x_interseccion
y1 = funcion_1(x1)

# Rango de valores para la segunda función (inicia en x_interseccion)
x2 = np.linspace(x_interseccion, 58, 100)  # Desde x_interseccion hasta x=50
y2 = funcion_2(x2)

# Graficar las funciones
plt.figure(figsize=(10, 6))
plt.plot(x1, y1, label="y = 0.6225x", color="blue")
plt.plot(x2, y2, label="y = -0.7705x + 43.115 (desplazada)", color="red")
plt.title("Gráfica de las funciones")
plt.xlabel("x")
plt.ylabel("y")
plt.axhline(0, color="black", linewidth=0.8, linestyle="--")  # Línea horizontal en y=0
plt.axvline(0, color="black", linewidth=0.8, linestyle="--")  # Línea vertical en x=0
plt.grid(True)
plt.legend()
plt.show()