# UI mejorada del casillero inteligente - Teikit
import tkinter as tk
from tkinter import ttk
import RPi.GPIO as GPIO
import board
import adafruit_dht
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.style as mplstyle

# Configuracion de estilo de matplotlib
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

def control(pin, state):
    GPIO.output(pin, GPIO.HIGH if (pin == LOCK_PIN and state == "activate") else GPIO.LOW if pin == LOCK_PIN else GPIO.LOW if state == "activate" else GPIO.HIGH)
    update_actuator_states()

def get_state_icon(pin, label_type):
    state = GPIO.input(pin)
    icons = {
        "fan": "💨 Encendido" if state == GPIO.LOW else "💤 Apagado",
        "lock": "🔓 Abierta" if state == GPIO.HIGH else "🔒 Cerrada",
        "pad": "🔥 Encendida" if state == GPIO.LOW else "❄️ Apagada",
    }
    return icons[label_type]

def update_actuator_states():
    fan_label.config(text=f"Ventilador: {get_state_icon(FAN_PIN, 'fan')}")
    lock_label.config(text=f"Cerradura: {get_state_icon(LOCK_PIN, 'lock')}")
    pad_label.config(text=f"Almohadilla: {get_state_icon(HEATING_PAD_PIN, 'pad')}")

def update_readings():
    h, t = read_dht()
    pad_t = read_pad_temp()
    if h and t and pad_t:
        humidity_data.append(h)
        temperature_data.append(t)
        pad_temperature_data.append(pad_t)
        time_data.append(len(time_data))
        if len(time_data) > 50:
            for lst in [time_data, humidity_data, temperature_data, pad_temperature_data]:
                lst.pop(0)
        hum_label.config(text=f"Humedad: {h:.1f} %")
        amb_label.config(text=f"Temp. Ambiente: {t:.1f} °C")
        padtemp_label.config(text=f"Temp. Almohadilla: {pad_t:.1f} °C")
    update_actuator_states()
    update_graphs()
    root.after(2000, update_readings)

# Gráficos y UI

def update_graphs():
    ax.clear()
    ax.plot(time_data, humidity_data, label="Humedad (%)", color="blue", linewidth=2)
    ax.plot(time_data, temperature_data, label="Ambiente (°C)", color="red", linewidth=2)
    ax.plot(time_data, pad_temperature_data, label="Pad (°C)", color="green", linewidth=2)
    ax.set_title("Temperatura y Humedad (últimos 50s)")
    ax.set_xlabel("Tiempo")
    ax.set_ylabel("Valores")
    ax.legend(loc="upper left")
    canvas.draw()

def on_close():
    GPIO.cleanup()
    root.destroy()

# Interfaz principal
root = tk.Tk()
root.title("Casillero Inteligente - Teikit")
root.attributes('-fullscreen', True)
root.configure(bg='#f54c09')
root.protocol("WM_DELETE_WINDOW", on_close)

# Logo
try:
    img = Image.open("../assets/teikit_banner.png").resize((400, 100))
    logo = ImageTk.PhotoImage(img)
    tk.Label(root, image=logo, bg="#f54c09").pack(pady=10)
except: pass

main_frame = tk.Frame(root, bg="#f54c09")
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

left = tk.Frame(main_frame, bg="#f54c09")
right = tk.Frame(main_frame, bg="#f54c09")
left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Labels sensores
label_style = {"font": ("Arial", 20), "bg": "#f54c09", "fg": "white"}

amb_label = tk.Label(left, text="Temp. Ambiente: ---", **label_style)
amb_label.pack(pady=5)
hum_label = tk.Label(left, text="Humedad: ---", **label_style)
hum_label.pack(pady=5)
padtemp_label = tk.Label(left, text="Temp. Almohadilla: ---", **label_style)
padtemp_label.pack(pady=5)

# Estados
fan_label = tk.Label(left, text="Ventilador: ---", **label_style)
fan_label.pack(pady=5)
lock_label = tk.Label(left, text="Cerradura: ---", **label_style)
lock_label.pack(pady=5)
pad_label = tk.Label(left, text="Almohadilla: ---", **label_style)
pad_label.pack(pady=5)

# Botones
btn_style = {"font": ("Arial", 14), "fg": "white", "width": 22, "height": 1}

def add_button(text, pin, state):
    bg = "#4caf50" if "Activar" in text or "Abrir" in text else "#b71c1c"
    tk.Button(left, text=text, command=lambda: control(pin, state), bg=bg, **btn_style).pack(pady=3)

btns = [
    ("Activar Ventilador", FAN_PIN, "activate"),
    ("Desactivar Ventilador", FAN_PIN, "deactivate"),
    ("Abrir Cerradura", LOCK_PIN, "activate"),
    ("Cerrar Cerradura", LOCK_PIN, "deactivate"),
    ("Activar Almohadilla", HEATING_PAD_PIN, "activate"),
    ("Desactivar Almohadilla", HEATING_PAD_PIN, "deactivate")
]
for t, p, s in btns:
    add_button(t, p, s)

# Gráfico
fig, ax = plt.subplots(figsize=(7, 4))
canvas = FigureCanvasTkAgg(fig, master=right)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Iniciar
update_readings()
root.mainloop()
