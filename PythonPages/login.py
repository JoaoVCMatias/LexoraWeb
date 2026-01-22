import sys
import httpx
from pathlib import Path
from nicegui import ui, app

class Login:
    # Caminhos e URLs
    LOGO_PATH = '/images/logo.png'
    API_LOGIN_URL = "https://lexora-api.onrender.com/usuarios/Login"

    def __init__(self):
        self.configure_static_paths()

    @staticmethod
    def configure_static_paths():
        try:
            script_dir = Path(__file__).parent.resolve()
            root_dir = script_dir.parent
            images_dir = root_dir / 'images'
            if not images_dir.is_dir():
                print(f"Aviso: Diretório de imagens não encontrado em: {images_dir}", file=sys.stderr)
                return
            try:
                app.add_static_files('/images', str(images_dir))
            except ValueError: pass 
        except Exception as e:
            print(f"Erro ao configurar caminhos: {e}", file=sys.stderr)

    async def handle_login(self):
        email = self.email_input.value
        password = self.password_input.value

        if not email or not password:
            ui.notify('Por favor, preencha o E-mail e a Senha.', color='negative')
            return

        login_data = {"email": email, "senha": password}

        try:
            async with httpx.AsyncClient() as client:
                print(f"Enviando para API: {login_data}")
                # Timeout um pouco maior para evitar erros de rede
                response = await client.post(self.API_LOGIN_URL, json=login_data, timeout=15.0)
                
                response.raise_for_status()
                
                # --- LÓGICA DE TOKEN CORRIGIDA ---
                token_raw = response.text.strip().replace('"', '')
                token = token_raw if len(token_raw) > 20 and '.' in token_raw else None
                
                # Fallback JSON se necessário
                if not token:
                    try:
                        data = response.json()
                        token = data.get('token') or data.get('access_token')
                    except: pass

                if not token:
                    ui.notify('Erro: Token inválido.', color='negative')
                    return

                # --- REDIRECIONAMENTO QUE FUNCIONA ---
                print(f"✅ Token OK! Redirecionando...")
                ui.notify('Login realizado com sucesso!', color='positive')
                
                # Passa o token via URL para o main.py pegar
                ui.navigate.to(f'/?auth_token={token}')

        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status in (401, 403, 404):
                ui.notify('E-mail ou senha incorretos.', color='negative')
            else:
                ui.notify(f'Erro no servidor: {status}', color='negative')
        except Exception as e:
            ui.notify(f'Erro inesperado: {str(e)}', color='negative')

    def go_to_signup(self):
        ui.navigate.to('/cadastro')

    def render(self):
        """Monta a interface visual do login (LAYOUT ORIGINAL)."""
        ui.query('body').style('background-color: #FFFFFF; overflow: hidden;')

        with ui.row().classes('w-full h-screen justify-center items-center'):
            with ui.column().classes('gap-y-2 items-center'):

                # Logo e Textos
                ui.image(self.LOGO_PATH).classes('w-28 mb-4').props('fit=contain')
                ui.label('BEM-VINDO DE VOLTA').classes('text-2xl font-bold text-gray-800')
                ui.label('Acesse sua conta para continuar a aprender!').classes('text-sm text-gray-600 mb-6')

                # Inputs estilizados
                with ui.input(label='E-mail', placeholder='Ex: nome@email.com') \
                        .props('outlined rounded').classes('w-96') as self.email_input:
                    with self.email_input.add_slot('prepend'):
                        ui.icon('mail_outline')

                with ui.input(label='Senha', placeholder='•••••••••••••••',
                              password=True, password_toggle_button=True) \
                        .props('outlined rounded').classes('w-96') as self.password_input:
                    with self.password_input.add_slot('prepend'):
                        ui.icon('lock_outline')

                # Link Esqueci Senha
                ui.link('Esqueci minha senha', '#') \
                    .classes('self-end text-sm text-gray-600 hover:text-gray-800 -mt-2 mb-4')

                # Botões
                ui.button('Entrar na conta', on_click=self.handle_login) \
                    .classes('w-96 text-lg normal-case text-white py-3') \
                    .props('color="blue-700" rounded')

                ui.button('Não possuo conta ainda', on_click=self.go_to_signup) \
                    .classes('w-96 text-lg normal-case text-gray-700 py-3') \
                    .props('outline rounded color="grey-7"')
