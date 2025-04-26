import json
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from chart.models import Cargo, Colaborador, User

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

# View - OrgChart
def orgchart(request):
    data = [
        { "id": 1, "name": "Diretor Geral", "title": "CEO", "img": "/static/img/ceo.jpg" },
        { "id": 2, "pid": 1, "name": "Maria", "title": "Financeiro", "img": "/static/img/maria.jpg" },
        { "id": 3, "pid": 1, "name": "Carlos", "title": "Operações", "img": "/static/img/carlos.jpg" },
        { "id": 4, "pid": 2, "name": "Ana", "title": "Tesouraria", "img": "/static/img/ana.jpg" },
    ]
    if request.user.is_authenticated:
        return render(request, "orgchart.html", {"data": json.dumps(data)})
    
    return redirect("signin")

# ======================================

# View - Cadastrar Colaborador
def register_employee(request):
    cargo = Cargo.objects.all()
    supervisor = Colaborador.objects.all()

    return render(request, 'register_employee.html', {
        "cargo": cargo,
        "supervisor": supervisor
        }
    )

# View - Listar Colaborador
def list_employee(request, id=None):
    if id:
        pass

    return None

# View - Deletar Colaborador
def delete_employee(request):
    pass

# ======================================