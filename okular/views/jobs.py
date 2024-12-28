from okular.views.base import BaseView

class JobsView(BaseView):
    def __init__(self, model):
        super().__init__(model)

    def generateHTML(self):
        body = f''
        return super().generateHTML(body)