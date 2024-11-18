from pyfiglet import Figlet
from colorama import Fore, Style
import random
from .monitor import start_monitoring_thread, webhooks_carregados
from .url_manager import run_single_check, view_urls, add_url, edit_url, remove_url

# Boas-vindas em cores aleatórias
def print_welcome_message():
    fig = Figlet(font='small')
    ascii_art = fig.renderText('Availability URL Monitor!')
    
    colors = [Fore.BLUE, Fore.GREEN, Fore.CYAN, Fore.MAGENTA] # Lista de cores possíveis
    
    selected_color = random.choice(colors) # Randomiza as cores
    
    print(selected_color + ascii_art + Style.RESET_ALL)

# Mensagem de alerta de webhook não configurado
def print_webhook_alert():
    if not webhooks_carregados:
        print(Fore.RED + "[!] Nenhum webhook configurado. Notificações não serão enviadas.\n" + Style.RESET_ALL)

# Iniciar o monitoramento ao executar o programa
def start_monitoring():
    print("Monitoring...")
    start_monitoring_thread()

def main_menu():
    while True:
        print("\n--- Menu Principal ---")
        print("1. Rodar verificação manual")
        print("2. Visualizar URLs")
        print("3. Adicionar URL")
        print("4. Editar URL")
        print("5. Remover URL")
        print("0. Sair")

        choice = input("Escolha uma opção: ").strip()

        if choice == "1":
            run_single_check()

        elif choice == "2":
            view_urls()

        elif choice == "3":
            add_url()

        elif choice == "4":
            edit_url()

        elif choice == "5":
            remove_url()

        elif choice == "0":
            print("\nBye...")
            break

        else:
            print("Opção inválida. Tente novamente.")

def main():
    # Exibe a mensagem de boas-vindas com cor aleatória
    print_welcome_message()

    # Exibe o alerta de webhook, se necessário
    print_webhook_alert()

    # Inicia o monitoramento
    start_monitoring()

    # Chama o menu principal
    main_menu()

if __name__ == "__main__":
    main()
