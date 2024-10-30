import time
from machine import UART

class Bluetooth:
    def __init__(self, tx_pin, rx_pin, baudrate=9600):
        self.uart = UART(1, baudrate=baudrate, tx=tx_pin, rx=rx_pin)
        self.buffer = bytearray()

    def send_command(self, command, timeout=1000):
        self.uart.write(command + '\r\n')
        self.buffer = bytearray()
        start = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start) < timeout:
            if self.uart.any():
                self.buffer.extend(self.uart.read())
        return self.buffer.decode('utf-8').strip()

    def init_module(self):
        response = self.send_command('AT')
        if 'OK' in response:
            print("Bluetooth module initialized successfully.")
        else:
            print("Failed to initialize Bluetooth module.")

    def set_name(self, name):
        response = self.send_command(f'AT+NAME={name}')
        if 'OK' in response:
            print(f"Bluetooth name set to {name}.")
        else:
            print("Failed to set Bluetooth name.")

    def get_name(self):
        response = self.send_command('AT+BLENAME?')
        if response:
            for line in response.split('\n'):
                if '+BLENAME:' in line:
                    name = line.split(':')[1].strip()
                    print(f"Bluetooth name is: {name}")
                    return name
        print("Failed to get Bluetooth name.")
        return None

    def reset(self):
        response = self.send_command('AT+RST')
        if 'OK' in response:
            print("Bluetooth module reset successfully.")
        else:
            print("Failed to reset Bluetooth module.")

    def ble_init(self):
        response = self.send_command('AT+BLEINIT=2')
        if 'OK' in response:
            print("BLE initialized successfully.")
        else:
            print("Failed to initialize BLE.")
        time.sleep(1)

    def ble_gatts_srv_cre(self):
        response = self.send_command('AT+BLEGATTSSRVCRE')
        if 'OK' in response:
            print("BLE GATT service created successfully.")
        else:
            print("Failed to create BLE GATT service.")
        time.sleep(1)

    def ble_gatts_srv_start(self):
        response = self.send_command('AT+BLEGATTSSRVSTART')
        if 'OK' in response:
            print("BLE GATT service started successfully.")
        else:
            print("Failed to start BLE GATT service.")
        time.sleep(1)

    def ble_adv_start(self):
        response = self.send_command('AT+BLEADVSTART')
        if 'OK' in response:
            print("BLE advertising started successfully.")
        else:
            print("Failed to start BLE advertising.")
        time.sleep(1)

    def enable_notify(self, handle):
        command = f"AT+BLEGATTSENABLE={handle},1"
        response = self.send_command(command)
        if 'OK' in response:
            print(f"Notification enabled for handle: {handle}")
        else:
            print(f"Failed to enable notification for handle: {handle}")

    def send_notification(self, message):
        command = f"AT+BLEGATTSNTFY=0,1,6,{len(message)+2}"
        response = self.send_command(command)
        if '>' in response:
            print("Ready to send message")
        else:
            print("Failed to initiate notification.")
        
    def check_connection_status(self):
        response = self.send_command('AT+BLECONN?')
        if '0' in response:
            return "connected" 
        else:
            return "disconnected" 

    def send_message(self, message):
        self.uart.write('\n' + message + '\n')
        print(f"Notification message sent: {message}")


