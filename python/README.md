Use these commands to run server
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m setup install
cd async_server
python3 -m server_twisted
```

Use these commands to run tests
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m setup install
python3 -m unittest discover tests
```