# 🖥️ Aplicação Web com NiceGUI

Este projeto é uma aplicação web desenvolvida em Python utilizando o framework [NiceGUI](https://nicegui.io/), que permite criar interfaces modernas e responsivas com facilidade.

---

## 🚀 Requisitos

- Python 3.10 ou superior
- Navegador web moderno (Chrome, Firefox, Edge, etc.)

---

## 📦 Instalação

1️⃣ Ambiente virtual:

# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate

2️⃣ Instale as dependências:
# Windows
python -m venv .venv
.venv\Scripts\activate.ps1

# Linux/macOS
python -m venv .venv
source .venv/bin/activate

3️⃣ Instale as dependências:
pip install -r requirements.txt

▶️ Execução
python main.py 

uvicorn main:fastapi_app --host 0.0.0.0 --port 10000 --reload

