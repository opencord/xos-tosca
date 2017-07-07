from flask import Flask, make_response, request, render_template
import os
from tosca.parser import TOSCA_Parser
from tosca.default import TOSCA_DEFS_DIR

BANNER = """
   _  ______  _____    __________  _____ _________ 
  | |/ / __ \/ ___/   /_  __/ __ \/ ___// ____/   |
  |   / / / /\__ \     / / / / / /\__ \/ /   / /| |
 /   / /_/ /___/ /    / / / /_/ /___/ / /___/ ___ |
/_/|_\____//____/    /_/  \____//____/\____/_/  |_|
"""

class TOSCA_WebServer:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    template_dir = os.path.join(current_dir, 'templates/')
    app = Flask('TOSCA-Web-Server', template_folder=template_dir)

    @app.route("/", methods=['GET', 'POST'])
    def home():
        if request.method == 'GET':
            response =  make_response(BANNER)
            response.headers["content-type"] = "text/plain"
            tosca_defs = [f for f in os.listdir(TOSCA_DEFS_DIR) if not f.startswith('.')]
            return render_template('tosca-types-list.html.j2', types=tosca_defs)
        else:
            try:
                # print request.headers['xos-password']
                parsed = TOSCA_Parser(request.get_data())
                response_text = "Created models: %s" % str(parsed.ordered_models_name)
                return make_response(response_text, 201)
            except Exception, e:
                return make_response(e.message, 400)

    @app.route("/custom_type/<name>")
    def custom_type(name):
        custom_type = open(TOSCA_DEFS_DIR + '/' + name).read()
        return render_template('tosca-types-detail.html.j2', custom_type=custom_type, name=name)

    def __init__(self):
        self.app.run(host='localhost', port='9200')