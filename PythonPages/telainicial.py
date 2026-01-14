from nicegui import ui, app
import calendar
import requests
from datetime import datetime

# ====== CONFIGURAÇÕES DE API ======
API_URL_BASE = 'https://lexora-api.onrender.com/'

# ⚠️ IMPORTANTE: Cole seu token de acesso aqui para testar (ou puxe do login)
TOKEN_USUARIO = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZF91c3VhcmlvIjoxLCJleHAiOjE3Njg0NDMwOTB9.m_njn9-eLn0_hTRFplWnpAaee7x8Lih1OndQwTbFw-0"

def get_headers():
    return {
        'Authorization': f'Bearer {TOKEN_USUARIO}',
        'accept': 'application/json'
    }

# ====== ARQUIVOS ESTÁTICOS (IMAGENS) ======
# Ajuste o caminho se necessário
app.add_static_files('/images', r'C:\Users\Luca\Desktop\Lexora\LexoraWeb\images')

# CORES E CAMINHOS
PRIMARY = '#1153BE'
LOGO_PATH = '/images/logo.png'
FIRE_PATH = '/images/fogo.png'
SNOW_PATH = '/images/triste.png'
FIRE_DARK_PATH = '/images/fogoescuro.png'
FIRE_GRAY_PATH = '/images/fogocinza.png'
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]

# ====== CSS GLOBAL ======
ui.add_head_html("""
<style>
body { background: #F3F4F6; font-family: system-ui, -apple-system, sans-serif; }
.logo-fixa { height: 20px !important; width: auto !important; object-fit: contain !important; display: block !important; }
.calcel { display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; padding: 0 !important; margin: 0 !important; }
.calicone { width: 18px !important; height: 24px !important; object-fit: contain !important; display: block !important; }
.menu-card, .center-card, .calendar-card, .right-card { background: #FFFFFF; border-radius: 16px; box-shadow: 0 10px 25px rgba(15, 23, 42, 0.06); }
.menu-card { width: 230px; padding: 18px; }
.center-card { width: 640px; padding: 20px 26px 24px 26px; margin: 0 16px; }
.right-card { width: 260px; padding: 14px 16px; }
.ofensiva-title { font-size: 14px; font-weight: 600; color: #111827; }
.ofensiva-sub { font-size: 13px; color: #6B7280; }
.estat-title { font-size: 13px; letter-spacing: 0.08em; font-weight: 600; color: #9CA3AF; }
.estat-box { flex: 1; background: #F9FAFB; border-radius: 14px; padding: 14px 12px; }
.estat-num { font-size: 20px; font-weight: 700; color: #111827; }
.estat-sub { font-size: 13px; color: #6B7280; }
</style>
""", shared=True)

# ====== FUNÇÕES DE INTEGRAÇÃO (BACKEND) ======

def buscar_dados_perfil():
    # Rota 1: Informações do Usuário
    try:
        resp = requests.get(f'{API_URL_BASE}usuarios/UsuarioInformacao', headers=get_headers())
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Erro ao buscar perfil: {e}")
    return {}

def buscar_estatisticas_gerais():
    # Rota 2: Estatísticas do Usuário
    try:
        resp = requests.get(f'{API_URL_BASE}relatorio/EstatisticaUsuario', headers=get_headers())
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Erro ao buscar estatísticas: {e}")
    return {}

def buscar_ofensiva():
    # Rota 3: Ofensiva do Usuário
    try:
        resp = requests.get(f'{API_URL_BASE}relatorio/OfensivaUsuario', headers=get_headers())
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Erro ao buscar ofensiva: {e}")
    return {}

def buscar_atividade_grafico():
    # Rota 4: Atividade (Gráfico)
    try:
        resp = requests.get(f'{API_URL_BASE}relatorio/AtividadeUsuario', headers=get_headers())
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Erro ao buscar atividades: {e}")
    return []

# ====== COMPONENTES VISUAIS ======

def calendario(data_dias, mes, ano, callback_mes):
    with ui.column().classes('calendar-card').style('align-items:stretch;width:100%'):
        # Dias da semana
        with ui.grid(columns=7).classes('w-full').style('gap:0;margin-bottom:2px'):
            for d in DIAS:
                with ui.element('div').classes('calcel'):
                    ui.label(d).style('font-size:12px;font-weight:600;color:#6B7280;text-transform:lowercase;')
        
        # Foguinhos da semana (exemplo estático por enquanto)
        with ui.grid(columns=7).classes('w-full').style('gap:0;margin-bottom:10px'):
            dias_hoje = [FIRE_PATH] * 6 + [SNOW_PATH]
            for img in dias_hoje:
                with ui.element('div').classes('calcel'):
                    ui.image(img).classes('calicone')

        # Cabeçalho Mês
        with ui.row().style('margin:0 0 4px 0;align-items:center;justify-content:center;position:relative'):
            ui.button('←', on_click=lambda: callback_mes(-1)).props('flat round dense color=grey').style('position:absolute;left:0;')
            ui.label(f"{mes.upper()} {ano}").style('font-size:13px;font-weight:600;color:#6B7280;letter-spacing:0.18em')
            ui.button('→', on_click=lambda: callback_mes(1)).props('flat round dense color=grey').style('position:absolute;right:0;')

        # Dias numéricos
        with ui.grid(columns=7).classes('w-full').style('gap:0;margin-top:2px;margin-bottom:2px'):
            for d in DIAS:
                with ui.element('div').classes('calcel'):
                    ui.label(d + ".").style('font-size:11px;font-weight:500;color:#9CA3AF;text-align:center;text-transform:lowercase;')

        # Foguinhos do mês
        with ui.grid(columns=7).classes('w-full').style('gap:0;margin-top:2px;margin-bottom:0'):
            for ico in data_dias:
                with ui.element('div').classes('calcel'):
                    if ico: ui.image(ico).classes('calicone')
                    else: ui.label("").style('min-width:18px;min-height:24px')

def grafico_barras(valores, total=1000):
    with ui.row().style('margin-top:14px;margin-bottom:12px;justify-content:center;gap:10px;max-width:480px;width:100%;margin-left:auto;margin-right:auto;'):
        gray_height = 96
        # Se vier vazio da API, mostra zeros
        if not valores: valores = [0] * 15
        
        # Pega apenas os últimos 15 dias se vierem muitos dados
        dados_recentes = valores[-15:]
        
        for v in dados_recentes:
            val = float(v) # garante que é número
            pct = min(val / total, 1.0)
            label = f"{int(val / 1000)}k" if val >= 1000 else f"{int(val)}"
            with ui.column().style('align-items:center;gap:4px;'):
                with ui.element('div').style(f'width:16px;height:{gray_height}px;background:#E5E7EB;position:relative;border-radius:10px 10px 0 0;display:flex;align-items:flex-end;overflow:visible'):
                    ui.element('div').style(f'width:16px;height:{int(gray_height * pct)}px;background:{PRIMARY};position:absolute;left:0;bottom:0;border-radius:10px 10px 0 0;')
                ui.label(label).style('font-size:11px;color:#9CA3AF;text-align:center;min-width:16px;')

# ====== PÁGINA PRINCIPAL ======
@ui.page('/')
def main():
    # --- 1. CARREGAR DADOS DO BACKEND ---
    perfil = buscar_dados_perfil()
    estatisticas = buscar_estatisticas_gerais()
    ofensiva = buscar_ofensiva()
    atividades_grafico = buscar_atividade_grafico()

    # --- 2. PROCESSAR DADOS (COM VALORES PADRÃO) ---
    
    # Perfil
    nome_completo = perfil.get('nome', 'Usuário')
    email_user = perfil.get('email', '---')
    data_nasc_raw = perfil.get('dataNascimento', '---')
    # Tenta formatar a data se vier YYYY-MM-DD
    try:
        if data_nasc_raw != '---':
            data_nasc = datetime.strptime(data_nasc_raw.split('T')[0], '%Y-%m-%d').strftime('%d / %m / %Y')
        else:
            data_nasc = '---'
    except:
        data_nasc = data_nasc_raw

    # Estatísticas
    dias_ativos = estatisticas.get('diasAtivos', 0)
    atividades_feitas = estatisticas.get('atividadesConcluidas', 0) # Ajuste o nome da chave se necessário
    pontos_total = estatisticas.get('pontos', 0)
    seq_atual = estatisticas.get('ofensivaAtual', 0)
    seq_recorde = estatisticas.get('ofensivaRecorde', 0)

    # Ofensiva (assumindo que retorna um numero ou objeto com numero)
    dias_ofensiva = ofensiva.get('dias', 0) if isinstance(ofensiva, dict) else 0

    # Gráfico (extrair apenas valores numéricos se vier objeto complexo)
    # Supondo que a API retorne uma lista de números [10, 50, 20...] ou objetos [{'pontos': 10}, ...]
    valores_grafico = []
    if isinstance(atividades_grafico, list):
        for item in atividades_grafico:
            if isinstance(item, (int, float)):
                valores_grafico.append(item)
            elif isinstance(item, dict):
                valores_grafico.append(item.get('pontos', 0)) # Ajuste chave se necessário

    # Se não tiver dados suficientes no gráfico, preenche com dummy
    if not valores_grafico:
        valores_grafico = [0] * 15

    # --- 3. RENDERIZAR TELA ---

    # Topo
    with ui.row().classes('w-full').style('align-items:center;justify-content:space-between;margin-bottom:8px;'):
        with ui.row().style('align-items:center;gap:8px;margin-left:16px;'):
            ui.image(LOGO_PATH).classes('logo-fixa').props('fit=contain')
            ui.label('Lexora').style('font-size:20px;font-weight:600;color:#111827;')
        with ui.row().style('align-items:center;gap:6px;margin-right:18px'):
            ui.label('Sair da conta').style('font-size:14px;color:#6B7280;')
            ui.icon('logout').style('color:#6B7280;font-size:18px;')

    # Conteúdo
    with ui.row().style('margin-top:8px;justify-content:center;width:100%;gap:18px'):
        
        # CARD ESQUERDA (PERFIL)
        with ui.column().classes('menu-card').style('align-items:flex-start;gap:8px'):
            ui.html('<b>Meu perfil</b>', sanitize=False)
            ui.html(f'<div class="perfil-row"><span class="perfil-icon">👤</span><span class="perfil-value">Nome completo<br><span style="font-weight:400;font-size:13px">{nome_completo}</span></span></div>', sanitize=False)
            ui.html(f'<div class="perfil-row"><span class="perfil-icon">📅</span><span class="perfil-value">Data de nascimento<br><span style="font-weight:400;font-size:13px">{data_nasc}</span></span></div>', sanitize=False)
            ui.html(f'<div class="perfil-row"><span class="perfil-icon">📧</span><span class="perfil-value">E-mail<br><span style="font-weight:400;font-size:13px">{email_user}</span></span></div>', sanitize=False)
            ui.html('<div class="perfil-row"><span class="perfil-icon">🌎</span><span class="perfil-value">Idioma<br><span style="font-weight:400;font-size:13px">Inglês</span></span></div>', sanitize=False)

        # CARD CENTRAL (ESTATÍSTICAS)
        with ui.column().classes('center-card').style('gap:6px'):
            ui.label('Meu aprendizado').style('font-size: 20px; font-weight:700; margin-bottom: 4px; color:#111827')
            
            # Botões (estáticos por enquanto)
            with ui.row().style('gap:10px;margin-bottom:8px'):
                ui.button('IDIOMA INGLÊS').props('flat').style('background:#D2E4FD;font-size:14px;color:#111827;border-radius:12px;font-weight:600;height:36px;padding:0 18px')
                ui.button('NÍVEL AVANÇADO').props('flat').style('background:#FCF3D6;font-size:14px;color:#854D0E;border-radius:12px;font-weight:600;height:36px;padding:0 18px')
                ui.button('OBJETIVO VIAGEM ✏️', on_click=lambda: ui.notify('Editar')).props('flat').style('background:#C9F0DB;font-size:14px;color:#166534;border-radius:12px;font-weight:600;height:36px;padding:0 18px')

            # Meta diária (estático por enquanto)
            ui.html('<div style="color:#6B7280;font-size:13px;margin-bottom:0px;">Meta diária</div>', sanitize=False)
            with ui.element('div').style('margin:6px 0 4px 0;width:100%'):
                with ui.element('div').style('width:100%;background:#E5E7EB;height:6px;border-radius:999px'):
                    ui.element('div').style('height:100%;width:70%;background:#111827;border-radius:999px')
                with ui.row().style('align-items:center;gap:6px;margin-top:4px'):
                    ui.label('7/10 lições').style('font-size:12px;color:#4B5563;')

            # Números dinâmicos da API
            ui.label('ESTATÍSTICAS').classes('estat-title').style('margin-top:10px;text-align:center;align-self:center;')
            with ui.column().style('width:100%;align-items:center'):
                with ui.row().classes('estat-cards').style('gap:10px;margin-top:6px;justify-content:center;max-width:460px'):
                    with ui.element('div').classes('estat-box'):
                        ui.label(str(dias_ativos)).classes('estat-num')
                        ui.label('Dias ativos').classes('estat-sub').style('margin-top:-2px')
                    with ui.element('div').classes('estat-box'):
                        ui.label(str(atividades_feitas)).classes('estat-num')
                        ui.label('Atividades feitas').classes('estat-sub')
                    with ui.element('div').classes('estat-box'):
                        # Formata pontos com ponto de milhar
                        ui.label(f"{pontos_total:,}".replace(',', '.')).classes('estat-num')
                        ui.label('Total de pontos').classes('estat-sub')

                with ui.row().classes('estat-cards').style('gap:10px;margin-top:8px;justify-content:center;max-width:320px'):
                    with ui.element('div').classes('estat-box'):
                        ui.label(str(seq_atual)).classes('estat-num')
                        ui.label('Sequência').classes('estat-sub')
                    with ui.element('div').classes('estat-box'):
                        ui.label(str(seq_recorde)).classes('estat-num')
                        ui.label('Sequência recorde').classes('estat-sub')

            # Gráfico dinâmico da API
            ui.label('Pontos').style('margin-top:12px;margin-bottom:0px;font-size:14px;color:#111827;font-weight:600;text-align:center;align-self:center')
            ui.label('Últimos 15 dias').style('font-size:12px;color:#9CA3AF;margin-bottom:2px;text-align:center;align-self:center')
            
            grafico_barras(valores_grafico, total=1200)

        # CARD DIREITA (CALENDÁRIO/OFENSIVA)
        with ui.column().classes('right-card').style('align-items:stretch;gap:8px'):
            with ui.row().style('align-items:center;justify-content:space-between'):
                ui.label('Ofensiva').classes('ofensiva-title')
                ui.label(f'{dias_ofensiva} dias').classes('ofensiva-sub')

            hoje = datetime.now()
            mes_num = hoje.month
            ano_num = hoje.year
            meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
            
            # Lógica simples de calendário (primeiros X dias azuis)
            # Idealmente a API retornaria quais dias foram concluídos
            dias_no_mes = calendar.monthrange(ano_num, mes_num)[1]
            dias_status = []
            for dia in range(1, dias_no_mes + 1):
                if dia <= dias_ofensiva: # Pinta azul se estiver dentro da ofensiva
                    dias_status.append(FIRE_DARK_PATH)
                else:
                    dias_status.append(FIRE_GRAY_PATH)
            
            # Completa grid 6x7 (42 células)
            while len(dias_status) < 42:
                dias_status.append("")

            def muda_mes(delta):
                ui.notify('Troca de mês não implementada')

            calendario(dias_status, meses[mes_num - 1], ano_num, muda_mes)

ui.run()
