# Etapa 7: Parametrizando seu codigo
# parametrizar seu código para que ele seja executado com valores diversos fornecidos pelo usuário.


from api import RandomUserAPI
import utilities


def main(**kwargs):
  generator = RandomUserAPI()

  # excluindo categorias na solcitacao a api.
  blacklist = kwargs.get('blacklist', [])
  generator.update_blacklist(blacklist)

  # Filtrando por nacionalidade, se necessario
  nats = kwargs.get('nat', [])
  generator.update_nat(nats)

  # obtendo o DataFrame
  n = kwargs.get('requests', 500)
  consulta = generator.request(n = n, as_dataframe=True)
  
  # Modifica o formato dos numeros de telefone e celular para E164
  # Apenas se solicitado
  if kwargs.get('format_cellphone', False):
    consulta = utilities.format_phonenumber(consulta)

  # Salva as informacoes em um arquivo csv localizado na mesma pasta do script
  # Padrao é salvar pelo menos os dados em um arquivo de texto
  destino = kwargs.get('fname', 'data')
  consulta.to_csv(destino + '.csv', index = False)

  # Gera e salva um relatorio em um arquivo txt
  # Apenas se solicitado
  if kwargs.get('get_report', False):
    utilities.relatorio(df = consulta, fname = 'relatorio.txt')
  
  # Gera e salva uma figura com a distribuicao de idade
  # Apenas se solicitado
  if kwargs.get('get_figure', False):
    dx = kwargs.get('age_interval', 5) # intervalo do eixo horizontal no histograma
    utilities.age_histogram(
      df = consulta,
      fname = 'histograma_idade.png',
      dx = dx
      )

  # particiona no formato Hive por pais e estado
  # Apenas se solicitado
  if kwargs.get('partition', False):
    criterios = ['location_country', 'location_state']
    utilities.create_partition(consulta, criterios, destino)


if __name__ == "__main__":
  kwargs = {
    'blacklist' : ['login'], # categorias para excluir da solicitacao
    'nat' : ['BR', 'US'], # filtrar por nacionalidade
    'requests' : 500, # numeros de pedidos
    'fname' : 'consulta', # nome do arquivo csv
    'get_report' : True, # se incluir relatorio
    'get_figure' : True, # se incluir figura do histograma de idade
    'format_cellphone' : True, # modifica o formato dos numeros de telefone / celular
    'age_interval' : 5, # intervalo do histograma
    'partition' : True, # se particionar em formato hive
  }
  main(**kwargs)