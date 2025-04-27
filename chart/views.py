import json
from django.shortcuts import redirect, render
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

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
            "img": colaborador.imagem if colaborador.imagem else "/static/img/user.png"
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
                return render(request, "register_employee.html", {"error": "O campo 'Novo Cargo' é obrigatório."})
            
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
    pass

# View - Listar Colaborador
def list_employee(request, id=None):
    colaboradores = Colaborador.objects.all()

    return render(request, 'list_employee.html', {"employees": colaboradores})

# View - Deletar Colaborador
def delete_employee(request):
    pass

# ======================================
# View - Upload Excel
def view_upload_excel(request):
    # Recebe o arquivo Excel
    file = request.FILES.get('file')

    # Verifica se o arquivo foi enviado
    if file:
        # Verifica se o arquivo é um arquivo Excel
        if file.name.endswith('.xlsx') or file.name.endswith('.xls'):
            # Verifica se o arquivo é válido
            if upload_excel(file):
                # Retorna uma mensagem de sucesso
                return render(request, 'list_employee.html', {'success': 'Arquivo importado com sucesso!'})
            else:
                # Retorna uma mensagem de erro
                return render(request, 'list_employee.html', {'error': 'Erro ao importar o arquivo!'})
        else:
            # Retorna uma mensagem de erro
            return render(request, 'list_employee.html', {'error': 'Arquivo inválido!'})
    else:
        # Retorna uma mensagem de erro
        return render(request, 'list_employee.html', {'error': 'Arquivo não enviado!'})

# View - Download Excel
def view_download_excel(request):
    # Baixa o arquivo Excel
    file_path = download_excel()

    # Retorna o arquivo para download
    return FileResponse(open(file_path, 'rb'), as_attachment=True)