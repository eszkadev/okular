class BaseView:
    def __init__(self, model):
        self.model = model

    def generateHTML(self, body):
        style = '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">'
        navbar = f'''<nav class="navbar navbar-expand-lg navbar-light bg-light">
            <div class="container-fluid">
                <span class="nav-item">{self.model.jenkins_api}</span>
                <span class="nav-item">Last update: {self.model.last_update_str}</span>
                <span class="nav-item">{self.model.navbar_right}</span>
            </div>
        </nav>'''

        return f'''<html>
            <head>{style}</head>
            <body>
                {navbar}
                {body}
            </body>
            </html>'''