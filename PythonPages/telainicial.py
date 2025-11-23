from nicegui import ui, app
import calendar
from datetime import datetime

# ====== ARQUIVOS ESTÁTICOS (IMAGENS) ======
app.add_static_files(
    '/images',
    r'C:\Users\Luca\Desktop\Lexora\LexoraWeb\images'
)

# CORES E CAMINHOS
PRIMARY = '#1153BE'
BG_LIGHT = '#F3F4F6'
CARD = '#FFFFFF'
BORDER = '#E5E7EB'
SUBTLE = '#6B7280'
GRAY_BG = '#F3F4F6'
TEXT = '#2D3641'
GRAY = '#C6C6C6'

LOGO_PATH = '/images/logo.png'
FIRE_PATH = '/images/fogo.png'
SNOW_PATH = '/images/triste.png'
FIRE_DARK_PATH = '/images/fogoescuro.png'   # azul
FIRE_GRAY_PATH = '/images/fogocinza.png'    # cinza

DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]

# ====== CSS GLOBAL ======
ui.add_head_html("""
<style>
body {
    background: #F3F4F6;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* logo com altura parecida com o texto "Lexora" */
.logo-fixa {
    height: 20px !important;
    width: auto !important;
    object-fit: contain !important;
    margin: 0 !important;
    display: block !important;
}

.calcel {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* fogo um pouco mais alto para não cortar */
.calicone {
    width: 18px !important;
    height: 24px !important;
    object-fit: contain !important;
    display: block !important;
    margin: 0 !important;
    padding: 0 !important;
}

.menu-card, .center-card, .calendar-card, .right-card {
    background: #FFFFFF;
    border-radius: 16px;
    box-shadow: 0 10px 25px rgba(15, 23, 42, 0.06);
}

.menu-card {
    width: 230px;
    padding: 18px 18px 20px 18px;
}

.center-card {
    width: 640px;
    padding: 20px 26px 24px 26px;
    margin: 0 16px;
}

.right-card {
    width: 260px;
    padding: 14px 16px 16px 16px;
}

.ofensiva-title {
    font-size: 14px;
    font-weight: 600;
    color: #111827;
}

.ofensiva-sub {
    font-size: 13px;
    color: #6B7280;
}

.estat-title {
    font-size: 13px;
    letter-spacing: 0.08em;
    font-weight: 600;
    color: #9CA3AF;
}

.estat-box {
    flex: 1;
    background: #F9FAFB;
    border-radius: 14px;
    padding: 14px 12px;
}

.estat-num {
    font-size: 20px;
    font-weight: 700;
    color: #111827;
}

.estat-sub {
    font-size: 13px;
    color: #6B7280;
}
</style>
""", shared=True)

# ====== COMPONENTES ======
def calendario(data_dias, mes, ano, callback_mes):
    with ui.column().classes('calendar-card').style('align-items:stretch;width:100%'):
        # linha dias semana ofensiva (topo)
        with ui.grid(columns=7).classes('w-full').style('gap:0;margin-bottom:2px'):
            for d in DIAS:
                with ui.element('div').classes('calcel'):
                    ui.label(d).style(
                        'font-size:12px;font-weight:600;'
                        'color:#6B7280;text-align:center;text-transform:lowercase;'
                    )

        # linha ícones ofensiva
        with ui.grid(columns=7).classes('w-full').style('gap:0;margin-bottom:10px'):
            dias_hoje = [FIRE_PATH] * 6 + [SNOW_PATH]
            for img in dias_hoje:
                with ui.element('div').classes('calcel'):
                    ui.image(img).classes('calicone')

        # cabeçalho mês com setas (mês centralizado)
        with ui.row().style(
            'margin:0 0 4px 0;align-items:center;justify-content:center;position:relative'):
            ui.button('←', on_click=lambda: callback_mes(-1)).props(
                'flat round dense color=grey'
            ).style('position:absolute;left:0;')
            ui.label(f"{mes.upper()} {ano}").style(
                'font-size:13px;font-weight:600;color:#6B7280;letter-spacing:0.18em')
            ui.button('→', on_click=lambda: callback_mes(1)).props(
                'flat round dense color=grey'
            ).style('position:absolute;right:0;')

        # dias semana do calendário principal
        with ui.grid(columns=7).classes('w-full').style('gap:0;margin-top:2px;margin-bottom:2px'):
            for d in DIAS:
                with ui.element('div').classes('calcel'):
                    ui.label(d + ".").style(
                        'font-size:11px;font-weight:500;'
                        'color:#9CA3AF;text-align:center;text-transform:lowercase;'
                    )

        # corpo do calendário com ícones
        with ui.grid(columns=7).classes('w-full').style('gap:0;margin-top:2px;margin-bottom:0'):
            for ico in data_dias:
                with ui.element('div').classes('calcel'):
                    if ico:
                        ui.image(ico).classes('calicone')
                    else:
                        ui.label("").style('min-width:18px;min-height:24px')


def grafico_barras(valores, total=1000):
    """Cada barra e seu número ficam na mesma coluna, garantindo alinhamento."""
    with ui.row().style(
        'margin-top:14px;margin-bottom:12px;justify-content:center;gap:10px;'
        'max-width:480px;width:100%;margin-left:auto;margin-right:auto;'):
        gray_height = 96
        for v in valores:
            pct = min(v / total, 1.0)
            label = f"{int(v / 1000)}k" if v >= 1000 else f"{int(v)}"
            with ui.column().style('align-items:center;gap:4px;'):
                with ui.element('div').style(
                    f'width:16px;height:{gray_height}px;background:#E5E7EB;position:relative;'
                    'border-radius:10px 10px 0 0;display:flex;align-items:flex-end;overflow:visible'):
                    ui.element('div').style(
                        f'width:16px;height:{int(gray_height * pct)}px;'
                        f'background:{PRIMARY};position:absolute;left:0;bottom:0;'
                        'border-radius:10px 10px 0 0;'
                    )
                ui.label(label).style(
                    'font-size:11px;color:#9CA3AF;text-align:center;min-width:16px;')

# ====== PÁGINA ======
@ui.page('/')
def main():
    # TOPO – logo + nome
    with ui.row().classes('w-full').style(
        'align-items:center;justify-content:space-between;margin-bottom:8px;'):
        with ui.row().style('align-items:center;gap:8px;margin-left:16px;'):
            ui.image(LOGO_PATH).classes('logo-fixa').props('fit=contain')
            ui.label('Lexora').style(
                'font-size:20px;font-weight:600;color:#111827;')
        with ui.row().style('align-items:center;gap:6px;margin-right:18px'):
            ui.label('Sair da conta').style('font-size:14px;color:#6B7280;')
            ui.icon('logout').style('color:#6B7280;font-size:18px;')

    # CONTEÚDO PRINCIPAL
    with ui.row().style('margin-top:8px;justify-content:center;width:100%;gap:18px'):
        # LATERAL ESQUERDA
        with ui.column().classes('menu-card').style('align-items:flex-start;gap:8px'):
            ui.html('<b>Meu perfil</b>', sanitize=False)
            ui.html(
                '<div class="perfil-row"><span class="perfil-icon">👤</span>'
                '<span class="perfil-value">Nome completo<br>'
                '<span style="font-weight:400;font-size:13px">'
                'Ana Maria Menezes da Silva</span></span></div>',
                sanitize=False,
            )
            ui.html(
                '<div class="perfil-row"><span class="perfil-icon">📅</span>'
                '<span class="perfil-value">Data de nascimento<br>'
                '<span style="font-weight:400;font-size:13px">'
                '29 / 07 / 2004</span></span></div>',
                sanitize=False,
            )
            ui.html(
                '<div class="perfil-row"><span class="perfil-icon">📧</span>'
                '<span class="perfil-value">E-mail<br>'
                '<span style="font-weight:400;font-size:13px">'
                'ana.maria.menezes@gmail.com</span></span></div>',
                sanitize=False,
            )
            ui.html(
                '<div class="perfil-row"><span class="perfil-icon">🌎</span>'
                '<span class="perfil-value">Idioma<br>'
                '<span style="font-weight:400;font-size:13px">'
                'Inglês</span></span></div>',
                sanitize=False,
            )

        # CARD CENTRAL
        with ui.column().classes('center-card').style('gap:6px'):
            ui.label('Meu aprendizado').style(
                'font-size: 20px; font-weight:700; margin-bottom: 4px; color:#111827')

            with ui.row().style('gap:10px;margin-bottom:8px'):
                ui.button('IDIOMA INGLÊS', on_click=None).props('flat').style(
                    'background:#D2E4FD;font-size:14px;color:#111827;'
                    'border-radius:12px;font-weight:600;height:36px;padding:0 18px'
                )
                ui.button('NÍVEL AVANÇADO', on_click=None).props('flat').style(
                    'background:#FCF3D6;font-size:14px;color:#854D0E;'
                    'border-radius:12px;font-weight:600;height:36px;padding:0 18px'
                )
                ui.button('OBJETIVO VIAGEM ✏️',
                          on_click=lambda: ui.notify('Editar objetivo')).props('flat').style(
                    'background:#C9F0DB;font-size:14px;color:#166534;'
                    'border-radius:12px;font-weight:600;height:36px;padding:0 18px'
                )

            ui.html(
                '<div style="color:#6B7280;font-size:13px;margin-bottom:0px;">'
                'Meta diária</div>',
                sanitize=False,
            )
            with ui.element('div').style('margin:6px 0 4px 0;width:100%'):
                with ui.element('div').style(
                    'width:100%;background:#E5E7EB;height:6px;border-radius:999px'):
                    ui.element('div').style(
                        'height:100%;width:70%;background:#111827;border-radius:999px')
                with ui.row().style('align-items:center;gap:6px;margin-top:4px'):
                    ui.label('7/10 lições').style(
                        'font-size:12px;color:#4B5563;')
                    ui.button('EDITAR',
                              on_click=lambda: ui.notify('Editar meta')).props('flat').style(
                        'color:#6B7280;font-size:12px;')

            ui.label('ESTATÍSTICAS').classes('estat-title').style(
                'margin-top:10px;text-align:center;align-self:center;')

            with ui.column().style('width:100%;align-items:center'):
                with ui.row().classes('estat-cards').style(
                    'gap:10px;margin-top:6px;justify-content:center;max-width:460px'):
                    with ui.element('div').classes('estat-box'):
                        ui.label('168').classes('estat-num')
                        ui.label('Dias ativos').classes('estat-sub').style('margin-top:-2px')
                    with ui.element('div').classes('estat-box'):
                        ui.label('237').classes('estat-num')
                        ui.label('Atividades feitas').classes('estat-sub')
                    with ui.element('div').classes('estat-box'):
                        ui.label('112.459').classes('estat-num')
                        ui.label('Total de pontos').classes('estat-sub')

                with ui.row().classes('estat-cards').style(
                    'gap:10px;margin-top:8px;justify-content:center;max-width:320px'):
                    with ui.element('div').classes('estat-box'):
                        ui.label('12').classes('estat-num')
                        ui.label('Sequência').classes('estat-sub')
                    with ui.element('div').classes('estat-box'):
                        ui.label('237').classes('estat-num')
                        ui.label('Sequência recorde').classes('estat-sub')

            ui.label('Pontos').style(
                'margin-top:12px;margin-bottom:0px;font-size:14px;'
                'color:#111827;font-weight:600;text-align:center;align-self:center')
            ui.label('Últimos 15 dias').style(
                'font-size:12px;color:#9CA3AF;margin-bottom:2px;'
                'text-align:center;align-self:center')

            grafico_barras(
                [932, 126, 543, 190, 756, 764, 158, 789, 804, 850,
                 434, 284, 622, 502, 750],
                total=1200,
            )

        # COLUNA DIREITA (OFENSIVA + CALENDÁRIO)
        with ui.column().classes('right-card').style('align-items:stretch;gap:8px'):
            with ui.row().style('align-items:center;justify-content:space-between'):
                ui.label('Ofensiva').classes('ofensiva-title')
                ui.label('22 dias').classes('ofensiva-sub')

            hoje = datetime.now()
            mes_num = hoje.month
            ano_num = hoje.year
            meses = [
                "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
            ]
            calendario_mes = meses[mes_num - 1]
            dias_no_mes = calendar.monthrange(ano_num, mes_num)[1]

            # primeiros 22 dias azuis, restante cinza
            dias_status = []
            for dia in range(1, dias_no_mes + 1):
                if dia <= 22:
                    dias_status.append(FIRE_DARK_PATH)
                else:
                    dias_status.append(FIRE_GRAY_PATH)

            # completa até 42 posições
            while len(dias_status) < 42:
                dias_status.append("")

            def muda_mes(delta):
                ui.notify('Troca de mês não implementada')

            calendario(dias_status, calendario_mes, ano_num, muda_mes)


ui.run()
