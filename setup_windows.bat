@echo off
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

echo Environment ready. Activate with: .venv\\Scripts\\activate
