import httpx
import re
import asyncio
from nicegui import app, ui
from pathlib import Path

API_BASE_URL = "https://lexora-api.onrender.com"

base_dir = Path(__file__).parent
images_path = (base_dir / '../images').resolve()
if images_path.exists():
    try: app.add_static_files('/images', str(images_path))
    except: pass

class Gabarito:
    def __init__(self):
        self.token = app.storage.user.get('token')
        if not self.token: ui.navigate.to('/')
        
        self.dados_formatados = []
        self.stats = {"pontos": 0, "porcentagem": 0, "id_conjunto": 0, "origem": "-"}
        self.loading = True

    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def separar_frase(self, texto, chave):
        if not texto: return "", str(chave) if chave else "...", ""
        partes = re.split(r'_{2,}', texto)
        return partes[0] if len(partes)>0 else "", str(chave) if chave else "...", partes[1] if len(partes)>1 else ""

    def processar_prova(self, dados_prova, origem):
        if not dados_prova: return None
        try: id_val = dados_prova.get('id_conjunto_questao', 0)
        except AttributeError: return None

        qs = []
        if 'questoes' in dados_prova:
            raw = dados_prova['questoes']
            if isinstance(raw, list) and raw:
                if isinstance(raw[0], dict) and 'questoes' in raw[0]: qs = raw[0]['questoes']
                else: qs = raw
        
        if not qs: return None

        total, acertos, formatadas = len(qs), 0, []

        for q in qs:
            desc = q.get('descricao_questao', '')
            corr = str(q.get('resposta', ''))
            user = str(q.get('resposta_usuario', ''))
            win = q.get('acerto') is True
            if win: acertos += 1
            
            grupo = []
            if win:
                p, w, a = self.separar_frase(desc, corr)
                grupo.append({"status": "correct", "pre": p, "word": w, "post": a})
            else:
                if user and user not in ["ERRO", "None", "null", ""]:
                    p, w, a = self.separar_frase(desc, user)
                    grupo.append({"status": "wrong", "pre": p, "word": w, "post": a})
                else:
                    p, _, a = self.separar_frase(desc, "___")
                    grupo.append({"status": "wrong", "pre": p, "word": "(sem resposta)", "post": a})
                
                if corr and corr not in ["None", "null"]:
                    p, w, a = self.separar_frase(desc, corr)
                    grupo.append({"status": "correct", "pre": p, "word": w, "post": a})
            
            formatadas.append(grupo)

        return {
            "id_conjunto": id_val,
            "pontos": acertos, 
            "origem": origem,
            "porcentagem": int((acertos/total)*100) if total else 0,
            "questoes_ui": formatadas
        }

    async def carregar_dados(self, id_filtro=None):
        try:
            async with httpx.AsyncClient(headers=self.get_headers()) as client:
                r1, r2 = await asyncio.gather(
                    client.get(f"{API_BASE_URL}/Questao/ConjuntoQuestao"),
                    client.get(f"{API_BASE_URL}/Questao/RelatorioDesempenho"),
                    return_exceptions=True
                )
                
                candidatos = []
                if not isinstance(r1, Exception) and r1.status_code == 200:
                    dados = r1.json()
                    if isinstance(dados, dict):
                        proc = self.processar_prova(dados, "Atual")
                        if proc: candidatos.append(proc)
                
                if not isinstance(r2, Exception) and r2.status_code == 200:
                    lista = r2.json()
                    if isinstance(lista, list):
                        for item in lista:
                            if item: 
                                proc = self.processar_prova(item, "Histórico")
                                if proc: candidatos.append(proc)
                
                if candidatos:
                    escolhido = None
                    if id_filtro:
                        # Busca exata (convertendo tudo para string para garantir)
                        escolhido = next((c for c in candidatos if str(c['id_conjunto']) == str(id_filtro)), None)
                    
                    if not escolhido:
                        candidatos.sort(key=lambda x: x['id_conjunto'], reverse=True)
                        escolhido = candidatos[0]

                    self.stats = escolhido
                    self.dados_formatados = escolhido['questoes_ui']
                else:
                    self.dados_formatados = [] # Garante lista vazia se não achar nada
        except Exception as e:
            print(f"Erro Gabarito: {e}")
        finally:
            self.loading = False
            self.layout.refresh()

    def render(self, id: str = None):
        if self.loading:
            ui.timer(0.1, lambda: self.carregar_dados(id), once=True)
        self.layout()

    @ui.refreshable
    def layout(self):
        ui.query('body').style('background-color: #f8fafc;')
        
        with ui.column().classes('w-full min-h-screen items-center p-4'):
            
            with ui.row().classes('w-full max-w-5xl justify-between items-center mb-6'):
                ui.image('/images/logo.png').classes('w-24 md:w-32').props('fit=contain')

            with ui.card().classes('w-full max-w-4xl bg-white rounded-xl shadow-sm p-6 md:p-10'):
                with ui.row().classes('w-full justify-between items-start mb-8'):
                    with ui.column().classes('gap-1'):
                        ui.label('Gabarito da atividade').classes('text-xl md:text-2xl font-bold text-black')
                        
                        id_c = self.stats.get('id_conjunto', 'N/A')
                        pts = self.stats.get('pontos', 0)
                        pct = self.stats.get('porcentagem', 0)
                        
                        ui.label(f"ID Prova: {id_c} | Acertos: {pts} ({pct}%)").classes('text-base md:text-lg text-blue-600 font-bold')
                    ui.button(icon='close', on_click=lambda: ui.navigate.to('/')).props('flat round dense')

                if self.loading:
                    with ui.column().classes('w-full items-center py-10'):
                        ui.spinner('dots', size='lg')
                elif not self.dados_formatados:
                    with ui.column().classes('w-full items-center py-10'):
                        ui.icon('assignment_late', size='4rem', color='grey')
                        ui.label('Nenhum dado encontrado.').classes('text-gray-500')
                
                for i, group in enumerate(self.dados_formatados):
                    with ui.column().classes('w-full gap-3'):
                        for att in group:
                            is_corr = att['status'] == 'correct'
                            color = 'text-green-700' if is_corr else 'text-red-900'
                            icon = 'check' if is_corr else 'close'
                            icon_c = 'text-green-600' if is_corr else 'text-red-900'
                            
                            with ui.row().classes('w-full items-center gap-4'):
                                with ui.element('div').classes(f'w-6 h-6 flex items-center justify-center {"" if is_corr else "bg-red-50 rounded"}'):
                                    ui.icon(icon, size='xs').classes(f'{icon_c} font-bold')
                                
                                ui.html(
                                    f"{att['pre']} <span class='font-bold {color}'>{att['word']}</span> {att['post']}",
                                    sanitize=False
                                ).classes('text-lg leading-tight')
                    
                    if i < len(self.dados_formatados) - 1:
                        ui.separator().classes('my-6 bg-gray-200')