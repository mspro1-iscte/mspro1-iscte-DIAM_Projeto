from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.core import serializers
import json
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test

from .models import Cliente, Produto, Categoria


def index(request):
    lista_categoria = Categoria.objects.all()
    lista_produto = Produto.objects.all()
    context = {'lista_categoria': lista_categoria, 'lista_produto': lista_produto}
    return render(request, 'loja/index.html', context)


def loginview(request):
    username = request.POST['username']
    password = request.POST['pass']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        request.session['lista_carrinho'] = []
        return HttpResponseRedirect(reverse('loja:index'))
    else:
        return HttpResponseRedirect(reverse('loja:index'))


def logoutview(request):
    logout(request)
    return HttpResponseRedirect(reverse('loja:index'))


def registaruser(request):
    return render(request, 'loja/registaruser.html')


def detalhe_produto(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    return render(request, 'loja/detalhe_produto.html', {'produto': produto})


def detalhe_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    lista_categoria = Categoria.objects.all()
    lista_produto = []
    for p in Produto.objects.all():
        if p.categoria_id == categoria_id:
            lista_produto.append(p)
    context = {'lista_produto': lista_produto, 'categoria': categoria,'lista_categoria': lista_categoria}
    return render(request, 'loja/detalhe_categoria.html', context)


def carrinho(request):
    lista_ids = request.session['lista_carrinho']
    lista_carrinho = []
    for id in lista_ids:
        produto = get_object_or_404(Produto, pk=id)
        lista_carrinho.append(produto)
    context = {'lista_carrinho': lista_carrinho}
    return render(request, 'loja/carrinho.html', context)


def nova_categoria(request):
    categoria_nome = request.POST['categoria_nome']
    if bool(request.FILES.get('categoria_file', False)):
        myfile = request.FILES['categoria_file']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)[5:]  # remover /loja
        categoria = Categoria(categoria_nome=categoria_nome, foto=uploaded_file_url)
    else:
        categoria = Categoria(categoria_nome=categoria_nome)
    categoria.save()
    return HttpResponseRedirect(reverse('loja:index'))


def novo_produto(request, categoria_id):
    produto_nome = request.POST['produto_nome']
    produto_texto = request.POST['produto_texto']
    preco_data = request.POST['preco_data']
    cat = get_object_or_404(Categoria, pk=categoria_id)
    if bool(request.FILES.get('produto_file', False)):
        myfile = request.FILES['produto_file']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)[5:]  # remover /loja
        print(uploaded_file_url)
        produto = Produto(produto_nome=produto_nome, produto_texto=produto_texto, preco_data=preco_data,
                          categoria=cat, foto=uploaded_file_url)

    else:
        produto = Produto(produto_nome=produto_nome, produto_texto=produto_texto, preco_data=preco_data,
                          categoria=cat)
    produto.save()

    return HttpResponseRedirect(reverse('loja:index'))


def adicionar_carrinho(request, produto_id):

    if not 'lista_carrinho' in request.session or not request.session['lista_carrinho']:
        request.session['lista_carrinho'] = [produto_id]

    else:
        lista_carrinho = request.session['lista_carrinho']
        lista_carrinho.append(produto_id)
        request.session['lista_carrinho'] = lista_carrinho
    print(request.session['lista_carrinho'])
    return HttpResponseRedirect(reverse('loja:index'))
    #return render(request, 'loja/detalhe_produto.html', {'produto': produto})


def remover_carrinho(request, produto_id):
    lista_carrinho = request.session['lista_carrinho']
    lista_carrinho.remove(produto_id)
    request.session['lista_carrinho'] = lista_carrinho
    return HttpResponseRedirect(reverse('loja:carrinho'))


def registo(request):
    username = request.POST['username']
    password = request.POST['pass']
    email = request.POST.get('email')
    curso = request.POST['curso']
    user = User.objects.create_user(username, email, password)
    user.save()
    if bool(request.FILES.get('myfile', False)):
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)[5:]  # remover /loja
        cliente = Cliente(user=user, curso=curso, foto=uploaded_file_url)
    else:
        cliente = Cliente(user=user, curso=curso)
    cliente.save()
    login(request, user)
    return HttpResponseRedirect(reverse('loja:index'))


def perfil(request):
    cliente = Cliente.objects.filter(user=request.user)
    return render(request, 'loja/perfil.html', {'cliente': cliente})


def apagar_categoria(request, categoria_id):
    record = Categoria.objects.get(id=categoria_id)
    record.delete()
    return HttpResponseRedirect(reverse('loja:index'))


def apagar_produto(request, produto_id):
    record = Produto.objects.get(id=produto_id)
    record.delete()
    return HttpResponseRedirect(reverse('loja:index'))


def criar_categoria(request):
    return render(request, 'loja/criar_categoria.html')


def criar_produto(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    context = {'categoria': categoria}
    return render(request, 'loja/criar_produto.html', context)
