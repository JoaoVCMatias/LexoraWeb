import sys
import httpx
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
API_LOGIN_URL = "https://lexora-api.onrender.com/usuarios/Login"


async def handle_login():
    email = email_input.value
    password = password_input.value
    
    if not email or not password:
        ui.notify('Por favor, preencha o E-mail e a Senha.', color='negative')
        return

    login_data = {
        "email": email,
        "senha": password 
    }

    try:

        async with httpx.AsyncClient() as client:
            print(f"Enviando para API: {login_data}")
            
            response = await client.post(API_LOGIN_URL, json=login_data)
            response.raise_for_status() 
            api_response_data = response.json()
            
            ui.notify('Login realizado com sucesso!', color='positive')
            
            print(f"Resposta da API: {api_response_data}")

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401 or e.response.status_code == 404:
            ui.notify('E-mail ou senha inválidos.', color='negative')
        else:
            ui.notify(f'Erro da API: {e.response.status_code}', color='negative')
        print(f"Erro HTTP: {e}")
        
    except httpx.RequestError as e:
        ui.notify('deu ruim na api.', color='negative')
        print(f"Erro de Rede: {e}")
        
    except Exception as e:
        ui.notify(f'ocorreu um erro inesperado: {e}', color='negative')
        print(f"Erro Inesperado: {e}")


def go_to_signup():
    print("Navegando para a página de cadastro")

    ui.notify('Indo para a página de cadastro...', color='info')

ui.query('body').style(f'background-color: #FFFFFF; overflow: hidden;')

with ui.row().classes('w-full h-screen justify-center items-center'):
    with ui.column().classes('gap-y-2 items-center'):
        
        ui.image(LOGO_PATH).classes('w-28 mb-4')
        
        ui.label('BEM-VINDO DE VOLTA').classes('text-2xl font-bold text-gray-800')
        
        ui.label('Acesse sua conta para continuar a aprender!').classes('text-sm text-gray-600 mb-6')
        
        with ui.input(label='E-mail', placeholder='Ex: nome@email.com') \
            .props('outlined rounded').classes('w-96') as email_input:
        
            with email_input.add_slot('prepend'):
                ui.icon('mail_outline')
        
        with ui.input(label='Senha', placeholder='•••••••••••••••', password=True, password_toggle_button=True) \
            .props('outlined rounded').classes('w-96') as password_input:
            
            with password_input.add_slot('prepend'):
                ui.icon('lock_outline')

        ui.link('Esqueci minha senha', '#') \
            .classes('self-end text-sm text-gray-600 hover:text-gray-800 -mt-2 mb-4')
        
        ui.button('Entrar na conta', on_click=handle_login) \
            .classes('w-96 text-lg normal-case text-white py-3') \
            .props('color="blue-700" rounded')

        ui.button('Não possuo conta ainda', on_click=go_to_signup) \
            .classes('w-96 text-lg normal-case text-gray-700 py-3') \
            .props('outline rounded color="grey-7"')

ui.run(title='Lexora - Login')