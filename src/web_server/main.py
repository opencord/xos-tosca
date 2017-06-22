from flask import Flask, make_response

class TOSCA_WebServer:
    app = Flask('TOSCA-Web-Server')

    @app.route("/")
    def hello():
        response =  make_response("""
   _  ______  _____    __________  _____ _________ 
  | |/ / __ \/ ___/   /_  __/ __ \/ ___// ____/   |
  |   / / / /\__ \     / / / / / /\__ \/ /   / /| |
 /   / /_/ /___/ /    / / / /_/ /___/ / /___/ ___ |
/_/|_\____//____/    /_/  \____//____/\____/_/  |_|
                                                   
        """)
        response.headers["content-type"] = "text/plain"
        return response

    def __init__(self):
        self.app.run(host='localhost', port='9200')