from nicegui import ui, app
from pathlib import Path

class HomePage:
    def __init__(self):

        base_dir = Path(__file__).parent.resolve()
        images_dir = (base_dir.parent / 'images').resolve()
        
        try:
            app.add_static_files('/images', str(images_dir))
        except ValueError:
            pass 

        self.LOGO_PATH = '/images/logo.png'
        self.HOMEPAGE_IMG_PATH = '/images/homepage.png'

    def handle_create_account(self):
        ui.navigate.to('/cadastro')

    def handle_go_to_login(self):
        ui.navigate.to('/login')

    def render(self):
 
        ui.add_head_html("""
        <style>
           
            body { margin: 0; padding: 0; overflow: hidden !important; background-color: white; }
            .nicegui-content { padding: 0 !important; margin: 0 !important; width: 100%; height: 100%; }
            
            .imagem-fundo-pc {
                position: fixed;
                bottom: 0;
                right: 0;
                z-index: 0;
                width: 350px;     
                opacity: 1.0;
                pointer-events: none;   
                display: block;        
            }


            @media (max-width: 1000px) {
                .imagem-fundo-pc {
                    display: none !important; 
                }
            }
        </style>
        """)

        with ui.element('div').classes('w-screen h-screen relative bg-white'):
            
            ui.image(self.HOMEPAGE_IMG_PATH).classes('imagem-fundo-pc')
            
            with ui.column().classes('w-full h-full flex flex-col justify-center items-center relative z-10'):
                
                ui.image(self.LOGO_PATH).classes('w-32 mb-4')
                
                ui.label('APRENDIZADO DESCOMPLICADO DE IDIOMAS')\
                    .classes('text-2xl font-bold text-gray-800 text-center px-4 leading-tight')
                
                ui.label('Leva menos de um minuto para começar gratuitamente!')\
                    .classes('text-sm text-gray-600 mb-6 text-center px-4')

                ui.button('Criar nova conta', on_click=self.handle_create_account) \
                    .classes('w-80 md:w-96 text-lg normal-case text-white py-3') \
                    .props('color=blue-700 rounded')

                ui.button('Entrar em conta existente', on_click=self.handle_go_to_login) \
                    .classes('w-80 md:w-96 text-lg normal-case text-gray-700 py-3') \
                    .props('outline rounded color=grey-7')