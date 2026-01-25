from nicegui import ui, app
import sys
from pathlib import Path

# Defina a URL base aqui para evitar erros (mantida, mas não usamos POST aqui)
API_URL_BASE = 'https://lexora-api.onrender.com/'


class Cadastro:
    PRIMARY_BLUE = '#1153BE'
    FIELD_BG = '#F7F8FA'
    FIELD_BORDER = '#E5E7EB'
    LABEL_COLOR = '#4B5563'
    SUBTLE = '#6B7280'

    def __init__(self):
        """Configura caminhos de imagens (pasta static/images)"""
        try:
            script_dir = Path(__file__).parent.resolve()
            root_dir = script_dir.parent  # sobe até a raiz
            images_dir = root_dir / 'images'

            # Fallback: se não achar na raiz, tenta na pasta atual
            if not images_dir.is_dir():
                images_dir = script_dir / 'images'

            if not images_dir.is_dir():
                # Apenas avisa em vez de fechar o programa
                print(f"AVISO: Diretório de imagens não encontrado: {images_dir}")
            else:
                # Disponibiliza /images no servidor NiceGUI
                try:
                    app.add_static_files('/images', str(images_dir))
                except ValueError:
                    pass  # Evita erro se já estiver adicionado
        except Exception as e:
            print(f"Erro ao configurar arquivos estáticos: {e}", file=sys.stderr)

    # ------------------------------------------------------------
    #  Renderização da página
    # ------------------------------------------------------------
    def render(self):
        self._adicionar_estilos()

        # Função para ir ao login
        def ir_para_login():
            ui.navigate.to('/login')

        # ✅ Alterado: Passo 1 do cadastro (valida -> salva -> navega para /pos-cadastro)
        def continuar_para_pos_cadastro():
            nome_val = nome.value
            email_val = email.value
            senha_val = senha.value
            confirmar_val = confirmar.value

            if not nome_val or not email_val or not senha_val or not confirmar_val:
                ui.notify('Preencha todos os campos!', color='negative', position='top')
                return

            if senha_val != confirmar_val:
                ui.notify('As senhas não conferem!', color='negative', position='top')
                return

            # Salva os dados para o próximo passo (pos_cadastro.py)
            app.storage.user['pending_signup'] = {
                "nome": nome_val,
                "email": email_val,
                "senha": senha_val,
            }

            ui.notify('Dados validados! Indo para o próximo passo...', color='positive', position='top')
            ui.navigate.to('/pos-cadastro')

        def campo_senha(ph, nome_img_eye, nome_img_eyef):
            with ui.element('div').classes('cad-row-box'):
                ui.image('/images/cadeado.png').classes('cad-icon')

                # .props('borderless dense') para alinhar o texto verticalmente
                campo = ui.input('', password=True, placeholder=ph) \
                    .props('borderless dense autocomplete=off') \
                    .classes('cad-field')

                eye_state = {'show': False}
                eye_img = ui.image(f'/images/{nome_img_eyef}').classes('eye-clicavel')

                def toggle_eye():
                    eye_state['show'] = not eye_state['show']
                    eye_img.set_source(f'/images/{nome_img_eye}' if eye_state['show'] else f'/images/{nome_img_eyef}')
                    type_target = "text" if eye_state['show'] else "password"
                    # Correção JS para alternar type
                    campo.props(f'type={type_target}')

                eye_img.on('click', toggle_eye)
            return campo

        # ---------------- Layout principal ----------------
        with ui.row().classes('w-full justify-center items-center min-h-screen p-4'):

            with ui.column().classes('items-center w-full').style('max-width:450px; margin-top:20px; z-index:10;'):
                ui.image('/images/logo.png').style('margin-bottom:8px; max-width:120px;')
                ui.label('CRIE SUA CONTA').style(
                    f'color:{self.PRIMARY_BLUE}; font-size:22px; font-weight:bold; margin:2px 0 4px 0; text-align:center;'
                )
                ui.label('Leva menos de um minuto para começar gratuitamente!').style(
                    f'color:{self.SUBTLE}; font-size:13px; margin-bottom:28px; text-align:center'
                )

                with ui.element('div').classes('cad-card w-full'):
                    # Nome
                    ui.html('<div class="cad-label">Nome completo</div>', sanitize=False)
                    with ui.element('div').classes('cad-field-wrap'):
                        with ui.element('div').classes('cad-row-box'):
                            ui.image('/images/user.png').classes('cad-icon')
                            nome = ui.input('', placeholder='Ex: Ana Maria Menezes').props('borderless dense').classes('cad-field')

                    # E-mail
                    ui.html('<div class="cad-label">E-mail</div>', sanitize=False)
                    with ui.element('div').classes('cad-field-wrap'):
                        with ui.element('div').classes('cad-row-box'):
                            ui.image('/images/mail.png').classes('cad-icon')
                            email = ui.input('', placeholder='Ex: nome@email.com').props('borderless dense').classes('cad-field')

                    # Senha
                    ui.html('<div class="cad-label">Senha</div>', sanitize=False)
                    with ui.element('div').classes('cad-field-wrap'):
                        senha = campo_senha('Escolha uma senha segura', 'eye.png', 'eyef.png')

                    # Confirmar Senha
                    ui.html('<div class="cad-label">Confirmar senha</div>', sanitize=False)
                    with ui.element('div').classes('cad-field-wrap'):
                        confirmar = campo_senha('Digite novamente a senha', 'eye.png', 'eyef.png')

                    # ✅ Botão chama a nova função que vai para /pos-cadastro
                    ui.button('CRIAR CONTA', on_click=continuar_para_pos_cadastro, color=self.PRIMARY_BLUE).classes('cad-btn')

                    ui.button('JÁ POSSUO CONTA', on_click=ir_para_login, color='white').classes('cad-btn2')

        # Imagem lateral (Manequim)
        ui.image('/images/ImageM.png').classes('sideimg').style(
            'position:fixed; right:60px; bottom:28px; max-width:350px; max-height:380px; z-index:1;'
        )

    # ------------------------------------------------------------
    #  Estilos globais
    # ------------------------------------------------------------
    def _adicionar_estilos(self):
        ui.add_head_html(f"""
        <style>
        body {{ background: #FCFCFC; margin: 0; }}
        
        .cad-card {{
            width: 100%; 
            max-width: 450px; 
            margin: 0 auto; 
            background: #fff; 
            border-radius: 20px;
            box-shadow: 0 2px 18px #eee; 
            padding: 38px 36px 34px 36px; 
            border:none;
            box-sizing: border-box;
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
            flex: 1;
            margin-left: 8px;
            font-size: 16px;
        }}
        .cad-field .q-field__control {{ height: 100% !important; min-height: unset !important; }}
        .cad-field .q-field__native {{ padding: 0 !important; color: {self.LABEL_COLOR}; }}

        .cad-label {{ color: {self.LABEL_COLOR}; font-size:14px; margin-bottom:6px; font-weight:600; }}
        .cad-icon {{ width:24px; height:24px; opacity: 0.7; }}
        
        .eye-clicavel {{
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            width: 28px; height: 28px;
            cursor:pointer;
            z-index: 3;
        }}
        
        .cad-btn {{
            width:100%; height:52px; border-radius:12px; font-size:19px; font-weight:700; margin-bottom:16px;
        }}
        .cad-btn2 {{
            width:100%; height:52px; border-radius:12px; font-size:17px;
            color:{self.SUBTLE}; border:1px solid {self.FIELD_BORDER}; background:#fff;
        }}
        
        @media (max-width: 1100px){{
            .sideimg {{ display:none !important; }}
        }}
        
        @media (max-width: 500px){{
            .cad-card {{ padding: 25px 20px; }}
            .cad-btn, .cad-btn2 {{ height: 48px; font-size: 16px; }}
        }}
        </style>
        """)
