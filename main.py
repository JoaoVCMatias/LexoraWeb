from nicegui import ui
import os
from PythonPages.homepage import HomePage
from PythonPages.cadastro import Cadastro  # importe a classe de cadastro

# --- ROTAS DO APP ---

@ui.page('/')
def homepage():
    """Página inicial"""
    HomePage().render()

@ui.page('/cadastro')
def cadastro():
    """Página de cadastro"""
    Cadastro().render()

# --- EXECUÇÃO DO SERVIDOR ---

if __name__ in {"__main__", "__mp_main__"}:
    port = int(os.environ.get("PORT", 10000))
    ui.run(host="0.0.0.0", port=port)
