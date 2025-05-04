import adafruit_dht
import board
import time

# Configurar el sensor DHT22 en el pin GPIO correspondiente
dht_device = adafruit_dht.DHT22(board.D5)  # Usa el pin GPIO que corresponde

def read_humidity_and_temp():
    try:
        # Leer la humedad y la temperatura
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        return humidity, temperature
    except RuntimeError as error:
        print(f"Error reading from DHT22: {error}")
        return None, None

def main():
    print("Starting sensor readings. Press Ctrl+C to exit.")
    while True:
        humidity, temperature = read_humidity_and_temp()

        if humidity is not None and temperature is not None:
            print(f"Humidity: {humidity:.2f}%, Temperature: {temperature:.2f}°C")
        else:
            print("Failed to retrieve data from humidity sensor")

        time.sleep(2)  # Esperar 2 segundos antes de la siguiente lectura

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
