from src.integrations import models

from .server_auth import ServerUser


class FlaskServerAuth(ServerUser):
    def __init__(self, app=None, model=None):
        super(FlaskServerAuth, self).__init__(app, model)

    def init_app(self, app=None, model=None):
        super().init_app(app, integration_model=models.BrandIntegration)


server_user = FlaskServerAuth()
