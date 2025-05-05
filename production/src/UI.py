import tkinter as tk
import RPi.GPIO as GPIO
import board
import adafruit_dht
from PIL import Image, ImageTk

# Pines
DHT_SENSOR_PIN = board.D5
device_file = '/sys/bus/w1/devices/28-3de10457e49d/w1_slave'
FAN_PIN = 22
LOCK_PIN = 17
HEATING_PAD_PIN = 27

dht_sensor = adafruit_dht.DHT22(DHT_SENSOR_PIN)

GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)
GPIO.setup(LOCK_PIN, GPIO.OUT)
GPIO.setup(HEATING_PAD_PIN, GPIO.OUT)

def read_humidity_and_temp():
    try:
        humidity = dht_sensor.humidity
        temperature = dht_sensor.temperature
        return humidity, temperature
    except RuntimeError as error:
        print(f"Error DHT22: {error.args[0]}")
        return None, None

def read_pad_temperature():
    try:
        with open(device_file, 'r') as f:
            lines = f.readlines()
            temp_output = lines[1].find('t=')
            if temp_output != -1:
                temp_string = lines[1].strip()[temp_output + 2:]
                return float(temp_string) / 1000.0
    except Exception as e:
        print(f"Error Pad: {e}")
    return None

def control_actuator(pin, state):
    GPIO.output(pin, GPIO.LOW if state == "activate" else GPIO.HIGH)
    update_actuator_states()

def get_state_text(pin, label_type):
    state = GPIO.input(pin)
    if label_type == "fan":
        return "Encendido" if state == GPIO.LOW else "Apagado"
    elif label_type == "lock":
        return "Abierta" if state == GPIO.LOW else "Cerrada"
    elif label_type == "pad":
        return "Encendida" if state == GPIO.LOW else "Apagada"

def update_actuator_states():
    fan_state_label.config(text=f"Ventilador: {get_state_text(FAN_PIN, 'fan')}")
    lock_state_label.config(text=f"Cerradura: {get_state_text(LOCK_PIN, 'lock')}")
    pad_state_label.config(text=f"Almohadilla: {get_state_text(HEATING_PAD_PIN, 'pad')}")

def update_readings():
    humidity, ambient_temp = read_humidity_and_temp()
    pad_temp = read_pad_temperature()

    if humidity is not None:
        humidity_label.config(text=f"Humedad: {humidity:.1f} %")
    if ambient_temp is not None:
        ambient_temp_label.config(text=f"Temp. Ambiente: {ambient_temp:.1f} °C")
    if pad_temp is not None:
        pad_temp_label.config(text=f"Temp. del Pad: {pad_temp:.1f} °C")

    update_actuator_states()
    root.after(2000, update_readings)

# UI
root = tk.Tk()
root.title("Casillero Inteligente - Teikit")
root.attributes('-fullscreen', True)
root.configure(bg='#f54c09')

# Configurar grid
root.rowconfigure(list(range(7)), weight=1)
root.columnconfigure(0, weight=1)

# Logo
try:
    logo = Image.open("../assets/teikit_banner.png")
    logo = logo.resize((400, 100))
    logo_img = ImageTk.PhotoImage(logo)
    logo_label = tk.Label(root, image=logo_img, bg='#f54c09')
    logo_label.grid(row=0, column=0, pady=5)
except Exception as e:
    print(f"No se pudo cargar el logo: {e}")

# Sensores
label_font = ("Arial", 20)
humidity_label = tk.Label(root, text="Humedad: ---", font=label_font, bg="#f54c09", fg="white")
humidity_label.grid(row=1, column=0)

ambient_temp_label = tk.Label(root, text="Temp. Ambiente: ---", font=label_font, bg="#f54c09", fg="white")
ambient_temp_label.grid(row=2, column=0)

pad_temp_label = tk.Label(root, text="Temp. del Pad: ---", font=label_font, bg="#f54c09", fg="white")
pad_temp_label.grid(row=3, column=0)

# Estados
state_font = ("Arial", 18)
fan_state_label = tk.Label(root, text="Ventilador: ---", font=state_font, bg="#f54c09", fg="white")
fan_state_label.grid(row=4, column=0)

lock_state_label = tk.Label(root, text="Cerradura: ---", font=state_font, bg="#f54c09", fg="white")
lock_state_label.grid(row=5, column=0)

pad_state_label = tk.Label(root, text="Almohadilla: ---", font=state_font, bg="#f54c09", fg="white")
pad_state_label.grid(row=6, column=0)

# Frame de botones
button_frame = tk.Frame(root, bg='#f54c09')
button_frame.grid(row=7, column=0, pady=10)
for i in range(2): button_frame.columnconfigure(i, weight=1)

button_font = ("Arial", 16)
btn_opts = {"font": button_font, "bg": "#4caf50", "fg": "white", "width": 18, "height": 1}

buttons = [
    ("Activar Ventilador", lambda: control_actuator(FAN_PIN, "activate")),
    ("Desactivar Ventilador", lambda: control_actuator(FAN_PIN, "deactivate")),
    ("Abrir Cerradura", lambda: control_actuator(LOCK_PIN, "activate")),
    ("Cerrar Cerradura", lambda: control_actuator(LOCK_PIN, "deactivate")),
    ("Activar Almohadilla", lambda: control_actuator(HEATING_PAD_PIN, "activate")),
    ("Desactivar Almohadilla", lambda: control_actuator(HEATING_PAD_PIN, "deactivate"))
]

for idx, (text, cmd) in enumerate(buttons):
    bg = "#4caf50" if "Activar" in text or "Abrir" in text else "#b71c1c"
    tk.Button(button_frame, text=text, command=cmd, bg=bg, **btn_opts).grid(row=idx // 2, column=idx % 2, padx=10, pady=5)

# Botón de cerrar
tk.Button(root, text="Cerrar", font=("Arial", 18, "bold"), bg="#ff4d4d", fg="white",
          width=15, height=1, command=lambda: (GPIO.cleanup(), root.destroy())).grid(row=8, column=0, pady=10)

update_readings()
root.mainloop()
