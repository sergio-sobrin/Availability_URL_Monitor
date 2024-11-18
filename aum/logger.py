import logging

# Configuração do logging
logging.basicConfig(
    filename='url_monitoring.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S'
)

# Função para registrar eventos de erro
def log_error(url, error_type):
    logging.error(f"URL {url} caiu com o erro: {error_type}")

# Função para registrar quando a URL volta
def log_recovery(url, downtime):
    downtime = int(downtime)
    logging.info(f"URL {url} voltou após {downtime} segundos.")
