from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import shutil
import subprocess

# Função para criar a pasta de configuração e log em /etc/aum/
def create_config_files():
    config_dir = '/etc/aum'
    os.makedirs(config_dir, exist_ok=True)
    
    # Copiar o arquivo webhooks.conf se ele não existir no diretório de destino
    if not os.path.exists(f"{config_dir}/webhooks.conf"):
        shutil.copy('config/webhooks.conf', f"{config_dir}/webhooks.conf")
    
    # Criar um arquivo de log vazio url_monitoring.log, se não existir
    log_file = f"{config_dir}/url_monitoring.log"
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            pass  # Cria o arquivo vazio

    # Configurar permissões para o diretório e arquivos
    os.chmod(config_dir, 0o777)  # Permissões para o diretório /etc/aum
    os.chmod(f"{config_dir}/webhooks.conf", 0o666)  # Permissões para o arquivo webhooks.conf
    os.chmod(f"{config_dir}/url_monitoring.log", 0o666)  # Permissões para o arquivo de log

# Função para configurar o serviço systemd
def setup_systemd_service():
    service_file = 'aum_monitor/systemd/aum-monitor.service'
    target_path = '/etc/systemd/system/aum-monitor.service'
    
    # Copiar o arquivo .service
    if os.path.exists(service_file):
        shutil.copy(service_file, target_path)
    else:
        raise FileNotFoundError(f"Service file not found at {service_file}")
    
    # Ajusta as permissões do arquivo de serviço
    os.chmod(target_path, 0o644)
    
    # Recarrega o systemd e habilita o serviço
    try:
        subprocess.run(['systemctl', 'daemon-reload'], check=True)
        subprocess.run(['systemctl', 'enable', 'aum-monitor.service'], check=True)
        subprocess.run(['systemctl', 'start', 'aum-monitor.service'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error setting up systemd service: {e}")
        raise

# Classe de instalação personalizada para executar o script pós-instalação
class CustomInstallCommand(install):
    def run(self):
        install.run(self)  # Executa o processo padrão de instalação
        create_config_files()  # Cria os arquivos de configuração e log
        setup_systemd_service()  # Configura o serviço systemd

# Configuração do setup.py
setup(
    name='aum',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        # Dependências aqui (ex: 'requests', 'pyfiglet', etc.)
    ],
    entry_points={
        'console_scripts': [
            'aum=aum.aum:main',  # Permite rodar o programa com o comando 'aum'
            'aum-daemon=aum.daemon:main',  # Configura o comando 'aum-daemon'
        ]
    },
    data_files=[
        ('/etc/aum', ['config/webhooks.conf']),  # Inclui o arquivo de configuração no build
    ],
    cmdclass={
        'install': CustomInstallCommand,  # Usa a classe personalizada durante a instalação
    },
)
