"""
This script runs the fantuantuan application using a development server.
"""

from os import environ
from fantuantuan import app

if __name__ == '__main__':
    HOST = "0.0.0.0"#environ.get('SERVER_HOST', 'localhost')
    #try:
        #PORT = int(environ.get('SERVER_PORT', '5555'))
    #except ValueError:
        #PORT = 5555
    PORT=5555
    app.run(host=HOST,port=PORT)
