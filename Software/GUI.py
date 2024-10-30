import serial
import tkinter as tk
from tkinter import messagebox
import json
import os

json_file_path = r"C:\RP2040 code for thesis\rfid_data.json"

def load_json():
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as file:
            return json.load(file)
    return {}

def save_json(data):
    with open(json_file_path, "w") as file:
        json.dump(data, file, indent=4)

def show_all_data():
    data = load_json()
    text_area.delete(1.0, tk.END) 
    if data:
        for rfid, info in data.items():
            text_area.insert(tk.END, f"RFID: {rfid}\n")
            text_area.insert(tk.END, f"Name: {info.get('Plant_Name')}\n")
            text_area.insert(tk.END, f"Date: {info.get('Plant_Date')}\n")
            text_area.insert(tk.END, "-" * 40 + "\n")
    else:
        text_area.insert(tk.END, "No data available.\n")

def add_data():
    rfid = entry_rfid.get().strip()
    name = entry_name.get().strip()
    date = entry_date.get().strip()

    if not rfid or not name or not date:
        messagebox.showwarning("Input Error", "All fields are required!")
        return

    data = load_json()

    if rfid in data:
        messagebox.showerror("Duplicate Error", "RFID already exists!")
        return

    data[rfid] = {
        "Plant_Name": name,
        "Plant_Date": date
    }

    save_json(data)
    messagebox.showinfo("Success", "Data added successfully!")
    
    entry_rfid.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_date.delete(0, tk.END)
    
    show_all_data()

def delete_data():
    rfid_to_delete = entry_delete_rfid.get().strip()

    if not rfid_to_delete:
        messagebox.showwarning("Input Error", "Please enter an RFID UID to delete!")
        return

    data = load_json()

    if rfid_to_delete not in data:
        messagebox.showerror("Not Found", "RFID UID not found!")
        return

    del data[rfid_to_delete]

    save_json(data)
    messagebox.showinfo("Success", f"RFID {rfid_to_delete} deleted successfully!")
    
    entry_delete_rfid.delete(0, tk.END)
    show_all_data()

# Function to send the JSON data via serial port
def send_json():
    com_port = entry_com_port.get().strip() 
    data = load_json()
    
    if not com_port:
        messagebox.showwarning("Input Error", "Please enter a COM Port!")
        return
    
    if not data:
        messagebox.showwarning("Data Error", "No data to send!")
        return

    start_symbol = "<"         
    end_symbol = ">"              
    json_message = json.dumps(data)
    full_message = f"{start_symbol}{json_message}{end_symbol}"

    try:
        ser = serial.Serial(com_port, 115200, timeout=1)
        ser.write(full_message.encode())
        ser.close()
        messagebox.showinfo("Success", "JSON data sent successfully!") 

    except serial.SerialException as e:
        messagebox.showerror("Error", f"Failed to open COM port: {e}") 

root = tk.Tk()
root.title("RFID Tag Manager")
root.geometry("700x600")

left_frame = tk.Frame(root)
left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

label_rfid = tk.Label(left_frame, text="RFID:")
label_rfid.grid(row=0, column=0, pady=5, sticky="w")
entry_rfid = tk.Entry(left_frame, width=30)
entry_rfid.grid(row=0, column=1, pady=5)

label_name = tk.Label(left_frame, text="Plant Name:")
label_name.grid(row=1, column=0, pady=5, sticky="w")
entry_name = tk.Entry(left_frame, width=30)
entry_name.grid(row=1, column=1, pady=5)

label_date = tk.Label(left_frame, text="Plant Date (YYYY-MM-DD):")
label_date.grid(row=2, column=0, pady=5, sticky="w")
entry_date = tk.Entry(left_frame, width=30)
entry_date.grid(row=2, column=1, pady=5)

add_button = tk.Button(left_frame, text="Add Data", command=add_data)
add_button.grid(row=3, columnspan=2, pady=10)

label_delete_rfid = tk.Label(left_frame, text="Enter RFID UID to Delete:")
label_delete_rfid.grid(row=4, column=0, pady=5, sticky="w")
entry_delete_rfid = tk.Entry(left_frame, width=30)
entry_delete_rfid.grid(row=4, column=1, pady=5)

delete_button = tk.Button(left_frame, text="Delete Data", command=delete_data)
delete_button.grid(row=5, columnspan=2, pady=10)

label_com_port = tk.Label(left_frame, text="COM Port:")
label_com_port.grid(row=6, column=0, pady=5, sticky="w")
entry_com_port = tk.Entry(left_frame, width=30)
entry_com_port.grid(row=6, column=1, pady=5)

send_button = tk.Button(left_frame, text="Send JSON via COM", command=send_json)
send_button.grid(row=7, columnspan=2, pady=10)

right_frame = tk.Frame(root)
right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

label_all_data = tk.Label(right_frame, text="All stored RFID tags' UID and messages")
label_all_data.pack(pady=5)
text_area = tk.Text(right_frame, height=20, width=40)
text_area.pack(pady=5)

show_all_data()

root.mainloop()

