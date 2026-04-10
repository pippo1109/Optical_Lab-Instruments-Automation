import os
import shutil
from datetime import datetime

def save_last_images():
    # Diretórios
    source_dir = "Oscilloscope_DPO 4104B-L/images"
    dest_dir = "Oscilloscope_DPO 4104B-L/last_saved_images"

    # Cria a pasta de destino se não existir
    os.makedirs(dest_dir, exist_ok=True)

    # Arquivos a copiar
    bmp_file = os.path.join(source_dir, "captura.bmp")
    png_file = os.path.join(source_dir, "resultado_final.png")

    # Timestamp para nomes únicos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Copia BMP se existir
    if os.path.exists(bmp_file):
        dest_bmp = os.path.join(dest_dir, f"captura_{timestamp}.bmp")
        shutil.copy2(bmp_file, dest_bmp)
        print(f"BMP salvo em: {dest_bmp}")
    else:
        print("Arquivo BMP não encontrado.")

    # Copia PNG se existir
    if os.path.exists(png_file):
        dest_png = os.path.join(dest_dir, f"resultado_final_{timestamp}.png")
        shutil.copy2(png_file, dest_png)
        print(f"PNG salvo em: {dest_png}")
    else:
        print("Arquivo PNG não encontrado.")

    print("Processo concluído.")

if __name__ == "__main__":
    save_last_images()