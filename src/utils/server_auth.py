from uuid import UUID
from typing import List

from .serializer_helper import serializer_helper


class UserRole(object):
    name = None


class ServerUser(object):
    app = None
    integration_model = None
    roles: List[UserRole] = []
    permissions: List[str] = []
    shop_ids: List[str] = []
    brand_id: str = None

    def __init__(self, app=None, integration_model=None):
        if app and integration_model:
            self.init_app(app, integration_model)

    def init_app(self, app=None, integration_model=None):

        self.app = app
        self.integration_model = integration_model

    def set_user(self, token):
        secret_key = self.integration_model.query.with_entities(self.integration_model.secret_key) \
            .filter(self.integration_model.access_key == token.replace('Bearer ', '')).scalar()
        if secret_key:
            brand_id, shop_ids, permissions, roles = serializer_helper.deserialize_data(secret_key)
            for role in roles:
                user_role = UserRole()
                user_role.name = role
                self.roles.append(user_role)
            self.permissions = permissions
            self.shop_ids = shop_ids
            self.brand_id = brand_id

            return self
        return None

    @property
    def is_active(self):
        """Returns `True` if the user is active."""
        return bool(self.brand_id)

    @property
    def id(self):
        """Returns `True` if the user is active."""
        return None

    @property
    def is_authenticated(self):
        """Returns `True` if the user is active."""
        return bool(self.brand_id)

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def has_shop_access(self, shop_id):
        return str(shop_id) in self.shop_ids

    def has_permission(self, permission):
        return permission in self.permissions

    @property
    def retail_brand_id(self):
        return UUID(self.brand_id)

    @property
    def retail_shop_ids(self):
        return self.shop_ids

    def find_role(self, role):
        return self.roles[self.roles.index(role)]

    @property
    def has_retail_shops(self):
        return len(self.shop_ids)
