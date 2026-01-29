from nicegui import ui, app
from pathlib import Path
import httpx

API_BASE_URL = "https://lexora-api.onrender.com"

# Configuração de Imagens
try:
    base_dir = Path(__file__).parent.resolve()
    images_path = (base_dir.parent / 'images').resolve()
    if images_path.exists():
        app.add_static_files('/images', str(images_path))
except: pass

class TarefaConcluida:
    def __init__(self):
        self.token = app.storage.user.get('token')
        self.dados = {
            "pontos": "...",
            "precisao": "...",
            "tempo": "...",
            "sequencia": "..."
        }
        self.loading = True
        self.id_prova = None

    async def fetch_stats(self, id_prova):
        if not id_prova or not self.token:
            self.loading = False
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
            async with httpx.AsyncClient(headers=headers) as client:
                response = await client.get(f"{API_BASE_URL}/Questao/RelatorioDesempenho")
                if response.status_code == 200:
                    lista = response.json()
                    alvo = next((item for item in lista if str(item.get('id_conjunto_questao')) == str(id_prova)), None)
                    
                    if alvo:

                        try:

                            pt = int(float(alvo.get('pontos', 0))) 
                            self.dados["pontos"] = str(pt)
                        except:
                            self.dados["pontos"] = "0"
                            
                        try:
                            acc = float(alvo.get('porcentagem_acerto', 0))
                            if acc.is_integer():
                                self.dados["precisao"] = f"{int(acc)}%"
                            else:
                                self.dados["precisao"] = f"{acc:.1f}%"
                        except:
                            self.dados["precisao"] = "0%"
                        
                        tempo_cru = str(alvo.get('tempo', '00:00:00')).split('.')[0]
                        partes = tempo_cru.split(':')
                        
                        try:
                            if len(partes) == 3:
                                h, m, s = int(partes[0]), int(partes[1]), int(partes[2])
                                if h > 0: self.dados["tempo"] = f"{h}:{m:02}:{s:02}"
                                else: self.dados["tempo"] = f"{m:02}:{s:02}"
                            elif len(partes) == 2:
                                m, s = int(partes[0]), int(partes[1])
                                self.dados["tempo"] = f"{m:02}:{s:02}"
                            else:
                                self.dados["tempo"] = tempo_cru
                        except:
                            self.dados["tempo"] = tempo_cru
                        
                        self.dados["sequencia"] = str(alvo.get('sequencia_acerto', 0))

        except Exception as e:
            print(f"Erro ao buscar stats: {e}")
        finally:
            self.loading = False
            self.layout.refresh()

    def render(self, id: str = None):
        self.id_prova = id
        if self.loading:
            ui.timer(0.1, lambda: self.fetch_stats(id), once=True)
        self.layout()

    @ui.refreshable
    def layout(self):
        ui.query('body').style('background-color: #f9fafb;')
        
        with ui.column().classes('w-full min-h-screen items-center p-4'):
            
            with ui.row().classes('w-full max-w-6xl justify-between items-center mb-8'):
                ui.image('/images/logo.png').classes('w-24 md:w-32').props('fit=contain')

            with ui.card().classes('w-full max-w-5xl bg-white rounded-2xl shadow-sm p-8 md:p-16 items-center text-center'):
                
                ui.label("Tarefa concluída com sucesso!").classes('text-2xl md:text-4xl font-bold text-black mb-4')
                ui.label("Parabéns! Veja abaixo seu desempenho nesta atividade.").classes('text-gray-500 max-w-3xl text-sm md:text-lg mb-10')

                ui.image('/images/tarefa.png').classes('w-full max-w-sm md:max-w-md mb-12 h-auto')

                if self.loading:
                    ui.spinner('dots', size='lg')
                else:
                    with ui.grid().classes('w-full max-w-4xl grid-cols-2 md:grid-cols-4 gap-4 md:gap-6 mb-12'):
                        
                        def stat_card(valor, label):
                            with ui.column().classes('bg-blue-50 rounded-2xl p-6 items-center justify-center gap-1 overflow-hidden'):
                                ui.label(valor).classes('text-3xl md:text-4xl font-bold text-blue-900 text-center break-all leading-tight')
                                ui.label(label).classes('text-xs md:text-sm text-gray-600 font-medium')

                        stat_card(self.dados['tempo'], "Tempo Total")
                        stat_card(self.dados['pontos'], "Pontos")
                        stat_card(self.dados['precisao'], "Precisão")
                        stat_card(self.dados['sequencia'], "Sequência")

                with ui.row().classes('gap-4 flex-wrap justify-center w-full'):
                    
                    ui.button('Ir para página inicial', on_click=lambda: ui.navigate.to('/')) \
                        .classes('bg-blue-100 text-blue-800 hover:bg-blue-200 rounded-xl px-8 py-3 font-bold shadow-none normal-case text-base')

                    if self.id_prova:
                        ui.button('Checar gabarito', on_click=lambda: ui.navigate.to(f'/gabarito?id={self.id_prova}')) \
                            .classes('bg-blue-700 text-white hover:bg-blue-800 rounded-xl px-8 py-3 font-bold shadow-none normal-case text-base')