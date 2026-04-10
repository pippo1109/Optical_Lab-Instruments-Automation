import sys
import os
import subprocess
import venv

venv_path = os.path.join(os.path.dirname(__file__), 'Bibliotecas configuradas')

if sys.prefix == sys.base_prefix:
    if not os.path.exists(venv_path):
        print("Criando ambiente virtual com Python 3.12...")
        subprocess.check_call(['python3.12', '-m', 'venv', venv_path])
    
    print("Instalando bibliotecas...")
    # determine pip executable path
    if os.name == 'nt':
        pip_path = os.path.join(venv_path, 'Scripts', 'pip.exe')
    else:
        pip_path = os.path.join(venv_path, 'bin', 'pip')

    # bibliotecas necessárias para os scripts do osciloscópio
    general_packages = [
        'pyvisa',
        'pyvisa-py',
        'PyUSB',
        'pillow',
        'opencv-python',
        'numpy'
    ]

    windows_packages = [
        # sem dependências adicionais específicas do Windows
    ]

    unix_packages = [
        # sem dependências adicionais específicas do Linux/macOS
    ]

    packages = general_packages + (windows_packages if os.name == 'nt' else unix_packages)

    # checa os pacotes já instalados e instala apenas os faltantes
    try:
        installed_output = subprocess.check_output([pip_path, 'list', '--format=freeze'], text=True)
        installed_packages = {line.split('==')[0].lower() for line in installed_output.splitlines() if line.strip()}
    except subprocess.CalledProcessError:
        installed_packages = set()

    missing_packages = [pkg for pkg in packages if pkg.split('==')[0].lower() not in installed_packages]

    if missing_packages:
        for pkg in missing_packages:
            try:
                subprocess.check_call([pip_path, 'install', pkg])
            except subprocess.CalledProcessError:
                print(f"Aviso: não foi possível instalar {pkg}, pulando...")
    else:
        print('Todas as bibliotecas necessárias já estão instaladas.')

    if os.name == 'nt':
        venv_bin_dir = os.path.join(venv_path, 'Scripts')
    else:
        venv_bin_dir = os.path.join(venv_path, 'bin')

    os.environ['VIRTUAL_ENV'] = venv_path
    os.environ['PATH'] = venv_bin_dir + os.pathsep + os.environ.get('PATH', '')
    print(f'Virtualenv ativado no PATH: {venv_bin_dir}')

    # Imprime o caminho do interpretador da venv para seleção manual
    if os.name == 'nt':
        python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
    else:
        python_exe = os.path.join(venv_path, 'bin', 'python')
    print(f'Interpretador da venv: {python_exe}')

    # Configura o VS Code para usar o interpretador da venv se existir, senão global
    vscode_dir = os.path.join(os.path.dirname(__file__), '..', '..', '.vscode')
    os.makedirs(vscode_dir, exist_ok=True)
    settings_file = os.path.join(vscode_dir, 'settings.json')
    
    import json
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            settings = json.load(f)
    else:
        settings = {}
    
    if os.path.exists(venv_path):
        settings['python.defaultInterpreterPath'] = python_exe
        print(f'VS Code configurado para usar venv: {python_exe}')
    else:
        # Remove a configuração se existir, para usar global
        settings.pop('python.defaultInterpreterPath', None)
        print('VS Code configurado para usar interpretador global (venv não encontrada)')
    
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=4)
