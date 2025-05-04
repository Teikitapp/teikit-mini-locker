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

# Ventana principal
root = tk.Tk()
root.attributes('-fullscreen', True)
root.configure(bg='#f54c09')

# Canvas scroll
canvas = tk.Canvas(root, bg='#f54c09', highlightthickness=0)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollable_frame = tk.Frame(canvas, bg='#f54c09')
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox('all'))
scrollable_frame.bind("<Configure>", on_configure)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Imagen
try:
    logo = Image.open("../assets/teikit_banner.png")
    logo = logo.resize((logo.width // 2, logo.height // 2))
    logo_img = ImageTk.PhotoImage(logo)
    logo_label = tk.Label(scrollable_frame, image=logo_img, bg='#f54c09')
    logo_label.grid(row=0, column=0, columnspan=2, pady=20)
except Exception as e:
    print(f"No se pudo cargar el logo: {e}")

# Lecturas
label_font = ("Arial", 30, "bold")
humidity_label = tk.Label(scrollable_frame, text="Humedad: ---", font=label_font, bg="#f54c09", fg="white")
humidity_label.grid(row=1, column=0, columnspan=2, pady=10)

ambient_temp_label = tk.Label(scrollable_frame, text="Temp. Ambiente: ---", font=label_font, bg="#f54c09", fg="white")
ambient_temp_label.grid(row=2, column=0, columnspan=2, pady=10)

pad_temp_label = tk.Label(scrollable_frame, text="Temp. del Pad: ---", font=label_font, bg="#f54c09", fg="white")
pad_temp_label.grid(row=3, column=0, columnspan=2, pady=10)

# Estado de actuadores
state_font = ("Arial", 22, "bold")
fan_state_label = tk.Label(scrollable_frame, text="Ventilador: ---", font=state_font, bg="#f54c09", fg="white")
fan_state_label.grid(row=4, column=0, columnspan=2, pady=5)

lock_state_label = tk.Label(scrollable_frame, text="Cerradura: ---", font=state_font, bg="#f54c09", fg="white")
lock_state_label.grid(row=5, column=0, columnspan=2, pady=5)

pad_state_label = tk.Label(scrollable_frame, text="Almohadilla: ---", font=state_font, bg="#f54c09", fg="white")
pad_state_label.grid(row=6, column=0, columnspan=2, pady=5)

# Botones
button_font = ("Arial", 26, "bold")
def create_button(row, text, command, color):
    btn = tk.Button(scrollable_frame, text=text, command=command, font=button_font,
                    bg=color, fg="white", width=20, height=2)
    btn.grid(row=row, column=0, columnspan=2, pady=10, sticky="ew")

create_button(7, "Activar Ventilador", lambda: control_actuator(FAN_PIN, "activate"), "#4caf50")
create_button(8, "Desactivar Ventilador", lambda: control_actuator(FAN_PIN, "deactivate"), "#b71c1c")
create_button(9, "Abrir Cerradura", lambda: control_actuator(LOCK_PIN, "activate"), "#4caf50")
create_button(10, "Cerrar Cerradura", lambda: control_actuator(LOCK_PIN, "deactivate"), "#b71c1c")
create_button(11, "Activar Almohadilla", lambda: control_actuator(HEATING_PAD_PIN, "activate"), "#4caf50")
create_button(12, "Desactivar Almohadilla", lambda: control_actuator(HEATING_PAD_PIN, "deactivate"), "#b71c1c")

# Botón salir
exit_btn = tk.Button(scrollable_frame, text="Cerrar", font=("Arial", 26, "bold"),
                     bg="#ff4d4d", fg="white", command=lambda: (GPIO.cleanup(), root.destroy()),
                     width=15, height=2)
exit_btn.grid(row=13, column=0, columnspan=2, pady=40)

# Expandir columnas al 100%
scrollable_frame.grid_columnconfigure(0, weight=1)
scrollable_frame.grid_columnconfigure(1, weight=1)

update_readings()
root.mainloop()
