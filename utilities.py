import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# ----------------------------------------------------------------------------
# Variaveis Globais
# ----------------------------------------------------------------------------

# Paises disponiveis na API RandomUser (v1.4), e seu DDI.
COUNTRY_CODE = {'AU' : 61, 'BR' : 55, 'CA' : 1, 'CH' : 41, 'DE' : 49, 'DK' : 45,
            'ES' : 34, 'FI' : 358, 'FR' : 33, 'GB' : 44, 'IE' : 353, 'IN' : 91,
            'IR' : 98, 'MX' : 52, 'NL' : 31, 'NO' : 47, 'NZ' : 64, 'RS' : 381,
            'TR' : 90, 'UA' : 380, 'US' : 1}

# A = Area Code ; S = Subscriber Code; L = Leading Zero
# coluna 1 = Cell format | coluna 2 = phone format
CELLPHONE_FORMAT = {
    'AU' : ('LAAA-SSS-SSS', 'LA-SSSS-SSSS'), # Australia
    'BR' : ('(AA) SSSS-SSSS', '(AA) SSSS-SSSS'), # Brasil
    'CA' : ('AAA-SSS-SSSS', 'AAA-SSS-SSSS'), # Canada
    'CH' : ('LAA SSS SS SS', 'LAA SSS SS SS'), # Suíça
    'DE' : ('LAAA-SSSSSSS', 'LAAA-SSSSSSS'), # Alemanha
    'DK' : ('SSSSSSSS', 'SSSSSSSS'), # Dinamarca
    'ES' : ('AAA-SSS-SSS', 'AAA-SSS-SSS'), # Espanha
    'FI' : ('LAA-SSS-SS-SS', 'LA-SSS-SSS'), # Finlandia
    'FR' : ('LA-SS-SS-SS-SS', 'LA-SS-SS-SS-SS'), # França
    'GB' : ('LAAAA SSSSSS', 'LAAAAAA SSS SSSS'), # Reino unido
    'IE' : ('LAA-SSS-SSSS', 'LAA-SSS-SSSS'), # Irlanda
    'IN' : ('AAAAASSSSS', 'AAASSSSSSS'), # India
    'IR' : ('LAAA-SSS-SSSS','LAA-SSSSSSSS'), # Ira
    'MX' : ('(AAA) SSS SSSS', '(AAA) SSS SSSS'), # Mexico
    'NL' : ('(LA) SSSSSSSS', '(LAA) SSSSSSS'), # Paises Baixos
    'NO' : ('SSSSSSSS', 'SSSSSSSS'), # Noruega
    'NZ' : ('(AAA)-SSS-SSSS', '(AAA)-SSS-SSSS'), # Nova Zelandia
    'RS' : ('AAA-SSSS-SSS', 'AAA-SSSS-SSS'), # Servia
    'TR' : ('(AAA)-SSS-SSSS', '(AAA)-SSS-SSSS'), # Turquia
    'UA' : ('(LAA) SSS-SSSS', '(LAA) SSS-SSSS'), # Ucrania
    'US' : ('(AAA) SSS-SSSS', '(AAA) SSS-SSSS'), # Estados Unidos
}

# ----------------------------------------------------------------------------
# Funções
# ----------------------------------------------------------------------------

def unpack_dictionary(dicionario : dict, preffix : str = "") -> dict:
    '''
    No caso de um dicionario conter diversos dicionarios dentro de si, descompacta
    todas as chaves, sub-chaves e respectivos valores em um unico dicionario final
    com a informacao resumida.

    Utiliza recursão para esse fim.
    '''
    new_dict = {}
    for k, v in dicionario.items():
        if isinstance(v, dict):
            old_dict = unpack_dictionary(v, preffix = preffix + k + "_")
            new_dict = new_dict | old_dict
        
        else:
            new_key = preffix + k
            new_dict[new_key] = v

    return new_dict


def format_phonenumber(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Formata os numeros de telefone e celular em um formato padrao unico.
    Formato escolhido foi o E164 Composto por:
            +(Country Code) (Area Code) (Subscriber Code)

    Exemplo: +55 21 12345678
    '''
    df = df.copy() # Copia do DataFrame original
    countries = np.unique(df['nat']) # extrais nacionalidades unicas
    columns = ['cell', 'phone']

    # Realiza as alterações, por nacionalidade.
    for i in range(countries.shape[0]):
        condition = df['nat'] == countries[i]
        country = df.loc[condition]

        # loop entre as colunas 'cell' e 'phone'
        for j in range(len(columns)):
            old_values = country[columns[j]]
            str_format = CELLPHONE_FORMAT[countries[i]][j]
            ddi = '+{} '.format(COUNTRY_CODE[countries[i]])
            series = pd.Series([ddi] * country.shape[0], index = country.index)

            # Incluindo o Area Code, se houver.
            if 'A' in str_format:
                area_idx = str_format.index('A')
                area_size = str_format.count('A')
                series = series + old_values.str.slice(area_idx, area_idx + area_size) + ' '
            
            # Obtendo o subscriber code
            sub_idx_ini = str_format.index('S')
            sub_idx_last = str_format.rfind('S') + 1
            subscribe_code = old_values.str.slice(sub_idx_ini, sub_idx_last)

            # remove os caracteres '-' e ' '
            subscribe_code = subscribe_code.str.replace('-', '')
            subscribe_code = subscribe_code.str.replace(' ', '')

            # incluindo o resultado
            series = series + subscribe_code
            df.loc[condition, columns[j]] = series

    return df


def relatorio(df : pd.DataFrame, fname : str) -> None:
    '''
    Recebe um DataFrame e gera um relatorio contendo a porcentagem de usuarios
    por pais e por genero.
    O relatorio é salvo em um arquivo txt.
    '''
    total = df.shape[0] # Total de usuarios
    genders, gender_count = np.unique(df['gender'], return_counts = True)
    gender_pct = gender_count / total * 100 # resultado em porcentagem
    idx_male = list(genders).index('male')
    idx_female = (idx_male + 1) % 2

    # Paises unicos e contagem
    countries, count = np.unique(df['location_country'], return_counts = True)
    country_pct = count / total * 100

    # Incluindo extensao se nao houver
    fname = fname + ".txt" if ".txt" not in fname else fname

    # Outros
    linestyle1 = '\n' + '-' * 70 + "\n"
    datetime_fmt = "%d/%m/%Y %H:%M"
    with open(fname, 'w') as file:
        # Escrevendo as informacoes gerais
        file.write(linestyle1)
        file.write("INFORMAÇÕES GERAIS")
        file.write(linestyle1)

        file.write('\nRandom User Generator API v1.4\n')
        file.write('Usuarios na amostra = {}\n'.format(total))
        file.write('Data & Hora: ' + datetime.now().strftime(datetime_fmt) + '\n')

        # escrevendo os resultados sobre o genero
        file.write(linestyle1)
        file.write('RELATÓRIO')
        file.write(linestyle1)

        text = '\nAo todo, {:.2f}% da amostra é composta por usuários do sexo '\
        'masculino\nenquanto os {:.2f}% restantes são compostos por '\
        'usuários do sexo feminino.'.format(gender_pct[idx_male], gender_pct[idx_female])
        file.write(text + '\n')

        # escrevendo informacoes sobre a nacionalidade
        file.write("\nA distribuicao de usuários por país é a que segue:\n")
        
        for i in range(countries.shape[0]):
            text = "{:20} -> {:.2f}%\n".format(countries[i], country_pct[i])
            file.write(text)


def age_histogram(df : pd.DataFrame, fname : str, dx : int = 5) -> None:
    '''
    Gera uma imagem (histograma) contendo o grafico de distribuição da idade 
    dos usuários.
    '''
    # acessando a coluna com os valores e deduzindo o maximo e minimo
    ages = df['dob_age']
    max_value = np.ceil(ages.max() / 10) * 10
    min_value = np.floor(ages.min() / 10) * 10

    # intervalos
    binx = np.arange(min_value, max_value, dx).astype(int)

    # histograma
    hist, bin_edges = np.histogram(ages, binx)
    pct = hist / ages.shape[0] * 100

    # Plot
    fig, ax = plt.subplots(figsize = (12, 8))
    bars = ax.bar(binx[:-1], pct, color = "chocolate", edgecolor = 'white',
                align = 'edge', width = dx)
    ax.bar_label(bars, labels = hist)

    # propriedades do plot
    ax.set_title("Distribuição da idade dos usuários", fontsize = 20)
    ax.grid(True, axis = 'y')

    # Eixo X
    ax.set_xlabel("Idade", fontsize = 20)
    ax.set_xticks(binx)
    ax.set_xticklabels(binx, fontsize = 14)

    # Eixo Y
    ax.set_ylabel("Frequência (%)", fontsize = 20)
    ymax = np.ceil(pct.max() * 1.1 / 10) * 10
    yticks = np.arange(0, ymax, 3).astype(int)
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticks, fontsize = 14)

    # salva e exibe a figura
    fig.savefig(fname, dpi = 200, bbox_inches = 'tight')
    plt.show()

    return None


def groupby_country_state(df : pd.DataFrame) -> pd.DataFrame:
    '''
    Agrupa o DataFrame contendo informações de usuários de acordo com o seu
    país e estado.
    Após agrupar, retorna um DataFrame com a quantidade de usuários por grupo e 
    uma nova coluna com uma "lista" contendo a referencia para cada usuario.
    '''

    # Selecionando colunas
    country  = df['location_country']
    state = df['location_state']

    # cria uma coluna como ID de cada usuario, baseado nos indices do DataFrame
    df["user_id"] = df.index 

    # Agrupa, Conta e Reinicia os índices
    group = df.groupby([country, state]) 
    count = group.agg(
        user_count = ('id_name', 'count'), # conta o numero de usuarios
        users = ('user_id', lambda x: list(x)) # lista com o indice de cada usuarios
        ) # retorna um MultiIndex

    count = count.reset_index() # transforma um MultiIndex em um DataFrame

    # organiza em ordem decrescente de acordo com a quantidade de usuarios por grupo.
    count = count.sort_values(by = ["user_count"], ascending = False)
    count.reset_index(drop= False) 

    return count