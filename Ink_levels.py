import requests
from bs4 import BeautifulSoup
import urllib3
import re

# Desactivar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL de la página de la impresora
url = "https://192.168.4.77/hp/device/DeviceStatus/Index"  # Cambia por tu URL real

# Obtener la página ignorando SSL
response = requests.get(url, verify=False)

# Analizar el HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Buscar por ID

ink_level = soup.find('span', id='SupplyPLR0')
if ink_level:
    print("Black Ink:", ink_level.text.strip())
    
    ink_level = soup.find('span', id='SupplyPLR1')
if ink_level:
    print("Cyan Ink:", ink_level.text.strip())
    
    ink_level = soup.find('span', id='SupplyPLR2')
if ink_level:
    print("Magenta Ink:", ink_level.text.strip())
   
    ink_level = soup.find('span', id='SupplyPLR3')
if ink_level:
    print("Yellow Ink:", ink_level.text.strip())



# Función para extraer y mostrar tinta si está por debajo del 20%
def mostrar_tinta_baja(id_tinta, color):
    elemento = soup.find('span', id=id_tinta)
    if elemento:
        texto = elemento.text.strip()
        # Extraer porcentaje usando regex
        match = re.search(r'(\d+)%', texto)
        if match:
            porcentaje = int(match.group(1))
            if porcentaje < 20:
                print(f"{color} Ink: {porcentaje}%")
                
        elif '--%' in texto or '--%*' in texto:
            print(f"{color} Ink: Empty or Not Detected ({texto})")


# Verificar cada color
mostrar_tinta_baja('SupplyPLR0', 'Black')
mostrar_tinta_baja('SupplyPLR1', 'Cyan')
mostrar_tinta_baja('SupplyPLR2', 'Magenta')
mostrar_tinta_baja('SupplyPLR3', 'Yellow')
