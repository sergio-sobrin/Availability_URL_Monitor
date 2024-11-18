import os
import shutil

# Função para remover arquivos de configuração
def remove_config_files():
    config_dir = '/etc/aum'
    if os.path.exists(config_dir):
        shutil.rmtree(config_dir)  # Remove o diretório e seu conteúdo

if __name__ == "__main__":
    remove_config_files()
    print("Arquivos de configuração e logs do AUM foram removidos.")
