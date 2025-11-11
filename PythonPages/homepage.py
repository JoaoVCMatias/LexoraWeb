from nicegui import ui, app
from pathlib import Path

class HomePage:
    def __init__(self):
        images_dir = Path(__file__).parent.parent / 'images'
        app.add_static_files('/images', str(images_dir))
        self.LOGO_PATH = '/images/logo.png'
        self.HOMEPAGE_IMG_PATH = '/images/homepage.png'

    def handle_create_account(self):
        # Navega para a página de cadastro
        ui.run_javascript("window.location.href = '/cadastro';")

    def handle_go_to_login(self):
        ui.run_javascript("window.location.href = '/login';")
        ui.notify('Indo para a página de login...')

    def render(self):
        ui.query('body').style('background-color: #FFFFFF; overflow: hidden;')

        with ui.row().classes('w-full h-screen justify-center items-center'):
            with ui.column().classes('items-center gap-y-4'):
                ui.image(self.LOGO_PATH).classes('w-32 mb-4')
                ui.label('APRENDIZADO DESCOMPLICADO DE IDIOMAS').classes('text-2xl font-bold text-gray-800')
                ui.label('Leva menos de um minuto para começar gratuitamente!').classes('text-sm text-gray-600 mb-6')

                ui.button('Criar nova conta', on_click=self.handle_create_account) \
                    .classes('w-88 text-lg normal-case text-white py-3') \
                    .props('color=\"blue-700\" rounded')

                ui.button('Entrar em conta existente', on_click=self.handle_go_to_login) \
                    .classes('w-88 text-lg normal-case text-gray-700 py-3') \
                    .props('outline rounded color=\"grey-7\"')

        ui.image(self.HOMEPAGE_IMG_PATH) \
            .classes('max-w-lg') \
            .style('position: absolute; bottom: 0; right: 0px;')


@ui.page('/')
def homepage():
    tela = HomePage()
    tela.render()
