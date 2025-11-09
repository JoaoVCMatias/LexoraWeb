from nicegui import ui, app
import requests
import sys
from pathlib import Path
from config import API_URL_BASE


class Cadastro:
    PRIMARY_BLUE = '#1153BE'
    FIELD_BG = '#F7F8FA'
    FIELD_BORDER = '#E5E7EB'
    LABEL_COLOR = '#4B5563'
    SUBTLE = '#6B7280'
    #API_URL = 'https://lexora-api.onrender.com/usuarios/'
    API_URL = f'{API_URL_BASE}usuarios/'

    def __init__(self):
        """Configura caminhos de imagens (pasta static/images)"""
        try:
            script_dir = Path(__file__).parent.resolve()
            root_dir = script_dir.parent  # sobe até a raiz
            images_dir = root_dir / 'images'

            if not images_dir.is_dir():
                raise FileNotFoundError(f"Diretório de imagens não encontrado: {images_dir}")

            # Disponibiliza /images no servidor NiceGUI
            app.add_static_files('/images', str(images_dir))
        except Exception as e:
            print(f"Erro ao configurar arquivos estáticos: {e}", file=sys.stderr)
            sys.exit(1)

    # ------------------------------------------------------------
    #  Renderização da página
    # ------------------------------------------------------------
    def render(self):
        self._adicionar_estilos()

        def criar_conta():
            nome_val = nome.value
            email_val = email.value
            senha_val = senha.value
            confirmar_val = confirmar.value

            if not nome_val or not email_val or not senha_val or not confirmar_val:
                ui.notify('Preencha todos os campos!', color='negative')
                return

            if senha_val != confirmar_val:
                ui.notify('As senhas não conferem!', color='negative')
                return

            dados = {"nome": nome_val, "email": email_val, "senha": senha_val}

            try:
                resposta = requests.post(self.API_URL, json=dados)
                if resposta.status_code == 200:
                    ui.notify('Conta criada com sucesso!', color='positive')
                else:
                    ui.notify(f'Erro ao criar conta: {resposta.text}', color='negative')
            except Exception as e:
                ui.notify(f'Erro de conexão: {str(e)}', color='negative')

        def campo_senha(ph, nome_img_eye, nome_img_eyef):
            with ui.element('div').classes('cad-row-box'):
                ui.image('/images/cadeado.png').classes('cad-icon')
                campo = ui.input('', password=True, placeholder=ph).props('autocomplete=off').classes('cad-field')

                eye_state = {'show': False}
                eye_img = ui.image(f'/images/{nome_img_eyef}').classes('eye-clicavel')

                def toggle_eye():
                    eye_state['show'] = not eye_state['show']
                    eye_img.set_source(f'/images/{nome_img_eye}' if eye_state['show'] else f'/images/{nome_img_eyef}')
                    type_target = "text" if eye_state['show'] else "password"
                    ui.run_javascript(f"""
                        var el = document.querySelectorAll('input[placeholder="{ph}"]');
                        if (el.length) el[el.length-1].type = '{type_target}';
                    """)

                eye_img.on('click', toggle_eye)
            return campo

        # ---------------- Layout principal ----------------
        with ui.row().classes('w-full justify-center items-center min-h-screen'):
            with ui.column().classes('items-center').style('max-width:650px; width:100%; margin-top:30px;'):
                ui.image('/images/logo.png').style('margin-bottom:8px; max-width:120px;')
                ui.label('CRIE SUA CONTA').style(
                    f'color:{self.PRIMARY_BLUE}; font-size:22px; font-weight:bold; margin:2px 0 4px 0; text-align:center;'
                )
                ui.label('Leva menos de um minuto para começar gratuitamente!').style(
                    f'color:{self.SUBTLE}; font-size:13px; margin-bottom:28px; text-align:center'
                )

                with ui.element('div').classes('cad-card'):
                    # Nome
                    ui.html('<div class="cad-label">Nome completo</div>', sanitize=False)
                    with ui.element('div').classes('cad-field-wrap'):
                        with ui.element('div').classes('cad-row-box'):
                            ui.image('/images/user.png').classes('cad-icon')
                            nome = ui.input('', placeholder='Ex: Ana Maria Menezes da Silva').classes('cad-field')

                    # E-mail
                    ui.html('<div class="cad-label">E-mail</div>', sanitize=False)
                    with ui.element('div').classes('cad-field-wrap'):
                        with ui.element('div').classes('cad-row-box'):
                            ui.image('/images/mail.png').classes('cad-icon')
                            email = ui.input('', placeholder='Ex: nome@email.com').classes('cad-field')

                    # Senha
                    ui.html('<div class="cad-label">Senha</div>', sanitize=False)
                    with ui.element('div').classes('cad-field-wrap'):
                        senha = campo_senha('Escolha uma senha segura', 'eye.png', 'eyef.png')

                    # Confirmar Senha
                    ui.html('<div class="cad-label">Confirmar senha</div>', sanitize=False)
                    with ui.element('div').classes('cad-field-wrap'):
                        confirmar = campo_senha('Digite novamente a senha', 'eye.png', 'eyef.png')

                    ui.button('CRIAR CONTA', on_click=criar_conta, color=self.PRIMARY_BLUE).classes('cad-btn')
                    ui.button('JÁ POSSUO CONTA', color='white').classes('cad-btn2')

        ui.image('/images/ImageM.png').classes('sideimg').style(
            'position:fixed; right:60px; bottom:28px; max-width:350px; max-height:380px; z-index:1;'
        )

    # ------------------------------------------------------------
    #  Estilos globais
    # ------------------------------------------------------------
    def _adicionar_estilos(self):
        ui.add_head_html(f"""
        <style>
        body {{ background: #FCFCFC; }}
        .cad-card {{
            max-width: 450px; margin: 0 auto; background: #fff; border-radius: 20px;
            box-shadow: 0 2px 18px #eee; padding: 38px 36px 34px 36px; border:none;
        }}
        .cad-field-wrap {{ position:relative; margin-bottom:22px; }}
        .cad-row-box {{
            position: relative;
            display: flex;
            align-items: center;
            background: {self.FIELD_BG};
            border-radius: 12px;
            border: 1px solid {self.FIELD_BORDER};
            height: 52px;
            width: 100%;
            padding-left: 16px;
            box-sizing: border-box;
            font-size: 17px;
        }}
        .cad-field {{
            flex: 1 1 0%;
            border: none;
            background: transparent;
            font-size: 17px;
            color: {self.LABEL_COLOR};
            outline: none;
            margin-left: 9px;
            height: 100%;
            min-width: 0;
            padding: 0 44px 0 0;
            box-sizing: border-box;
            display: block;
            vertical-align: middle;
        }}
        .cad-field::placeholder {{
            color: #888;
            opacity: 1;
            font-size: 16px;
            vertical-align: middle;
        }}
        .cad-label {{ color: {self.LABEL_COLOR}; font-size:14px; margin-bottom:6px; font-weight:600; }}
        .cad-icon {{ width:24px; height:24px; }}
        .eye-clicavel {{
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            width: 28px; height: 28px;
            cursor:pointer;
            user-select:none;
            background: transparent;
            padding: 0;
            z-index: 3;
        }}
        .cad-btn {{
            width:100%; height:52px; border-radius:12px; font-size:19px; font-weight:700; margin-bottom:16px;
        }}
        .cad-btn2 {{
            width:100%; height:52px; border-radius:12px; font-size:17px;
            color:{self.SUBTLE}; border:1px solid {self.FIELD_BORDER}; background:#fff;
        }}
        @media (max-width: 900px){{
            .sideimg {{display:none !important;}}
        }}
        </style>
        """)
