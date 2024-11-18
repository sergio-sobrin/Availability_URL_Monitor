from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from datetime import datetime
import time
import json
import os
from threading import Thread
from .logger import log_error, log_recovery
from .webhook import load_webhooks, send_notification

status_anterior = {} # Dicionário para rastrear o estado anterior das URLs

url_file = "/etc/aum/urls.json" # Caminho absoluto para o arquivo .json onde as URLs são armazenadas

# Carregar webhooks do arquivo de configuração
webhooks = load_webhooks()
webhooks_carregados = bool(webhooks)
if not webhooks_carregados:
    print("Nenhum webhook configurado. Notificações não serão enviadas.")

# Carregar URLs do arquivo .json
def load_urls():
    if os.path.exists(url_file):
        with open(url_file, "r") as file:
            data = json.load(file)
            return [{"url": item['url'], "webhook": item.get('webhook')} for item in data if 'url' in item]
    return []

# Verificar o status da URL
def check_url_status(url):
    try:
        response = requests.get(url, timeout=30)
        return response.status_code
    except requests.RequestException:
        return "timeout"

def formatar_tempo_inativo(segundos):
    horas, resto = divmod(int(segundos), 3600)
    minutos, segundos = divmod(resto, 60)
    return f"{horas}h {minutos}m {segundos}s"

# Executar o monitoramento de URLs continuamente
def monitorar():
    numero_threads = 50
    intervalo = 60

    while True:
        urls = load_urls()
        total_urls = len(urls)
        ok_count = 0
        error_count = 0
        erros_por_tipo = {}

        with ThreadPoolExecutor(max_workers=numero_threads) as executor:
            future_to_url = {executor.submit(check_url_status, url['url']): url for url in urls}
            for future in as_completed(future_to_url):
                url_info = future_to_url[future]
                url = url_info['url']
                webhook_alias = url_info['webhook']

                status = future.result()

                if status == 200:
                    ok_count += 1
                    if url in status_anterior and status_anterior[url]["status"] != 200:
                        tempo_inativo = datetime.now() - status_anterior[url]["down_since"]
                        tempo_inativo_str = formatar_tempo_inativo(tempo_inativo.total_seconds())
                        mensagem_retorno = f"✅ RECOVERY - ({url}) voltou ao ar após {tempo_inativo_str}."
                        if webhooks_carregados and webhook_alias:
                            send_notification(webhook_alias, mensagem_retorno, webhooks)
                        elif not webhook_alias:
                            print("[!] webhook não localizado, o alerta não será enviado!")
                        log_recovery(url, int(tempo_inativo.total_seconds()))

                    status_anterior[url] = {"status": 200, "down_since": None}

                else:
                    error_count += 1
                    erros_por_tipo.setdefault(status, []).append(url)
                    if url not in status_anterior or status_anterior[url]["status"] == 200:
                        mensagem_erro = (
                            f"⚠️ MONITOR DOWN - ({url}) retornou erro {status}. "
                            f"Caiu em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                        )
                        if webhooks_carregados and webhook_alias:
                            send_notification(webhook_alias, mensagem_erro, webhooks)
                        elif not webhook_alias:
                            print("[!] webhook não localizado, o alerta não será enviado!")
                        log_error(url, status)

                        status_anterior[url] = {"status": status, "down_since": datetime.now()}

        time.sleep(intervalo)

# Roda uma verificação única de monitoramento
def run_single_monitoring(urls):
    numero_threads = 50
    total_urls = len(urls)
    ok_count = 0
    error_count = 0
    erros_por_tipo = {}

    with ThreadPoolExecutor(max_workers=numero_threads) as executor:
        future_to_url = {executor.submit(check_url_status, url['url']): url for url in urls}
        for future in as_completed(future_to_url):
            url_info = future_to_url[future]
            url = url_info['url']
            status = future.result()

            if status == 200:
                ok_count += 1
            else:
                error_count += 1
                erros_por_tipo.setdefault(status, []).append(url)

    # Exibindo o resumo do monitoramento
    print("\n===== Resumo da Verificação Única =====")
    print(f"Total de URLs monitoradas: {total_urls}")
    print(f"URLs OK: {ok_count}")
    print(f"URLs com erro: {error_count}")
    
    for status, urls in erros_por_tipo.items():
        print(f"\n================\n   ERRO: {status}\n================")
        for url in urls:
            print(url)
    print("===================================\n")

# Execução do monitoramento contínuo em segundo plano
def start_monitoring_thread():
    monitor_thread = Thread(target=monitorar)
    monitor_thread.daemon = True
    monitor_thread.start()

if __name__ == "__main__":
    start_monitoring_thread()
    while True:
        pass
