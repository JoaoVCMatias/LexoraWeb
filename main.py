from nicegui import ui, app

from PythonPages.homepage import HomePage
from PythonPages.cadastro import Cadastro
from PythonPages.login import Login
from PythonPages.telainicial import TelaInicial
from PythonPages.questoes import Questoes
from PythonPages.pos_cadastro import PosCadastro


@ui.page('/')
def main_page(auth_token: str = None):
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


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(host='0.0.0.0', port=10000, storage_secret='segredo123', reload=True)
