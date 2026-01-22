from nicegui import ui, app
from pathlib import Path

base_dir = Path(__file__).parent
images_path = (base_dir / '../images').resolve()

if not images_path.exists():
    print(f"AVISO CRÍTICO: A pasta de imagens não foi encontrada em: {images_path}")

app.add_static_files('/images', images_path)

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


@ui.page('/')
def task_completed_page():

    with ui.column().classes('w-full min-h-screen bg-gray-50 items-center p-4'):
        
        with ui.row().classes('w-full max-w-6xl justify-between items-center mb-8'):

            ui.image('/images/logo.png').classes('w-24 md:w-32') 

        with ui.card().classes('w-full max-w-5xl bg-white rounded-2xl shadow-sm p-8 md:p-16 items-center text-center'):

            ui.label(task_result_data['title']).classes('text-2xl md:text-4xl font-bold text-black mb-4')
            ui.label(task_result_data['subtitle']).classes('text-gray-500 max-w-3xl text-sm md:text-lg leading-relaxed mb-10')

            ui.image('/images/tarefa.png').classes('w-full max-w-sm md:max-w-md mb-12 h-auto')

            with ui.grid().classes('w-full max-w-4xl grid-cols-2 md:grid-cols-4 gap-4 md:gap-6 mb-12'):

                with ui.column().classes('bg-blue-50 rounded-2xl p-6 items-center justify-center gap-1'):
                    ui.label(task_result_data['stats']['time_value']).classes('text-3xl md:text-4xl font-bold text-blue-900')
                    ui.label(task_result_data['stats']['time_label']).classes('text-xs md:text-sm text-gray-600 font-medium')

                with ui.column().classes('bg-blue-50 rounded-2xl p-6 items-center justify-center gap-1'):
                    ui.label(task_result_data['stats']['points_value']).classes('text-3xl md:text-4xl font-bold text-blue-900')
                    ui.label(task_result_data['stats']['points_label']).classes('text-xs md:text-sm text-gray-600 font-medium')

                with ui.column().classes('bg-blue-50 rounded-2xl p-6 items-center justify-center gap-1'):
                    ui.label(task_result_data['stats']['accuracy_value']).classes('text-3xl md:text-4xl font-bold text-blue-900')
                    ui.label(task_result_data['stats']['accuracy_label']).classes('text-xs md:text-sm text-gray-600 font-medium')

                with ui.column().classes('bg-blue-50 rounded-2xl p-6 items-center justify-center gap-1'):
                    ui.label(task_result_data['stats']['streak_value']).classes('text-3xl md:text-4xl font-bold text-blue-900')
                    ui.label(task_result_data['stats']['streak_label']).classes('text-xs md:text-sm text-gray-600 font-medium')

            with ui.row().classes('gap-4 flex-wrap justify-center w-full'):

                ui.button('Ir para página inicial', on_click=lambda: ui.notify('Navegando para Home...')) \
                    .classes('bg-blue-100 text-blue-800 hover:bg-blue-200 rounded-xl px-8 py-3 font-bold shadow-none normal-case text-base transition')

                ui.button('Checar resultados', on_click=lambda: ui.notify('Abrindo detalhes...')) \
                    .classes('bg-blue-700 text-white hover:bg-blue-800 rounded-xl px-8 py-3 font-bold shadow-none normal-case text-base transition')

ui.run(title='Lexora - Tarefa Concluída')