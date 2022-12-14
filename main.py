from os import environ as env
# Usando a biblioteca de manipulação da API do Podio.
# Algumas alterações foram feitas para possibilitar a execução deste código
from pypodio2 import api
from pypodio2.transport import TransportException

from get_time import getHour
from podio_create_tables import createTables
from podio_insert_items import insertItems
from podio_tools import handlingPodioError

import time

from logging_tools import logger

if __name__ == '__main__':
    # Período de atualização do banco
    timeOffset = int(env.get('TIMEOFFSET'))

    # Recuperando as variáveis de ambiente e guardando
    client_id = env.get('PODIO_CLIENT_ID')
    client_secret = env.get('PODIO_CLIENT_SECRET')
    username = env.get('PODIO_USERNAME')
    password = env.get('PODIO_PASSWORD')
    # Apps IDs
    apps_ids = list(map(int, env.get('PODIO_APPS_IDS').split(',')))

    message = "==== PODIO API PYTHON SCRIPT ===="
    logger.info(message)
    # Autenticando na plataforma do Podio com as credenciais recuperadas acima
    try:
        podio = api.OAuthClient(
            client_id,
            client_secret,
            username,
            password
        )
    # Caso haja erro, provavelmente o token de acesso a API expirou.
    except TransportException as err:
        handled = handlingPodioError(err)
        if handled == 'status_400':
            logger.error("Terminando o programa.")
        exit(1)
    else:
        cycle = 1
        while True:
            message = f"==== Ciclo {cycle} ===="
            logger.info(message)
            creation = createTables(podio, apps_ids)
            if creation == 0:
                insertion = insertItems(podio, apps_ids)
                # Caso o limite de requisições seja atingido, espera-se mais 1 hora até a seguinte iteração
                if insertion == 2:
                    hour = getHour(hours=1)
                    message = f"Esperando a hora seguinte. Até às {hour}"
                    logger.info(message)
                    time.sleep(3600)
                    try:
                        podio = api.OAuthClient(
                            client_id,
                            client_secret,
                            username,
                            password
                        )
                    except:
                        message = 'Erro na obtenção do novo cliente Podio! Tentando novamente...'
                        logger.error(message)
                elif insertion == 0:
                    # Nesse caso foi criado o primeiro snapshot do Podio no BD. Próxima iteração no dia seguinte
                    hours = getHour(hours=8)
                    message = f"Esperando as próximas {timeOffset//3600}hs. Até às {hours}"
                    logger.info(message)
                    time.sleep(timeOffset)
                    try:
                        podio = api.OAuthClient(
                            client_id,
                            client_secret,
                            username,
                            password
                        )
                    except:
                        message = 'Erro na obtenção do novo cliente Podio! Tentando novamente...'
                        logger.error(message)
                else:
                    message = "Tentando novamente..."
                    logger.info(message)
                    try:
                        podio = api.OAuthClient(
                            client_id,
                            client_secret,
                            username,
                            password
                        )
                    except:
                        message = 'Erro na obtenção do novo cliente Podio! Tentando novamente...'
                        logger.error(message)
                    time.sleep(1)
            elif creation == 2:
                hour = getHour(hours=1)
                message = f"Esperando a hora seguinte às {hour}"
                logger.info(message)
                time.sleep(3600)
                try:
                    podio = api.OAuthClient(
                        client_id,
                        client_secret,
                        username,
                        password
                    )
                except:
                    message = 'Erro na obtenção do novo cliente Podio! Tentando novamente...'
                    logger.error(message)
            elif creation == 3:
                message = "Tentando novamente..."
                logger.info(message)
                try:
                    podio = api.OAuthClient(
                        client_id,
                        client_secret,
                        username,
                        password
                    )
                except:
                    message = 'Erro na obtenção do novo cliente Podio! Tentando novamente...'
                    logger.error(message)
                time.sleep(1)
            else:
                message = f"Erro inesperado na criação/atualização do BD. Terminando o programa."
                logger.error(message)
                exit(1)
            cycle += 1
