import tkinter as tk
from tkinter import ttk
import RPi.GPIO as GPIO
import board
import adafruit_dht
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.style as mplstyle

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

def control(pin, state):
    GPIO.output(pin, GPIO.HIGH if (pin == LOCK_PIN and state == "activate") else GPIO.LOW if pin == LOCK_PIN else GPIO.LOW if state == "activate" else GPIO.HIGH)
    update_actuator_states()

def get_state_icon(pin, label_type):
    state = GPIO.input(pin)
    icons = {
        "fan": "💨" if state == GPIO.LOW else "🌀", 
        "lock": "🔓" if state == GPIO.HIGH else "🔒",
        "pad": "🔥" if state == GPIO.LOW else "❄️",
    }
    return icons[label_type]

def update_actuator_states():
    fan_state = GPIO.input(FAN_PIN)
    lock_state = GPIO.input(LOCK_PIN)
    pad_state = GPIO.input(HEATING_PAD_PIN)

    fan_label.config(text=f"Ventilador: {get_state_icon(FAN_PIN, 'fan')} {'Encendido' if fan_state == GPIO.HIGH else 'Apagado'}")
    lock_label.config(text=f"Cerradura: {get_state_icon(LOCK_PIN, 'lock')} {'Abierta' if lock_state == GPIO.HIGH else 'Cerrada'}")
    pad_label.config(text=f"Almohadilla: {get_state_icon(HEATING_PAD_PIN, 'pad')} {'Encendida' if pad_state == GPIO.HIGH else 'Apagada'}")
    
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

    # Añadir un fondo con color
    ax.set_facecolor('#f0f0f0')

    # Configurar las líneas
    ax.plot(time_data, humidity_data, label="Humedad (%)", color="dodgerblue", linewidth=2)
    ax.plot(time_data, temperature_data, label="Ambiente (°C)", color="tomato", linewidth=2)
    ax.plot(time_data, pad_temperature_data, label="Pad (°C)", color="forestgreen", linewidth=2)

    # Añadir título y etiquetas
    ax.set_title("Temperatura y Humedad", fontsize=14, color='black')
    ax.set_xlabel("Tiempo (s)", fontsize=12)
    ax.set_ylabel("Valores", fontsize=12)

    # Configurar la leyenda y los estilos
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Mejorar la apariencia de los ejes
    ax.tick_params(axis='both', which='major', labelsize=10)

    canvas.draw()


def toggle_fullscreen(event=None):
    global fullscreen
    fullscreen = not fullscreen
    root.attributes('-fullscreen', fullscreen)
    if fullscreen:
        root.bind('<Escape>', toggle_fullscreen)  # Salir del fullscreen con la tecla ESC
    else:
        root.bind('<F11>', toggle_fullscreen)    # Volver a fullscreen con F11

fullscreen = True  # Establecer al principio en modo pantalla completa
root = tk.Tk()

root.title("Casillero Inteligente - Teikit")
root.configure(bg='#f54c09')

# Pantalla completa
root.attributes('-fullscreen', fullscreen)
root.bind('<F11>', toggle_fullscreen)

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

# Estilo de las etiquetas
label_style = {"font": ("Arial", 20), "bg": "#f54c09", "fg": "white"}

hum_label = tk.Label(left, text="---", **label_style)
hum_label.pack(pady=5)
amb_label = tk.Label(left, text="---", **label_style)
amb_label.pack(pady=5)
padtemp_label = tk.Label(left, text="---", **label_style)
padtemp_label.pack(pady=5)

# Estados
fan_label = tk.Label(left, text="Ventilador: ---", **label_style)
fan_label.pack(pady=5)
lock_label = tk.Label(left, text="Cerradura: ---", **label_style)
lock_label.pack(pady=5)
pad_label = tk.Label(left, text="Almohadilla: ---", **label_style)
pad_label.pack(pady=5)

# Botones
btn_style = {"font": ("Arial", 14), "bg": "#4caf50", "fg": "white", "width": 22, "height": 1}

def add_button(text, pin, state, row):
    bg = "#4caf50" if "Activar" in text or "Abrir" in text else "#b71c1c"
    btn_style["bg"] = bg
    tk.Button(left, text=text, command=lambda: control(pin, state), **btn_style).pack(pady=3)

btns = [
    ("Activar Ventilador", FAN_PIN, "activate"),
    ("Desactivar Ventilador", FAN_PIN, "deactivate"),
    ("Abrir Cerradura", LOCK_PIN, "activate"),
    ("Cerrar Cerradura", LOCK_PIN, "deactivate"),
    ("Activar Almohadilla", HEATING_PAD_PIN, "activate"),
    ("Desactivar Almohadilla", HEATING_PAD_PIN, "deactivate")
]
for i, (t, p, s) in enumerate(btns):
    add_button(t, p, s, i)

# Botón cerrar
root.protocol("WM_DELETE_WINDOW", lambda: (GPIO.cleanup(), root.quit()))

# Gráfico
fig, ax = plt.subplots(figsize=(7, 4))
canvas = FigureCanvasTkAgg(fig, master=right)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

update_readings()
root.mainloop()
