from nicegui import ui, app
from pathlib import Path

# Configuração de arquivos estáticos (Imagens)
# Tenta localizar a pasta images subindo um nível a partir de PythonPages
try:
    base_dir = Path(__file__).parent.resolve()
    images_path = (base_dir.parent / 'images').resolve()
    if images_path.exists():
        app.add_static_files('/images', str(images_path))
except Exception as e:
    print(f"Erro ao carregar imagens: {e}")

task_result_data = {
    "title": "Tarefa concluída com sucesso!",
    "subtitle": "Parabéns pela tarefa bem sucedida, você pode ver mais detalhes sobre o resultado da atividade ou ir direto para a página inicial.",
    "stats": {
        "time_value": "01:56",
        "time_label": "Você é a velocidade!",
        "points_value": "526",
        "points_label": "Pontos recebidos",
        "accuracy_value": "78%",
        "accuracy_label": "Taxa de acertos",
        "streak_value": "4",
        "streak_label": "Acertos em sequência"
    }
}

def task_completed_page():
    # Limpa o background para garantir estilo correto
    ui.query('body').style('background-color: #f9fafb; margin: 0; padding: 0;')

    with ui.column().classes('w-full min-h-screen bg-gray-50 items-center p-4'):
        
        # Cabeçalho com Logo
        with ui.row().classes('w-full max-w-6xl justify-between items-center mb-8'):
            ui.image('/images/logo.png').classes('w-24 md:w-32')

        # Card Principal
        with ui.card().classes('w-full max-w-5xl bg-white rounded-2xl shadow-sm p-8 md:p-16 items-center text-center'):
            
            ui.label(task_result_data['title']).classes('text-2xl md:text-4xl font-bold text-black mb-4')
            ui.label(task_result_data['subtitle']).classes('text-gray-500 max-w-3xl text-sm md:text-lg leading-relaxed mb-10')
            
            # Imagem Central
            ui.image('/images/tarefa.png').classes('w-full max-w-sm md:max-w-md mb-12 h-auto')

            # Grid de Estatísticas
            with ui.grid().classes('w-full max-w-4xl grid-cols-2 md:grid-cols-4 gap-4 md:gap-6 mb-12'):
                # Tempo
                with ui.column().classes('bg-blue-50 rounded-2xl p-6 items-center justify-center gap-1'):
                    ui.label(task_result_data['stats']['time_value']).classes('text-3xl md:text-4xl font-bold text-blue-900')
                    ui.label(task_result_data['stats']['time_label']).classes('text-xs md:text-sm text-gray-600 font-medium')
                
                # Pontos
                with ui.column().classes('bg-blue-50 rounded-2xl p-6 items-center justify-center gap-1'):
                    ui.label(task_result_data['stats']['points_value']).classes('text-3xl md:text-4xl font-bold text-blue-900')
                    ui.label(task_result_data['stats']['points_label']).classes('text-xs md:text-sm text-gray-600 font-medium')
                
                # Precisão
                with ui.column().classes('bg-blue-50 rounded-2xl p-6 items-center justify-center gap-1'):
                    ui.label(task_result_data['stats']['accuracy_value']).classes('text-3xl md:text-4xl font-bold text-blue-900')
                    ui.label(task_result_data['stats']['accuracy_label']).classes('text-xs md:text-sm text-gray-600 font-medium')
                
                # Sequência
                with ui.column().classes('bg-blue-50 rounded-2xl p-6 items-center justify-center gap-1'):
                    ui.label(task_result_data['stats']['streak_value']).classes('text-3xl md:text-4xl font-bold text-blue-900')
                    ui.label(task_result_data['stats']['streak_label']).classes('text-xs md:text-sm text-gray-600 font-medium')

            # Botões de Ação (CORRIGIDOS)
            with ui.row().classes('gap-4 flex-wrap justify-center w-full'):
                
                # Botão 1: Ir para Home
                ui.button('Ir para página inicial', on_click=lambda: ui.navigate.to('/')) \
                    .classes('bg-blue-100 text-blue-800 hover:bg-blue-200 rounded-xl px-8 py-3 font-bold shadow-none normal-case text-base transition')
                
                # Botão 2: Ir para Gabarito
                ui.button('Checar resultados', on_click=lambda: ui.navigate.to('/gabarito')) \
                    .classes('bg-blue-700 text-white hover:bg-blue-800 rounded-xl px-8 py-3 font-bold shadow-none normal-case text-base transition')
