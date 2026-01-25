from nicegui import ui, app
import requests
import sys
from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime

# =========================
# CONFIG API
# =========================
API_URL_BASE = 'https://lexora-api.onrender.com/'

URL_CRIAR_USUARIO = urljoin(API_URL_BASE, 'usuarios/')
URL_LOGIN = urljoin(API_URL_BASE, 'usuarios/Login')
URL_USUARIO_INFORMACAO = urljoin(API_URL_BASE, 'usuarios/UsuarioInformacao')
URL_IDIOMA_EXPERIENCIA = urljoin(API_URL_BASE, 'usuarios/Usuario/IdiomaExperiencia')


# =========================
# HELPERS
# =========================
def setup_static_images() -> None:
    try:
        script_dir = Path(__file__).parent.resolve()
        root_dir = script_dir.parent
        images_dir = root_dir / 'images'
        if not images_dir.is_dir():
            images_dir = script_dir / 'images'
        
        if not images_dir.is_dir():
            print(f"AVISO: Diretório de imagens não encontrado: {images_dir}")
        else:
            try:
                app.add_static_files('/images', str(images_dir))
            except ValueError:
                pass
    except Exception as e:
        print(f"Erro ao configurar arquivos estáticos: {e}", file=sys.stderr)


def get_auth_headers(token: str) -> dict:
    return {'Authorization': f'Bearer {token}'}


def br_date_to_iso_z(date_br: str) -> str:
    dt = datetime.strptime(date_br.strip(), '%d/%m/%Y')
    return dt.strftime('%Y-%m-%dT00:00:00.000Z')


# =========================
# CLASSE EXPORTÁVEL
# =========================
class PosCadastro:
    PRIMARY_BLUE = '#1153BE'
    FIELD_BG = '#F7F8FA'
    FIELD_BORDER = '#E5E7EB'
    LABEL_COLOR = '#4B5563'
    SUBTLE = '#6B7280'

    # Apenas Inglês (ID 2)
    IDIOMAS = {2: 'Inglês'}

    EXPERIENCIAS = {
        1: 'Básico',
        2: 'Intermediário',
        3: 'Avançado',
    }

    OBJETIVOS = {
        1: 'Viagem',
        2: 'Trabalho',
        3: 'Morar fora',
        4: 'Tecnologia'
    }

    DISPONIBILIDADES = {
        1: 'Leve (0.5h por semana)',
        2: 'Moderado (1h por semana)',
        3: 'Intenso (2h por semana)'
    }

    def __init__(self):
        setup_static_images()

    def render(self):
        self._adicionar_estilos()

        def deslogar():
            if app.storage.user is not None:
                app.storage.user.clear()
            ui.navigate.to('/')

        def concluir_cadastro_e_criar_usuario():
            # Recupera dados salvos no passo 1 (cadastro.py)
            pending = app.storage.user.get('pending_signup')
            if not pending:
                ui.notify('Sessão de cadastro expirou. Volte e preencha novamente.', color='negative', position='top')
                ui.navigate.to('/cadastro')
                return

            # Validação dos campos
            if (not data_nascimento.value or not idioma_id.value or 
                not experiencia_id.value or not objetivo_id.value or 
                not disponibilidade_id.value):
                ui.notify('Preencha todos os campos!', color='negative', position='top')
                return

            try:
                data_iso = br_date_to_iso_z(data_nascimento.value)
            except Exception:
                ui.notify('Data inválida. Use DD/MM/AAAA.', color='negative', position='top')
                return

            # 1) Criar usuário na API
            try:
                resp_create = requests.post(
                    URL_CRIAR_USUARIO,
                    json={'nome': pending['nome'], 'email': pending['email'], 'senha': pending['senha']},
                    timeout=20,
                )
            except Exception as e:
                ui.notify(f'Erro de conexão ao criar usuário: {e}', color='negative', position='top')
                return

            if resp_create.status_code not in (200, 201):
                ui.notify(f'Erro ao criar usuário ({resp_create.status_code}): {resp_create.text}', color='negative', position='top')
                return

            # 2) Fazer Login para obter token
            try:
                resp_login = requests.post(
                    URL_LOGIN,
                    json={'email': pending['email'], 'senha': pending['senha']},
                    timeout=20,
                )
            except Exception as e:
                ui.notify(f'Erro de conexão ao logar: {e}', color='negative', position='top')
                return

            if resp_login.status_code != 200:
                ui.notify(f'Erro ao logar ({resp_login.status_code}): {resp_login.text}', color='negative', position='top')
                return

            token = (resp_login.text or '').strip().strip('"')
            if not token:
                ui.notify('Login não retornou token.', color='negative', position='top')
                return

            headers = get_auth_headers(token)

            # 3) Enviar Informações Complementares (UsuarioInformacao)
            payload_info = {
                'id_idioma': int(idioma_id.value),
                'id_experiencia_idioma': int(experiencia_id.value),
                'id_objetivo': int(objetivo_id.value),
                'id_disponibilidade': int(disponibilidade_id.value),
                'data_nascimento': data_iso,
            }

            try:
                resp_info = requests.post(
                    URL_USUARIO_INFORMACAO,
                    json=payload_info,
                    headers=headers,
                    timeout=20,
                )
            except Exception as e:
                ui.notify(f'Erro de conexão ao salvar informações: {e}', color='negative', position='top')
                return

            if resp_info.status_code not in (200, 201):
                ui.notify(f'Erro UsuarioInformacao ({resp_info.status_code}): {resp_info.text}', color='negative', position='top')
                return

            # 4) Salvar Idioma/Experiência
            # CORREÇÃO CRÍTICA: Usando params= para enviar na Query String
            try:
                resp_ie = requests.post(
                    URL_IDIOMA_EXPERIENCIA,
                    params={
                        'id_idioma': int(idioma_id.value),
                        'id_experiencia_idioma': int(experiencia_id.value),
                    },
                    headers=headers,
                    timeout=20,
                )
            except Exception as e:
                ui.notify(f'Erro de conexão IdiomaExperiencia: {e}', color='negative', position='top')
                return

            if resp_ie.status_code not in (200, 201):
                ui.notify(f'Erro IdiomaExperiencia ({resp_ie.status_code}): {resp_ie.text}', color='negative', position='top')
                return

            # Finaliza e vai pro login
            app.storage.user['token'] = token
            app.storage.user.pop('pending_signup', None)

            ui.notify('Cadastro concluído com sucesso!', color='positive', position='top')
            ui.navigate.to('/login')

        # ================= UI =================
        with ui.row().classes('w-full justify-center items-center min-h-screen p-4'):
            with ui.column().classes('items-center w-full').style('max-width:520px; z-index:10;'):
                ui.image('/images/logo.png').style('margin-bottom:10px; max-width:120px;')
                ui.label('ÚLTIMO PASSO').style(
                    f'color:{self.LABEL_COLOR}; font-size:14px; font-weight:800; letter-spacing:0.5px; margin:2px 0 2px 0;'
                )
                ui.label('Informe o seguinte para iniciar a sua primeira lição').style(
                    f'color:{self.SUBTLE}; font-size:12.5px; margin-bottom:18px; text-align:center'
                )

                with ui.element('div').classes('pc-card w-full'):
                    # Data de Nascimento
                    ui.html('<div class="pc-label">Data de nascimento</div>', sanitize=False)
                    with ui.element('div').classes('pc-field-wrap'):
                        with ui.element('div').classes('pc-row-box'):
                            ui.icon('calendar_month').classes('pc-qicon')
                            data_nascimento = (
                                ui.input('', placeholder='DD/MM/AAAA')
                                .props('borderless dense mask="##/##/####" fill-mask')
                                .classes('pc-field')
                            )

                    # Idioma
                    ui.html('<div class="pc-label">Idioma</div>', sanitize=False)
                    with ui.element('div').classes('pc-field-wrap'):
                        with ui.element('div').classes('pc-row-box'):
                            ui.icon('language').classes('pc-qicon')
                            # Define value=2 para vir selecionado por padrão como Inglês
                            idioma_id = ui.select(self.IDIOMAS, value=2).props('borderless dense').classes('pc-field')

                    # Conhecimento Prévio
                    ui.html('<div class="pc-label">Conhecimento prévio</div>', sanitize=False)
                    with ui.element('div').classes('pc-field-wrap'):
                        with ui.element('div').classes('pc-row-box'):
                            ui.icon('star').classes('pc-qicon')
                            experiencia_id = ui.select(self.EXPERIENCIAS, value=None).props('borderless dense').classes('pc-field')

                    # Objetivo
                    ui.html('<div class="pc-label">Objetivo principal</div>', sanitize=False)
                    with ui.element('div').classes('pc-field-wrap'):
                        with ui.element('div').classes('pc-row-box'):
                            ui.icon('flag').classes('pc-qicon')
                            objetivo_id = ui.select(self.OBJETIVOS, value=None) \
                                .props('borderless dense') \
                                .classes('pc-field')

                    # Disponibilidade
                    ui.html('<div class="pc-label">Disponibilidade diária</div>', sanitize=False)
                    with ui.element('div').classes('pc-field-wrap'):
                        with ui.element('div').classes('pc-row-box'):
                            ui.icon('schedule').classes('pc-qicon')
                            disponibilidade_id = ui.select(self.DISPONIBILIDADES, value=None) \
                                .props('borderless dense') \
                                .classes('pc-field')

                    ui.button('Concluir cadastro', on_click=concluir_cadastro_e_criar_usuario, color=self.PRIMARY_BLUE).classes('pc-btn')
                    ui.button('Deslogar', on_click=deslogar, color='white').classes('pc-btn2')

        ui.image('/images/ImageM.png').classes('sideimg').style(
            'position:fixed; right:60px; bottom:28px; max-width:360px; max-height:380px; z-index:1;'
        )

    def _adicionar_estilos(self):
        ui.add_head_html(f"""
        <style>
        body {{ background: #FCFCFC; margin: 0; }}

        .pc-card {{
            width: 100%;
            max-width: 520px;
            margin: 0 auto;
            background: #fff;
            border-radius: 18px;
            box-shadow: 0 2px 18px #eee;
            padding: 26px 26px 22px 26px;
            border:none;
            box-sizing: border-box;
        }}

        .pc-field-wrap {{ position:relative; margin-bottom:16px; }}

        .pc-row-box {{
            position: relative;
            display: flex;
            align-items: center;
            background: {self.FIELD_BG};
            border-radius: 12px;
            border: 1px solid {self.FIELD_BORDER};
            height: 50px;
            width: 100%;
            padding-left: 14px;
            box-sizing: border-box;
            font-size: 16px;
        }}

        .pc-field {{
            flex: 1;
            margin-left: 8px;
            font-size: 15px;
        }}
        .pc-field .q-field__control {{ height: 100% !important; min-height: unset !important; }}
        .pc-field .q-field__native {{ padding: 0 !important; color: {self.LABEL_COLOR}; }}

        .pc-label {{
            color: {self.LABEL_COLOR};
            font-size: 13px;
            margin-bottom: 6px;
            font-weight: 700;
        }}

        .pc-qicon {{
            color: {self.SUBTLE};
            opacity: 0.85;
        }}

        .pc-btn {{
            width:100%;
            height:50px;
            border-radius:12px;
            font-size:16px;
            font-weight:800;
            margin-top:6px;
            margin-bottom:12px;
            text-transform:none;
        }}

        .pc-btn2 {{
            width:100%;
            height:50px;
            border-radius:12px;
            font-size:15px;
            color:{self.SUBTLE};
            border:1px solid {self.FIELD_BORDER};
            background:#fff;
            text-transform:none;
        }}

        @media (max-width: 1100px) {{
            .sideimg {{ display:none !important; }}
        }}

        @media (max-width: 520px) {{
            .pc-card {{ padding: 20px 18px; }}
            .pc-btn, .pc-btn2 {{ height: 46px; font-size: 15px; }}
        }}
        </style>
        """)
