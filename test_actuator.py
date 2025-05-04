import RPi.GPIO as GPIO
import time

# Configuración de la numeración de los pines (BCM o BOARD)
GPIO.setmode(GPIO.BOARD)  # Cambia a GPIO.BCM si prefieres la numeración BCM

# Definición de los pines
PIN_FAN = 15
PIN_LOCK = 11
PIN_HEATING_PAD = 13

# Configuración de los pines como salidas y asegurarse de que inicien en HIGH (Relé desactivado)
GPIO.setup(PIN_FAN, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(PIN_LOCK, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(PIN_HEATING_PAD, GPIO.OUT, initial=GPIO.HIGH)

# Funciones para controlar cada actuador con lógica inversa
def activate_fan():
    GPIO.output(PIN_FAN, GPIO.LOW)
    print("Fan activated")

def deactivate_fan():
    GPIO.output(PIN_FAN, GPIO.HIGH)
    print("Fan deactivated")

def activate_lock():
    GPIO.output(PIN_LOCK, GPIO.LOW)
    print("Lock activated")

def deactivate_lock():
    GPIO.output(PIN_LOCK, GPIO.HIGH)
    print("Lock deactivated")

def activate_heating_pad():
    GPIO.output(PIN_HEATING_PAD, GPIO.LOW)
    print("Heating pad activated")

def deactivate_heating_pad():
    GPIO.output(PIN_HEATING_PAD, GPIO.HIGH)
    print("Heating pad deactivated")

# Función principal para interactuar con los actuadores
def control_actuators():
    try:
        while True:
            command = input("Enter a command (af/df/al/dl/ah/dh/exit): ").strip().lower()

            if command == "af":
                activate_fan()
            elif command == "df":
                deactivate_fan()
            elif command == "al":
                activate_lock()
            elif command == "dl":
                deactivate_lock()
            elif command == "ah":
                activate_heating_pad()
            elif command == "dh":
                deactivate_heating_pad()
            elif command == "exit":
                print("Exiting...")
                break
            else:
                print("Command not recognized. Please try again.")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup done.")

# Ejecutar la función principal
if __name__ == "__main__":
    control_actuators()
