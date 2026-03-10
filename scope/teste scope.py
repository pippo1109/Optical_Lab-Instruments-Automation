import sys
import os
import subprocess
import venv

venv_path = os.path.join(os.path.dirname(__file__), 'venv')

if sys.prefix == sys.base_prefix:
    if not os.path.exists(venv_path):
        print("Criando ambiente virtual...")
        venv.create(venv_path, with_pip=True)
    
    print("Instalando bibliotecas...")
    pip_path = os.path.join(venv_path, 'bin', 'pip')
    packages = [
        'appdirs==1.4.4',
        'attrs==23.2.0',
        'Babel==2.10.3',
        'bcc==0.29.1',
        'beautifulsoup4==4.12.3',
        'blinker==1.7.0',
        'Bottleneck==1.3.5',
        'Brlapi==0.8.5',
        'Brotli==1.1.0',
        'certifi==2023.11.17',
        'chardet==5.2.0',
        'click==8.1.6',
        'cloud-init==25.3',
        'colorama==0.4.6',
        'command-not-found==0.3',
        'configobj==5.0.8',
        'contourpy==1.0.7',
        'cryptography==41.0.7',
        'cssselect==1.2.0',
        'cupshelpers==1.0',
        'cycler==0.11.0',
        'dbus-python==1.3.2',
        'decorator==5.1.1',
        'defer==1.0.6',
        'defusedxml==0.7.1',
        'distro==1.9.0',
        'distro-info==1.7+build1',
        'et-xmlfile==1.0.1',
        'fonttools==4.46.0',
        'fs==2.4.16',
        'html5lib==1.1',
        'httplib2==0.20.4',
        'idna==3.6',
        'importlib-metadata==4.12.0',
        'Jinja2==3.1.2',
        'jsonpatch==1.32',
        'jsonpointer==2.0',
        'jsonschema==4.10.3',
        'kiwisolver==0.0.0',
        'language-selector==0.1',
        'launchpadlib==1.11.0',
        'lazr.restfulclient==0.14.6',
        'lazr.uri==1.0.6',
        'louis==3.29.0',
        'lxml==5.2.1',
        'lz4==4.0.2+dfsg',
        'markdown-it-py==3.0.0',
        'MarkupSafe==2.1.5',
        'matplotlib==3.6.3',
        'mdurl==0.1.2',
        'more-itertools==10.2.0',
        'mpmath==0.0.0',
        'netaddr==0.8.0',
        'numexpr==2.9.0',
        'numpy==1.26.4',
        'oauthlib==3.2.2',
        'odfpy==1.4.2',
        'olefile==0.46',
        'openpyxl==3.1.2',
        'packaging==24.0',
        'pandas==2.1.4+dfsg',
        'pexpect==4.9.0',
        'pillow==10.2.0',
        'ptyprocess==0.7.0',
        'py-cpuinfo==9.0.0',
        'pycairo==1.25.1',
        'pycups==2.0.1',
        'pygame==2.5.2',
        'Pygments==2.17.2',
        'PyGObject==3.48.2',
        'PyJWT==2.7.0',
        'pyparsing==3.1.1',
        'pyrsistent==0.20.0',
        'pyserial==3.5',
        'python-apt==2.7.7+ubuntu5.2',
        'python-dateutil==2.8.2',
        'python-debian==0.1.49+ubuntu2',
        'pytz==2024.1',
        'pyxdg==0.28',
        'PyYAML==6.0.1',
        'requests==2.31.0',
        'rich==13.7.1',
        'SciPy==1.11.4',
        'screen-resolution-extra==0.0.0',
        'setuptools==68.1.2',
        'six==1.16.0',
        'soupsieve==2.5',
        'ssh-import-id==5.11',
        'sympy==1.12',
        'systemd-python==235',
        'tables==3.9.2',
        'tabulate==0.8.10',
        'ubuntu-drivers-common==0.0.0',
        'ubuntu-pro-client==8001',
        'ufoLib2==0.16.0',
        'ufw==0.36.2',
        'unattended-upgrades==0.1',
        'urllib3==2.0.7',
        'wadllib==1.3.6',
        'webencodings==0.5.1',
        'wheel==0.42.0',
        'wxPython==4.2.1',
        'xdg==5',
        'xkit==0.0.0',
        'zipp==1.0.0'
    ]
    subprocess.check_call([pip_path, 'install'] + packages)
    
    python_path = os.path.join(venv_path, 'bin', 'python')
    subprocess.check_call([python_path, __file__])
    sys.exit(0)

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
        with open("scope/captura.bmp", "wb") as f:
            f.write(image_bytes)
            
        # Convertendo para PNG automaticamente
        img = Image.open(BytesIO(image_bytes))
        img.save("scope/resultado_final.png")
        
        print(f"Sucesso! Imagem convertida: resultado_final.png ({len(image_bytes)} bytes)")
    else:
        print("Dados incompletos recebidos.")

except Exception as e:
    print(f"Erro: {e}")
finally:
    if 'scope' in locals(): scope.close()