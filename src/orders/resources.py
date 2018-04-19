from sqlalchemy.sql import false
from flask_security import current_user

from src.utils import ModelResource, operators as ops
from src.user.models import Store

from .models import Item, Order, ItemTax, Status
from .schemas import ItemSchema, ItemTaxSchema, OrderSchema, StatusSchema


class OrderResource(ModelResource):

    model = Order
    schema = OrderSchema

    optional = ('items', 'time_line')

    order_by = ('id', 'invoice_number', 'created_on')

    filters = {
        'id': [ops.Equal],
        'customer_id': [ops.Equal],
        'store_id': [ops.Equal, ops.In],
        'current_status_id':  [ops.Equal],
        'created_on': [ops.DateLesserEqual, ops.DateEqual, ops.DateGreaterEqual],
        'updated_on': [ops.Greaterequal, ops.DateGreaterEqual, ops.DateEqual, ops.DateLesserEqual]
    }

    auth_required = True

    roles_accepted = ('admin',)

    def has_read_permission(self, qs):
        if current_user.has_permission('view_order'):
            return qs.filter(self.model.store_id.in_(current_user.store_ids))
        else:
            return qs.filter(false())

    def has_change_permission(self, obj):
        return current_user.has_shop_access(obj.store_id)

    def has_delete_permission(self, obj):
        return current_user.has_shop_access(obj.store_id) and current_user.has_permission('remove_order')

    def has_add_permission(self, objects):
        for obj in objects:
            store_id = current_user.store_ids[0]
            obj.user_id = current_user.id
            obj.store_id = store_id
            store = Store.query.get(store_id)
            Store.query.filter(Store.id == store_id) \
                .update({'invoice_number': Store.invoice_number + 1}, 'fetch')
            obj.invoice_number = store.invoice_number
        return True


class ItemTaxResource(ModelResource):
    model = ItemTax
    schema = ItemTaxSchema

    auth_required = True
    roles_required = ('admin',)

    def has_read_permission(self, qs):
        if current_user.has_permission('view_order_item'):
            return qs.filter(self.model.store_id.in_(current_user.store_ids))
        else:
            return qs.filter(false())

    def has_change_permission(self, obj):
        return current_user.has_shop_access(obj.store_id) and current_user.has_permission('change_order_item')

    def has_delete_permission(self, obj):
        return current_user.has_shop_access(obj.store_id) and current_user.has_permission('remove_order_item')

    def has_add_permission(self, obj):
        return current_user.has_shop_access(obj.store_id) and current_user.has_permission('create_order_item')


class ItemResource(ModelResource):

    model = Item
    schema = ItemSchema

    optional = ('add_ons', 'taxes')

    filters = {
        'id': [ops.Equal, ops.In],
        'order_id': [ops.Equal, ops.In],
        'product_id': [ops.Equal, ops.In],
        'store_id': [ops.Equal, ops.In],
        'stock_id': [ops.Equal, ops.In],
        'update_on': [ops.DateLesserEqual, ops.DateEqual, ops.DateGreaterEqual],
        'created_on': [ops.DateLesserEqual, ops.DateEqual, ops.DateGreaterEqual]
    }

    order_by = ['id']

    only = ()

    exclude = ()

    auth_required = True

    def has_read_permission(self, qs):
        qs = qs.filter(self.model.store_id.in_(current_user.store_ids))
        return qs

    def has_change_permission(self, obj):
        return current_user.has_shop_access(obj.store_id)

    def has_delete_permission(self, obj):
        return current_user.has_shop_access(obj.store_id)

    def has_add_permission(self, obj):
        return current_user.has_shop_access(obj.store_id)


class StatusResource(ModelResource):
    model = Status
    schema = StatusSchema

    auth_required = True

    roles_required = ('admin',)

    def has_read_permission(self, qs):
        qs = qs.filter(self.model.store_id.in_(current_user.store_ids))
        return qs

    def has_change_permission(self, obj):
        return current_user.has_shop_access(obj.store_id)

    def has_delete_permission(self, obj):
        return current_user.has_shop_access(obj.store_id)

    def has_add_permission(self, obj):
        return current_user.has_shop_access(obj.store_id)

