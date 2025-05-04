import time
import os
import glob

# Configuración de los archivos del sensor DS18B20
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Ruta al archivo del sensor DS18B20
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    """Lee los datos crudos del sensor DS18B20"""
    with open(device_file, 'r') as f:
        lines = f.readlines()
    return lines

def read_temp():
    """Lee la temperatura del sensor DS18B20"""
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def main():
    print("Starting temperature readings. Press Ctrl+C to exit.")
    while True:
        temperature = read_temp()
        print(f"Temperature: {temperature:.2f}°C")
        time.sleep(2)  # Esperar 2 segundos antes de la siguiente lectura

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
