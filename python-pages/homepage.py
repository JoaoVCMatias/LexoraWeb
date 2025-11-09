import sys
from pathlib import Path
from nicegui import ui, app

try:
    script_dir = Path(__file__).parent.resolve()
    root_dir = script_dir.parent
    images_dir = root_dir / 'images'
    
    if not images_dir.is_dir():
        raise FileNotFoundError(f"Diretório de imagens não encontrado em: {images_dir}")
        
    app.add_static_files('/images', str(images_dir))

except Exception as e:
    print(f"Erro crítico ao configurar os caminhos estáticos: {e}", file=sys.stderr)
    print("Verifique se a estrutura de pastas está correta.", file=sys.stderr)
    sys.exit(1)

LOGO_PATH = '/images/logo.png'
HOMEPAGE_IMG_PATH = '/images/homepage.png'

def handle_create_account():
    print("Navegando para 'Criar nova conta'")
    ui.notify('Indo para a página de cadastro...')

def handle_go_to_login():
    print("Navegando para 'Entrar em conta existente'")
    ui.notify('Indo para a página de login...')

ui.query('body').style(f'background-color: #FFFFFF; overflow: hidden;')

with ui.row().classes('w-full h-screen justify-center items-center'):
    
    with ui.column().classes('items-center gap-y-4'):
        
        ui.image(LOGO_PATH).classes('w-32 mb-4')
        
        ui.label('APRENDIZADO DESCOMPLICADO DE IDIOMAS') \
            .classes('text-2xl font-bold text-gray-800')
        
        ui.label('Leva menos de um minuto para começar gratuitamente!') \
            .classes('text-sm text-gray-600 mb-6')
        
        ui.button('Criar nova conta', on_click=handle_create_account) \
            .classes('w-88 text-lg normal-case text-white py-3') \
            .props('color="blue-700" rounded')
            
        ui.button('Entrar em conta existente', on_click=handle_go_to_login) \
            .classes('w-88 text-lg normal-case text-gray-700 py-3') \
            .props('outline rounded color="grey-7"')

ui.image(HOMEPAGE_IMG_PATH) \
    .classes('max-w-lg') \
    .style('position: absolute; bottom: 0; right: 0px;')

ui.run(title='Lexora - Bem-vindo!')