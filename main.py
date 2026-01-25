from fastapi import FastAPI, Request
from nicegui import ui, app

from PythonPages.homepage import HomePage
from PythonPages.cadastro import Cadastro
from PythonPages.login import Login
from PythonPages.telainicial import TelaInicial
from PythonPages.questoes import Questoes
from PythonPages.pos_cadastro import PosCadastro
from PythonPages.tarefa_concluida import task_completed_page
from PythonPages.gabarito import gabarito_page 

app_fastapi = FastAPI()

@ui.page('/')
def main_page(request: Request):
    auth_token = request.query_params.get('auth_token')
    storage = app.storage.user or {}
    token = auth_token or storage.get('token')

    if auth_token and app.storage.user is not None:
        app.storage.user['token'] = auth_token
        ui.run_javascript(f'document.cookie="lexora_token={auth_token}; path=/; max-age=604800;"')

    if token:
        TelaInicial().render()
    else:
        HomePage().render()

@ui.page('/questoes')
def questoes_page():
    storage = app.storage.user or {}
    if not storage.get('token'):
        ui.navigate.to('/')
        return
    Questoes().render()

@ui.page('/tarefa-concluida')
def tarefa_concluida_route():
    storage = app.storage.user or {}
    if not storage.get('token'):
        ui.navigate.to('/')
        return
    task_completed_page()

# 2. Rota Nova para o Gabarito
@ui.page('/gabarito')
def gabarito_route():
    storage = app.storage.user or {}
    if not storage.get('token'):
        ui.navigate.to('/')
        return
    gabarito_page()

@ui.page('/login')
def login_page():
    Login().render()

@ui.page('/cadastro')
def cadastro_page():
    Cadastro().render()

@ui.page('/pos-cadastro')
def pos_cadastro_page():
    PosCadastro().render()

@ui.page('/logout')
def logout():
    if app.storage.user is not None:
        app.storage.user.clear()
    ui.navigate.to('/')

ui.run_with(app_fastapi, storage_secret='segredo123')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run('main:app_fastapi', host='0.0.0.0', port=10000, reload=True)
