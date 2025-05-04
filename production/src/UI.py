import tkinter as tk
import RPi.GPIO as GPIO
import board
import adafruit_dht
from PIL import Image, ImageTk

# Configuración de los pines
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

def update_readings():
    humidity, ambient_temp = read_humidity_and_temp()
    pad_temp = read_pad_temperature()

    if humidity is not None:
        humidity_label.config(text=f"Humedad: {humidity:.1f} %")
    if ambient_temp is not None:
        ambient_temp_label.config(text=f"Temp. Ambiente: {ambient_temp:.1f} °C")
    if pad_temp is not None:
        pad_temp_label.config(text=f"Temp. del Pad: {pad_temp:.1f} °C")

    root.after(2000, update_readings)

# UI
root = tk.Tk()
root.title("Casillero Inteligente - Teikit")
root.configure(bg='#f54c09')
root.geometry("800x600")

# Scrollable frame
canvas = tk.Canvas(root, bg='#f54c09', highlightthickness=0)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg='#f54c09')

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Carga del logo
try:
    logo = Image.open("assets/teikit_banner.png")
    logo = logo.resize((int(logo.width * 0.5), int(logo.height * 0.5)))
    logo_img = ImageTk.PhotoImage(logo)
    logo_label = tk.Label(scrollable_frame, image=logo_img, bg='#f54c09')
    logo_label.pack(pady=10)
except Exception as e:
    print(f"No se pudo cargar el logo: {e}")

# Lecturas
label_font = ("Arial", 24, "bold")
humidity_label = tk.Label(scrollable_frame, text="Humedad: ---", font=label_font, bg="#f54c09", fg="white")
humidity_label.pack(pady=10)

ambient_temp_label = tk.Label(scrollable_frame, text="Temp. Ambiente: ---", font=label_font, bg="#f54c09", fg="white")
ambient_temp_label.pack(pady=10)

pad_temp_label = tk.Label(scrollable_frame, text="Temp. del Pad: ---", font=label_font, bg="#f54c09", fg="white")
pad_temp_label.pack(pady=10)

# Botones
button_font = ("Arial", 20, "bold")
def create_button(text, command, color):
    return tk.Button(scrollable_frame, text=text, command=command, font=button_font,
                     bg=color, fg="white", width=20, height=2)

create_button("Activar Ventilador", lambda: control_actuator(FAN_PIN, "activate"), "#4caf50").pack(pady=5)
create_button("Desactivar Ventilador", lambda: control_actuator(FAN_PIN, "deactivate"), "#b71c1c").pack(pady=5)
create_button("Abrir Cerradura", lambda: control_actuator(LOCK_PIN, "activate"), "#4caf50").pack(pady=5)
create_button("Cerrar Cerradura", lambda: control_actuator(LOCK_PIN, "deactivate"), "#b71c1c").pack(pady=5)
create_button("Activar Almohadilla", lambda: control_actuator(HEATING_PAD_PIN, "activate"), "#4caf50").pack(pady=5)
create_button("Desactivar Almohadilla", lambda: control_actuator(HEATING_PAD_PIN, "deactivate"), "#b71c1c").pack(pady=5)

# Botón de cerrar
tk.Button(scrollable_frame, text="Cerrar", font=("Arial", 18, "bold"),
          bg="#ff4d4d", fg="white", command=lambda: (GPIO.cleanup(), root.destroy()),
          width=10, height=2).pack(pady=20)

update_readings()
root.mainloop()
