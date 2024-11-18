import json
import os
from .monitor import run_single_monitoring

# Caminho absoluto para o arquivo de URLs
url_file = "/etc/aum/urls.json"
webhook_file = "/etc/aum/webhooks.conf"

# Função para carregar URLs do arquivo JSON
def load_urls():
    if os.path.exists(url_file):
        with open(url_file, "r") as file:
            return json.load(file)
    return []

# Função para salvar URLs no arquivo JSON
def save_urls(urls):
    with open(url_file, "w") as file:
        json.dump(urls, file, indent=4)

# Função para garantir que a URL comece com "https://"
def ensure_https(url):
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url

# Função para carregar webhooks de um arquivo de configuração no formato [alias]\nurl = <url>
def load_webhooks():
    webhooks = {}
    if os.path.exists(webhook_file):
        with open(webhook_file, "r") as file:
            alias = None
            for line in file:
                line = line.strip()
                if line.startswith("[") and line.endswith("]"):
                    alias = line[1:-1]
                elif line.startswith("url = ") and alias:
                    webhooks[alias] = line.split("=", 1)[1].strip()
                    alias = None  # Reset para próximo alias
    return webhooks

# Função para salvar um novo webhook no arquivo de configuração no formato [alias]\nurl = <url>
def save_webhook(alias, url):
    with open(webhook_file, "a") as file:
        file.write(f"\n[{alias}]\nurl = {url}\n")

# Função para rodar uma verificação única de monitoramento
def run_single_check():
    while True:
        urls = load_urls()  # Carrega as URLs antes de chamar `run_single_monitoring`
        run_single_monitoring(urls)  # Passa as URLs como argumento

        choice = input("Deseja rodar novamente (1) ou voltar ao menu (2)? ").strip()
        if choice == "2":
            break
        elif choice != "1":
            print("Opção inválida. Tente novamente.")

# Função para visualizar todas as URLs e seus aliases
def view_urls():
    urls = load_urls()
    print("URLs monitoradas:")
    for i, entry in enumerate(urls, start=1):
        if isinstance(entry, dict) and 'url' in entry and 'webhook' in entry:
            print(f"{i}. URL: {entry['url']}, Webhook Alias: {entry['webhook']}")
        else:
            print(f"Erro: entrada inválida encontrada no índice {i} - {entry}")

# Função para adicionar URLs
def add_url():
    print("Escolha uma opção:")
    print("1. Adicionar uma nova URL manualmente")
    print("2. Carregar URLs de um arquivo (txt ou json)")
    print("Digite '0' para cancelar e voltar ao menu.")

    choice = input("Opção: ").strip()
    if choice == "0":
        print("Operação cancelada. Retornando ao menu principal.")
        return

    urls = load_urls()
    webhooks = load_webhooks()

    if choice == "1":
        url = input("Digite a URL que deseja adicionar: ").strip()
        url = ensure_https(url.lower())

        # Exibe os webhooks existentes e dá a opção de criar um novo
        if webhooks:
            print("Escolha um alias de webhook existente ou crie um novo:")
            for i, alias in enumerate(webhooks.keys(), 1):
                print(f"{i}. {alias} -> {webhooks[alias]}")
            print(f"{len(webhooks) + 1}. Criar um novo alias de webhook")

            choice = input(f"Digite o número da opção desejada (1-{len(webhooks) + 1}): ").strip()
            if choice == str(len(webhooks) + 1):
                webhook_alias = input("Digite o alias do novo webhook: ").strip()
                webhook_url = input("Digite a URL do novo webhook: ").strip()
                save_webhook(webhook_alias, webhook_url)
                webhooks[webhook_alias] = webhook_url
            else:
                try:
                    webhook_alias = list(webhooks.keys())[int(choice) - 1]
                except (ValueError, IndexError):
                    print("Opção inválida. Retornando ao menu.")
                    return
        else:
            # Nenhum webhook configurado; cria um novo webhook
            print("Nenhum webhook configurado. Criando um novo webhook.")
            webhook_alias = input("Digite o alias do novo webhook: ").strip()
            webhook_url = input("Digite a URL do novo webhook: ").strip()
            save_webhook(webhook_alias, webhook_url)
            webhooks[webhook_alias] = webhook_url

        # Adiciona a URL com o alias de webhook selecionado
        urls.append({"url": url, "webhook": webhook_alias})
        save_urls(urls)
        print("URL e webhook associados com sucesso!")

    elif choice == "2":
        file_path = input("Digite o caminho do arquivo (txt ou json): ").strip()
        if not os.path.exists(file_path):
            print("Arquivo não encontrado.")
            return

        new_urls = []
        if file_path.endswith(".txt"):
            with open(file_path, "r") as file:
                for line in file:
                    url = ensure_https(line.strip().lower())
                    print("Escolha um alias de webhook existente:")
                    for i, alias in enumerate(webhooks.keys(), 1):
                        print(f"{i}. {alias} -> {webhooks[alias]}")

                    webhook_choice = input(f"Digite o número do alias de webhook (1-{len(webhooks)}): ").strip()
                    try:
                        webhook_alias = list(webhooks.keys())[int(webhook_choice) - 1]
                    except (ValueError, IndexError):
                        print("Opção inválida. Retornando ao menu.")
                        return
                    new_urls.append({"url": url, "webhook": webhook_alias})

        elif file_path.endswith(".json"):
            with open(file_path, "r") as file:
                try:
                    data = json.load(file)
                    if isinstance(data, dict):
                        for url, webhook_alias in data.items():
                            url = ensure_https(url.lower())
                            if webhook_alias not in webhooks:
                                webhook_url = input(f"Digite a URL do webhook para '{webhook_alias}': ").strip()
                                save_webhook(webhook_alias, webhook_url)
                                webhooks[webhook_alias] = webhook_url
                            new_urls.append({"url": url, "webhook": webhook_alias})
                    else:
                        print("O arquivo JSON deve conter URLs e aliases.")
                        return
                except json.JSONDecodeError:
                    print("Erro ao ler o arquivo JSON.")
                    return

        urls.extend(new_urls)
        save_urls(urls)
        print(f"{len(new_urls)} novas URLs foram adicionadas com sucesso!")
    else:
        print("Opção inválida. Tente novamente.")

# Função para editar uma URL existente
# Função para editar uma URL existente
def edit_url():
    urls = load_urls()
    if not urls:
        print("Nenhuma URL para editar.")
        return

    query = input("Digite uma parte da URL para filtrar (ou pressione Enter para ver todas): ").strip()
    filtered_urls = [(i, url_entry) for i, url_entry in enumerate(urls) if query in url_entry['url']] if query else list(enumerate(urls))

    if not filtered_urls:
        print(f"Nenhuma URL encontrada para a pesquisa: {query}")
        return

    print("URLs correspondentes:")
    for i, (original_index, url_entry) in enumerate(filtered_urls, 1):
        print(f"{i}. URL: {url_entry['url']}, Webhook Alias: {url_entry['webhook']}")

    index = input("Digite o número da URL que deseja editar (ou '0' para cancelar): ").strip()
    if index == "0":
        print("Edição cancelada. Retornando ao menu principal.")
        return

    try:
        original_index = int(index) - 1
        if 0 <= original_index < len(urls):
            # Editar URL (se necessário)
            new_url = input("Digite a nova URL (ou pressione Enter para manter a atual): ").strip()
            if new_url:
                urls[original_index]['url'] = ensure_https(new_url)

            # Oferecer a opção de editar apenas o webhook
            webhooks = load_webhooks()
            print("Escolha um alias de webhook existente ou digite um novo para associar à URL:")

            # Exibir webhooks existentes
            for i, alias in enumerate(webhooks.keys(), 1):
                print(f"{i}. {alias} -> {webhooks[alias]}")

            # Adicionar nova opção para inserir um novo webhook
            print(f"{len(webhooks) + 1}. Criar um novo alias de webhook")

            webhook_choice = input(f"Digite o número da opção desejada (1-{len(webhooks) + 1}): ").strip()
            if webhook_choice == str(len(webhooks) + 1):
                # Criar novo webhook
                new_alias = input("Digite o alias do novo webhook: ").strip()
                new_webhook_url = input("Digite a URL do novo webhook: ").strip()
                save_webhook(new_alias, new_webhook_url)
                webhooks[new_alias] = new_webhook_url
                urls[original_index]['webhook'] = new_alias
            else:
                try:
                    new_alias = list(webhooks.keys())[int(webhook_choice) - 1]
                    if new_alias != urls[original_index]['webhook']:
                        urls[original_index]['webhook'] = new_alias
                except (ValueError, IndexError):
                    print("Opção inválida. Retornando ao menu.")
                    return

            save_urls(urls)
            print("URL e alias de webhook atualizados com sucesso!")
        else:
            print("Número inválido.")
    except ValueError:
        print("Entrada inválida. Por favor, insira um número ou '0' para cancelar.")

# Função para remover URLs
def remove_url():
    urls = load_urls()
    if not urls:
        print("Nenhuma URL para remover.")
        return

    query = input("Digite uma parte da URL para filtrar (ou pressione Enter para ver todas): ").strip()
    filtered_urls = [(i, url_entry) for i, url_entry in enumerate(urls) if query in url_entry['url']] if query else list(enumerate(urls))

    if not filtered_urls:
        print(f"Nenhuma URL encontrada para a pesquisa: {query}")
        return

    print("URLs correspondentes:")
    for i, (original_index, url_entry) in enumerate(filtered_urls, 1):
        print(f"{i}. URL: {url_entry['url']}, Webhook Alias: {url_entry['webhook']}")

    index = input("Digite o número da URL que deseja remover (ou '0' para cancelar): ").strip()
    if index == "0":
        print("Remoção cancelada. Retornando ao menu principal.")
        return

    try:
        original_index = int(index) - 1
        if 0 <= original_index < len(urls):
            del urls[original_index]
            save_urls(urls)
            print("URL removida com sucesso!")
        else:
            print("Número inválido.")
    except ValueError:
        print("Entrada inválida. Por favor, insira um número ou '0' para cancelar.")

# Função de menu principal
def main():
    while True:
        print("\nMenu Principal")
        print("1. Rodar monitoramento manual")
        print("2. Ver URLs monitoradas")
        print("3. Adicionar URL")
        print("4. Editar URL")
        print("5. Remover URL")
        print("6. Sair")

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
        elif choice == "6":
            print("Saindo do programa...")
            break
        else:
            print("Opção inválida. Tente novamente.")
