# webhook.py
import requests
import configparser

# Função para carregar webhooks de um arquivo .conf
import configparser

def load_webhooks():
    config = configparser.ConfigParser()
    config_file = '/etc/aum/webhooks.conf'
    config.read(config_file)
    
    webhooks = {}
    for section in config.sections():
        webhook_url = config[section].get('url')
        if webhook_url:
            webhooks[section] = webhook_url
        else:
            print(f"[!] Webhook URL missing for alias '{section}' in webhooks.conf")
    return webhooks


# Função para enviar notificações para um webhook específico
def send_notification(webhook_name, message, webhooks):
    webhook_url = webhooks.get(webhook_name)
    if webhook_url:
        payload = {"content": message}
        try:
            requests.post(webhook_url, json=payload, timeout=10)
        except requests.RequestException as e:
            print(f"Erro ao enviar para {webhook_name}: {e}")
    else:
        print("\033[91m[!] Webhook não localizado, o alerta não será enviado!\033[0m")  # Exibe mensagem em vermelho
