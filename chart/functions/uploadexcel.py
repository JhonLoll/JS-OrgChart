def upload_excel(file):
    # Lê o arquivo Excel
    import pandas as pd
    from chart.models import Cargo, Colaborador
    
    try:
        # Lê o arquivo Excel
        df = pd.read_excel(file)
        
        # Verifica se as colunas necessárias existem
        required_columns = ['Nome', 'Email', 'Telefone', 'Cargo', 'Supervisor']

        for column in required_columns:
            if column not in df.columns:
                return False
        
        # Processa cada linha do Excel
        for _, row in df.iterrows():
            # Obtém ou cria o cargo
            cargo_nome = row['Cargo']
            cargo, created = Cargo.objects.get_or_create(
                nome=cargo_nome,
                defaults={'salario': 0}  # Valor padrão para salário
            )
            
            # Obtém o supervisor (se existir)
            supervisor = None
            if pd.notna(row['Supervisor']):
                supervisor_nome = row['Supervisor']
                try:
                    supervisor = Colaborador.objects.get(nome=supervisor_nome)
                except Colaborador.DoesNotExist:
                    # Supervisor não encontrado, será criado depois
                    pass
            
            # Cria ou atualiza o colaborador
            colaborador, created = Colaborador.objects.update_or_create(
                email=row['Email'],
                defaults={
                    'Nome': row['Nome'],
                    'Telefone': row['Telefone'] if pd.notna(row['Telefone']) else '',
                    'Cargo': cargo,
                    'Supervisor': supervisor
                }
            )
        
        # Segundo passo: atualizar supervisores que não foram encontrados
        # (caso o supervisor esteja listado depois do colaborador no Excel)
        for _, row in df.iterrows():
            if pd.notna(row['Supervisor']):
                colaborador = Colaborador.objects.get(email=row['Email'])
                supervisor_nome = row['Supervisor']
                try:
                    supervisor = Colaborador.objects.get(nome=supervisor_nome)
                    colaborador.supervisor = supervisor
                    colaborador.save()
                except Colaborador.DoesNotExist:
                    # Supervisor não encontrado mesmo após processar todo o arquivo
                    pass
        
        return True
    except Exception as e:
        print(f"Erro ao processar o arquivo Excel: {e}")
        return False
