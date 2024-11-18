from colorama import Fore, Style
from threading import Event
from .monitor import start_monitoring_thread, webhooks_carregados

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

    print_webhook_alert()
    start_monitoring()

    Event().wait()  # Espera indefinidamente até ser interrompido externamente

if __name__ == "__main__":
    main()
