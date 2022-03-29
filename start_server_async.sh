#!/bin/bash
#gunicorn --bind 0.0.0.0:5000 server:app --worker-class aiohttp.GunicornWebWorker  --log-level debug --threads 3 --workers 3
#source /opt/pyweb3/venv/bin/activate
gunicorn --bind 0.0.0.0:5000 server:app --worker-class aiohttp.GunicornUVLoopWebWorker  --log-level debug --threads 3 --workers 3 --graceful-timeout 120 --timeout 120  #--error-logfile error.log --capture-output




