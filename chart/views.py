import json
from django.shortcuts import render
from django.http import HttpResponse

from chart.models import User

def index(request):
    # Verifica se o usuário está logado
    if request.user.is_authenticated:
        # Se estiver logado, renderiza a página do organograma
        return render(request, "orgchart.html", {"usuario": request.user})
    else:
        # Se não estiver logado, redireciona para a página de login
        return render(request, "signin.html")
    
# View - Login
def signin(request):
    if request.method == "POST":
        # Captura os dados do formulário
        email = request.POST.get("email")
        senha = request.POST.get("password")

        # Verifica se o usuário existe
        usuario = User.objects.filter(email=email, senha=senha).first()

        if usuario:
            # Se existir, envia para a tela do organograma
            return render(request, "orgchart.html", {"usuario": usuario})
        
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
        usuario = User(nome=nome, email=email, senha=senha, is_admin=False)

        usuario.save()

        # Redireciona para a página de login
        return render(request, "signin.html")
    
    return render(request, "signup.html")