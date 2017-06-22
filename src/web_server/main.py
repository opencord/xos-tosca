from flask import Flask, make_response, request
from tosca.parser import TOSCA_Parser

BANNER = """
   _  ______  _____    __________  _____ _________ 
  | |/ / __ \/ ___/   /_  __/ __ \/ ___// ____/   |
  |   / / / /\__ \     / / / / / /\__ \/ /   / /| |
 /   / /_/ /___/ /    / / / /_/ /___/ / /___/ ___ |
/_/|_\____//____/    /_/  \____//____/\____/_/  |_|
"""

class TOSCA_WebServer:
    app = Flask('TOSCA-Web-Server')

    @app.route("/", methods=['GET', 'POST'])
    def home():
        if request.method == 'GET':
            response =  make_response(BANNER)
            response.headers["content-type"] = "text/plain"
            return response
        else:
            try:
                # print request.headers['xos-password']
                parsed = TOSCA_Parser(request.get_data())
                return make_response(str(parsed.ordered_names), 201)
            except Exception, e:
                return make_response(e.message, 400)

    def __init__(self):
        self.app.run(host='localhost', port='9200')