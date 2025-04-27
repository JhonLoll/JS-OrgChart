import pandas as pd
from chart.models import Colaborador

# Função para importar os dados do arquivo excel
def upload_excel(file):
    # Lê o arquivo excel
    df = pd.read_excel(file)

    # Cria uma lista com os dados do arquivo excel
    data = df.to_dict('records')

    # Cria uma lista com os dados do arquivo excel
    for row in data:
        # Verifica se o colaborador já existe
        if Colaborador.objects.filter(id=row['id']).exists():
            # Se existir, atualiza os dados
            colaborador = Colaborador.objects.get(id=row['id'])
            colaborador.nome = row['nome']
            colaborador.email = row['email']
            colaborador.telefone = row['telefone']
            colaborador.cargo = row['cargo']
            colaborador.supervisor = row['supervisor']
            colaborador.save()
        else:
            # Se não existir, cria um novo colaborador
            colaborador = Colaborador(
                id=row['id'],
                nome=row['nome'],
                email=row['email'],
                telefone=row['telefone'],
                cargo=row['cargo'],
                supervisor=row['supervisor']
            )
            colaborador.save()
        return True
    return False
