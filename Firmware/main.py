from machine import Pin, UART, I2C
from utime import sleep_ms
import binascii
import sys
import time
from ssd1306 import SSD1306_I2C
from bluetooth import Bluetooth
import json
import select

bluetooth_icon = [
    0b00000000, 0b00000000, 
    0b00000001, 0b10000000, 
    0b00000001, 0b11000000, 
    0b00000001, 0b01100000, 
    0b00001001, 0b00110000, 
    0b00001101, 0b00110000, 
    0b00000111, 0b01100000, 
    0b00000011, 0b11000000, 
    0b00000001, 0b10000000, 
    0b00000011, 0b11000000, 
    0b00000111, 0b01100000, 
    0b00001101, 0b00110000, 
    0b00001001, 0b00110000, 
    0b00000001, 0b01100000, 
    0b00000001, 0b11000000, 
    0b00000001, 0b10000000
]

charging_icon = [
    0b00000000, 0b00000000, 
    0b00000100, 0b00000000, 
    0b00001100, 0b00000000,
    0b00011100, 0b00000000,
    0b00111100, 0b00000000,
    0b01111111, 0b11110000, 
    0b11111111, 0b11111100,
    0b11111111, 0b11111110,
    0b01111111, 0b11111100,
    0b00000001, 0b11111000,
    0b00000001, 0b11100000, 
    0b00000001, 0b11000000,
    0b00000001, 0b10000000,
    0b00000001, 0b00000000,
    0b00000000, 0b00000000, 
    0b00000000, 0b00000000  
]

def save_json_to_file(json_data, filename="rfid_data.json"):
    try:
        with open(filename, "w") as f:
            json.dump(json_data, f)
        print(f"JSON data saved to {filename}")
    except Exception as e:
        print(f"Error saving JSON to file: {e}")

def display_message(message, x, y, clear_area=False):
    if clear_area:
        oled.fill_rect(x, y, 128, 10, 0)
    oled.text(message, x, y)
    oled.show()

def display_bluetooth_icon(x, y):
    for row in range(16):
        for col in range(16):
            byte_index = row * 2 + col // 8
            bit_index = 7 - (col % 8)
            byte = bluetooth_icon[byte_index]
            if (byte >> bit_index) & 1:
                oled.pixel(x + col, y + row, 1)
            else:
                oled.pixel(x + col, y + row, 0)
    oled.show()

def display_charging_icon(x, y):
    for row in range(16):
        for col in range(16):
            byte_index = row * 2 + col // 8
            bit_index = 7 - (col % 8)
            byte = charging_icon[byte_index]
            if (byte >> bit_index) & 1:
                oled.pixel(x + col, y + row, 1)
            else:
                oled.pixel(x + col, y + row, 0)
    oled.show()

def clear_icon(x, y):
    oled.fill_rect(x, y, 16, 16, 0)
    oled.show()

def read_uart_data(uart):
    if uart.any():
        read_data = uart.read()
        try:
            print("Origin data:", read_data)

            uid = extract_uid(read_data)
            if uid:
                print("Extracted UID:", uid)

                rfid_data = read_json_file()
                if rfid_data and uid in rfid_data:
                    plant_info = rfid_data[uid]
                    plant_name = plant_info['Plant_Name']
                    plant_date = plant_info['Plant_Date']
                    oled.fill_rect(0, 20, 128, 20, 0)
                    oled.text(f"Name:{plant_name}", 0, 20)
                    oled.text(f"Date:{plant_date}", 0, 30)
                    oled.show()
                    
                    # Send information over Bluetooth if available
                    if bluetooth_active:
                        message_to_send = f"Name: {plant_name}, Date: {plant_date}"
                        bluetooth.send_notification(message=message_to_send)
                        bluetooth.send_message(message=message_to_send)
                else:
                    print(f"UID not found: {uid}")
                    oled.fill_rect(0, 20, 128, 20, 0)
                    oled.text(f"UID {uid} not found!", 0, 20)
                    oled.show()
                    
                    # Send the UID that was not found over Bluetooth
                    if bluetooth_active:
                        message_to_send = f"UID {uid} not found"
                        bluetooth.send_notification(message=message_to_send)
                        bluetooth.send_message(message=message_to_send)

            else:
                print("No UID detected")

        except Exception as e:
            print("Error decoding UART data:", e)

            
def read_json_file():
    try:
        with open("rfid_data.json", "r") as file:
            data = json.load(file)
            return data
    except Exception as e:
        print(f"wrong read process: {e}")
        return None

def extract_uid(data):
    try:
        uid = data[1:-3] 
        return uid.decode('utf-8')
    except Exception as e:
        print("wrong extract:", e)
        return None

led = Pin(25, Pin.OUT)
i2c = I2C(1, sda=Pin(2), scl=Pin(3), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)
uart_RFID = UART(0, baudrate=9600, rx=Pin(17))
charging_pin = Pin(19, Pin.IN, Pin.PULL_UP)
bluetooth = Bluetooth(tx_pin=8, rx_pin=9, baudrate=115200)
oled.show()
bluetooth.reset()
bluetooth.init_module()
connected = False
bluetooth_active = False
charging_active = False
buffer = ""
is_reading = False
start_symbol = "<"
end_symbol = ">"
timeout_seconds = 1
start_time = time.time()
input_detected = False


rfid_data = read_json_file()

while True:
    if not input_detected:
        if not bluetooth_active:
            bluetooth_name = bluetooth.get_name()
            display_message("Bluetooth name:", 0, 45)
            display_message(bluetooth_name, 0, 55)
            display_message("Loading 0%", 0, 0)
            bluetooth.ble_init()
            display_message("Loading 25%", 0, 0, clear_area=True)
            bluetooth.ble_gatts_srv_cre()
            display_message("Loading 50%", 0, 0, clear_area=True)
            bluetooth.ble_gatts_srv_start()
            display_message("Loading 75%", 0, 0, clear_area=True)
            bluetooth.ble_adv_start()
            display_message("Loading 100%", 0, 0, clear_area=True)
            sleep_ms(1000)
            display_message("BLE Ready", 0, 0, clear_area=True)
            bluetooth_active = True
        
        status = bluetooth.check_connection_status()
        if status == "connected" and not connected:
            display_bluetooth_icon(115, 0)
            connected = True
        elif status == "disconnected" and connected:
            clear_icon(115, 0)
            connected = False
        
        charging_state = charging_pin.value()
        if charging_state == 0 and not charging_active:
            display_charging_icon(115, 0)
            charging_active = True
        elif charging_state == 1 and charging_active:
            clear_icon(100, 0)
            charging_active = False
        
        read_uart_data(uart_RFID)
    
    rlist, _, _ = select.select([sys.stdin], [], [], 0)
    if rlist:
        input_detected = True
        data = sys.stdin.read(1)
        if data:
            if data == start_symbol:
                buffer = "" 
                print("Start recording message...")
                start_time = time.time()
            elif data != end_symbol:
                buffer += data
            elif data == end_symbol:
                print("End of message. Parsing JSON data:")
                print("Received:", buffer)

                try:
                    json_data = json.loads(buffer)
                    print("Parsed JSON:", json_data)
                    for rfid, info in json_data.items():
                        plant_name = info.get("Plant_Name", "Unknown")
                        plant_date = info.get("Plant_Date", "Unknown")
                    save_json_to_file(json_data)
                    input_detected = False
                except ValueError as e:
                    print("Error parsing JSON:", e)
                    display_message("Invalid JSON", 0, 0, clear_area=True)
                led.toggle()
                buffer = ""
                
    sleep_ms(1)



