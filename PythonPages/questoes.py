import os
import json
import httpx
from nicegui import app, ui

API_BASE_URL = "https://lexora-api.onrender.com"
#TOKEN MANUAL(ALTERAR PRA USAR EM TODAS AS PAGINAS)
TOKEN_FIXO = "".strip()

base_dir = os.path.dirname(os.path.abspath(__file__))
images_dir = os.path.join(base_dir, '../Images')
if os.path.exists(images_dir):
    app.add_static_files('/local_images', images_dir)

class QuizState:
    def __init__(self):
        self.indice_atual = 0
        self.numero_questao_atual = 1
        self.questoes = [] 
        self.carregando = True 
        self.id_conjunto_atual = None 
        self.total_questoes = 0
        self.ja_iniciou_busca = False 

state = QuizState()

def get_headers():
    return {
        "Authorization": f"Bearer {TOKEN_FIXO}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

async def carregar_questoes_api():
    if len(state.questoes) > 0:
        state.carregando = False
        renderizar_pagina.refresh()
        return

    state.carregando = True
    renderizar_pagina.refresh()
    
    try:
        async with httpx.AsyncClient(headers=get_headers(), follow_redirects=True) as client:
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
                        "tema": "Geral", 
                        "pergunta_texto": q.get('descricao_questao'),
                        "opcoes": opcoes_ui
                    })
                
                state.questoes = questoes_formatadas
                state.total_questoes = len(state.questoes)
            
            elif response.status_code == 403:
                ui.notify('Token inválido ou expirado.', type='negative')
            else:
                ui.notify(f'Erro API: {response.status_code}', type='warning')
                
    except Exception as e:
        ui.notify(f'Erro de conexão: {str(e)}', type='negative')
    finally:
        state.carregando = False
        renderizar_pagina.refresh()

async def registrar_resposta_api(id_questao, indice_numerico):
    if not state.id_conjunto_atual:
        return None

    url = (f"{API_BASE_URL}/Questao/ResponderQuestao/"
           f"{id_questao}/{indice_numerico}/{state.id_conjunto_atual}")

    try:
        async with httpx.AsyncClient(headers=get_headers()) as client:
            response = await client.post(url)
            
            if response.status_code == 200:
                return response.json() 
            else:
                print(f"Erro POST ({response.status_code}): {response.text}")
                return None
    except Exception as e:
        print(f"Erro POST: {e}")
        return None

@ui.refreshable
def renderizar_pagina():
    if not state.ja_iniciou_busca:
        state.ja_iniciou_busca = True
        ui.timer(0.1, carregar_questoes_api, once=True)

    if state.carregando:
        with ui.column().classes('w-full h-screen items-center justify-center'):
            ui.spinner(size='lg')
            ui.label('Carregando...').classes('text-gray-500')
        return

    if not state.questoes or state.indice_atual >= len(state.questoes):
        with ui.column().classes('w-full h-screen items-center justify-center gap-4'):
            if not state.questoes:
                ui.icon('warning', size='4rem', color='orange')
                ui.label('Sem questões disponíveis.').classes('text-xl')
            else:
                ui.icon('emoji_events', size='4rem', color='green')
                ui.label('Atividade Concluída!').classes('text-2xl font-bold')
        return 

    dados = state.questoes[state.indice_atual]

    with ui.row().classes('w-full justify-between items-center q-px-md q-py-sm'):
        with ui.row().classes('items-center gap-2'):
            ui.icon('school', color='black', size='sm') 
            ui.label('Lexora').classes('text-lg font-bold text-black')
        ui.button('Sair').props('flat dense no-caps icon-right=logout')

    with ui.column().classes('w-full max-w-5xl mx-auto q-pa-md'):
        
        with ui.column().classes('w-full q-mb-md gap-1'):
            with ui.element('div').classes('w-full h-3 bg-blue-100 rounded-full overflow-hidden'):
                if state.total_questoes > 0:
                    pct = (state.numero_questao_atual / state.total_questoes) * 100
                else:
                    pct = 0
                ui.element('div').classes('h-full bg-[#1e2e45]').style(f'width: {pct}%')
            ui.label(f'{state.numero_questao_atual} / {state.total_questoes}').classes('text-xs text-gray-500 self-end')

        with ui.card().classes('w-full rounded-[20px] shadow-sm border border-gray-100 q-pa-lg'):
            
            with ui.row().classes('w-full justify-between items-start'):
                with ui.column().classes('gap-0'):
                    ui.label(dados['titulo']).classes('text-xl font-bold text-gray-900')
                    ui.label(f"Tema: {dados['tema']}").classes('text-md text-gray-600')

            with ui.row().classes('w-full justify-between items-start q-mt-md wrap'):
                
                with ui.column().classes('w-full md:w-1/3 items-center justify-center min-h-[200px]'):
                     ui.icon('quiz', size='6rem', color='grey-4')

                with ui.column().classes('w-full md:w-3/5 gap-6'):
                    
                    with ui.row().classes('bg-blue-50 rounded-lg px-6 py-4 items-center w-full'):
                        ui.label(dados['pergunta_texto']).classes('text-lg font-medium text-gray-900 leading-tight')

                    lista_botoes = []

                    async def selecionar_alternativa(btn_clicado, opcao_obj):
                        btn_clicado.props('loading') 
                        
                        for btn, _ in lista_botoes:
                            btn.disable()
                        
                        resultado = await registrar_resposta_api(dados['id'], opcao_obj['indice'])
                        
                        btn_clicado.props('remove loading')

                        acertou = False
                        if resultado is True:
                            acertou = True
                        elif resultado is False:
                            acertou = False
                        
                        if acertou:
                            btn_clicado.classes('!bg-green-100 !border-green-500 !text-green-900')
                            btn_clicado.props('icon=check')
                            ui.notify('Resposta Correta!', type='positive')
                        else:
                            btn_clicado.classes('!bg-red-100 !border-red-500 !text-red-900')
                            btn_clicado.props('icon=close')
                            ui.notify('Resposta Incorreta.', type='negative')

                        btn_proxima.set_visibility(True)

                    with ui.column().classes('w-full gap-3'):
                        for opcao in dados['opcoes']:
                            btn = ui.button().classes(
                                'w-full bg-white border border-gray-300 text-gray-700 '
                                'rounded-lg px-4 py-3 text-left normal-case hover:bg-gray-50 shadow-sm transition-all'
                            ).props('flat')
                            
                            with btn:
                                with ui.row().classes('w-full items-center gap-4'):
                                    ui.label(opcao['letra']).classes(
                                        'font-bold text-blue-800 bg-blue-50 px-2 py-1 rounded text-sm'
                                    )
                                    ui.label(opcao['texto']).classes('text-base font-medium')

                            btn.on('click', lambda b=btn, o=opcao: selecionar_alternativa(b, o))
                            lista_botoes.append((btn, opcao))

            with ui.row().classes('w-full justify-between items-center q-mt-xl'):
                ui.button('Pular').classes('text-gray-500').props('flat no-caps')

                btn_proxima = ui.button('Próxima questão', on_click=proxima).classes('bg-[#1e2e45] text-white font-bold px-6 rounded-lg normal-case')
                btn_proxima.props('unelevated icon-right=arrow_forward')
                btn_proxima.set_visibility(False)

def proxima():
    state.indice_atual += 1
    state.numero_questao_atual += 1
    renderizar_pagina.refresh()

if __name__ in {"__main__", "__mp_main__"}:
    ui.query('body').style('background-color: #f8fafc; margin: 0; padding: 0;')
    renderizar_pagina()
    ui.run(title='Lexora Atividade', port=8080)