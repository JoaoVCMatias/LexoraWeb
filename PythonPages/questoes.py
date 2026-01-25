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

class Questoes:
    def __init__(self):
        # 1. Proteção: Garante que 'storage' não seja None
        storage = app.storage.user or {}
        self.token = storage.get('token')
        
        if not self.token:
            print("⚠️ Token não encontrado em Questoes! Redirecionando...")
            ui.navigate.to('/')
    
    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def carregar_questoes_api(self, forcar_atualizacao=False, apenas_atualizar=False):
        if len(state.questoes) > 0 and not forcar_atualizacao:
            state.carregando = False
            self.renderizar_conteudo.refresh()
            return

        if not forcar_atualizacao and not apenas_atualizar:
            state.carregando = True
            self.renderizar_conteudo.refresh()
        
        try:
            async with httpx.AsyncClient(headers=self.get_headers(), follow_redirects=True) as client:
                # --- Tenta BUSCAR prova existente (GET) ---
                response = await client.get(f"{API_BASE_URL}/Questao/ConjuntoQuestao", timeout=30.0)
                
                lista_crua = []
                dados_api = {}

                if response.status_code == 200:
                    dados_api = response.json()
                    # 2. Proteção: Verifica se dados_api é válido
                    if dados_api and isinstance(dados_api, dict):
                        lista_crua = dados_api.get('questoes', [])
                
                # --- Se não achou, tenta CRIAR nova prova (POST) ---
                if not apenas_atualizar:
                    if not lista_crua and response.status_code != 403:
                        if state.indice_atual == 0:
                            print("--- Gerando nova prova (POST)... ---")
                            resp_post = await client.post(f"{API_BASE_URL}/Questao/ConjuntoQuestao", timeout=30.0)
                            
                            if resp_post.status_code == 200:
                                dados_api = resp_post.json()
                                # 3. Proteção CRÍTICA no POST: Verifica se retornou None
                                if dados_api and isinstance(dados_api, dict):
                                    lista_crua = dados_api.get('questoes', [])
                                    state.id_conjunto_atual = dados_api.get('id_conjunto_questao')
                                else:
                                    print(f"AVISO: POST retornou dados inválidos: {dados_api}")

                    # Se achou questões (seja do GET ou do POST), processa
                    if lista_crua:
                        if not state.id_conjunto_atual and isinstance(dados_api, dict):
                             state.id_conjunto_atual = dados_api.get('id_conjunto_questao')

                        questoes_formatadas = []
                        for q in lista_crua:
                            if not isinstance(q, dict): continue

                            try:
                                raw_op = q.get('json_opcao', '[]') or '[]'
                                ops = []
                                # Tenta decodificar JSON ou literal_eval se falhar
                                try: ops = json.loads(raw_op)
                                except: ops = []
                                
                                if not isinstance(ops, list): ops = []
                            except:
                                ops = []

                            opcoes_ui = [
                                {"letra": chr(65+i), "texto": str(t), "indice": i} 
                                for i, t in enumerate(ops)
                            ]

                            questoes_formatadas.append({
                                "id": q.get('id_questao'),
                                "titulo": "Atividade Prática",
                                "pergunta_texto": q.get('descricao_questao'),
                                "opcoes": opcoes_ui,
                                "resposta_correta_texto": str(q.get('resposta') or '').strip()
                            })
                        
                        state.questoes = questoes_formatadas
                        state.total_questoes = len(state.questoes)
                    
                    elif response.status_code == 403:
                        ui.notify('Sessão expirada.', type='negative')
                        ui.navigate.to('/login')

        except Exception as e:
            print(f"ERRO: {e}") # Log no terminal para debug
            ui.notify(f'Erro de conexão: {str(e)}', type='negative')
        finally:
            state.carregando = False
            if not forcar_atualizacao and not apenas_atualizar:
                self.renderizar_conteudo.refresh()

    async def registrar_resposta_api(self, id_questao, indice_numerico):
        if not state.id_conjunto_atual: return False
        url = f"{API_BASE_URL}/Questao/ResponderQuestao/{id_questao}/{indice_numerico}/{state.id_conjunto_atual}"
        try:
            async with httpx.AsyncClient(headers=self.get_headers()) as client:
                res = await client.post(url)
                return res.status_code == 200 and res.text.strip().lower() == 'true'
        except: return False

    def proxima(self):
        if state.indice_atual >= len(state.questoes) - 1:
            # Acabou as questões
            state.reset()
            ui.navigate.to('/') # Ou para uma tela de parabéns
        else:
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
                ui.label('Carregando...').classes('text-gray-500')
            return

        if not state.questoes:
            with ui.column().classes('w-full h-screen items-center justify-center'):
                ui.label('Nenhuma questão encontrada.').classes('text-xl')
                ui.button('Voltar', on_click=self.sair)
            return

        # Proteção de índice
        if state.indice_atual >= len(state.questoes):
            state.reset()
            ui.navigate.to('/')
            return

        dados = state.questoes[state.indice_atual]

        with ui.row().classes('w-full justify-between items-center px-4 py-2 bg-white shadow-sm'):
            ui.label('Lexora').classes('text-lg font-bold')
            ui.button('Sair', on_click=self.sair).props('flat dense icon-right=logout')

        with ui.column().classes('w-full max-w-5xl mx-auto p-4'):
            with ui.column().classes('w-full mb-4 gap-2'):
                with ui.element('div').classes('w-full h-3 bg-blue-100 rounded-full overflow-hidden'):
                    pct = (state.numero_questao_atual / state.total_questoes) * 100 if state.total_questoes > 0 else 0
                    ui.element('div').classes('h-full bg-[#1e2e45]').style(f'width: {pct}%')
                ui.label(f'{state.numero_questao_atual} / {state.total_questoes}').classes('text-sm text-gray-600 font-bold self-end')

            with ui.card().classes('w-full rounded-[20px] shadow-sm border border-gray-100 p-6'):
                ui.label(dados['titulo']).classes('text-xl font-bold')

                with ui.row().classes('w-full gap-6 mt-4 wrap'):
                    with ui.column().classes('w-full md:w-1/3 items-center justify-center'):
                        ui.image('/local_images/img_questao.png').classes('max-w-[250px]')

                    with ui.column().classes('w-full md:w-3/5 gap-4'):
                        ui.label(dados['pergunta_texto']).classes('text-lg bg-blue-50 p-4 rounded w-full')

                        lista_botoes = []

                        async def click_op(btn, op):
                            for b_obj, _ in lista_botoes: b_obj.disable()
                            
                            acertou = await self.registrar_resposta_api(dados['id'], op['indice'])
                            dados_atualizados = state.questoes[state.indice_atual]
                            texto_correto = dados_atualizados.get('resposta_correta_texto', '')

                            if acertou:
                                btn.classes('!bg-green-100 !border-green-500 !text-green-900')
                                btn.props('icon=check')
                                ui.notify('Correto!', type='positive')
                            else:
                                btn.classes('!bg-red-100 !border-red-500 !text-red-900')
                                btn.props('icon=close')
                                ui.notify(f'Incorreto. Resposta: {texto_correto}', type='negative')

                            btn_prox.set_visibility(True)

                        for op in dados['opcoes']:
                            b = ui.button().classes('w-full bg-white border border-gray-300 text-gray-700 rounded-lg px-4 py-3 text-left normal-case shadow-sm').props('flat')
                            with b:
                                with ui.row().classes('items-center gap-4'):
                                    ui.label(op['letra']).classes('font-bold text-blue-800 bg-blue-50 px-2 rounded')
                                    ui.label(op['texto'])
                            
                            b.on('click', lambda _, btn=b, o=op: click_op(btn, o))
                            lista_botoes.append((b, op))
                        
                        btn_prox = ui.button('Próxima', on_click=self.proxima).classes('self-end mt-4')
                        btn_prox.set_visibility(False)

    def render(self):
        ui.query('body').style('background-color: #f8fafc; margin: 0; padding: 0;')
        self.renderizar_conteudo()
