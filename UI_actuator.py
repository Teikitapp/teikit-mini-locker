import tkinter as tk
import RPi.GPIO as GPIO

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.OUT)  # Fan
GPIO.setup(17, GPIO.OUT)  # Cerradura magnética
GPIO.setup(27, GPIO.OUT)  # Almohadilla calefactora

# Función para controlar actuadores
def control_actuator(pin, state):
    GPIO.output(pin, GPIO.LOW if state == "activate" else GPIO.HIGH)

# Configuración de la UI
root = tk.Tk()
root.title("Control de Casillero Teikit")

# Botones para los actuadores
tk.Button(root, text="Activar Ventilador", command=lambda: control_actuator(22, "activate")).pack()
tk.Button(root, text="Desactivar Ventilador", command=lambda: control_actuator(22, "deactivate")).pack()
tk.Button(root, text="Activar Cerradura", command=lambda: control_actuator(17, "activate")).pack()
tk.Button(root, text="Desactivar Cerradura", command=lambda: control_actuator(17, "deactivate")).pack()
tk.Button(root, text="Activar Almohadilla", command=lambda: control_actuator(27, "activate")).pack()
tk.Button(root, text="Desactivar Almohadilla", command=lambda: control_actuator(27, "deactivate")).pack()

# Iniciar el loop de la UI
try:
    root.mainloop()
finally:
    GPIO.cleanup()
