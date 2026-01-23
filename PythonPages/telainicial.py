from nicegui import ui, app
import calendar
import requests
from datetime import datetime, timedelta
from pathlib import Path

# ====== CONFIGURAÇÕES DE API ======
API_URL_BASE = 'https://lexora-api.onrender.com/'

def get_headers() -> dict:
    token = app.storage.user.get('token')
    if not token:
        print('❌ [API] Token ausente.')
        return {'accept': 'application/json'}
    return {'Authorization': f'Bearer {token}', 'accept': 'application/json'}

# ====== ARQUIVOS ESTÁTICOS ======
try:
    local_images_dir = Path(r'C:\Users\Luca\Desktop\Lexora\LexoraWeb\images')
    if local_images_dir.exists():
        app.add_static_files('/images', str(local_images_dir))
except Exception: pass

# CORES E CAMINHOS
PRIMARY = '#1153BE'
LOGO_PATH = '/images/logo.png'
FIRE_PATH = '/images/fogo.png'
SNOW_PATH = '/images/triste.png'
FIRE_DARK_PATH = '/images/fogoescuro.png'
FIRE_GRAY_PATH = '/images/fogocinza.png'

# ====== CSS GLOBAL ======
ui.add_head_html("""
<style>
.calicone { width: 32px !important; height: auto !important; object-fit: contain !important; display: block !important; }
.menu-card, .center-card, .right-card { background: #FFFFFF; border-radius: 16px; box-shadow: 0 10px 25px rgba(15, 23, 42, 0.06); }
.menu-card { width: 230px; padding: 18px; }
.center-card { width: 640px; padding: 20px 26px 24px 26px; margin: 0 16px; }
.right-card { width: 260px; padding: 14px 16px; }
.estat-box { flex: 1; background: #F9FAFB; border-radius: 14px; padding: 14px 12px; min-width: 100px; text-align: center; }
.estat-num { font-size: 20px; font-weight: 700; color: #111827; }
.estat-sub { font-size: 13px; color: #6B7280; }
.logo-fixa { height: 32px; width: auto; }
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
def buscar_atividade_grafico(): return get_json('relatorio/AtividadeUsuario', [])

# ====== COMPONENTES ======
def grafico_barras(valores, max_valor=5):
    with ui.row().style('margin-top:14px;margin-bottom:12px;justify-content:center;gap:10px;max-width:480px;width:100%;margin-left:auto;margin-right:auto;'):
        if not valores: valores = [0] * 15
        dados = valores[-15:] if len(valores) >= 15 else list(valores)
        while len(dados) < 15: dados.insert(0, 0)

        for v in dados:
            val = float(v) if v else 0
            pct = min(val / max_valor, 1.0) if max_valor > 0 else 0
            label = f"{int(val/1000)}k" if val >= 1000 else f"{int(val)}"
            with ui.column().style('align-items:center;gap:4px;'):
                with ui.element('div').style('width:16px;height:96px;background:#E5E7EB;position:relative;border-radius:10px 10px 0 0;display:flex;align-items:flex-end;overflow:visible'):
                    ui.element('div').style(f'width:16px;height:{int(96 * pct)}px;background:{PRIMARY};position:absolute;left:0;bottom:0;border-radius:10px 10px 0 0;')
                ui.label(label).style('font-size:11px;color:#111827;text-align:center;min-width:16px;font-weight:600;')
                ui.label(str(int(val))).style('font-size:10px;color:#9CA3AF;text-align:center;min-width:16px;')

# ====== RENDER ======
def render_tela_inicial() -> None:
    if not app.storage.user.get('token'):
        ui.navigate.to('/')
        return

    def logout():
        app.storage.user.clear()
        ui.navigate.to('/')

    def ir_para_questoes():
        ui.notify('Carregando atividade...', color='info')
        ui.navigate.to('/questoes')

    # Carregamento de dados
    perfil = buscar_dados_perfil()
    estatisticas = buscar_estatisticas_gerais()
    ofensiva = buscar_ofensiva()
    atividades_grafico = buscar_atividade_grafico()

    # Processamento
    nome_completo = perfil.get('nome', 'Usuário')
    email_user = perfil.get('email', '---')
    data_nasc_raw = perfil.get('data_nascimento', '---')
    idioma = perfil.get('usuario_experiencia_idioma', {}).get('descricao_idioma', 'Idioma')
    experiencia = perfil.get('usuario_experiencia_idioma', {}).get('descricao_experiencia_idioma', '---')
    objetivo = perfil.get('objetivos_usuario', {}).get('descricao_objetivo', '---')

    try:
        data_nasc = datetime.strptime(data_nasc_raw.split('T')[0], '%Y-%m-%d').strftime('%d / %m / %Y') if data_nasc_raw != '---' else '---'
    except: data_nasc = data_nasc_raw

    dias_ativos = estatisticas.get('dias_ativo', 0)
    atividades_feitas_total = estatisticas.get('atividades_feitas', 0)
    pontos_total = estatisticas.get('pontos_totais', 0)
    seq_atual = estatisticas.get('ultima_sequencia', 0)
    seq_recorde = estatisticas.get('maior_sequencia', 0)

    atividades_feitas_hoje = 0
    meta_diaria = 5
    valores_grafico = [0] * 15

    if isinstance(atividades_grafico, dict):
        atividades_feitas_hoje = atividades_grafico.get('atividades_feitas', 0)
        meta_diaria = atividades_grafico.get('meta', 5)

    dias_ofensiva = seq_atual
    if isinstance(ofensiva, dict): dias_ofensiva = ofensiva.get('dias', seq_atual)
    elif isinstance(ofensiva, (int, float)): dias_ofensiva = int(ofensiva)

    # --- UI ---
    with ui.column().classes('w-full').style('align-items:center'):
        # Topbar
        with ui.row().classes('w-full').style('align-items:center;justify-content:space-between;margin-bottom:8px;padding:0 16px;max_width:1000px'):
            with ui.row().style('align-items:center;gap:8px;'):
                ui.image(LOGO_PATH).classes('logo-fixa').props('fit=contain')
                ui.label('Lexora').style('font-size:20px;font-weight:600;color:#111827;')
            ui.button('Sair', icon='logout', on_click=logout).props('flat dense').style('color:#6B7280;')

        with ui.row().style('margin-top:8px;justify-content:center;width:100%;gap:18px;flex-wrap:wrap'):
            
            # Card Perfil (Esquerda)
            with ui.column().classes('menu-card').style('align-items:flex-start;gap:8px'):
                ui.html('<b>Meu perfil</b>', sanitize=False)
                ui.html(f'<div class="perfil-row"><span class="perfil-icon">👤</span><span class="perfil-value">Nome<br><span style="font-weight:400;font-size:13px">{nome_completo}</span></span></div>', sanitize=False)
                ui.html(f'<div class="perfil-row"><span class="perfil-icon">📅</span><span class="perfil-value">Nascimento<br><span style="font-weight:400;font-size:13px">{data_nasc}</span></span></div>', sanitize=False)
                ui.html(f'<div class="perfil-row"><span class="perfil-icon">📧</span><span class="perfil-value">E-mail<br><span style="font-weight:400;font-size:13px">{email_user}</span></span></div>', sanitize=False)
                ui.html(f'<div class="perfil-row"><span class="perfil-icon">🌎</span><span class="perfil-value">Idioma<br><span style="font-weight:400;font-size:13px">{idioma}</span></span></div>', sanitize=False)

            # Card Central (Aprendizado e Stats)
            with ui.column().classes('center-card').style('gap:6px'):
                ui.label('Meu aprendizado').style('font-size: 20px; font-weight:700; margin-bottom: 4px; color:#111827')
                
                with ui.row().style('gap:10px;margin-bottom:8px;flex-wrap:wrap'):
                    ui.button(f'IDIOMA {idioma.upper()}').props('flat').style('background:#D2E4FD;font-size:14px;color:#111827;border-radius:12px;font-weight:600;height:36px;padding:0 18px')
                    ui.button(f'NÍVEL {experiencia.upper()}').props('flat').style('background:#FCF3D6;font-size:14px;color:#854D0E;border-radius:12px;font-weight:600;height:36px;padding:0 18px')
                    # ✅ BOTÃO OBJETIVO (Adicionado aqui)
                    ui.button(f'OBJETIVO {objetivo.upper()} ✏️').props('flat').style('background:#C9F0DB;font-size:14px;color:#166534;border-radius:12px;font-weight:600;height:36px;padding:0 18px')
                    
                    ui.button('INICIAR ATIVIDADE', icon='play_arrow', on_click=ir_para_questoes).props('flat').style('background:#E6F4FF;font-size:14px;color:#111827;border-radius:12px;font-weight:600;height:36px;padding:0 18px')

                ui.html('<div style="color:#6B7280;font-size:13px;margin-bottom:0px;">Meta diária</div>', sanitize=False)
                with ui.element('div').style('margin:6px 0 4px 0;width:100%'):
                    pct_meta = min((atividades_feitas_hoje / meta_diaria) * 100, 100) if meta_diaria > 0 else 0
                    with ui.element('div').style('width:100%;background:#E5E7EB;height:6px;border-radius:999px'):
                        ui.element('div').style(f'height:100%;width:{pct_meta}%;background:{PRIMARY};border-radius:999px')
                    ui.label(f'{int(atividades_feitas_hoje)}/{int(meta_diaria)} lições').style('font-size:12px;font-weight:500;color:#4B5563;margin-top:4px')

                # Estatísticas (4 blocos)
                ui.label('ESTATÍSTICAS').classes('estat-title').style('margin-top:10px;text-align:center;align-self:center;')
                with ui.column().style('width:100%;align-items:center'):
                    with ui.row().classes('estat-cards').style('gap:10px;margin-top:6px;justify-content:center;max-width:460px'):
                        with ui.element('div').classes('estat-box'):
                            ui.label(str(dias_ativos)).classes('estat-num')
                            ui.label('Dias ativos').classes('estat-sub')
                        with ui.element('div').classes('estat-box'):
                            ui.label(str(atividades_feitas_total)).classes('estat-num')
                            ui.label('Atividades feitas').classes('estat-sub')
                        with ui.element('div').classes('estat-box'):
                            ui.label(f"{int(pontos_total):,}".replace(',', '.')).classes('estat-num')
                            ui.label('Total de pontos').classes('estat-sub')

                    with ui.row().classes('estat-cards').style('gap:10px;margin-top:8px;justify-content:center;max-width:320px'):
                        with ui.element('div').classes('estat-box'):
                            ui.label(str(seq_atual)).classes('estat-num')
                            ui.label('Sequência').classes('estat-sub')
                        with ui.element('div').classes('estat-box'):
                            ui.label(str(seq_recorde)).classes('estat-num')
                            ui.label('Sequência recorde').classes('estat-sub')

                ui.label('Pontos - Últimos 15 dias').style('margin-top:12px;font-size:14px;font-weight:600;text-align:center;align-self:center')
                if valores_grafico and any(valores_grafico):
                    grafico_barras(valores_grafico, max_valor=meta_diaria)
                else:
                    ui.label('Nenhuma atividade recente').style('color:#9CA3AF;text-align:center;padding:20px')

            # Card Direito (Ofensiva Simplificada)
            with ui.column().classes('right-card').style('align-items:center;gap:12px;justify-content:center;min-height:150px'):
                
                # Título
                ui.label('Ofensiva').style('font-size:14px;font-weight:600;color:#111827;')
                
                # Ícone do Fogo
                img_fogo = FIRE_DARK_PATH if dias_ofensiva > 0 else SNOW_PATH
                ui.image(img_fogo).classes('calicone').style('width:40px;height:auto;')
                
                # Texto da Ofensiva
                if dias_ofensiva > 0:
                    ui.label(f'{dias_ofensiva} {"dia" if dias_ofensiva == 1 else "dias"}').style(f'font-size:24px;font-weight:700;color:{PRIMARY};')
                    if dias_ofensiva == 1:
                        ui.label('Você está no seu primeiro dia de ofensiva!').style('font-size:13px;color:#6B7280;text-align:center;line-height:1.4')
                    else:
                        ui.label('dias de ofensiva seguidos!').style('font-size:13px;color:#6B7280;text-align:center')
                else:
                    ui.label('0 dias').style('font-size:24px;font-weight:700;color:#9CA3AF;')
                    ui.label('Sem ofensiva ativa').style('font-size:13px;color:#9CA3AF;text-align:center')

class TelaInicial:
    def render(self):
        render_tela_inicial()
