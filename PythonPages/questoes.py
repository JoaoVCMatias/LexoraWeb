import os
import json
import httpx
from nicegui import app, ui
from pathlib import Path

# Configuração da API
API_BASE_URL = "https://lexora-api.onrender.com"

# Configuração de Imagens (Static)
try:
    script_dir = Path(__file__).parent.resolve()
    images_dir = script_dir.parent / 'images'
    try:
        app.add_static_files('/local_images', str(images_dir))
    except ValueError: pass
except Exception: pass

class QuizState:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.indice_atual = 0
        self.numero_questao_atual = 1
        self.questoes = [] 
        self.carregando = True 
        self.id_conjunto_atual = None 
        self.total_questoes = 0
        self.ja_iniciou_busca = False

# Estado global da página
state = QuizState()

# ✅ A CLASSE QUE O MAIN.PY ESTÁ PROCURANDO
class Questoes:
    def __init__(self):
        # Tenta pegar token do storage ou da URL (caso tenha vindo de login recente)
        self.token = app.storage.user.get('token')
        
        if not self.token:
            print("⚠️ Token não encontrado em Questoes! Redirecionando...")
            ui.navigate.to('/')
    
    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def carregar_questoes_api(self, forcar_atualizacao=False):
        if len(state.questoes) > 0 and not forcar_atualizacao:
            state.carregando = False
            self.renderizar_conteudo.refresh()
            return

        if not forcar_atualizacao:
            state.carregando = True
            self.renderizar_conteudo.refresh()
        
        try:
            async with httpx.AsyncClient(headers=self.get_headers(), follow_redirects=True) as client:
                response = await client.get(f"{API_BASE_URL}/Questao/ConjuntoQuestao", timeout=30.0)
                
                if response.status_code == 200:
                    dados_api = response.json()
                    state.id_conjunto_atual = dados_api.get('id_conjunto_questao')
                    lista_crua = dados_api.get('questoes', [])
                    
                    questoes_formatadas = []
                    for q in lista_crua:
                        try:
                            raw_op = q.get('json_opcao')
                            if raw_op:
                                if "'" in raw_op and '"' not in raw_op:
                                    raw_op = raw_op.replace("'", '"')
                                lista_opcoes = json.loads(raw_op)
                            else:
                                lista_opcoes = []
                        except:
                            lista_opcoes = []

                        opcoes_ui = []
                        letras = ['A', 'B', 'C', 'D', 'E']
                        for i, texto in enumerate(lista_opcoes):
                            letra = letras[i] if i < len(letras) else str(i)
                            opcoes_ui.append({
                                "letra": letra, 
                                "texto": texto, 
                                "indice": i 
                            })

                        questoes_formatadas.append({
                            "id": q.get('id_questao'),
                            "titulo": "Atividade Prática",
                            "pergunta_texto": q.get('descricao_questao'),
                            "opcoes": opcoes_ui,
                            "resposta_correta_texto": q.get('resposta') 
                        })
                    
                    state.questoes = questoes_formatadas
                    state.total_questoes = len(state.questoes)
                
                elif response.status_code == 403:
                    ui.notify('Sessão expirada.', type='negative')
                    ui.navigate.to('/login')
                elif response.status_code == 404:
                     state.questoes = []
                    
        except Exception as e:
            ui.notify(f'Erro de conexão: {str(e)}', type='negative')
        finally:
            state.carregando = False
            if not forcar_atualizacao:
                self.renderizar_conteudo.refresh()

    async def registrar_resposta_api(self, id_questao, indice_numerico):
        if not state.id_conjunto_atual: return False

        url = (f"{API_BASE_URL}/Questao/ResponderQuestao/"
            f"{id_questao}/{indice_numerico}/{state.id_conjunto_atual}")

        try:
            async with httpx.AsyncClient(headers=self.get_headers()) as client:
                response = await client.post(url)
                if response.status_code == 200:
                    return response.text.strip().lower() == 'true'
                return False
        except Exception:
            return False

    def proxima(self):
        state.indice_atual += 1
        state.numero_questao_atual += 1
        self.renderizar_conteudo.refresh()

    def sair(self):
        state.reset()
        ui.navigate.to('/')

    @ui.refreshable
    def renderizar_conteudo(self):
        if not state.ja_iniciou_busca:
            state.ja_iniciou_busca = True
            ui.timer(0.1, lambda: self.carregar_questoes_api(False), once=True)

        if state.carregando:
            with ui.column().classes('w-full h-screen items-center justify-center'):
                ui.spinner(size='lg')
                ui.label('Carregando atividade...').classes('text-gray-500')
            return

        if not state.questoes or state.indice_atual >= len(state.questoes):
            with ui.column().classes('w-full h-screen items-center justify-center gap-4'):
                if not state.questoes:
                    ui.icon('warning', size='4rem', color='orange')
                    ui.label('Sem questões disponíveis.').classes('text-xl')
                else:
                    ui.icon('emoji_events', size='4rem', color='green')
                    ui.label('Atividade Concluída!').classes('text-2xl font-bold')
                
                ui.button('Voltar ao Menu', on_click=self.sair).props('color=primary')
            return 

        dados = state.questoes[state.indice_atual]

        with ui.row().classes('w-full justify-between items-center px-4 py-2 bg-white shadow-sm'):
            with ui.row().classes('items-center gap-2'):
                ui.icon('school', color='primary', size='sm') 
                ui.label('Lexora').classes('text-lg font-bold text-gray-800')
            ui.button('Sair', on_click=self.sair).props('flat dense no-caps icon-right=logout text-color=grey-7')

        with ui.column().classes('w-full max-w-5xl mx-auto p-4'):
            
            with ui.column().classes('w-full mb-4 gap-1'):
                with ui.element('div').classes('w-full h-3 bg-blue-100 rounded-full overflow-hidden'):
                    pct = (state.numero_questao_atual / state.total_questoes) * 100 if state.total_questoes > 0 else 0
                    ui.element('div').classes('h-full bg-[#1e2e45]').style(f'width: {pct}%')
                ui.label(f'{state.numero_questao_atual} / {state.total_questoes}').classes('text-xs text-gray-500 self-end')

            with ui.card().classes('w-full rounded-[20px] shadow-sm border border-gray-100 p-6'):
                ui.label(dados['titulo']).classes('text-xl font-bold text-gray-900')

                with ui.row().classes('w-full justify-between items-start mt-4 gap-6 wrap'):
                    with ui.column().classes('w-full md:w-1/3 items-center justify-center min-h-[200px]'):
                        ui.image('/local_images/img_questao.png').classes('max-w-[250px] w-full object-contain')

                    with ui.column().classes('w-full md:w-3/5 gap-6'):
                        with ui.row().classes('bg-blue-50 rounded-lg px-6 py-4 items-center w-full'):
                            ui.label(dados['pergunta_texto']).classes('text-lg font-medium text-gray-900 leading-tight')

                        lista_botoes_refs = []

                        async def selecionar_alternativa(btn_clicado, opcao_obj):
                            for btn, _, _ in lista_botoes_refs: btn.disable()
                            
                            acertou_bool = await self.registrar_resposta_api(dados['id'], opcao_obj['indice'])
                            dados_atualizados = state.questoes[state.indice_atual]
                            texto_correto = dados_atualizados.get('resposta_correta_texto')

                            if acertou_bool:
                                btn_clicado.classes('!bg-green-100 !border-green-500 !text-green-900')
                                for b, _, icon in lista_botoes_refs:
                                    if b == btn_clicado: icon.props('name=check color=green'); icon.set_visibility(True)
                                ui.notify('Resposta Correta!', type='positive')
                            else:
                                btn_clicado.classes('!bg-red-100 !border-red-500 !text-red-900')
                                for b, _, icon in lista_botoes_refs:
                                    if b == btn_clicado: icon.props('name=close color=red'); icon.set_visibility(True)
                                ui.notify('Resposta Incorreta.', type='negative')

                                if texto_correto:
                                    for btn, op, icon in lista_botoes_refs:
                                        if str(op['texto']).strip().lower() == str(texto_correto).strip().lower():
                                            btn.classes('!bg-green-100 !border-green-500 !text-green-900')
                                            icon.props('name=check color=green'); icon.set_visibility(True)

                            btn_proxima.set_visibility(True)

                        with ui.column().classes('w-full gap-3'):
                            for opcao in dados['opcoes']:
                                btn = ui.button().classes(
                                    'w-full bg-white border border-gray-300 text-gray-700 '
                                    'rounded-lg px-4 py-3 text-left normal-case hover:bg-gray-50 shadow-sm transition-all'
                                ).props('flat')
                                
                                with btn:
                                    with ui.row().classes('w-full items-center gap-4 no-wrap'):
                                        ui.label(opcao['letra']).classes('font-bold text-blue-800 bg-blue-50 px-2 py-1 rounded text-sm')
                                        ui.label(opcao['texto']).classes('text-base font-medium grow')
                                        icone = ui.icon('check', size='sm').classes('opacity-0'); icone.set_visibility(False)

                                btn.on('click', lambda b=btn, o=opcao: selecionar_alternativa(b, o))
                                lista_botoes_refs.append((btn, opcao, icone))

                with ui.row().classes('w-full justify-between items-center mt-8'):
                    ui.button('Pular', on_click=self.proxima).classes('text-gray-500').props('flat no-caps')
                    btn_proxima = ui.button('Próxima questão', on_click=self.proxima).classes('bg-[#1e2e45] text-white font-bold px-6 rounded-lg normal-case').props('unelevated icon-right=arrow_forward')
                    btn_proxima.set_visibility(False)

    def render(self):
        ui.query('body').style('background-color: #f8fafc; margin: 0; padding: 0;')
        if state.indice_atual == 0 and not state.ja_iniciou_busca:
            state.reset()
        self.renderizar_conteudo()
