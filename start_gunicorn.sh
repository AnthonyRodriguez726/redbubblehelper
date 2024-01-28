#!/bin/bash

# Activate the virtual environment
source /home/bellpep/myenv/bin/activate

# Start Gunicorn
/home/bellpep/myenv/bin/gunicorn --timeout 300 --workers 3 --bind unix:/home/bellpep/deployment/redbubbleapi.sock -m 007 app:app

# Change group ownership of the socket to www-data
chgrp www-data /home/bellpep/deployment/redbubbleapi.sock

# Optionally set permissions
chmod 660 /home/bellpep/deployment/redbubbleapi.sock

