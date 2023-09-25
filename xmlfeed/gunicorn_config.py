command = 'srv/www/my_venv/venv/bin/gunicorn'
pythonpath = 'srv/www/master/'
bind = '0.0.0.0:8000'
workers = 1
accesslog = "/var/logs/gunicorn/gunicorn.access.log"
# Error log - records Gunicorn server goings-on
errorlog = "/var/logs/gunicorn/gunicorn.error.log"
# Whether to send Django output to the error log
capture_output = True
# How verbose the Gunicorn error logs should be
loglevel = "debug"
