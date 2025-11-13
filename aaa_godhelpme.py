import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib3
import re
import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import json


# Global variables
ip_info = {}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Function to get the correct path for resources
def get_excel_path():
    config_file = 'printer_config.txt'
    network_path = None
    
    # Try to read network path from config file
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                network_path = f.read().strip()
    except Exception:
        pass
    
    # Verify if network path is accessible
    if network_path and os.path.exists(network_path):
        return network_path
    else:
        # Use local file as fallback
        return "Grey and Creech Printers.xlsx"

def set_excel_path(path):
    """Set custom Excel file path in config."""
    if os.path.exists(path):
        with open('printer_config.txt', 'w') as f:
            f.write(path)
        print(f"✅ Excel path saved: {path}")
        return True
    else:
        print(f"❌ Invalid path or file not accessible: {path}")
        return False

def load_printer_data():
    global ip_info
    try:
        # Get Excel file path
        excel_file = get_excel_path()
        
        # Clear existing data
        ip_info.clear()
        
        # Read Excel file
        with pd.ExcelFile(excel_file, engine='openpyxl') as xls:
            # Load data from each sheet
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name, engine='openpyxl')
                if 'IP' in df.columns and 'Location' in df.columns and 'ID#' in df.columns:
                    # Use 'Model' if present, else fallback to sheet name
                    has_model = 'Model' in df.columns
                    for _, row in df.iterrows():
                        ip = str(row['IP']).strip()
                        location = str(row['Location']).strip()
                        printer_id = str(row['ID#']).strip()
                        model = str(row['Model']).strip() if has_model and not pd.isna(row['Model']) else sheet_name
                        if ip != 'nan' and ip.count('.') == 3:
                            ip_info[ip] = (location, printer_id, model, sheet_name)
        print(f"✅ Loaded {len(ip_info)} printers from {excel_file}")
    except Exception as e:
        print(f"❌ Error loading Excel file: {str(e)}")

def check_ink(ip):
    url = f"https://{ip}/hp/device/DeviceStatus/Index"
    try:
        response = requests.get(url, verify=False, timeout=2.5)
        soup = BeautifulSoup(response.text, 'html.parser')
        location, printer_id, model, sheet_name = ip_info.get(ip, ("Unknown location", "Unknown ID", "Unknown model", "Unknown sheet"))

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
            result = f"\n📍 Location: {location}, {sheet_name}\n🆔 ID: {printer_id}\n🌐 IP: {ip}\n🖨️Model: {model}\n"
            for ink in low_ink:
                result += ink + "\n"
            return result
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
        location, printer_id, model, sheet_name = ip_info.get(ip, ("Unknown location", "Unknown ID", "Unknown model", "Unknown sheet"))
        return f"\n📍 Location: {location}, {sheet_name}\n🆔 ID: {printer_id}\n🌐 IP: {ip}\n🖨️Model: {model}\n⚠️ Connection error: Printer not responding\n"

def check_printers(output_file="printer_status.json", max_workers=10):
    """Check all printers in parallel and export results to JSON."""
    results = {
        "active_printers": [],
        "disconnected_printers": [],
        "summary": {}
    }
    
    print(f"\n🖨️ Checking {len(ip_info)} printers in parallel ({max_workers} workers)...")
    print("=" * 60)
    
    # Lock for thread-safe appending to results
    results_lock = threading.Lock()
    checked_count = [0]  # Use list to allow modification in nested function
    
    def save_results_to_file():
        """Save current results to JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    def check_and_store(ip):
        """Check single printer and store result."""
        try:
            result = check_ink(ip)
            with results_lock:
                if result:
                    if "Connection error" in result:
                        results["disconnected_printers"].append(result)
                        status = "⚠️  Disconnected"
                    else:
                        results["active_printers"].append(result)
                        status = "✅ OK (Low ink detected)"
                else:
                    status = "✅ OK"
                
                checked_count[0] += 1
                print(f"[{checked_count[0]:02d}/{len(ip_info)}] {ip:18} - {status}")
                
                # Save results incrementally every 5 printers
                if checked_count[0] % 5 == 0 or checked_count[0] == len(ip_info):
                    save_results_to_file()
        except Exception as e:
            with results_lock:
                checked_count[0] += 1
                print(f"[{checked_count[0]:02d}/{len(ip_info)}] {ip:18} - ❌ Error: {str(e)[:40]}")
                if checked_count[0] % 5 == 0 or checked_count[0] == len(ip_info):
                    save_results_to_file()
    
    # Use ThreadPoolExecutor for parallel execution
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(check_and_store, ip) for ip in ip_info]
        for future in as_completed(futures):
            future.result()  # Wait for all threads to complete
    
    results["summary"] = {
        "total_printers": len(ip_info),
        "active": len(results["active_printers"]),
        "disconnected": len(results["disconnected_printers"])
    }
    
    # Final save with summary
    save_results_to_file()
    
    print("\n" + "=" * 60)
    print(f"✅ Scan complete!")
    print(f"📊 Summary: {results['summary']['active']} with low ink, {results['summary']['disconnected']} disconnected")
    print(f"💾 Results saved to {output_file}")
    print("=" * 60)
    return results

# CLI Main execution
if __name__ == "__main__":
    print("="*60)
    print("HP Printer Ink Level Monitor - CLI Version")
    print("="*60)
    
    # Load printer data
    load_printer_data()
    
    # Check if we have printers
    if not ip_info:
        print("\n❌ No printers found. Check your Excel file configuration.")
        sys.exit(1)
    
    # Run the scan and export to JSON
    check_printers("printer_status.json")

df = pd.read_excel("ruta/a/tu/archivo.xlsx")
data = df.to_dict(orient="records")

with open("printers.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
