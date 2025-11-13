import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib3
import re
import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import threading

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

excel_file = "Grey and Creech Printers.xlsx"
xls = pd.ExcelFile(excel_file, engine='openpyxl')
printer_id = ''

ip_info = {}
for sheet_name in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet_name, engine='openpyxl')
    if 'IP' in df.columns and 'Location' in df.columns and 'ID#' in df.columns:
        for _, row in df.iterrows():
            ip = str(row['IP']).strip()
            location = str(row['Location']).strip()
            printer_id = str(row['ID#']).strip()
            if ip != 'nan' and ip.count('.') == 3:
                ip_info[ip] = (location + ", " + sheet_name, printer_id)

def check_ink(ip):
    url = f"https://{ip}/hp/device/DeviceStatus/Index"
    try:
        response = requests.get(url, verify=False, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        location, printer_id = ip_info.get(ip, ("Unknown location", "Unknown ID"))

        low_ink = []

        def verify_ink(ink_id, color):
            element = soup.find('span', id=ink_id)
            if element:
                text = element.text.strip()
                match = re.search(r'(\d+)%', text)
                if match:
                    percentage = int(match.group(1))
                    if percentage <= 20:
                        low_ink.append(f"⚠️ {color} Ink: {percentage}%")
                elif '--%' in text or '--%*' in text:
                    low_ink.append(f"❌ {color} Ink: EMPTY or Not Detected ({text})")

        verify_ink('SupplyPLR0', 'Black')
        verify_ink('SupplyPLR1', 'Cyan')
        verify_ink('SupplyPLR2', 'Magenta')
        verify_ink('SupplyPLR3', 'Yellow')

        result = ""
        if low_ink:
            result = f"\n📍 Location: {location}\n🆔 ID: {printer_id}\n🌐 IP: {ip}\n"
            for ink in low_ink:
                result += ink + "\n"
            return result

    except requests.exceptions.RequestException:
        location, printer_id = ip_info.get(ip, ("Unknown location", "Unknown ID"))
        return f"\n📍 Location: {location}\n🆔 ID: {printer_id}\n🌐 IP: {ip}\n⚠️ Connection error: Printer not responding\n"

def check_printers_in_thread():
    def task():
        output_text.delete(1.0, tk.END)
        total = len(ip_info)
        progress_bar['maximum'] = total
        progress_bar['value'] = 0
        counter = 0
        
        # Lists to temporarily store results
        printers_ok = []
        printers_error = []
        
        # Collect results
        for ip in ip_info:
            result = check_ink(ip)
            if result:
                if "Connection error" in result:
                    printers_error.append(result)
                else:
                    printers_ok.append(result)
            counter += 1
            progress_bar['value'] = counter
            
            # Update display in real time
            output_text.delete(1.0, tk.END)
            
            # Show active printers
            if printers_ok:
                output_text.insert(tk.END, "🖨️ ACTIVE PRINTERS:\n" + "="*50 + "\n")
                for res in printers_ok:
                    output_text.insert(tk.END, res + "\n" + "-"*50 + "\n")
            
            # Show printers with errors at the end
            if printers_error:
                output_text.insert(tk.END, "\n⚠️ DISCONNECTED PRINTERS:\n" + "="*50 + "\n")
                for error in printers_error:
                    output_text.insert(tk.END, error)
                output_text.insert(tk.END, "\n" + "="*50)
            
            output_text.see(tk.END)
            window.update_idletasks()
        
        output_text.insert(tk.END, "\n\n✅ Scan complete!\n")
        output_text.see(tk.END)
    threading.Thread(target=task).start()

# Graphical Interface
window = tk.Tk()
window.title("Printer Ink Level Monitor")

# Main frame with padding
main_frame = ttk.Frame(window, padding="10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Frame for header with logo and button
top_frame = ttk.Frame(main_frame)
top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
top_frame.columnconfigure(1, weight=1)  # Make the middle column expandable

# Load and display logo on the left
try:
    logo_img = Image.open("logo.png")  # Make sure you have a logo.png file
    logo_img = logo_img.resize((300, 100))  # Adjust size as needed
    logo_photo = ImageTk.PhotoImage(logo_img)
    logo_label = ttk.Label(top_frame, image=logo_photo)
    logo_label.image = logo_photo  # Keep a reference
    logo_label.grid(row=0, column=0, padx=5)
except Exception as e:
    print(f"Error loading logo: {e}")
    # Create empty space if logo can't be loaded
    logo_label = ttk.Label(top_frame, width=10)
    logo_label.grid(row=0, column=0, padx=5)

# Empty frame in the middle to push button to the right
spacer = ttk.Frame(top_frame)
spacer.grid(row=0, column=1, padx=10)

# Check button on the right side
check_button = ttk.Button(top_frame, text="Check All Printers", command=check_printers_in_thread)
check_button.grid(row=0, column=2, padx=10, pady=10)

# Progress bar
progress_bar = ttk.Progressbar(main_frame, orient='horizontal', length=500, mode='determinate')
progress_bar.grid(row=1, column=0, pady=10)

# Text area for results
output_text = scrolledtext.ScrolledText(main_frame, width=100, height=30)
output_text.grid(row=2, column=0, pady=5)

window.mainloop()