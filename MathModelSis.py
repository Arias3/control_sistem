import numpy as np
import matplotlib.pyplot as plt
import control as ctrl

# Parámetros del sistema corregidos
A = np.pi * 10**2  # Área transversal del recipiente (cm^2)
K = 3.92           # Coeficiente de la bomba (cm^3/s por unidad de PWM)

# Función de transferencia del sistema
num = [K / A]
den = [1, 0]  # Sistema de primer orden: dh/dt = (K/A) * PWM
G = ctrl.TransferFunction(num, den)

Kp = 100
Ki = 1
Kd = 5

# Controlador PID
C = ctrl.TransferFunction([Kd, Kp, Ki], [1, 0])

# Sistema en lazo cerrado
G_cl = ctrl.feedback(C * G)

# Tiempo de simulación
T = np.linspace(0, 40, 1000)

# Señal de entrada (0 los primeros 20s, luego 15 por 30s)
U = np.piecewise(T, [T < 20, T >= 20], [0, 15])


# Simulación de la respuesta del sistema
T, Y = ctrl.forced_response(G_cl, T, U)

# Graficar resultados
plt.figure(figsize=(10, 5))
plt.plot(T, U, 'r--', label='Entrada (cm)')
plt.plot(T, Y, 'b', label='Salida del sistema (cm)')
plt.xlabel('Tiempo (s)')
plt.ylabel('Nivel del agua (cm)')
plt.title('Respuesta del Sistema de Nivel de Agua con Control PID')
plt.legend()
plt.grid()
plt.show()
