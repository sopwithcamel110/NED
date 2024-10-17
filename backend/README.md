# Backend

## Spin up
```bash
# cd into backend directory
python3 -m venv env
source env/bin/activate # env/Scripts/activate for Windows
pip install -r requirements.txt
waitress-serve --listen=*:8000 api:app
```
Site should respond at http://localhost:8000/ping
