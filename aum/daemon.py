from pyfiglet import Figlet
from colorama import Fore, Style
import random
from threading import Event  # Importa o Event correto para o uso síncrono
from .monitor import start_monitoring_thread, webhooks_carregados
from .url_manager import run_single_check, view_urls, add_url, edit_url, remove_url

# Função para exibir a arte ASCII de boas-vindas com cor aleatória
def print_welcome_message():
    fig = Figlet(font='small')
    ascii_art = fig.renderText('Availability URL Monitor!')
    
    colors = [Fore.BLUE, Fore.GREEN, Fore.CYAN, Fore.MAGENTA]
    selected_color = random.choice(colors)
    
    print(selected_color + ascii_art + Style.RESET_ALL)

# Função para exibir mensagem de alerta de webhook não configurado
def print_webhook_alert():
    if not webhooks_carregados:
        print(Fore.RED + "[!] Nenhum webhook configurado. Notificações não serão enviadas.\n" + Style.RESET_ALL)

# Função para iniciar o monitoramento
def start_monitoring():
    print("Monitoring...")
    start_monitoring_thread()

# Menu principal
def main():
    print_welcome_message()
    print_webhook_alert()
    start_monitoring()

    # Coloca o programa em espera sem consumir CPU
    Event().wait()  # Espera indefinidamente até ser interrompido externamente

if __name__ == "__main__":
    main()
