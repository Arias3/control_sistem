import numpy as np
import matplotlib.pyplot as plt

# Parámetros físicos
radio_cm = 4.5
A_cm2 = np.pi * radio_cm**2  # Área transversal del recipiente (cm²)

# Caudales
Q_llenado = 39.43  # Caudal de llenado real (cm³/s)
Q_vaciado = 49.35  # Caudal de vaciado real (cm³/s)

# Nivel máximo deseado
h_max = 15.5  # cm
t_llenado = 30  # segundos

# Tiempo total de simulación
t_total = 60
dt = 0.1
T = np.arange(0, t_total + dt, dt)

# Inicializar vector de nivel
nivel = np.zeros_like(T)

# Simulación paso a paso
for i in range(1, len(T)):
    t = T[i]

    if t <= 30:
        # Etapa de llenado
        dV = Q_llenado * dt
    else:
        # Etapa de vaciado
        dV = -Q_vaciado * dt

    # Calcular variación de altura
    dh = dV / A_cm2
    nivel[i] = nivel[i-1] + dh

    # Asegurarse de que el nivel no supere el máximo de 15.5 cm durante el llenado
    if t <= 30 and nivel[i] > h_max:
        nivel[i] = h_max

    # Evitar que el nivel sea negativo durante el vaciado
    if nivel[i] < 0:
        nivel[i] = 0

# Graficar resultados
plt.figure(figsize=(10, 5))
plt.plot(T, nivel, 'b', linewidth=2)
plt.axvline(30, color='gray', linestyle='--', label='Inicio vaciado')

# Personalizar los ejes
plt.xticks(np.arange(0, t_total + 1, 5))  # Más divisiones en el eje x (cada 5 segundos)
plt.yticks(np.arange(0, h_max + 1, 1))    # Más divisiones en el eje y (cada 1 cm)

# Aumentar la precisión de las etiquetas
plt.tick_params(axis='both', which='major', labelsize=10)
plt.gca().yaxis.set_major_formatter(plt.FormatStrFormatter('%.2f'))  # Mostrar 2 decimales en el eje y
plt.gca().xaxis.set_major_formatter(plt.FormatStrFormatter('%.2f'))  # Mostrar 2 decimales en el eje x

plt.title('Simulación de Llenado y Vaciado del Recipiente')
plt.xlabel('Tiempo (s)')
plt.ylabel('Nivel de agua (cm)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
