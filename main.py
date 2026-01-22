from fastapi import FastAPI
from nicegui import ui, app  # Importado como 'app'

from PythonPages.homepage import HomePage
from PythonPages.cadastro import Cadastro
from PythonPages.login import Login
from PythonPages.telainicial import TelaInicial
from PythonPages.questoes import Questoes

app_fastapi = FastAPI()

# ✅ ROTA PRINCIPAL QUE LÊ O TOKEN DA URL
@ui.page('/')
def main_page(auth_token: str = None):
    # 1. Prioridade: Token vindo da URL (acabou de logar)
    # 2. Fallback: Token que já estava no storage
    token = auth_token or app.storage.user.get('token')
    
    # Se veio pela URL, salva no storage para o futuro
    if auth_token:
        app.storage.user['token'] = auth_token
        # Opcional: tentar salvar cookie em background (sem travar)
        # Usamos try/except no JS para não quebrar se algo der errado
        ui.run_javascript(f'document.cookie="lexora_token={auth_token}; path=/; max-age=604800;"')

    print(f"\n🔍 [HOME] Token presente? {'SIM' if token else 'NÃO'}")

    if token:
        TelaInicial().render()
    else:
        HomePage().render()
        
@ui.page('/questoes')
def questoes_page():
    # CORREÇÃO: Usar 'app' ao invés de 'nicegui_app'
    if not app.storage.user.get('token'):
        ui.navigate.to('/')
        return
        
    Questoes().render()

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
    # Adicionado host='0.0.0.0' e reload=True para facilitar dev
    ui.run(port=10000, host='0.0.0.0', storage_secret='segredo123', reload=True)
