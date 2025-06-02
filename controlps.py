import numpy as np
import matplotlib.pyplot as plt

# Parámetros físicos del sistema
h_max = 20.0
dt = 0.01
t_total = 100
t = np.arange(0, t_total, dt)

# Velocidades
v_llenado = 0.726
v_vaciado = 0.5262

# Setpoint dinámico personalizado
setpoint = np.zeros_like(t)
setpoint[t < 10] = 20
setpoint[(t >= 10) & (t < 20)] = 20
setpoint[(t >= 20) & (t < 30)] = 20
setpoint[(t >= 30) & (t < 40)] = 20
setpoint[(t >= 40) & (t < 60)] = 0
setpoint[(t >= 60) & (t < 70)] = 0
setpoint[t >= 70] = 0


# Simulador PID/PI con control instantáneo
def simulate_pid(Kp, Ki, Kd, use_derivative=True, label=""):
    h = np.zeros_like(t)
    e = np.zeros_like(t)
    control_signal = np.zeros_like(t)

    integral = 0.0
    prev_error = 0.0

    for i in range(1, len(t)):
        e[i] = setpoint[i] - h[i - 1]
        error = e[i]
        derivative = (error - prev_error) / dt
        prev_error = error

        # Control law
        u = Kp * error + Ki * integral
        if use_derivative:
            u += Kd * derivative

        # Saturate control
        u_sat = np.clip(u, -1, 1)
        control_signal[i] = u_sat

        # --- Anti-windup: solo acumula integral si no está saturado ---
        if u == u_sat:
            integral += error * dt

        # Dinámica del sistema
        if u_sat > 0:
         dh = v_llenado * u_sat * dt
        elif u_sat < 0:
            dh = v_vaciado * abs(u_sat) * (-dt)
        else:
            dh = 0

        h[i] = h[i - 1] + dh
        h[i] = np.clip(h[i], 0, h_max)

    return h, label


# Simulaciones
controllers = [
    (1.5, 0.2, 0.05, True, "PID Kp=1.50 Ki=0.20 Kd=0.05"),
]

results = []
for Kp, Ki, Kd, use_derivative, label in controllers:
    h, lbl = simulate_pid(Kp, Ki, Kd, use_derivative, label)
    results.append((t, h, lbl))

# Gráfica
plt.figure(figsize=(12, 6))
for t_vals, h_vals, label in results:
    plt.plot(t_vals, h_vals, label=label)

plt.plot(t, setpoint, "k--", label="Setpoint", linewidth=2)
plt.xlabel("Tiempo (s)")
plt.ylabel("Altura del agua (cm)")
plt.title(
    "Controladores PID/PI"
)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
