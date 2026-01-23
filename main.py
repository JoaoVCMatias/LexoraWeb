from fastapi import FastAPI
from nicegui import ui, app

from PythonPages.homepage import HomePage
from PythonPages.cadastro import Cadastro
from PythonPages.login import Login
from PythonPages.telainicial import TelaInicial
from PythonPages.questoes import Questoes
from PythonPages.tarefa_concluida import TarefaConcluida
from PythonPages.gabarito import Gabarito

app_fastapi = FastAPI()

@ui.page('/')
def main_page(auth_token: str = None):
    token = auth_token or app.storage.user.get('token')
    if auth_token:
        app.storage.user['token'] = auth_token
        ui.run_javascript(f'document.cookie="lexora_token={auth_token}; path=/; max-age=604800;"')

    if token:
        TelaInicial().render()
    else:
        HomePage().render()

@ui.page('/questoes')
def questoes_page():
    if not app.storage.user.get('token'):
        ui.navigate.to('/')
        return
    Questoes().render()

@ui.page('/tarefa_concluida')
def tarefa_concluida_page(id: str = None):
    if not app.storage.user.get('token'):
        ui.navigate.to('/')
        return

    TarefaConcluida().render(id)

@ui.page('/gabarito')
def gabarito_page(id: str = None):
    if not app.storage.user.get('token'):
        ui.navigate.to('/')
        return
    Gabarito().render(id)

@ui.page('/login')
def login_page():
    Login().render()

@ui.page('/cadastro')
def cadastro_page():
    Cadastro().render()

@ui.page('/logout')
def logout():
    app.storage.user.clear()
    ui.navigate.to('/')

ui.run_with(app_fastapi, storage_secret='segredo123')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=10000, host='0.0.0.0', storage_secret='segredo123', reload=True)