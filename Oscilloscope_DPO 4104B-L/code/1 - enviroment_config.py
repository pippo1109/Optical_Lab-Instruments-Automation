import sys
import os
import subprocess
import json

# Detectar SO e definir caminhos
IS_WINDOWS = os.name == 'nt'
venv_path = os.path.join(os.path.dirname(__file__), 'Bibliotecas configuradas')

# Definir executáveis do venv baseado no SO
if IS_WINDOWS:
    pip_path = os.path.join(venv_path, 'Scripts', 'pip.exe')
    python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
    venv_bin_dir = os.path.join(venv_path, 'Scripts')
else:
    pip_path = os.path.join(venv_path, 'bin', 'pip')
    python_exe = os.path.join(venv_path, 'bin', 'python')
    venv_bin_dir = os.path.join(venv_path, 'bin')

# Criar ambiente virtual se não existir
if not os.path.exists(venv_path):
    print("Criando ambiente virtual...")
    try:
        subprocess.check_call([sys.executable, '-m', 'venv', venv_path])
        print(f"✓ Ambiente virtual criado em: {venv_path}")
    except subprocess.CalledProcessError as e:
        print(f"✗ Erro ao criar ambiente virtual: {e}")
        sys.exit(1)

print("Instalando bibliotecas...")

# bibliotecas necessárias para os scripts do osciloscópio
packages = [
    'pyvisa',
    'pyvisa-py',
    'PyUSB',
    'pillow',
    'opencv-python',
    'numpy',
    'libusb-package',
    'libusb1',
    'libusb0'
]

# checa os pacotes já instalados e instala apenas os faltantes
try:
    installed_output = subprocess.check_output([pip_path, 'list', '--format=freeze'], text=True)
    installed_packages = {line.split('==')[0].lower() for line in installed_output.splitlines() if line.strip()}
except subprocess.CalledProcessError:
    installed_packages = set()

missing_packages = [pkg for pkg in packages if pkg.lower() not in installed_packages]

if missing_packages:
    print(f"Instalando {len(missing_packages)} pacote(s)...")
    for pkg in missing_packages:
        try:
            subprocess.check_call([pip_path, 'install', pkg])
            print(f"✓ {pkg} instalado")
        except subprocess.CalledProcessError:
            print(f"✗ Erro ao instalar {pkg}, continuando...")
else:
    print('✓ Todas as bibliotecas necessárias já estão instaladas.')


# Configurar ambiente PATH
os.environ['VIRTUAL_ENV'] = venv_path
os.environ['PATH'] = venv_bin_dir + os.pathsep + os.environ.get('PATH', '')
print(f'\n✓ Virtualenv ativado no PATH: {venv_bin_dir}')
print(f'✓ Interpretador da venv: {python_exe}')

# Configurar VS Code para usar o interpretador da venv
try:
    vscode_dir = os.path.join(os.path.dirname(__file__), '..', '..', '.vscode')
    os.makedirs(vscode_dir, exist_ok=True)
    settings_file = os.path.join(vscode_dir, 'settings.json')
    
    if os.path.exists(settings_file):
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    else:
        settings = {}
    
    # Usar apenas forward slashes para compatibilidade
    python_exe_normalized = python_exe.replace('\\', '/')
    settings['python.defaultInterpreterPath'] = python_exe_normalized
    
    with open(settings_file, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)
    
    print(f'✓ VS Code configurado para usar venv')
except Exception as e:
    print(f'⚠ Aviso ao configurar VS Code: {e}')

# Verificar se um backend nativo libusb está disponível
try:
    import usb.backend.libusb1 as libusb1
    if libusb1.get_backend() is None:
        print('⚠ O PyUSB não encontrou uma biblioteca libusb-1.0 nativa.')
        print('  Instale um backend nativo como libusb-win32/libusb1 ou use Zadig no Windows.')
        print('  Também pode ser necessário instalar o driver libusb-win32 ou libusbK para o dispositivo.')
    else:
        print('✓ Backend libusb1 disponível.')
except Exception as e:
    print(f'⚠ Não foi possível verificar o backend libusb1: {e}')
    print('  Certifique-se de instalar o runtime libusb apropriado para o seu sistema.')

print('\n✓ Configuração concluída com sucesso!')
