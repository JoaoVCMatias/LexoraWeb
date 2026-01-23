from nicegui import ui, app
from pathlib import Path

base_dir = Path(__file__).parent

images_path = (base_dir / '../images').resolve()

if not images_path.exists():
    print(f"AVISO: A pasta não foi encontrada em: {images_path}")

app.add_static_files('/images', images_path)

gabarito_data = [
    [
        {"status": "correct", "pre_text": "I need to", "word": "book", "post_text": "a trip"},
        {"status": "wrong", "pre_text": "I need to", "word": "cast", "post_text": "a trip"},
    ],
    [
        {"status": "correct", "pre_text": "I'm going to", "word": "catch", "post_text": "a train tomorrow"},
    ],
    [
        {"status": "correct", "pre_text": "What about", "word": "taking", "post_text": "a flight to NY?"},
    ],
    [
        {"status": "correct", "pre_text": "Hurry up, or we will", "word": "miss", "post_text": "our flight!"},
        {"status": "wrong", "pre_text": "Hurry up, or we will", "word": "take", "post_text": "our flight!"},
    ],
    [
        {"status": "correct", "pre_text": "Passengers can now", "word": "board", "post_text": "the plane at gate 12"},
        {"status": "wrong", "pre_text": "Passengers can now", "word": "get into", "post_text": "the plane at gate 12"},
    ],
    [
        {"status": "correct", "pre_text": "We should", "word": "plan", "post_text": "our vacation for next July"},
    ]
]

@ui.page('/')
def gabarito_page():

    with ui.column().classes('w-full min-h-screen bg-gray-50 items-center p-4'):
        
        with ui.row().classes('w-full max-w-5xl justify-between items-center mb-6'):
            
            ui.image('/images/logo.png').classes('w-24 md:w-32') 

        with ui.card().classes('w-full max-w-4xl bg-white rounded-xl shadow-sm p-6 md:p-10'):
            
            with ui.row().classes('w-full justify-between items-start mb-8'):
                with ui.column().classes('gap-1'):
                    ui.label('Gabarito da atividade').classes('text-xl md:text-2xl font-bold text-black')
                    ui.label('Tema: aeroporto').classes('text-base md:text-lg text-gray-500')
                
                ui.icon('close', size='24px').classes('cursor-pointer text-black hover:text-gray-600')

            for i, group in enumerate(gabarito_data):
                
                with ui.column().classes('w-full gap-3'):
                    
                    for attempt in group:
                        is_correct = attempt['status'] == 'correct'
                        
                        word_color = 'text-green-700' if is_correct else 'text-red-900'
                        icon_name = 'check' if is_correct else 'close'
                        icon_color = 'text-green-600' if is_correct else 'text-red-900'

                        icon_bg = '' if is_correct else 'bg-red-50 rounded' 

                        with ui.row().classes('w-full items-center gap-4'):

                            with ui.element('div').classes(f'w-6 h-6 flex items-center justify-center {icon_bg}'):
                                ui.icon(icon_name, size='xs').classes(f'{icon_color} font-bold')

                            ui.html(
                                f"{attempt['pre_text']} <span class='font-bold {word_color}'>{attempt['word']}</span> {attempt['post_text']}",
                                sanitize=False
                            ).classes('text-base md:text-lg text-gray-800 font-normal leading-tight')

                if i < len(gabarito_data) - 1:
                    ui.separator().classes('my-6 bg-gray-200')

ui.run(title='Lexora - Gabarito')