bat

cd /d %~dp0

python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt
