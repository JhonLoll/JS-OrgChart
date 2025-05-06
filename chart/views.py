import json
import os
from django.shortcuts import redirect, render
from django.http import FileResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from OrgChart.settings import MEDIA_URL
from chart.models import Cargo, Colaborador, User

# Função para baixar o arquivo Excel
from chart.functions.downloadexcel import download_excel

# Função para importar os dados do arquivo Excel
from chart.functions.uploadexcel import upload_excel

def admin_required(view_func):
    """
    Decorador que verifica se o usuário está autenticado e é admin.
    Se não estiver autenticado, redireciona para a página de login.
    Se estiver autenticado mas não for admin, redireciona para a página de acesso negado.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('signin')
        if not request.user.is_staff:
            return redirect('access_denied')
        return view_func(request, *args, **kwargs)
    return wrapper

# @login_required
def index(request):
    # Verifica se o usuário está logado
    # if request.user.is_authenticated:
        # Se estiver logado, renderiza a página do organograma
    return redirect("orgchart")
    # else:
    #     # Se não estiver logado, redireciona para a página de login
    #     return redirect("signin")

# Função auxiliar para verificar se o usuário é admin
def is_admin(user):
    return user.is_authenticated and user.is_staff

# NÃO ADICIONE DECORADORES AQUI - páginas de autenticação devem ser acessíveis para todos
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
            messages.success(request, f"Bem-vindo, {usuario.nome}!")
            return redirect("orgchart")
        
        else:
            # Se não existir, retorna uma mensagem de erro
            messages.error(request, "Usuário ou senha inválidos.")
            return render(request, "signin.html")
    
    # Caso não seja um POST, renderiza a página de login
    return render(request, "signin.html")

# NÃO ADICIONE DECORADORES AQUI - páginas de cadastro devem ser acessíveis para todos
def signup(request):
    if request.method == "POST":
        # Captura os dados do formulário
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        senha = request.POST.get("password")
        confirmar_senha = request.POST.get("confirm-password")
        
        # Verifica se as senhas coincidem
        if senha != confirmar_senha:
            messages.error(request, "As senhas não coincidem.")
            return render(request, "signup.html")
        
        # Verifica se o email já existe
        if User.objects.filter(email=email).exists():
            messages.error(request, "Este email já está cadastrado.")
            return render(request, "signup.html")
        
        try:
            # Cria o usuário com senha criptografada
            usuario = User(nome=nome, email=email)
            usuario.set_password(senha)  # Criptografa a senha
            usuario.save()
            
            messages.success(request, "Cadastro realizado com sucesso! Faça login para continuar.")
            return redirect("signin")
        except Exception as e:
            messages.error(request, f"Erro ao criar usuário: {str(e)}")
            return render(request, "signup.html")
    
    return render(request, "signup.html")

# View Logout
@login_required
def _logout(request):
    messages.info(request, "Você saiu do sistema com sucesso.")
    logout(request)
    return redirect("signin")

# ======================================

# @login_required
def orgchart(request):
    colaboradores = Colaborador.objects.all()
    data = []
    
    for colaborador in colaboradores:
        item = {
            "id": colaborador.id,
            "name": colaborador.nome,
            "title": colaborador.cargo.nome if colaborador.cargo else "",
            "img": colaborador.imagem.url if colaborador.imagem else os.path.join(MEDIA_URL, "profile_pics", "user.png"),
            "email": colaborador.email,
            "telefone": colaborador.telefone,
            "supervisor_name": colaborador.supervisor.nome if colaborador.supervisor else ""
        }
        
        if colaborador.supervisor:
            item["pid"] = colaborador.supervisor.id
            
        data.append(item)

    # if request.user.is_authenticated:
    return render(request, "orgchart.html", {"data": json.dumps(data)})
    
    # return redirect("signin")
# ======================================

# View - Cadastrar Colaborador
@login_required
@user_passes_test(is_admin, login_url='access_denied')
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

        # Adicionar mensagem de sucesso
        messages.success(request, f"Colaborador {nome} cadastrado com sucesso!")
        return redirect("list_employee")

    return render(request, 'register_employee.html', {
        "cargo": cargo,
        "supervisor": supervisor
        }
    )

# View - Editar Colaborador
@login_required
@user_passes_test(is_admin)
def edit_employee(request, id):
    try:
        employee = Colaborador.objects.get(id=id)
    except Colaborador.DoesNotExist:
        messages.error(request, "Colaborador não encontrado.")
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
            
            # Salva a imagem antiga se existir
            old_image = None
            if employee.imagem:
                # Salva a imagem antiga em um arquivo temporário
                old_image = employee.imagem.path
        
            # Atribuir diretamente ao campo imagem
            employee.imagem = imagem

            # Exclui a imagem antiga se existir e não for a imagem padrão user.png
            if old_image and os.path.exists(old_image):
                # Verifica se o nome do arquivo não é user.png
                if not old_image.endswith('user.png'):
                    os.remove(old_image)
            
        employee.save()
        
        # Redireciona para a página de listagem
        return redirect("list_employee")
    
    return render(request, 'edit_employee.html', {
        "employee": employee,
        "cargos": cargos,
        "supervisores": supervisores
    })

# View - Listar Colaborador
@admin_required
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
@login_required
@user_passes_test(is_admin, login_url='access_denied')
def delete_employee(request, id):
    try:
        # Busca o colaborador pelo ID
        colaborador = Colaborador.objects.get(id=id)
        nome = colaborador.nome
        # Deleta o colaborador
        colaborador.delete()
        
        messages.success(request, f"Colaborador {nome} excluído com sucesso!")
    except Colaborador.DoesNotExist:
        messages.error(request, "Colaborador não encontrado.")
    except Exception as e:
        messages.error(request, f"Erro ao excluir colaborador: {str(e)}")
    
    # Redireciona para a página de listagem
    return redirect('list_employee')

# ======================================
# View - Upload Excel
@login_required
@user_passes_test(is_admin, login_url='access_denied')
def view_upload_excel(request):
    if request.method != 'POST':
        # Se não for POST, redireciona para a página de listagem
        return redirect('list_employee')
    
    # Recebe o arquivo Excel
    file = request.FILES.get('excel_file')

    # Verifica se o arquivo foi enviado
    if not file:
        # Retorna uma mensagem de erro
        messages.error(request, 'Arquivo não enviado!')
        return redirect('list_employee')
    
    # Verifica se o arquivo é um arquivo Excel
    if not (file.name.endswith('.xlsx') or file.name.endswith('.xls')):
        # Retorna uma mensagem de erro
        messages.error(request, 'Arquivo inválido! Apenas arquivos .xlsx ou .xls são aceitos.')
        return redirect('list_employee')
    
    # Tenta processar o arquivo
    try:
        # Verifica se o arquivo é válido
        if upload_excel(file):
            # Retorna uma mensagem de sucesso
            messages.success(request, 'Arquivo importado com sucesso!')
        else:
            # Retorna uma mensagem de erro
            messages.error(request, 'Erro ao importar o arquivo! Verifique o formato do arquivo.')
    except Exception as e:
        # Log do erro
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao processar upload de Excel: {str(e)}")
        
        # Retorna uma mensagem de erro
        messages.error(request, f'Erro ao processar o arquivo: {str(e)}')
    
    return redirect('list_employee')

# View - Download Excel
@login_required
@user_passes_test(is_admin, login_url='access_denied')
def view_download_excel(request):
    try:
        # Baixa o arquivo Excel
        file_path = download_excel()
        
        # Retorna o arquivo para download
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    except Exception as e:
        messages.error(request, f"Erro ao gerar arquivo Excel: {str(e)}")
        return redirect('list_employee')

# Não adicione decoradores aqui
def access_denied(request):
    messages.warning(request, "Você não tem permissão para acessar esta área.")
    return render(request, 'access_denied.html')
# ======================================