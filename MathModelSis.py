import numpy as np
import matplotlib.pyplot as plt
import control as ctrl

# Parámetros del recipiente
diametro_cm = 9
radio_cm = diametro_cm / 2
A_real = np.pi * radio_cm**2  # Área transversal (cm²)

# PWM máximo
PWM_max = 255

# Cálculo del caudal real de llenado (basado en datos medidos)
nivel_cm = 15.5
tiempo_seg = 25
volumen = np.pi * radio_cm**2 * nivel_cm  # Volumen total en cm³
Q_llenado_real = volumen / tiempo_seg     # Caudal en cm³/s
K_llenado_real = Q_llenado_real / PWM_max # Coeficiente K real (cm³/s por unidad PWM)

# Modelo del sistema (lleno)
K = K_llenado_real
num = [K / A_real]
den = [1, 0]
G = ctrl.TransferFunction(num, den)

# PID
Kp = 50
Ki = 0.5
Kd = 2
C = ctrl.TransferFunction([Kd, Kp, Ki], [1, 0])
G_cl = ctrl.feedback(C * G)

# Simulación
T = np.linspace(0, 60, 1000)
U = np.piecewise(T, [T < 20, (T >= 20) & (T < 42), T >= 42], [0, 15, 0])
T, Y = ctrl.forced_response(G_cl, T, U)

# Graficar
plt.figure(figsize=(10, 6))
plt.plot(T, U, 'r--', label='Referencia (cm)')
plt.plot(T, Y, 'b', label='Respuesta del sistema (cm)')
plt.xlabel('Tiempo (s)')
plt.ylabel('Nivel del agua (cm)')
plt.title('Respuesta del Sistema de Nivel con PID (Llenado)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
