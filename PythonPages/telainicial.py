from nicegui import ui, app
import calendar
import requests
from datetime import datetime, timedelta
from pathlib import Path

# ====== CONFIGURAÇÕES DE API ======
API_URL_BASE = 'https://lexora-api.onrender.com/'

def get_headers() -> dict:
    token = app.storage.user.get('token')
    if not token: return {'accept': 'application/json'}
    return {'Authorization': f'Bearer {token}', 'accept': 'application/json'}

# ====== ARQUIVOS ESTÁTICOS ======
try:
    script_dir = Path(__file__).parent.resolve()
    images_dir = script_dir.parent / 'images'
    if not images_dir.is_dir(): images_dir = script_dir / 'images'
    if images_dir.is_dir(): app.add_static_files('/images', str(images_dir))
except Exception: pass

# CORES E CAMINHOS
PRIMARY = '#1153BE'
LOGO_PATH = '/images/logo.png'
FIRE_PATH = '/images/fogo.png'          # Fogo Azul (Ativo)
FIRE_GRAY_PATH = '/images/fogocinza.png' # Fogo Cinza (Inativo)

# ====== CSS GLOBAL ======
ui.add_head_html("""
<style>
.calicone { width: 24px !important; height: auto !important; object-fit: contain; }
.menu-card, .center-card, .right-card { background: #FFFFFF; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); }
.menu-card { width: 260px; padding: 24px; height: fit-content; }
.center-card { flex: 1; max-width: 680px; padding: 32px; margin: 0 24px; }
.right-card { width: 300px; padding: 0; background: transparent; box-shadow: none; display: flex; flex-direction: column; gap: 20px;}
.rc-box { background: #fff; border-radius: 20px; padding: 20px; width: 100%; box-shadow: 0 4px 20px rgba(0,0,0,0.03); }

.estat-box { flex: 1; background: #F8FAFC; border-radius: 16px; padding: 20px 10px; min-width: 140px; text-align: center; }
.estat-num { font-size: 28px; font-weight: 800; color: #1e293b; line-height: 1.2; }
.estat-sub { font-size: 13px; color: #64748b; font-weight: 500; }

.perfil-row { display: flex; align-items: flex-start; margin-bottom: 16px; }
.perfil-icon { font-size: 18px; margin-right: 12px; width: 20px; text-align: center; opacity: 0.6; }
.perfil-value { font-size: 14px; color: #334155; font-weight: 600; line-height: 1.4; }

.cal-nav-btn { color: #64748b; cursor: pointer; font-size: 18px; user-select: none; }
.cal-nav-btn:hover { color: #1153BE; }
</style>
""", shared=True)

# ====== BACKEND ======
def get_json(path: str, default):
    try:
        resp = requests.get(f'{API_URL_BASE}{path}', headers=get_headers(), timeout=10)
        return resp.json() if resp.status_code == 200 else default
    except: return default

def buscar_dados_perfil(): return get_json('usuarios/UsuarioInformacao', {})
def buscar_estatisticas_gerais(): return get_json('relatorio/EstatisticaUsuario', {})
def buscar_ofensiva(): return get_json('relatorio/OfensivaUsuario', {})
def buscar_atividade_meta(): return get_json('relatorio/AtividadeUsuario', []) 
def buscar_historico_pontos(): return get_json('relatorio/DataUsuario', []) # Endpoint correto para calendário e gráfico

# ====== COMPONENTES ======

def grafico_barras_minimalista(valores, max_valor=100):
    if not any(valores): max_valor = 100
    max_dado = max(valores) if valores else 0
    if max_dado > max_valor: max_valor = max_dado
    
    with ui.row().style('justify-content:space-between; align-items:flex-end; height:140px; width:100%; gap:6px; padding-top:20px'):
        dados_finais = (([0]*15) + list(valores))[-15:] # Garante 15 itens

        for v in dados_finais:
            val = float(v)
            pct = min(val / max_valor, 1.0) if max_valor > 0 else 0
            label = f"{int(val/1000)}k" if val >= 1000 else f"{int(val)}"
            
            with ui.column().style('align-items:center; gap:6px; flex:1;'):
                # Valor no topo (opcional, pode ficar poluído)
                ui.label(label).style(f'font-size:10px; color:#64748b; opacity:{1 if val > 0 else 0}; font-weight:600')
                
                # Barra
                with ui.element('div').style('width:8px; height:100px; background:#F1F5F9; border-radius:99px; position:relative; overflow:hidden'):
                    if pct > 0:
                        ui.element('div').style(f'width:100%; height:{pct*100}%; background:{PRIMARY}; position:absolute; bottom:0; left:0; border-radius:99px')

# Estado do Calendário
class CalendarState:
    def __init__(self):
        self.hoje = datetime.now()
        self.ano_visivel = self.hoje.year
        self.mes_visivel = self.hoje.month

cal_state = CalendarState()

@ui.refreshable
def render_calendario(datas_ativas_set):
    # Cabeçalho do Calendário (Mês e Navegação)
    nome_mes = calendar.month_name[cal_state.mes_visivel].upper()
    # Tradução simples manual ou usar locale se preferir
    meses_pt = ["", "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO", "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]
    nome_mes_pt = meses_pt[cal_state.mes_visivel]

    with ui.row().classes('w-full items-center justify-between mb-4'):
        ui.icon('chevron_left').classes('cal-nav-btn').on('click', lambda: mudar_mes(-1, datas_ativas_set))
        ui.label(f'{nome_mes_pt} {cal_state.ano_visivel}').style('font-size:13px; font-weight:700; color:#334155; letter-spacing:0.5px')
        ui.icon('chevron_right').classes('cal-nav-btn').on('click', lambda: mudar_mes(1, datas_ativas_set))

    # Grade de Dias da Semana
    dias_semana = ['dom.', 'seg.', 'ter.', 'qua.', 'qui.', 'sex.', 'sáb.']
    with ui.row().classes('w-full justify-between mb-2'):
        for d in dias_semana:
            ui.label(d).style('font-size:11px; color:#94a3b8; width:28px; text-align:center;')

    # Grade de Dias do Mês
    cal = calendar.monthcalendar(cal_state.ano_visivel, cal_state.mes_visivel)
    
    # Ajusta para começar Domingo (padrão python é Segunda=0)
    # monthcalendar já retorna listas de semanas. Se setfirstweekday não for chamado, Segunda é o primeiro.
    # Vamos garantir Domingo como primeiro visualmente ajustando a lógica se necessário.
    calendar.setfirstweekday(calendar.SUNDAY) 
    cal = calendar.monthcalendar(cal_state.ano_visivel, cal_state.mes_visivel)

    for semana in cal:
        with ui.row().classes('w-full justify-between mb-2'):
            for dia in semana:
                with ui.column().style('width:28px; align-items:center; gap:2px'):
                    if dia == 0:
                        ui.label('').style('height:24px') # Espaço vazio
                    else:
                        # Verifica se o dia teve atividade
                        data_str = f"{cal_state.ano_visivel}-{cal_state.mes_visivel:02d}-{dia:02d}"
                        ativo = data_str in datas_ativas_set
                        img = FIRE_PATH if ativo else FIRE_GRAY_PATH
                        opacity = "1" if ativo else "0.3"
                        
                        ui.image(img).classes('calicone').style(f'opacity:{opacity}')
                        # ui.label(str(dia)).style('font-size:10px; color:#cbd5e1') # Opcional: número do dia

def mudar_mes(delta, datas_ativas_set):
    cal_state.mes_visivel += delta
    if cal_state.mes_visivel > 12:
        cal_state.mes_visivel = 1
        cal_state.ano_visivel += 1
    elif cal_state.mes_visivel < 1:
        cal_state.mes_visivel = 12
        cal_state.ano_visivel -= 1
    render_calendario.refresh()

# ====== TELA INICIAL ======
def render_tela_inicial() -> None:
    if not app.storage.user.get('token'):
        ui.navigate.to('/')
        return

    # Busca Dados
    perfil = buscar_dados_perfil() or {}
    estatisticas = buscar_estatisticas_gerais() or {}
    ofensiva_data = buscar_ofensiva() or {}
    meta_raw = buscar_atividade_meta() or []
    historico_raw = buscar_historico_pontos() or []

    # Processamento Perfil
    nome = perfil.get('nome', 'Usuário')
    email = perfil.get('email', '')
    nasc = perfil.get('data_nascimento', '')
    try: nasc = datetime.strptime(nasc.split('T')[0], '%Y-%m-%d').strftime('%d / %m / %Y')
    except: pass
    idioma = perfil.get('usuario_experiencia_idioma', {}).get('descricao_idioma', 'Inglês')
    nivel = perfil.get('usuario_experiencia_idioma', {}).get('descricao_experiencia_idioma', 'Iniciante')
    objetivo = perfil.get('objetivos_usuario', {}).get('descricao_objetivo', 'Aprender')

    # Processamento Histórico (Pontos e Datas Ativas)
    valores_grafico = []
    datas_ativas = set() # Set para busca rápida O(1)
    
    if isinstance(historico_raw, list):
        # Ordena cronologicamente
        historico_raw.sort(key=lambda x: x.get('data', ''))
        
        for item in historico_raw:
            data = item.get('data', '').split('T')[0]
            pts = float(item.get('pontos', 0))
            
            if pts > 0:
                datas_ativas.add(data)
                
            valores_grafico.append(pts)

    # Processamento Meta Diária
    hoje_str = datetime.now().strftime('%Y-%m-%d')
    pontos_hoje = 0
    # Procura se tem registro de hoje no histórico
    for item in historico_raw:
        if item.get('data', '').startswith(hoje_str):
            pontos_hoje = float(item.get('pontos', 0))
            break
            
    meta_diaria = 5 # Meta em Lições (conforme pedido anterior)
    # Tenta pegar atividades feitas da rota de Meta (que retorna lições, não pontos)
    licoes_hoje = 0
    if isinstance(meta_raw, dict): 
        licoes_hoje = meta_raw.get('atividades_feitas', 0)
        meta_diaria = meta_raw.get('meta', 5)
    elif isinstance(meta_raw, list) and meta_raw:
         if isinstance(meta_raw[-1], dict):
             licoes_hoje = meta_raw[-1].get('atividades_feitas', 0)
             meta_diaria = meta_raw[-1].get('meta', 5)

    # Processamento Ofensiva (Número)
    dias_ofensiva = estatisticas.get('ultima_sequencia', 0)

    # --- UI PRINCIPAL ---
    ui.query('body').style('background-color: #f8fafc;') # Fundo cinza claro igual imagem

    with ui.row().classes('w-full justify-center').style('padding:40px 20px; align-items:flex-start; max_width:1400px; margin:0 auto; gap:24px'):
        
        # 1. Coluna Esquerda: Perfil
        with ui.column().classes('menu-card'):
            ui.label('Meu perfil').style('font-size:18px; font-weight:800; color:#0f172a; margin-bottom:24px')
            
            ui.html(f'<div class="perfil-row"><span class="perfil-icon">👤</span><span class="perfil-value">Nome completo<br><span style="font-weight:400;font-size:13px;color:#64748b">{nome}</span></span></div>')
            ui.html(f'<div class="perfil-row"><span class="perfil-icon">📅</span><span class="perfil-value">Data de nascimento<br><span style="font-weight:400;font-size:13px;color:#64748b">{nasc}</span></span></div>')
            ui.html(f'<div class="perfil-row"><span class="perfil-icon">✉️</span><span class="perfil-value">E-mail<br><span style="font-weight:400;font-size:13px;color:#64748b">{email}</span></span></div>')
            ui.html(f'<div class="perfil-row"><span class="perfil-icon">🌐</span><span class="perfil-value">Idioma<br><span style="font-weight:400;font-size:13px;color:#64748b">{idioma}</span></span></div>')

        # 2. Coluna Central: Dashboard
        with ui.column().classes('center-card'):
            # Topo: Cards de Status
            ui.label('Meu aprendizado').style('font-size:22px; font-weight:800; color:#0f172a; margin-bottom:16px')
            
            with ui.row().classes('w-full').style('gap:16px; margin-bottom:32px'):
                # Idioma
                with ui.row().style('flex:1; background:#EEF2FF; padding:16px; border-radius:16px; align-items:center; gap:12px'):
                    ui.icon('public', color='blue-8').style('font-size:24px')
                    with ui.column().style('gap:0'):
                        ui.label('Idioma').style('font-size:11px; font-weight:700; color:#3b82f6')
                        ui.label(idioma).style('font-size:15px; font-weight:700; color:#1e3a8a')
                
                # Nível
                with ui.row().style('flex:1; background:#FFFBEB; padding:16px; border-radius:16px; align-items:center; gap:12px'):
                    ui.icon('star', color='orange-8').style('font-size:24px')
                    with ui.column().style('gap:0'):
                        ui.label('Nível').style('font-size:11px; font-weight:700; color:#d97706')
                        ui.label(nivel).style('font-size:15px; font-weight:700; color:#78350f')

                # Objetivo
                with ui.row().style('flex:1; background:#ECFDF5; padding:16px; border-radius:16px; align-items:center; gap:12px'):
                    ui.icon('track_changes', color='green-8').style('font-size:24px')
                    with ui.column().style('gap:0'):
                        ui.label('Objetivo').style('font-size:11px; font-weight:700; color:#059669')
                        ui.label(objetivo).style('font-size:15px; font-weight:700; color:#064e3b')

            # Meta Diária
            with ui.row().classes('w-full justify-between items-end mb-2'):
                ui.label('Meta diária').style('font-size:16px; font-weight:700; color:#0f172a')
                ui.label(f'{int(licoes_hoje)}/{int(meta_diaria)} lições').style('font-size:13px; font-weight:600; color:#64748b')
            
            pct_meta = min(licoes_hoje / meta_diaria, 1.0) if meta_diaria > 0 else 0
            with ui.element('div').classes('w-full').style('height:8px; background:#f1f5f9; border-radius:99px; overflow:hidden; margin-bottom:40px'):
                ui.element('div').style(f'height:100%; width:{pct_meta*100}%; background:#1e293b; border-radius:99px')

            # Estatísticas Grandes
            ui.label('ESTATÍSTICAS').style('font-size:13px; font-weight:800; color:#0f172a; text-transform:uppercase; letter-spacing:1px; margin:0 auto 20px auto')
            
            with ui.row().classes('w-full').style('gap:16px; margin-bottom:16px'):
                with ui.column().classes('estat-box'):
                    ui.label(str(estatisticas.get('dias_ativo', 0))).classes('estat-num')
                    ui.label('Dias ativos').classes('estat-sub')
                with ui.column().classes('estat-box'):
                    ui.label(str(estatisticas.get('atividades_feitas', 0))).classes('estat-num')
                    ui.label('Atividades feitas').classes('estat-sub')
                with ui.column().classes('estat-box'):
                    pts = int(estatisticas.get('pontos_totais', 0))
                    ui.label(f"{pts:,}".replace(",", ".")).classes('estat-num')
                    ui.label('Total de pontos').classes('estat-sub')
            
            with ui.row().classes('w-full justify-center').style('gap:16px; margin-bottom:40px'):
                with ui.column().classes('estat-box').style('max-width:240px'):
                    ui.label(str(estatisticas.get('ultima_sequencia', 0))).classes('estat-num')
                    ui.label('Sequência').classes('estat-sub')
                with ui.column().classes('estat-box').style('max-width:240px'):
                    ui.label(str(estatisticas.get('maior_sequencia', 0))).classes('estat-num')
                    ui.label('Sequência recorde').classes('estat-sub')

            # Gráfico
            ui.label('Pontos').style('font-size:16px; font-weight:700; color:#0f172a; margin:0 auto')
            ui.label('Últimos 15 dias').style('font-size:13px; color:#64748b; margin:0 auto')
            
            grafico_barras_minimalista(valores_grafico)


        # 3. Coluna Direita: Ofensiva e Calendário
        with ui.column().classes('right-card'):
            
            # --- Box 1: Ofensiva Semanal ---
            with ui.column().classes('rc-box'):
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Ofensiva').style('font-size:14px; font-weight:700; color:#334155')
                    ui.label(f'{dias_ofensiva} dias').style('font-size:16px; font-weight:800; color:#0f172a')
                
                # Gera dias da semana atual
                hoje = datetime.now()
                inicio_semana = hoje - timedelta(days=hoje.weekday() + 1) # Começa domingo
                if hoje.weekday() == 6: inicio_semana = hoje # Se hoje é domingo

                with ui.row().classes('w-full justify-between'):
                    dias_sigla = ['dom', 'seg', 'ter', 'qua', 'qui', 'sex', 'sáb']
                    for i in range(7):
                        dia_atual = inicio_semana + timedelta(days=i)
                        dia_str = dia_atual.strftime('%Y-%m-%d')
                        ativo = dia_str in datas_ativas
                        
                        with ui.column().style('align-items:center; gap:6px'):
                            img = FIRE_PATH if ativo else FIRE_GRAY_PATH
                            opacity = "1" if ativo else "0.3"
                            ui.image(img).classes('calicone').style(f'opacity:{opacity}; width:24px')
                            ui.label(dias_sigla[i]).style('font-size:11px; color:#64748b; font-weight:500')

            # --- Box 2: Calendário Mensal ---
            with ui.column().classes('rc-box'):
                render_calendario(datas_ativas)

class TelaInicial:
    def render(self):
        render_tela_inicial()
