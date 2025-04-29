import pandas as pd
from chart.models import Colaborador

def download_excel():
    # Carrega os dados dos colaboradores do banco de dados
    colaboradores = Colaborador.objects.all()

    # Itera sobre os colaboradores e cria uma lista de dicionários
    colaboradores_list = []
    for colaborador in colaboradores:
        colaborador_dict = {
            'Nome': colaborador.nome,
            'Email': colaborador.email,
            'Telefone': colaborador.telefone,
            'Cargo': colaborador.cargo.nome if colaborador.cargo else '',
            'Supervisor': colaborador.supervisor.nome if colaborador.supervisor else '',
        }
        # Atualiza o dicionário
        colaboradores_list.append(colaborador_dict)

    # Cria um DataFrame com os dados dos colaboradores
    df = pd.DataFrame(colaboradores_list)

    # Salva o DataFrame em um arquivo Excel
    df.to_excel('colaboradores.xlsx', index=False)

    return 'colaboradores.xlsx'
