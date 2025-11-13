# HP Printer Ink Level Monitor - Copilot Instructions

## Project Overview
This project is a Python-based monitoring system for HP printers that tracks ink levels across multiple network printers. The system consists of three main iterations (basic, CLI, and GUI versions) with progressively enhanced functionality.

## Core Components

### Data Sources
- Uses Excel file (`Grey and Creech Printers.xlsx`) as the printer inventory source
- Excel format requires columns: 'IP', 'Location', and 'ID#'
- Data is loaded using pandas with openpyxl engine

### Printer Communication
- Queries printer status via HTTPS endpoint: `https://{ip}/hp/device/DeviceStatus/Index`
- SSL verification is disabled due to printer self-signed certificates
- Timeout set to 5 seconds for each printer request
- Standard ink cartridge IDs:
  ```python
  SupplyPLR0: Black
  SupplyPLR1: Cyan
  SupplyPLR2: Magenta
  SupplyPLR3: Yellow
  ```

### GUI Implementation (`Test2.py`)
- Built with tkinter
- Uses threading to prevent UI freezing during printer checks
- Progress bar shows scan progress
- ScrolledText widget displays results
- Results formatted with emojis and separators for readability

## Key Patterns

### Error Handling
- Network timeouts handled with 5-second limit
- Invalid/empty IP addresses filtered during Excel import
- Non-responsive printers reported without crashing the application
- Empty cartridges detected via '--% or --%*' patterns

### Data Processing
- IP validation using dot count: `ip.count('.') == 3`
- Ink percentage extraction using regex: `r'(\d+)%'`
- Low ink threshold set at 20%

## Required Dependencies
```
pandas
requests
beautifulsoup4
urllib3
openpyxl
tkinter (built-in)
```

## Development Guidelines
1. Always maintain compatibility with the Excel data source format
2. Preserve the emoji-based status indicators for consistency
3. Keep SSL verification disabled for printer communication
4. Use threading for network operations in GUI version
5. Maintain consistent ink level threshold (20%) across implementations