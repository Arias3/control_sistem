import numpy as np
import matplotlib.pyplot as plt
import control as ctrl

# Parámetros físicos del sistema
diametro = 10  # cm
A = np.pi * (diametro/2)**2  # Área del tanque (cm²)
v_max_llenado = 0.726   # cm/s (velocidad máxima de llenado)
v_max_vaciado = 0.5262  # cm/s (velocidad máxima de vaciado)

# Tiempo para llenar de 0 a 20 cm a velocidad máxima
t_llenado_max = 20 / v_max_llenado  # ~27.5 segundos

print(f"Área del tanque: {A:.2f} cm²")
print(f"Velocidad máxima llenado: {v_max_llenado} cm/s")
print(f"Velocidad máxima vaciado: {v_max_vaciado} cm/s")
print(f"Tiempo para llenar 0-20cm a velocidad máxima: {t_llenado_max:.1f} s")

# Modelo del sistema: integrador con saturación
# dh/dt = (u * v_max) / A, donde u es la señal de control normalizada [-1, 1]
# En Laplace: H(s) = (v_max/A) * (1/s)

# Funciones de transferencia AJUSTADAS
H_llenado = ctrl.TransferFunction([v_max_llenado], [A, 0])  # (0.726/78.54)/s = 0.00924/s
H_vaciado = ctrl.TransferFunction([v_max_vaciado], [A, 0])  # (0.5262/78.54)/s = 0.0067/s

# Configuración de la simulación
t_total = 300  # Tiempo total de simulación (aumentado para ver mejor los comportamientos)
t_sim = np.linspace(0, t_total, 6000)
setpoint = np.zeros_like(t_sim)

# Setpoint escalonado con escalones más largos para ver el comportamiento completo
escalones_subida = [0, 4, 8, 12, 16, 20]  # Niveles objetivo
escalones_bajada = [20, 16, 12, 8, 4, 0]  # Niveles de descenso
t_escalon = 40  # Duración de cada escalón (aumentado a 40s)

for i, t in enumerate(t_sim):
    if t < len(escalones_subida) * t_escalon:
        # Fase de subida
        escalon_idx = int(t // t_escalon)
        if escalon_idx < len(escalones_subida):
            setpoint[i] = escalones_subida[escalon_idx]
        else:
            setpoint[i] = escalones_subida[-1]
    else:
        # Fase de bajada
        t_bajada = t - len(escalones_subida) * t_escalon
        escalon_idx = int(t_bajada // t_escalon)
        if escalon_idx < len(escalones_bajada):
            setpoint[i] = escalones_bajada[escalon_idx]
        else:
            setpoint[i] = escalones_bajada[-1]

def simulate_hybrid_controller(Kp, Ki, Kd, controller_type, t_sim, setpoint):
    """
    Simula un controlador híbrido que cambia entre llenado y vaciado
    según el error (positivo = llenar, negativo = vaciar)
    """
    try:
        dt = t_sim[1] - t_sim[0]
        y = np.zeros_like(t_sim)
        error_integral = 0
        error_prev = 0
        
        for i in range(1, len(t_sim)):
            # Error actual
            error = setpoint[i] - y[i-1]
            
            # Integral del error
            error_integral += error * dt
            
            # Derivada del error
            error_derivative = (error - error_prev) / dt
            
            # Señal de control
            if controller_type == 'PI':
                u = Kp * error + Ki * error_integral
            elif controller_type == 'PID':
                u = Kp * error + Ki * error_integral + Kd * error_derivative
            
            # Saturación de la señal de control [-1, 1]
            u = np.clip(u, -1, 1)
            
            # Selección de velocidad según el signo del control
            if u >= 0:
                # Llenado: velocidad positiva
                velocidad = u * v_max_llenado
            else:
                # Vaciado: velocidad negativa (u ya es negativo)
                velocidad = u * v_max_vaciado  # u es negativo, velocidad será negativa
            
            # Integración: nuevo nivel = nivel anterior + cambio
            y[i] = y[i-1] + velocidad * dt
            
            # Limitar el nivel físicamente (no puede ser negativo)
            y[i] = max(0, y[i])
            
            error_prev = error
        
        return t_sim, y
    
    except Exception as e:
        print(f"Error en simulación {controller_type}: {e}")
        return t_sim, np.full_like(t_sim, np.nan)

# Controladores variados para diferentes necesidades
controllers = {
    # 2. PID CRÍTICAMENTE AMORTIGUADO
    "PID_optimizado": {
    "type": "PID",
    "Kp": 18.0,  # Aumento controlado
    "Ki": 2.0,
    "Kd": 5.0,   # Amortiguación reforzada
    "slew_rate": 0.4  # Limita velocidad de cambio
}
    

}

# Crear figura con subplots
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Sistema de Control Híbrido de Tanque - Llenado/Vaciado Automático', fontsize=14)

# Colores para diferentes controladores
colors = ['blue', 'red', 'green', 'orange', 'purple']

# --- RESPUESTA TEMPORAL ---
ax1 = axes[0, 0]
ax1.set_title("Respuesta del Sistema de Control Híbrido")
ax1.plot(t_sim, setpoint, 'k--', linewidth=2, label="Setpoint")

print("Simulando controladores híbridos...")
valid_controllers = {}

for i, (name, params) in enumerate(controllers.items()):
    print(f"  Simulando {name}...")
    t_out, y_out = simulate_hybrid_controller(
        params["Kp"], params["Ki"], params["Kd"], 
        params["type"], t_sim, setpoint
    )
    if not np.isnan(y_out).all():
        ax1.plot(t_out, y_out, color=colors[i], linewidth=1.2, 
                label=f'{name} (Kp={params["Kp"]}, Ki={params["Ki"]}, Kd={params["Kd"]})')
        valid_controllers[name] = (t_out, y_out, params)
        print(f"    ✓ Simulación exitosa")
    else:
        print(f"    ✗ Simulación falló")

ax1.set_xlabel("Tiempo (s)")
ax1.set_ylabel("Nivel del tanque (cm)")
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)
ax1.set_xlim([0, t_total])
ax1.set_ylim([-1, 22])

# --- SEÑAL DE CONTROL ---
ax2 = axes[0, 1]
ax2.set_title("Señales de Control (Potencia del Motor)")

for i, (name, (t_out, y_out, params)) in enumerate(valid_controllers.items()):
    # Calcular señal de control
    control_signal = np.zeros_like(t_out)
    error_integral = 0
    error_prev = 0
    dt = t_out[1] - t_out[0]
    
    for j in range(1, len(t_out)):
        error = setpoint[j] - y_out[j-1]
        error_integral += error * dt
        error_derivative = (error - error_prev) / dt
        
        if params["type"] == 'PI':
            u = params["Kp"] * error + params["Ki"] * error_integral
        else:  # PID
            u = params["Kp"] * error + params["Ki"] * error_integral + params["Kd"] * error_derivative
        
        control_signal[j] = np.clip(u, -1, 1)
        error_prev = error
    
    ax2.plot(t_out, control_signal * 100, color=colors[i], linewidth=1.2, label=name)

ax2.axhline(y=0, color='k', linestyle='-', alpha=0.3)
ax2.axhline(y=100, color='r', linestyle=':', alpha=0.5, label='Potencia máxima')
ax2.axhline(y=-100, color='r', linestyle=':', alpha=0.5)
ax2.set_xlabel("Tiempo (s)")
ax2.set_ylabel("Potencia del motor (%)")
ax2.legend(fontsize=8)
ax2.grid(True, alpha=0.3)
ax2.set_xlim([0, t_total])

# --- ERROR DE CONTROL ---
ax3 = axes[1, 0]
ax3.set_title("Error de Control")

for i, (name, (t_out, y_out, params)) in enumerate(valid_controllers.items()):
    error = setpoint - y_out
    ax3.plot(t_out, error, color=colors[i], linewidth=1.2, label=name)

ax3.axhline(y=0, color='k', linestyle='-', alpha=0.3)
ax3.set_xlabel("Tiempo (s)")
ax3.set_ylabel("Error (cm)")
ax3.legend(fontsize=8)
ax3.grid(True, alpha=0.3)
ax3.set_xlim([0, t_total])

# --- VELOCIDAD DEL SISTEMA ---
ax4 = axes[1, 1]
ax4.set_title("Velocidad de Cambio del Nivel")

for i, (name, (t_out, y_out, params)) in enumerate(valid_controllers.items()):
    # Calcular velocidad (derivada del nivel)
    velocidad = np.gradient(y_out, t_out)
    ax4.plot(t_out, velocidad, color=colors[i], linewidth=1.2, label=name)

ax4.axhline(y=v_max_llenado, color='g', linestyle=':', alpha=0.7, label='Vel. máx. llenado')
ax4.axhline(y=-v_max_vaciado, color='r', linestyle=':', alpha=0.7, label='Vel. máx. vaciado')
ax4.axhline(y=0, color='k', linestyle='-', alpha=0.3)
ax4.set_xlabel("Tiempo (s)")
ax4.set_ylabel("Velocidad (cm/s)")
ax4.legend(fontsize=8)
ax4.grid(True, alpha=0.3)
ax4.set_xlim([0, t_total])

plt.tight_layout()
plt.show()

# --- ANÁLISIS CUANTITATIVO ---
print("\n" + "="*90)
print("ANÁLISIS DE RENDIMIENTO - DIFERENTES COMPORTAMIENTOS DE CONTROL")
print("="*90)

def calculate_performance_metrics(t, y, setpoint):
    """Calcula métricas de rendimiento del controlador"""
    error = setpoint - y
    
    # ISE (Integral Square Error)
    ise = np.trapz(error**2, t)
    
    # IAE (Integral Absolute Error)
    iae = np.trapz(np.abs(error), t)
    
    # Error RMS
    rms_error = np.sqrt(np.mean(error**2))
    
    # Tiempo de establecimiento (settling time) para el primer escalón significativo
    target = 4  # Primer escalón a 4 cm
    tolerance = 0.2  # Tolerancia de ±0.2 cm
    settling_time = None
    
    # Buscar cuando alcanza y se mantiene dentro de la tolerancia
    for i in range(len(t)):
        if t[i] > 5:  # Después de que cambie el setpoint
            if abs(y[i] - target) <= tolerance:
                # Verificar que se mantiene estable por al menos 5 segundos
                stable = True
                for j in range(i, min(i + int(5/(t[1]-t[0])), len(y))):
                    if abs(y[j] - target) > tolerance:
                        stable = False
                        break
                if stable:
                    settling_time = t[i]
                    break
    
    # Overshoot máximo para el primer escalón
    max_overshoot = 0
    if len(t) > 100:
        segment_4cm = y[int(len(y)*0.1):int(len(y)*0.25)]  # Primer escalón
        if len(segment_4cm) > 0:
            max_overshoot = max(0, np.max(segment_4cm) - target)
    
    return ise, iae, rms_error, settling_time, max_overshoot

print(f"{'Controlador':<15} {'ISE':<8} {'IAE':<8} {'RMS_Err':<8} {'T_settle':<10} {'Overshoot':<10}")
print("-" * 75)

for name, (t_out, y_out, params) in valid_controllers.items():
    ise, iae, rms_error, t_settle, overshoot = calculate_performance_metrics(t_out, y_out, setpoint)
    t_settle_str = f"{t_settle:.1f}s" if t_settle else "N/A"
    print(f"{name:<15} {ise:<8.0f} {iae:<8.1f} {rms_error:<8.2f} {t_settle_str:<10} {overshoot:<10.2f}")

print("\n" + "="*90)
print("CARACTERÍSTICAS DE CADA CONTROLADOR:")
print("-" * 50)
print("• PI_muy_lento:   Respuesta MUY lenta, sin overshoot, muy estable")
print("• PI_conservador: Respuesta lenta pero segura, mínimo overshoot")
print("• PI_equilibrado: Buen compromiso velocidad-estabilidad")
print("• PID_amortiguado: Derivativo alto para reducir oscilaciones")
print("• PID_agresivo:   Respuesta rápida, puede tener overshoot")
print("\nMÉTRICAS:")
print("- ISE: Error cuadrático integrado (menor = mejor)")
print("- IAE: Error absoluto integrado (menor = mejor)")
print("- T_settle: Tiempo hasta establecerse (menor = más rápido)")
print("- Overshoot: Sobreimpulso máximo (menor = más estable)")
print("="*90)