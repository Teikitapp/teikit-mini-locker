import tkinter as tk
from tkinter import messagebox
import time
import board
import adafruit_dht
import RPi.GPIO as GPIO

# Configuración de los pines
DHT_SENSOR_PIN = board.D5  # Pin para el sensor DHT22
device_file = '/sys/bus/w1/devices/28-3de10457e49d/w1_slave'  # Ruta del sensor DS18B20

RELAY_PIN = 18  # Pin GPIO que controla el relé

# Configuración del sensor DHT22
dht_sensor = adafruit_dht.DHT22(DHT_SENSOR_PIN)

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

def read_humidity_and_temp():
    try:
        humidity = dht_sensor.humidity
        temperature = dht_sensor.temperature
        return humidity, temperature
    except RuntimeError as error:
        print(f"Error reading DHT22 sensor: {error.args[0]}")
        return None, None

def read_pad_temperature():
    try:
        with open(device_file, 'r') as f:
            lines = f.readlines()
            temp_output = lines[1].find('t=')
            if temp_output != -1:
                temp_string = lines[1].strip()[temp_output + 2:]
                temp_celsius = float(temp_string) / 1000.0
                return temp_celsius
    except Exception as e:
        print(f"Error reading pad temperature: {e}")
        return None

def activate_pad():
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    print("Pad activated.")

def deactivate_pad():
    GPIO.output(RELAY_PIN, GPIO.LOW)
    print("Pad deactivated.")

def update_readings():
    humidity, ambient_temp = read_humidity_and_temp()
    pad_temp = read_pad_temperature()

    if humidity is not None and ambient_temp is not None:
        humidity_label.config(text=f"Humedad: {humidity:.2f}%")
        ambient_temp_label.config(text=f"Temperatura Ambiente: {ambient_temp:.2f}°C")
    
    if pad_temp is not None:
        pad_temp_label.config(text=f"Temperatura del Pad: {pad_temp:.2f}°C")
    
    root.after(2000, update_readings)  # Actualizar cada 2 segundos

# Configuración de la UI
root = tk.Tk()
root.title("Lecturas de Sensores")

# Labels para mostrar las lecturas
humidity_label = tk.Label(root, text="Humedad: ---")
humidity_label.pack()

ambient_temp_label = tk.Label(root, text="Temperatura Ambiente: ---")
ambient_temp_label.pack()

pad_temp_label = tk.Label(root, text="Temperatura del Pad: ---")
pad_temp_label.pack()

# Botones para controlar el relé
btn_activate_pad = tk.Button(root, text="Activar Almohadilla", command=activate_pad)
btn_activate_pad.pack()

btn_deactivate_pad = tk.Button(root, text="Desactivar Almohadilla", command=deactivate_pad)
btn_deactivate_pad.pack()

# Iniciar la actualización de lecturas
update_readings()

# Iniciar el loop de la UI
try:
    root.mainloop()
finally:
    GPIO.cleanup()
