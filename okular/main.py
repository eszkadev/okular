from flask import Flask

def create_app(jenkins_job):
    app = Flask(__name__)

    @app.route("/")
    def index():
        return f'<h1>okular</h1><p>Watching: {jenkins_job}'
    
    return app