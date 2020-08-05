import os

from app import create_app

app = create_app(os.getenv('PLOTTER_CONFIG', 'development'))
