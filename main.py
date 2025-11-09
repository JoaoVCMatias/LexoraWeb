from fastapi import FastAPI
from nicegui import ui
from PythonPages.homepage import HomePage
from PythonPages.cadastro import Cadastro

# Cria o app FastAPI
app = FastAPI()

# Registra as páginas do NiceGUI
@ui.page('/')
def homepage():
    HomePage().render()

@ui.page('/cadastro')
def cadastro_page():
    Cadastro().render()

# Conecta o NiceGUI com o app FastAPI
ui.run_with(app)

# Exporta o app FastAPI para o Render usar
fastapi_app = app

# Executa localmente
if __name__ in {"__main__", "__mp_main__"}:
    import os
    port = int(os.environ.get("PORT", 10000))
    ui.run(host="0.0.0.0", port=port)
