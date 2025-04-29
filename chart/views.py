import json
import os
from django.shortcuts import redirect, render
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Importa a biblioteca para trabalhar com a imagem de perfil
from PIL import Image

from chart.models import Cargo, Colaborador, User

# Função para baixar o arquivo Excel
from chart.functions.downloadexcel import download_excel

# Função para importar os dados do arquivo Excel
from chart.functions.uploadexcel import upload_excel

@login_required
def index(request):
    # Verifica se o usuário está logado
    if request.user.is_authenticated:
        # Se estiver logado, renderiza a página do organograma
        return redirect("orgchart")
    else:
        # Se não estiver logado, redireciona para a página de login
        return redirect("signin")

# ======================================
# View - Login
def signin(request):
    if request.method == "POST":
        # Captura os dados do formulário
        email = request.POST.get("email")
        senha = request.POST.get("password")
        # Verifica se o usuário existe
        usuario = authenticate(request=request, email=email, password=senha)

        if usuario:
            # Se existir, faz login e envia para a tela do organograma
            login(request=request, user=usuario)
            return redirect("orgchart")
        
        else:
            # Se não existir, retorna uma mensagem de erro
            return render(request, "signin.html", {"error": "Usuário ou senha inválidos."})
    
    # Caso não seja um POST, renderiza a página de login
    return render(request, "signin.html")


# View - Cadastro
def signup(request):
    if request.method == "POST":
        # Captura os dados do formulário
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        senha = request.POST.get("password")

        # Salva o novo usuario
        usuario = User(nome=nome, email=email, password=senha)

        usuario.save()

        # Redireciona para a página de login
        return render(request, "signin.html")
    
    return render(request, "signup.html")

# View Logout
@login_required
def _logout(request):
    logout(request)
    return redirect("signin")

# ======================================

def orgchart(request):
    colaboradores = Colaborador.objects.all()
    data = []
    
    for colaborador in colaboradores:
        item = {
            "id": colaborador.id,
            "name": colaborador.nome,
            "title": colaborador.cargo.nome if colaborador.cargo else "",
            "img": colaborador.imagem.url if colaborador.imagem else "/static/img/user.png",
            "email": colaborador.email,
            "telefone": colaborador.telefone,
            "supervisor_name": colaborador.supervisor.nome if colaborador.supervisor else ""
        }
        
        if colaborador.supervisor:
            item["pid"] = colaborador.supervisor.id
            
        data.append(item)

    if request.user.is_authenticated:
        return render(request, "orgchart.html", {"data": json.dumps(data)})
    
    return redirect("signin")
# ======================================

# View - Cadastrar Colaborador
def register_employee(request):
    cargo = Cargo.objects.all()
    supervisor = Colaborador.objects.all()

    if request.method == "POST":
        # Captura os dados do formulário
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        telefone = request.POST.get("telefone")
        supervisor_id = request.POST.get("supervisor")

        # Verifica se é um novo cargo
        selected_cargo = request.POST.get("cargo")
        if selected_cargo == "new":
            novo_cargo = request.POST.get("new_cargo")
            novo_salario = request.POST.get("salario", 0)

            # Verifica se o campo "novo_cargo" está vazio
            if not novo_cargo:
                messages.error(request, "O campo Novo Cargo é obrigatório.")
                return render(request, "register_employee.html", {
                    "form_list": {
                        "nome": nome, 
                        "email": email, 
                        "telefone": telefone, 
                        "supervisor": supervisor_id, 
                        "cargo": selected_cargo, 
                        "new_cargo": novo_cargo, 
                        "salario": novo_salario, 
                        "cargo_list": cargo, 
                        "supervisor_list": supervisor,
                    },
                    "cargo": cargo,
                    "supervisor": supervisor,
                })
            
            cargo = Cargo(nome=novo_cargo, salario=float(novo_salario) if novo_salario else 0)
            cargo.save()

        else:
            try:
                cargo = Cargo.objects.get(id=selected_cargo)
            except Cargo.DoesNotExist:
                cargo = None
                return render(request, "register_employee.html", {"error": "Cargo não encontrado."})
        
        # Verifica se é um novo supervisor
        supervisor = None
        if supervisor_id:
            try:
                supervisor = Colaborador.objects.get(id=supervisor_id)
            except Colaborador.DoesNotExist:
                supervisor = None
                return render(request, "register_employee.html", {"error": "Supervisor não encontrado."})
            
        # Salva o novo colaborador
        colaborador = Colaborador(nome=nome, email=email, telefone=telefone, supervisor=supervisor, cargo=cargo)
        colaborador.save()

        # Redireciona para a página de listagem
        return redirect("list_employee")

    return render(request, 'register_employee.html', {
        "cargo": cargo,
        "supervisor": supervisor
        }
    )

# View - Editar Colaborador
def edit_employee(request, id):
    try:
        employee = Colaborador.objects.get(id=id)
    except Colaborador.DoesNotExist:
        return redirect('list_employee')
    
    cargos = Cargo.objects.all()
    supervisores = Colaborador.objects.exclude(id=id)  # Exclui o próprio colaborador da lista
    
    if request.method == "POST":
        # Captura os dados do formulário
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        telefone = request.POST.get("telefone")
        
        # Verifica se é um novo cargo
        selected_cargo = request.POST.get("cargo")
        if selected_cargo == "new":
            novo_cargo = request.POST.get("new_cargo")
            novo_salario = request.POST.get("salario", 0)
            
            # Verifica se o campo "novo_cargo" está vazio
            if not novo_cargo:
                return render(request, "edit_employee.html", {
                    "error": "O campo 'Novo Cargo' é obrigatório.",
                    "employee": employee,
                    "cargos": cargos,
                    "supervisores": supervisores
                })
            
            cargo = Cargo(nome=novo_cargo, salario=float(novo_salario) if novo_salario else 0)
            cargo.save()
        else:
            try:
                cargo = Cargo.objects.get(id=selected_cargo)
            except Cargo.DoesNotExist:
                cargo = employee.cargo  # Mantém o cargo atual se não encontrar
        
        # Verifica se é um novo supervisor
        supervisor_id = request.POST.get("supervisor")
        supervisor = None
        if supervisor_id:
            try:
                supervisor = Colaborador.objects.get(id=supervisor_id)
            except Colaborador.DoesNotExist:
                supervisor = employee.supervisor  # Mantém o supervisor atual se não encontrar
        
        # Atualiza os dados do colaborador
        employee.nome = nome
        employee.email = email
        employee.telefone = telefone
        employee.cargo = cargo
        employee.supervisor = supervisor
        
        # Processa a imagem de perfil
        if 'imagem' in request.FILES:
            imagem = request.FILES['imagem']
            ext = os.path.splitext(imagem.name)[1]
            filename = f"{employee.id}{ext}"

            path = os.path.join('media', filename)

            employee.imagem(path, imagem)
        
        employee.save()
        
        # Redireciona para a página de listagem
        return redirect("list_employee")
    
    return render(request, 'edit_employee.html', {
        "employee": employee,
        "cargos": cargos,
        "supervisores": supervisores
    })

# View - Listar Colaborador
def list_employee(request, id=None):

    if request.GET.get('search_query'):
        # Captura o valor do campo de pesquisa
        search_query = request.GET.get('search_query')

        # Filtra os colaboradores com base na pesquisa
        colaboradores = Colaborador.objects.filter(nome__icontains=search_query)

    else:
        # Se não for POST, busca todos os colaboradores
        colaboradores = Colaborador.objects.all()

    return render(request, 'list_employee.html', {"employees": colaboradores})

# View - Deletar Colaborador
def delete_employee(request, id):
    # Busca o colaborador pelo ID
    colaborador = Colaborador.objects.get(id=id)
    # Deleta o colaborador
    colaborador.delete()

    # Redireciona para a página de listagem
    return redirect('list_employee')

# ======================================
# View - Upload Excel
@login_required
def view_upload_excel(request):
    if request.method != 'POST':
        # Se não for POST, redireciona para a página de listagem
        return redirect('list_employee')
    
    # Recebe o arquivo Excel
    file = request.FILES.get('excel_file')

    # Verifica se o arquivo foi enviado
    if not file:
        # Retorna uma mensagem de erro
        return render(request, 'list_employee.html', {'error': 'Arquivo não enviado!'})
    
    # Verifica se o arquivo é um arquivo Excel
    if not (file.name.endswith('.xlsx') or file.name.endswith('.xls')):
        # Retorna uma mensagem de erro
        return render(request, 'list_employee.html', {'error': 'Arquivo inválido! Apenas arquivos .xlsx ou .xls são aceitos.'})
    
    # Tenta processar o arquivo
    try:
        # Verifica se o arquivo é válido
        if upload_excel(file):
            # Retorna uma mensagem de sucesso
            return render(request, 'list_employee.html', {'success': 'Arquivo importado com sucesso!'})
        else:
            # Retorna uma mensagem de erro
            return render(request, 'list_employee.html', {'error': 'Erro ao importar o arquivo! Verifique o formato do arquivo.'})
    except Exception as e:
        # Log do erro
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao processar upload de Excel: {str(e)}")
        
        # Retorna uma mensagem de erro
        return render(request, 'list_employee.html', {'error': f'Erro ao processar o arquivo: {str(e)}'})


# View - Download Excel
def view_download_excel(request):
    # Baixa o arquivo Excel
    file_path = download_excel()

    # Retorna o arquivo para download
    return FileResponse(open(file_path, 'rb'), as_attachment=True)