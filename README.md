# HP Printer Ink Level Monitor

A Python CLI tool to monitor ink levels across multiple HP printers on your network. Scans all printers in parallel and exports results to JSON.

## Features

- 🖨️ **Parallel Scanning**: Checks all printers simultaneously for maximum speed
- 📊 **JSON Export**: Results saved in structured JSON format
- ⚡ **Fast**: Configurable timeout (default 2.5s) for quick network scanning
- 📋 **Excel Configuration**: Load printer inventory from Excel file
- 🔌 **Network Detection**: Identifies connected and disconnected printers
- ⚠️ **Low Ink Alerts**: Detects cartridges with ≤20% ink remaining

## Requirements

- Python 3.7+
- Network access to HP printers (HTTPS port 443)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/hp-printer-monitor.git
cd hp-printer-monitor
```

2. Create a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
source .venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. **Prepare your printer Excel file** with columns:
   - `IP`: Printer IP address
   - `Location`: Physical location
   - `ID#`: Printer ID
   - `Model` (optional): Printer model

2. **Create a config file** (optional):
   ```bash
   echo "path/to/your/printers.xlsx" > printer_config.txt
   ```
   Or place your Excel file as `Grey and Creech Printers.xlsx` in the script directory.

## Usage

Run the scanner:
```bash
python aaa_godhelpme.py
```

This will:
1. Load printer data from Excel
2. Scan all 55+ printers in parallel
3. Generate `printer_status.json` with results
4. Display progress in terminal

### Output Example

```json
{
  "active_printers": [
    "\n📍 Location: Floor 2, Office\n🆔 ID: P001\n🌐 IP: 192.168.1.100\n🖨️Model: HP LaserJet Pro\n⚠️ Black Ink: 15%\n"
  ],
  "disconnected_printers": [
    "\n📍 Location: Floor 3, Break Room\n🆔 ID: P023\n🌐 IP: 192.168.1.200\n🖨️Model: HP OfficeJet\n⚠️ Connection error: Printer not responding\n"
  ],
  "summary": {
    "total_printers": 55,
    "active": 30,
    "disconnected": 25
  }
}
```

## Configuration Options

### Adjust Number of Workers

Edit the main section to change parallel workers:
```python
check_printers("printer_status.json", max_workers=55)  # All at once (faster)
check_printers("printer_status.json", max_workers=20)  # Conservative
```

### Adjust Timeout

Modify the `check_ink()` function timeout parameter (currently 2.5s).

## Error Handling

- **Timeout errors**: Printer not reachable within 2.5 seconds
- **Connection errors**: Network unreachable or printer offline
- **Invalid IPs**: Non-standard IP addresses filtered automatically

## License

MIT License - See LICENSE file for details

## Author

Created for efficient HP printer inventory management across networked environments.

## Support

For issues or feature requests, please open a GitHub issue.
