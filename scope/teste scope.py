import pyvisa
import time
from io import BytesIO
from PIL import Image

RESOURCE_NAME = 'USB0::1689::1049::C030475::0::INSTR'
rm = pyvisa.ResourceManager('@py')

try:
    scope = rm.open_resource(RESOURCE_NAME)
    # Aumentamos o chunk_size para não truncar a leitura
    scope.chunk_size = 1024 * 1024 # 1MB
    scope.timeout = 1000

    print("Configurando osciloscópio...")
    scope.write('HARDCOPY:PORT USB')
    scope.write('HARDCOPY:FORMAT BMP')
    
    print("Solicitando imagem...")
    scope.write('HARDCOPY START')
    time.sleep(1)

    # Lendo os dados brutos
    raw_data = scope.read_raw()
    
    # O manual explica que os dados vem como #<num_digits><length><data>
    # Localizamos o 'BM' para ignorar o cabeçalho do protocolo
    if b'BM' in raw_data:
        offset = raw_data.find(b'BM')
        image_bytes = raw_data[offset:]
        
        # Salvando o BMP original
        with open("captura.bmp", "wb") as f:
            f.write(image_bytes)
            
        # Convertendo para PNG automaticamente
        img = Image.open(BytesIO(image_bytes))
        img.save("resultado_final.png")
        
        print(f"Sucesso! Imagem convertida: resultado_final.png ({len(image_bytes)} bytes)")
    else:
        print("Dados incompletos recebidos.")

except Exception as e:
    print(f"Erro: {e}")
finally:
    if 'scope' in locals(): scope.close()