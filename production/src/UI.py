import tkinter as tk
from tkinter import ttk, messagebox
import RPi.GPIO as GPIO
import board
import adafruit_dht
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.style as mplstyle
import os
import time
start_time = time.time()

# Configuración de estilo de matplotlib
mplstyle.use('seaborn-v0_8-dark-palette')
plt.rcParams.update({'axes.facecolor': 'white', 'figure.facecolor': 'white', 'axes.edgecolor': 'gray'})

# Pines y sensores
DHT_SENSOR_PIN = board.D5
DS18B20_DEVICE_FILE = '/sys/bus/w1/devices/28-3de10457e49d/w1_slave'
FAN_PIN, LOCK_PIN, HEATING_PAD_PIN = 22, 17, 27

dht_sensor = adafruit_dht.DHT22(DHT_SENSOR_PIN)
GPIO.setmode(GPIO.BCM)
GPIO.setup([FAN_PIN, LOCK_PIN, HEATING_PAD_PIN], GPIO.OUT)
GPIO.output(FAN_PIN, GPIO.HIGH)
GPIO.output(LOCK_PIN, GPIO.LOW)
GPIO.output(HEATING_PAD_PIN, GPIO.HIGH)

# Datos
time_data, humidity_data, temperature_data, pad_temperature_data = [], [], [], []

# Funciones sensores y actuadores
def read_dht():
    try:
        return dht_sensor.humidity, dht_sensor.temperature
    except RuntimeError:
        return None, None

def read_pad_temp():
    try:
        with open(DS18B20_DEVICE_FILE, 'r') as f:
            lines = f.readlines()
            temp_pos = lines[1].find('t=')
            if temp_pos != -1:
                return float(lines[1][temp_pos + 2:]) / 1000.0
    except: return None

def set_state(pin, state):
    GPIO.output(pin, state)
    update_actuator_states()

def update_actuator_states():
    fan_state = GPIO.input(FAN_PIN)
    fan_label.config(text=f"🌀 Ventilador: [ENCENDIDO]" if fan_state == GPIO.LOW else "🌀 Ventilador: [APAGADO]")

    lock_state = GPIO.input(LOCK_PIN)
    lock_label.config(text=f"🔓 Cerradura: [ABIERTA]" if lock_state == GPIO.HIGH else "🔒 Cerradura: [CERRADA]")

    pad_state = GPIO.input(HEATING_PAD_PIN)
    pad_label.config(text=f"🔥 Almohadilla: [ENCENDIDA]" if pad_state == GPIO.LOW else "❄️ Almohadilla: [APAGADA]")

def update_readings():
    h, t = read_dht()
    pad_t = read_pad_temp()
    if h and t and pad_t:
        humidity_data.append(h)
        temperature_data.append(t)
        pad_temperature_data.append(pad_t)
        time_data.append(round(time.time() - start_time, 1))
        if len(time_data) > 50:
            for lst in [time_data, humidity_data, temperature_data, pad_temperature_data]:
                lst.pop(0)
        hum_label.config(text=f"[{h:.1f}%] Humedad")
        amb_label.config(text=f"[{t:.1f}°C] Ambiente")
        padtemp_label.config(text=f"[{pad_t:.1f}°C] Almohadilla")
    update_actuator_states()
    update_graphs()
    root.after(2000, update_readings)

# Gráficos y UI
def update_graphs():
    ax.clear()
    ax.set_facecolor('#f0f0f0')
    ax.plot(time_data, humidity_data, label="Humedad (%)", color="dodgerblue", linewidth=2)
    ax.plot(time_data, temperature_data, label="Ambiente (°C)", color="tomato", linewidth=2)
    ax.plot(time_data, pad_temperature_data, label="Pad (°C)", color="forestgreen", linewidth=2)
    ax.set_title("Temperatura y Humedad", fontsize=14, color='black')
    ax.set_xlabel("Tiempo (s)", fontsize=12)
    ax.set_ylabel("Valores", fontsize=12)
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.tick_params(axis='both', which='major', labelsize=10)
    canvas.draw()

def toggle_fullscreen(event=None):
    global fullscreen
    fullscreen = not fullscreen
    root.attributes('-fullscreen', fullscreen)
    if fullscreen:
        root.bind('<Escape>', toggle_fullscreen)
    else:
        root.bind('<F11>', toggle_fullscreen)

fullscreen = True
root = tk.Tk()
root.title("Casillero Inteligente - Teikit")
root.configure(bg='#f54c09')
root.attributes('-fullscreen', fullscreen)
root.bind('<F11>', toggle_fullscreen)

# Logo
try:
    img = Image.open("../assets/teikit_banner.png")
    img.thumbnail((400, 100), Image.LANCZOS)
    logo = ImageTk.PhotoImage(img)
    tk.Label(root, image=logo, bg="#f54c09").pack(pady=10)
except: pass

main_frame = tk.Frame(root, bg="#f54c09")
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
left = tk.Frame(main_frame, bg="#f54c09")
right = tk.Frame(main_frame, bg="#f54c09")
left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

label_style = {"font": ("Arial", 20), "bg": "#f54c09", "fg": "white"}
btn_style_on = {"font": ("Arial", 14), "bg": "#a5d6a7", "fg": "black", "width": 10, "height": 1}
btn_style_off = {"font": ("Arial", 14), "bg": "#ef9a9a", "fg": "black", "width": 10, "height": 1}

# Condiciones actuales
tk.Label(left, text="🌡️ Condiciones Actuales", font=("Arial", 22, "bold"), bg="#f54c09", fg="white").pack(pady=(0, 10))
hum_label = tk.Label(left, text="[---%] Humedad", **label_style)
hum_label.pack()
amb_label = tk.Label(left, text="[---°C] Ambiente", **label_style)
amb_label.pack()
padtemp_label = tk.Label(left, text="[---°C] Almohadilla", **label_style)
padtemp_label.pack()

# Separador visual
tk.Frame(left, height=2, bd=1, relief=tk.SUNKEN, bg="white").pack(fill=tk.X, pady=15)

# Controles
tk.Label(left, text="🔧 Controles", font=("Arial", 22, "bold"), bg="#f54c09", fg="white").pack(pady=(10, 10))

fan_label = tk.Label(left, text="🌀 Ventilador: [---]", **label_style)
fan_label.pack()
frame_fan_btns = tk.Frame(left, bg="#f54c09")
frame_fan_btns.pack(pady=4)
tk.Button(frame_fan_btns, text="Encender", command=lambda: set_state(FAN_PIN, GPIO.LOW), **btn_style_on).pack(side=tk.LEFT, padx=5)
tk.Button(frame_fan_btns, text="Apagar", command=lambda: set_state(FAN_PIN, GPIO.HIGH), **btn_style_off).pack(side=tk.LEFT, padx=5)

lock_label = tk.Label(left, text="🔒 Cerradura: [---]", **label_style)
lock_label.pack(pady=(10, 0))
frame_lock_btns = tk.Frame(left, bg="#f54c09")
frame_lock_btns.pack(pady=4)
tk.Button(frame_lock_btns, text="Abrir", command=lambda: set_state(LOCK_PIN, GPIO.HIGH), **btn_style_on).pack(side=tk.LEFT, padx=5)
tk.Button(frame_lock_btns, text="Cerrar", command=lambda: set_state(LOCK_PIN, GPIO.LOW), **btn_style_off).pack(side=tk.LEFT, padx=5)

pad_label = tk.Label(left, text="🔥 Almohadilla: [---]", **label_style)
pad_label.pack(pady=(10, 0))
frame_pad_btns = tk.Frame(left, bg="#f54c09")
frame_pad_btns.pack(pady=4)
tk.Button(frame_pad_btns, text="Encender", command=lambda: set_state(HEATING_PAD_PIN, GPIO.LOW), **btn_style_on).pack(side=tk.LEFT, padx=5)
tk.Button(frame_pad_btns, text="Apagar", command=lambda: set_state(HEATING_PAD_PIN, GPIO.HIGH), **btn_style_off).pack(side=tk.LEFT, padx=5)

# Botón cerrar
root.protocol("WM_DELETE_WINDOW", lambda: (GPIO.cleanup(), root.quit()))

# Gráfico
fig, ax = plt.subplots(figsize=(7, 4))
canvas = FigureCanvasTkAgg(fig, master=right)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

update_readings()
root.mainloop()
