import json
import httpx
import ast
from nicegui import app, ui
from pathlib import Path

# Configuração da API
API_BASE_URL = "https://lexora-api.onrender.com"

# Configuração de Imagens
try:
    script_dir = Path(__file__).parent.resolve()
    images_dir = script_dir.parent / 'images'
    try: app.add_static_files('/local_images', str(images_dir))
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

state = QuizState()

class Questoes:
    def __init__(self):
        self.token = app.storage.user.get('token')
        if not self.token: ui.navigate.to('/')
    
    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

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
                response = await client.get(f"{API_BASE_URL}/Questao/ConjuntoQuestao", timeout=30.0)
                
                lista_crua = []
                dados_api = {}

                if response.status_code == 200:
                    try:
                        dados_api = response.json()
                        if isinstance(dados_api, dict):
                            lista_crua = dados_api.get('questoes', [])
                    except: pass

                if not apenas_atualizar:
                    if not lista_crua and response.status_code != 403:
                        if state.indice_atual == 0:
                            print("--- Gerando nova prova (POST)... ---")
                            resp_post = await client.post(f"{API_BASE_URL}/Questao/ConjuntoQuestao", timeout=30.0)
                            if resp_post.status_code == 200:
                                dados_api = resp_post.json()
                                lista_crua = dados_api.get('questoes', [])
                
                if lista_crua:
                    state.id_conjunto_atual = dados_api.get('id_conjunto_questao')
                    questoes_formatadas = []
                    
                    for q in lista_crua:
                        raw_op = q.get('json_opcao', '[]') or '[]'
                        ops = []
                        try: ops = json.loads(raw_op)
                        except:
                            try: ops = ast.literal_eval(raw_op)
                            except: ops = []
                        
                        if not isinstance(ops, list): ops = []
                        opcoes_ui = [{"letra": chr(65+i), "texto": str(t), "indice": i} for i, t in enumerate(ops)]
                        
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
                    ui.navigate.to('/')

        except Exception as e: print(f"Erro: {e}")
        finally:
            state.carregando = False
            if not forcar_atualizacao and not apenas_atualizar: 
                self.renderizar_conteudo.refresh()

    async def registrar_resposta_api(self, id_questao, indice_numerico):
        url = f"{API_BASE_URL}/Questao/ResponderQuestao/{id_questao}/{indice_numerico}/{state.id_conjunto_atual}"
        try:
            async with httpx.AsyncClient(headers=self.get_headers()) as client:
                res = await client.post(url)
                return res.status_code == 200 and res.text.strip().lower() == 'true'
        except: return False

    # BUSCA NO HISTÓRICO SE A PROVA FECHAR (Para a última questão)
    async def buscar_resposta_historico(self, id_questao):
        try:
            async with httpx.AsyncClient(headers=self.get_headers()) as client:
                r = await client.get(f"{API_BASE_URL}/Questao/RelatorioDesempenho")
                if r.status_code == 200:
                    for prova in r.json():
                        qs = prova.get('questoes', [])
                        if qs and isinstance(qs, list) and isinstance(qs[0], dict) and 'questoes' in qs[0]:
                            qs = qs[0]['questoes']
                        
                        for q in qs:
                            if str(q.get('id_questao')) == str(id_questao):
                                return str(q.get('resposta', '')).strip()
        except: pass
        return ""

    def proxima(self):
        # Se for a última questão, navega para a conclusão
        if state.indice_atual >= len(state.questoes) - 1:
            id_final = state.id_conjunto_atual
            state.reset()
            ui.navigate.to(f'/tarefa_concluida?id={id_final}')
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
                ui.label('Erro ao carregar.').classes('text-xl')
                ui.button('Tentar Novamente', on_click=lambda: self.carregar_questoes_api(True))
            return 

        dados = state.questoes[state.indice_atual]
        eh_ultima = state.indice_atual == len(state.questoes) - 1

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
                ui.label(f"{dados['titulo']} (ID: {state.id_conjunto_atual})").classes('text-xl font-bold')
                
                with ui.row().classes('w-full gap-6 mt-4 wrap'):
                    with ui.column().classes('w-full md:w-1/3 items-center justify-center'):
                         ui.image('/local_images/img_questao.png').classes('max-w-[250px]')

                    with ui.column().classes('w-full md:w-3/5 gap-4'):
                        ui.label(dados['pergunta_texto']).classes('text-lg bg-blue-50 p-4 rounded w-full')

                        lista_botoes = []

                        async def click_op(btn, op):
                            for b_obj, _ in lista_botoes: b_obj.disable()
                            
                            acertou = await self.registrar_resposta_api(dados['id'], op['indice'])
                            
                            await self.carregar_questoes_api(forcar_atualizacao=True, apenas_atualizar=True)
                            
                            dados_atualizados = state.questoes[state.indice_atual]
                            texto_correto = dados_atualizados.get('resposta_correta_texto', '')

                            if not texto_correto:
                                texto_correto = await self.buscar_resposta_historico(dados['id'])

                            if acertou:
                                btn.classes('!bg-green-100 !border-green-500 !text-green-900')
                                btn.props('icon=check')
                                ui.notify('Correto!', type='positive')
                            else:
                                btn.classes('!bg-red-100 !border-red-500 !text-red-900')
                                btn.props('icon=close')
                                ui.notify('Incorreto.', type='negative')
                                
                                # Pinta a certa
                                achou = False
                                for b_obj, op_data in lista_botoes:
                                    if str(op_data['texto']).strip().lower() == str(texto_correto).strip().lower():
                                        b_obj.classes('!bg-green-100 !border-green-500 !text-green-900')
                                        b_obj.props('icon=check')
                                        achou = True
                                
                                if not achou and texto_correto:
                                    ui.notify(f"Resposta: {texto_correto}", type='warning', timeout=5000)

                            btn_prox.set_visibility(True)

                        for op in dados['opcoes']:
                            b = ui.button().classes('w-full bg-white border border-gray-300 text-gray-700 rounded-lg px-4 py-3 text-left normal-case shadow-sm').props('flat')
                            with b:
                                with ui.row().classes('items-center gap-4'):
                                    ui.label(op['letra']).classes('font-bold text-blue-800 bg-blue-50 px-2 rounded')
                                    ui.label(op['texto'])
                            
                            b.on('click', lambda _, btn=b, o=op: click_op(btn, o))
                            lista_botoes.append((b, op))
                        
                        texto_botao = 'Concluir Atividade' if eh_ultima else 'Próxima'
                        cor_botao = 'green' if eh_ultima else '[#1e2e45]'
                        
                        btn_prox = ui.button(texto_botao, on_click=self.proxima) \
                            .classes(f'self-end bg-{cor_botao} text-white')
                        
                        if eh_ultima: btn_prox.classes('!bg-green-600 hover:!bg-green-700')
                        else: btn_prox.classes('bg-[#1e2e45]')

                        btn_prox.set_visibility(False)

    def render(self):
        ui.query('body').style('background-color: #f8fafc; margin: 0;')
        self.renderizar_conteudo()