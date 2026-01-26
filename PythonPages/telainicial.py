from nicegui import ui, app
import requests
from datetime import datetime, timedelta
from pathlib import Path
import calendar
import time  # Importante para o anti-cache

# ====== CONFIGURAÇÕES DE API ======
API_URL_BASE = 'https://lexora-api.onrender.com/'

# Opções (IDs devem ser inteiros > 0)
EXPERIENCIAS = {1: 'Básico', 2: 'Intermediário', 3: 'Avançado'}
OBJETIVOS = {1: 'Viagem', 2: 'Trabalho', 3: 'Morar fora', 4: 'Tecnologia'}
DISPONIBILIDADES = {1: 'Leve (0.5h)', 2: 'Moderado (1h)', 3: 'Intenso (2h)'}

def get_headers() -> dict:
    token = app.storage.user.get('token')
    if not token: return {'accept': 'application/json'}
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'accept': 'application/json'}

# Função GET com Anti-Cache (Força dados novos)
def get_json(path: str, default):
    try:
        url = f'{API_URL_BASE}{path}'
        # Adiciona timestamp para evitar que o navegador/proxy use cache antigo
        separator = '&' if '?' in url else '?'
        url += f'{separator}_t={int(time.time())}'
        
        resp = requests.get(url, headers=get_headers(), timeout=10)
        return resp.json() if resp.status_code == 200 else default
    except: return default

# Mantemos POST pois PUT retornou 405
def post_json(path: str, data: dict):
    print(f"🚀 [POST] Enviando Payload...")
    try:
        resp = requests.post(f'{API_URL_BASE}{path}', json=data, headers=get_headers(), timeout=15)
        print(f"📥 [RESP] {resp.status_code} | {resp.text}")
        # Aceita 200 ou 201 como sucesso
        return resp.status_code in [200, 201]
    except Exception as e:
        print(f"❌ [ERRO] {e}")
        return False
    
def put_json(path: str, data: dict):
    print(f"🚀 [PUT] Enviando Payload...")
    try:
        resp = requests.put(f'{API_URL_BASE}{path}', json=data, headers=get_headers(), timeout=15)
        print(f"📥 [RESP] {resp.status_code} | {resp.text}")
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ [ERRO] {e}")
        return False

# ====== ARQUIVOS ESTÁTICOS ======
basedir = Path(__file__).parent.resolve()
possible_paths = [basedir / 'images', basedir.parent / 'images', Path('images').absolute()]
images_dir = next((p for p in possible_paths if p.is_dir()), None)
if images_dir: app.add_static_files('/images', str(images_dir))

PRIMARY = '#1153BE'
LOGO_PATH = '/images/logo.png'

# ====== CSS ======
ui.add_head_html("""
<style>
body { background-color: #f8fafc; }
.page-wrap { width: 100%; max-width: 1100px; margin: 0 auto; padding: 20px 16px; display: flex; gap: 16px; align-items: flex-start; justify-content: center; }
.menu-card { width: 230px; flex-shrink: 0; padding: 20px; border-radius: 16px; background: #FFFFFF; box-shadow: 0 2px 10px rgba(0,0,0,0.02); }
.center-card { width: 580px; flex-shrink: 0; padding: 24px; border-radius: 16px; background: #FFFFFF; box-shadow: 0 2px 10px rgba(0,0,0,0.02); }
.right-card { width: 260px; flex-shrink: 0; display: flex; flex-direction: column; gap: 16px; }
.rc-box { padding: 20px; border-radius: 16px; background: #FFFFFF; box-shadow: 0 2px 10px rgba(0,0,0,0.02); }
@media (max-width: 1150px) { .page-wrap { flex-wrap: wrap; } .center-card { order: -1; width: 100%; max-width: 100%; } .menu-card, .right-card { width: 48%; } }
@media (max-width: 768px) { .menu-card, .right-card { width: 100%; } }
.estat-box { flex: 1; background: #F8FAFC; border-radius: 12px; padding: 12px 8px; min-width: 100px; text-align: center; }
.estat-num { font-size: 22px; font-weight: 800; color: #1e293b; line-height: 1.1; }
.estat-sub { font-size: 11px; color: #64748b; font-weight: 600; }
.perfil-row { display: flex; align-items: flex-start; margin-bottom: 12px; }
.perfil-icon { font-size: 16px; margin-right: 10px; width: 18px; text-align: center; opacity: 0.6; }
.perfil-value { font-size: 13px; color: #334155; font-weight: 600; line-height: 1.3; }
.cal-nav-btn { color: #64748b; cursor: pointer; font-size: 18px; user-select: none; }
.cal-nav-btn:hover { color: #1153BE; }
.grid-7-col { display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px; width: 100%; justify-items: center; }
.grid-cell { display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; }
</style>
""", shared=True)

# Endpoints de busca
def buscar_dados_perfil(): return get_json('usuarios/UsuarioInformacao', {})
def buscar_estatisticas_gerais(): return get_json('relatorio/EstatisticaUsuario', {})
def buscar_ofensiva(): return get_json('relatorio/OfensivaUsuario', {})
def buscar_atividade_meta(): return get_json('relatorio/AtividadeUsuario', []) 
def buscar_historico_pontos(): return get_json('relatorio/DataUsuario', [])

def render_fire_icon(active: bool, size: str = '20px'):
    color = PRIMARY if active else '#e2e8f0'
    ui.icon('local_fire_department').style(f'color:{color}; opacity:{1 if active else 1}; font-size:{size}; line-height:1;')

def grafico_barras_minimalista(valores):
    max_valor = max(valores) if valores else 100
    if max_valor == 0: max_valor = 100
    with ui.row().style('justify-content:space-between; align-items:flex-end; height:100px; width:100%; gap:6px; padding-top:10px'):
        dados_finais = (([0]*15) + list(valores))[-15:]
        for v in dados_finais:
            val = float(v)
            pct = min(val / max_valor, 1.0)
            visib = '1' if val > 0 else '0'
            with ui.column().style('align-items:center; gap:4px; flex:1;'):
                ui.label(f"{int(val/1000)}k" if val >= 1000 else f"{int(val)}").style(f'font-size:9px; color:#64748b; opacity:{visib}; font-weight:600')
                with ui.element('div').style('width:6px; height:80px; background:#F1F5F9; border-radius:99px; position:relative; overflow:hidden'):
                    if pct > 0: ui.element('div').style(f'width:100%; height:{pct*100}%; background:{PRIMARY}; position:absolute; bottom:0; left:0; border-radius:99px')

class CalendarState:
    def __init__(self):
        self.hoje = datetime.now()
        self.ano_visivel = self.hoje.year
        self.mes_visivel = self.hoje.month
        self.datas_ativas = set()
cal_state = CalendarState()

@ui.refreshable
def render_calendario():
    meses_pt = ["", "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO", "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]
    with ui.row().classes('w-full items-center justify-between mb-2'):
        ui.icon('chevron_left').classes('cal-nav-btn').on('click', lambda: mudar_mes(-1))
        ui.label(f'{meses_pt[cal_state.mes_visivel]} {cal_state.ano_visivel}').style('font-size:12px; font-weight:700; color:#334155; letter-spacing:0.5px')
        ui.icon('chevron_right').classes('cal-nav-btn').on('click', lambda: mudar_mes(1))
    with ui.element('div').classes('grid-7-col').style('margin-bottom:4px'):
        for d in ['dom.', 'seg.', 'ter.', 'qua.', 'qui.', 'sex.', 'sáb.']: ui.label(d).style('font-size:10px; color:#94a3b8; text-align:center;')
    calendar.setfirstweekday(calendar.SUNDAY)
    cal_weeks = calendar.monthcalendar(cal_state.ano_visivel, cal_state.mes_visivel)
    with ui.element('div').classes('grid-7-col').style('row-gap:8px'):
        for week in cal_weeks:
            for day in week:
                with ui.element('div').classes('grid-cell').style('height:20px'):
                    if day != 0:
                        ativo = f"{cal_state.ano_visivel}-{cal_state.mes_visivel:02d}-{day:02d}" in cal_state.datas_ativas
                        render_fire_icon(ativo, '18px')

def mudar_mes(delta):
    cal_state.mes_visivel += delta
    if cal_state.mes_visivel > 12: cal_state.mes_visivel, cal_state.ano_visivel = 1, cal_state.ano_visivel + 1
    elif cal_state.mes_visivel < 1: cal_state.mes_visivel, cal_state.ano_visivel = 12, cal_state.ano_visivel - 1
    render_calendario.refresh()

# ====== TELA INICIAL ======
def render_tela_inicial() -> None:
    if not app.storage.user.get('token'): return ui.navigate.to('/')

    # Carrega Dados (usando função anti-cache)
    perfil = buscar_dados_perfil() or {}
    estatisticas = buscar_estatisticas_gerais() or {}
    historico = buscar_historico_pontos() or []
    dados_ofensiva = buscar_ofensiva() or {}

    # --- Extração Segura de IDs ---
    id_idioma_atual = perfil.get('usuario_experiencia_idioma', {}).get('id_idioma') or 2
    if id_idioma_atual < 1: id_idioma_atual = 2

    id_exp_atual = perfil.get('usuario_experiencia_idioma', {}).get('id_experiencia_idioma') or 1
    if id_exp_atual < 1: id_exp_atual = 1

    id_obj_atual = perfil.get('objetivos_usuario', {}).get('id_objetivo') or 1
    if id_obj_atual < 1: id_obj_atual = 1

    # Lógica de Disponibilidade
    id_disp_atual = perfil.get('id_disponibilidade') or perfil.get('disponibilidade', {}).get('id_disponibilidade')
    if not id_disp_atual or int(id_disp_atual) < 1:
        desc_disp = perfil.get('descricao_disponibilidade', '')
        id_disp_atual = 1
        if 'Moderado' in desc_disp: id_disp_atual = 2
        elif 'Intenso' in desc_disp: id_disp_atual = 3
    else: id_disp_atual = int(id_disp_atual)

    nome_atual = perfil.get('nome', '')
    email_atual = perfil.get('email', '')
    # Telefone removido das variáveis
    
    data_raw = perfil.get('data_nascimento', '')
    data_iso = data_raw.split('T')[0] if data_raw and len(data_raw) > 9 else "2000-01-01"

    print(f"DEBUG: Carregado -> Exp:{id_exp_atual}, Obj:{id_obj_atual}, Disp:{id_disp_atual}")

    # --- Modal de Edição ---
    dialog_perfil = ui.dialog()
    with dialog_perfil, ui.card().style('min-width:350px; border-radius:16px; padding:24px; display:flex; flex-direction:column; gap:16px'):
        ui.label('Alterar Perfil').style('font-size:18px; font-weight:700; color:#1e293b')
        
        ui.input(value='Inglês').props('readonly outlined dense').classes('w-full')
        
        sel_exp = ui.select(options=EXPERIENCIAS, value=id_exp_atual, label='Experiência').classes('w-full').props('outlined dense')
        sel_obj = ui.select(options=OBJETIVOS, value=id_obj_atual, label='Objetivo').classes('w-full').props('outlined dense')
        sel_disp = ui.select(options=DISPONIBILIDADES, value=id_disp_atual, label='Disponibilidade').classes('w-full').props('outlined dense')
        
        def salvar_alteracao():
            try:
                # Garante que são inteiros
                val_exp = int(sel_exp.value) if sel_exp.value else id_exp_atual
                val_obj = int(sel_obj.value) if sel_obj.value else id_obj_atual
                val_disp = int(sel_disp.value) if sel_disp.value else id_disp_atual
                
                # Garante id_idioma seguro
                id_idioma_safe = id_idioma_atual if id_idioma_atual >= 1 else 2

                # --- SUPER PAYLOAD ---
                # Enviamos os IDs em vários formatos para garantir que a API reconheça um deles sds                              
                payload = {
                    "id_idioma": id_idioma_safe,
                    "id_experiencia_idioma": val_exp,
                    "id_objetivo": val_obj,
                    "id_disponibilidade": val_disp,
                    "data_nascimento": data_iso
                }
                print(f"🚀 [PAYLOAD] {payload}")
                print(app.storage.user.get('token'))
                if put_json('usuarios/UsuarioInformacao', payload):
                    ui.notify('Perfil atualizado!', color='positive')
                    dialog_perfil.close()
                    # Aguarda 1s para o banco persistir antes de recarregar
                    ui.timer(1.0, lambda: ui.navigate.reload())
                else:
                    ui.notify('Erro ao atualizar. Verifique o console.', color='negative')
            except Exception as e:
                print(f"Erro no salvar: {e}")
                ui.notify('Erro interno.', color='negative')

        with ui.row().classes('w-full justify-end'):
            ui.button('Cancelar', on_click=dialog_perfil.close).props('flat color=grey')
            ui.button('Confirmar', on_click=salvar_alteracao).props('unelevated color=primary')

    # --- UI Layout ---
    nasc_formatado = ''
    if data_raw:
        try: nasc_formatado = datetime.strptime(data_raw.split('T')[0], '%Y-%m-%d').strftime('%d / %m / %Y')
        except: pass

    desc_idioma = perfil.get('usuario_experiencia_idioma', {}).get('descricao_idioma', 'Inglês')
    desc_nivel = perfil.get('usuario_experiencia_idioma', {}).get('descricao_experiencia_idioma', 'Básico')
    desc_objetivo = perfil.get('objetivos_usuario', {}).get('descricao_objetivo', 'Viagem')

    # Dados Grafico e Ofensiva
    vals_graf = []
    cal_state.datas_ativas = set()
    if isinstance(historico, list):
        historico.sort(key=lambda x: x.get('data', ''))
        for item in historico:
            pts = float(item.get('pontos', 0))
            vals_graf.append(pts)
            if pts > 0: cal_state.datas_ativas.add(item.get('data', '').split('T')[0])
            
    meta_data = buscar_atividade_meta()
    if isinstance(meta_data, list) and meta_data: meta_data = meta_data[-1]
    if not isinstance(meta_data, dict): meta_data = {}
    meta_hoje = meta_data.get('atividades_feitas', 0)
    meta_alvo = meta_data.get('meta', 5)
    pct_meta = min(meta_hoje / meta_alvo, 1.0) if meta_alvo > 0 else 0
    
    # Lógica de Ofensiva Corrigida
    dias_ofensiva = 0
    if isinstance(dados_ofensiva, dict):
        dias_ofensiva = (
            dados_ofensiva.get('seq_atual') or 
            dados_ofensiva.get('dias') or 
            dados_ofensiva.get('sequencia') or 
            0
        )
    elif isinstance(dados_ofensiva, int):
        dias_ofensiva = dados_ofensiva
    
    if dias_ofensiva == 0 and estatisticas.get('ultima_sequencia', 0) > 0:
        dias_ofensiva = estatisticas.get('ultima_sequencia', 0)

    # Layout Principal
    with ui.column().classes('w-full').style('align-items:center; gap:0'):
        with ui.row().classes('w-full justify-between items-center').style('padding:8px 24px; max-width:1100px'):
            ui.image(LOGO_PATH).props('fit=contain').style('width:120px; height:auto; max-height:45px;')
            ui.button('Sair', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/'))).props('flat dense icon-right=logout').style('color:#64748b; font-size:12px')

        with ui.element('div').classes('page-wrap'):
            with ui.column().classes('menu-card'):
                ui.label('Meu perfil').style('font-size:16px; font-weight:800; color:#0f172a; margin-bottom:16px')
                ui.html(f'<div class="perfil-row"><span class="perfil-icon">👤</span><span class="perfil-value">Nome completo<br><span style="font-weight:400;font-size:12px;color:#64748b">{nome_atual}</span></span></div>', sanitize=False)
                ui.html(f'<div class="perfil-row"><span class="perfil-icon">📅</span><span class="perfil-value">Data de nascimento<br><span style="font-weight:400;font-size:12px;color:#64748b">{nasc_formatado}</span></span></div>', sanitize=False)
                ui.html(f'<div class="perfil-row"><span class="perfil-icon">✉️</span><span class="perfil-value">E-mail<br><span style="font-weight:400;font-size:12px;color:#64748b">{email_atual}</span></span></div>', sanitize=False)
                # Telefone removido da visualização
                ui.html(f'<div class="perfil-row"><span class="perfil-icon">🌐</span><span class="perfil-value">Idioma<br><span style="font-weight:400;font-size:12px;color:#64748b">{desc_idioma}</span></span></div>', sanitize=False)
                ui.separator().style('margin:10px 0')
                ui.button('Alterar perfil', on_click=dialog_perfil.open).props('outline dense icon=edit').classes('w-full').style('color:#1153BE; font-size:12px; border-radius:8px')

            with ui.column().classes('center-card'):
                ui.label('Meu aprendizado').style('font-size:20px; font-weight:800; color:#0f172a; margin-bottom:16px')
                with ui.row().classes('w-full').style('gap:10px; margin-bottom:24px; flex-wrap:nowrap'):
                    itens_stats = [('public', 'blue', 'Idioma', desc_idioma), ('star', 'orange', 'Nível', desc_nivel), ('track_changes', 'green', 'Objetivo', desc_objetivo)]
                    for ic, col, lb1, lb2 in itens_stats:
                        with ui.row().classes(f'bg-{col}-1').style(f'flex:1; padding:12px; border-radius:12px; align-items:center; gap:8px'):
                            ui.icon(ic, color=f'{col}-8').style('font-size:20px')
                            with ui.column().style('gap:0'):
                                ui.label(lb1).style(f'font-size:10px; font-weight:700; color:{col}-6')
                                ui.label(lb2).classes(f'text-{col}-9').style('font-size:12px; font-weight:700')

                with ui.row().classes('w-full justify-between items-end mb-1'):
                    ui.label('Meta diária').style('font-size:14px; font-weight:700; color:#0f172a')
                    ui.button('PRATICAR', on_click=lambda: ui.navigate.to('/questoes')).props('dense unelevated').classes('bg-blue-600 text-white').style('border-radius:8px; font-weight:700; font-size:11px; padding:4px 12px')
                
                ui.label(f'{int(meta_hoje)}/{int(meta_alvo)} lições').style('font-size:11px; font-weight:600; color:#64748b; margin-top:-24px; margin-bottom:8px; margin-left: auto; margin-right: 90px;')
                with ui.element('div').classes('w-full').style('height:8px; background:#f1f5f9; border-radius:99px; overflow:hidden; margin-bottom:32px'):
                    ui.element('div').style(f'height:100%; width:{pct_meta*100}%; background:#1e293b; border-radius:99px')

                ui.label('ESTATÍSTICAS').style('font-size:11px; font-weight:800; color:#0f172a; text-transform:uppercase; margin:0 auto 16px auto')
                with ui.row().classes('w-full').style('gap:12px; margin-bottom:32px'):
                    for val, txt in [(estatisticas.get('dias_ativo',0),'Dias ativos'), (estatisticas.get('atividades_feitas',0),'Atividades feitas'), (f"{int(estatisticas.get('pontos_totais',0)):,}".replace(',','.'),'Total de pontos')]:
                        with ui.column().classes('estat-box'): ui.label(str(val)).classes('estat-num'); ui.label(txt).classes('estat-sub')
                
                with ui.row().classes('w-full justify-center').style('gap:12px; margin-bottom:32px'):
                     with ui.column().classes('estat-box').style('max-width:200px'):
                        ui.label(str(dias_ofensiva)).classes('estat-num')
                        ui.label('Sequência').classes('estat-sub')
                     with ui.column().classes('estat-box').style('max-width:200px'):
                        ui.label(str(estatisticas.get('maior_sequencia', 0))).classes('estat-num')
                        ui.label('Sequência recorde').classes('estat-sub')

                ui.label('Pontos').style('font-size:14px; font-weight:700; color:#0f172a; margin:0 auto')
                ui.label('Últimos 15 dias').style('font-size:11px; color:#64748b; margin:0 auto')
                grafico_barras_minimalista(vals_graf)

            with ui.column().classes('right-card'):
                with ui.column().classes('rc-box'):
                    with ui.row().classes('w-full justify-between items-center mb-3'):
                        ui.label('Ofensiva').style('font-size:13px; font-weight:700; color:#334155')
                        ui.label(f'{dias_ofensiva} dias').style('font-size:14px; font-weight:800; color:#0f172a')
                    
                    dt_dom = datetime.now() - timedelta(days=(datetime.now().weekday()+1)%7)
                    with ui.element('div').classes('grid-7-col'):
                        for i, dname in enumerate(['dom','seg','ter','qua','qui','sex','sáb']):
                            dt_str = (dt_dom + timedelta(days=i)).strftime('%Y-%m-%d')
                            with ui.element('div').classes('grid-cell'):
                                render_fire_icon(dt_str in cal_state.datas_ativas, '20px')
                                ui.label(dname).style('font-size:9px; color:#64748b; font-weight:500')
                
                with ui.column().classes('rc-box'): render_calendario()

class TelaInicial:
    def render(self): render_tela_inicial()
