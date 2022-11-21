import requests
import json

from pandas import DataFrame
import numpy as np
from utilities import unpack_dictionary, COUNTRY_CODE


class RandomUserAPI():
    _source_API = "https://randomuser.me/api/"

    def __init__(self) -> None:
        self.blacklist = [] # Parametros a serem excluidos
        self.nat = [] # especifica a naturalidade, padrao é todos
        pass

    def update_nat(self, nat):
        '''
        Atualiza a nacionalidade do usuarios a serem requisitados
        na api
        '''
        valid_nat = list(COUNTRY_CODE.keys())
    
        if isinstance(nat, str):
          nat = [nat]
        
        # se nao houver uma nacionalidade valida
        # retorna uma lista vazia
        nat = np.array(nat)
        is_valid = np.isin(nat, valid_nat)
        self.nat = list(np.char.lower(nat[is_valid]))
        print(self.nat, is_valid)

        return None

    def request(self, n = 500, as_dataframe = True):
        # prepara o sufixo para o pedido
        suffix = "?results={}".format(n) # numero de pedidos

        # checa se um parametro deve ser excluido e inclui no sufixo
        if len(self.blacklist) > 0:
            # separado por virgula, nao precisa dos colchetes
            parameters = str(self.blacklist)[1:-1].replace("'", "").replace(' ', '')
            suffix += "&exc=" + parameters

        # checa se o usuario especificou uma nacionalidade
        if len(self.nat) > 0:
            parameters = str(self.nat)[1:-1].replace("'", "").replace(' ', '')
            suffix += "&nat=" + parameters

        # API contem como chaves -> ['results', 'info']
        # informacao desejada esta em 'results'
        request = requests.get(self._source_API + suffix)
        results =  json.loads(request.content)['results']

        # organizando o dicionario
        for i in range(n):
            results[i] = unpack_dictionary(results[i])

        # Unifica os resultados em uma unica "tabela"
        sample = self.join_samples(results)

        # converte para DataFrame, se solicitado.
        if as_dataframe:
            sample = DataFrame.from_dict(sample)

        return sample

    def update_blacklist(self, parameters : list):
        '''
        Atualiza a blacklist de parametros a serem excluidos durante a solicitacao
        de dados da API.
        '''
        
        # Pode ser uma lista vazia
        self.blacklist = parameters

        return None

    def join_samples(self, items):
        '''
        Gera uma única amostra a partir das "n" solicitações na API, e retorna
        um dicionario com os valores.
        '''
        n = len(items)
        unified_samples = {}

        for k in items[0].keys():
            values = [items[i][k] for i in range(n)]
            unified_samples[k] = values

        return unified_samples


