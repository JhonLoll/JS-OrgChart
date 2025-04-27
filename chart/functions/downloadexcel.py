import pandas as pd
from chart.models import Colaborador

def download_excel():
    # Carrega os dados dos colaboradores do banco de dados
    colaboradores = Colaborador.objects.all()

    # Cria um DataFrame com os dados dos colaboradores
    df = pd.DataFrame(list(colaboradores.values()))

    # Salva o DataFrame em um arquivo Excel
    df.to_excel('colaboradores.xlsx', index=False)

    return 'colaboradores.xlsx'
