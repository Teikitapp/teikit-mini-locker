import time
import board
import adafruit_dht
import RPi.GPIO as GPIO

# Configuración de los pines
DHT_SENSOR_PIN = board.D5  # Cambia esto al pin que estás usando para el DHT22
device_file = '/sys/bus/w1/devices/28-3de10457e49d/w1_slave'  # Ruta específica del sensor DS18B20
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

try:
    while True:
        humidity, ambient_temp = read_humidity_and_temp()
        pad_temp = read_pad_temperature()

        if humidity is not None and ambient_temp is not None:
            print(f"Humidity: {humidity:.2f}%")
            print(f"Ambient Temperature: {ambient_temp:.2f}°C")

        if pad_temp is not None:
            print(f"Pad Temperature: {pad_temp:.2f}°C")

        time.sleep(2)

except KeyboardInterrupt:
    print("Program terminated.")
finally:
    GPIO.cleanup()
