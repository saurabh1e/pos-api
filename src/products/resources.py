from flask_security import current_user
from sqlalchemy.sql import false

from src.utils import ModelResource, AssociationModelResource, operators as ops
from .models import Product, Tax, Stock, Brand, \
    DistributorBill, Distributor, ProductTax, Tag, Combo, Salt, ProductSalt, \
    ProductTag
from .schemas import ProductSchema, TaxSchema, StockSchema, BrandSchema, \
    DistributorBillSchema, DistributorSchema, ProductTaxSchema, TagSchema, ComboSchema, SaltSchema, \
    ProductSaltSchema, ProductTagSchema


class ProductResource(ModelResource):
    model = Product
    schema = ProductSchema

    auth_required = True

    default_limit = 100

    max_limit = 500

    optional = ('distributors', 'brand', 'store', 'stocks', 'similar_products', 'available_stocks',
                'last_purchase_amount', 'last_selling_amount', 'stock_required')

    filters = {
        'name': [ops.Equal, ops.Contains],
        'product_name': [ops.Equal, ops.Contains],
        'brand_name': [ops.Equal, ops.Contains],
        'stock_required': [ops.Equal, ops.Greater, ops.Greaterequal],
        'available_stock': [ops.Equal, ops.Greater, ops.Greaterequal],
        'id': [ops.Equal, ops.In, ops.NotEqual, ops.NotIn],
        'is_short': [ops.Boolean],
        'is_disabled': [ops.Boolean],
        'created_on': [ops.DateLesserEqual, ops.DateEqual, ops.DateGreaterEqual],
        'updated_on': [ops.Greaterequal, ops.DateGreaterEqual, ops.DateEqual, ops.DateLesserEqual]
    }
    order_by = ['id', 'name']

    def has_read_permission(self, qs):
        return qs.filter(self.model.is_disabled.isnot(True))

    def has_change_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and current_user.has_permission('change_product')

    def has_delete_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and current_user.has_permission('remove_product')

    def has_add_permission(self, objects):
        if not current_user.has_permission('create_product'):
            return False
        return True


class TagResource(ModelResource):
    model = Tag
    schema = TagSchema
    max_limit = 500
    auth_required = True

    optional = ('products', 'store')

    order_by = ['store_id', 'id', 'name']

    filters = {
        'name': [ops.Equal, ops.Contains],
        'store_id': [ops.Equal, ops.In],
        'created_on': [ops.DateLesserEqual, ops.DateEqual, ops.DateGreaterEqual],
        'updated_on': [ops.Greaterequal, ops.DateGreaterEqual, ops.DateEqual, ops.DateLesserEqual]
    }

    def has_read_permission(self, qs):
        if current_user.has_permission('view_tag'):
            return qs.filter(self.model.store_id.in_(current_user.store_ids))
        return qs.filter(false())

    def has_change_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and current_user.has_permission('change_tag')

    def has_delete_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and current_user.has_permission('remove_tag')

    def has_add_permission(self, objects):
        if not current_user.has_permission('create_tag'):
            return False
        for obj in objects:
            if not current_user.has_store_access(obj.store_id):
                return False
        return True


class StockResource(ModelResource):
    model = Stock
    schema = StockSchema

    auth_required = True

    roles_accepted = ('admin', 'owner', 'staff')

    export = True

    max_export_limit = 500

    optional = ('product', 'store', 'distributor_bill', 'product_name', 'store_id', 'distributor_name',
                'brand_name', 'product_id')

    filters = {
        'is_sold': [ops.Boolean],
        'expired': [ops.Boolean],
        'units_available': [ops.Equal, ops.Greater, ops.Greaterequal],
        'units_sold': [ops.Equal, ops.Lesser, ops.LesserEqual],
        'brand_name': [ops.Equal, ops.Contains],
        'product_name': [ops.Contains, ops.Equal],
        'store_id': [ops.Equal, ops.In],
        'product_id': [ops.Equal, ops.In],
        'id': [ops.Equal, ops.In, ops.NotEqual, ops.NotIn],
        'distributor_id': [ops.Equal, ops.In],
        'distributor_name': [ops.Contains, ops.Equal],
        'updated_on': [ops.DateGreaterEqual, ops.DateEqual, ops.DateLesserEqual],
        'created_on': [ops.DateLesserEqual, ops.DateEqual, ops.DateGreaterEqual, ops.DateBetween],
        'expiry_date': [ops.DateLesserEqual, ops.DateEqual, ops.DateGreaterEqual, ops.DateBetween]
    }

    order_by = ['expiry_date', 'units_sold', 'created_on']

    only = ()

    exclude = ()

    def has_read_permission(self, qs):
        return qs.filter(self.model.store_id.in_(current_user.store_ids))

    def has_change_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and current_user.has_permission('change_stock')

    def has_delete_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and current_user.has_permission('remove_stock')

    def has_add_permission(self, objects):
        for obj in objects:
            print(current_user.store_ids)
            obj.store_id = current_user.store_ids[0]
        return True


class DistributorResource(ModelResource):
    model = Distributor
    schema = DistributorSchema

    auth_required = True

    order_by = ['store_id', 'id', 'name']

    optional = ('products', 'store', 'bills')

    filters = {
        'id': [ops.Equal, ops.In],
        'name': [ops.Equal, ops.Contains],
        'store_id': [ops.Equal, ops.In],
        'created_on': [ops.DateLesserEqual, ops.DateEqual, ops.DateGreaterEqual],
        'updated_on': [ops.Greaterequal, ops.DateGreaterEqual, ops.DateEqual, ops.DateLesserEqual]
    }

    def has_read_permission(self, qs):
        if current_user.has_permission('view_distributor'):
            return qs.filter(self.model.store_id.in_(current_user.store_ids))
        return qs.filter(false())

    def has_change_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and current_user.has_permission('change_distributor')

    def has_delete_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and current_user.has_permission('remove_distributor')

    def has_add_permission(self, objects):
        if not current_user.has_permission('create_distributor'):
            return False
        for obj in objects:
            if not current_user.has_store_access(obj.store_id):
                return False
        return True


class DistributorBillResource(ModelResource):
    model = DistributorBill
    schema = DistributorBillSchema

    auth_required = True

    roles_required = ('admin',)

    optional = ('purchased_items',)

    max_limit = 50

    filters = {
        'id': [ops.Equal, ops.Contains],
        'distributor_id': [ops.Equal, ops.In],
        'store_id': [ops.Equal, ops.In],
        'store_name': [ops.Equal, ops.Contains],
        'created_on': [ops.DateLesserEqual, ops.DateEqual, ops.DateGreaterEqual],
        'updated_on': [ops.Greaterequal, ops.DateGreaterEqual, ops.DateEqual, ops.DateLesserEqual],
        'purchase_date': [ops.DateLesserEqual, ops.DateEqual, ops.DateGreaterEqual, ops.DateBetween],
    }

    default_limit = 10

    def has_read_permission(self, qs):
        if current_user.has_permission('view_distributor_bill'):
            return qs.filter(self.model.store_id.in_(current_user.store_ids))
        return qs.filter(false())

    def has_change_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and \
               current_user.has_permission('change_distributor_bill')

    def has_delete_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and \
               current_user.has_permission('remove_distributor_bill')

    def has_add_permission(self, objects):
        if not current_user.has_permission('create_distributor_bill'):
            return False
        for obj in objects:
            if not current_user.has_store_access(Distributor.query.with_entities(Distributor.store_id)
                                                        .filter(Distributor.id == obj.distributor_id).scalar()):
                return False
        return True


class BrandResource(ModelResource):
    model = Brand
    schema = BrandSchema

    auth_required = True
    max_limit = 500

    order_by = ['store_id', 'id', 'name']

    optional = ('products', 'store', 'distributors')

    filters = {
        'name': [ops.Equal, ops.Contains],
        'store_id': [ops.Equal, ops.In],
        'created_on': [ops.DateLesserEqual, ops.DateEqual, ops.DateGreaterEqual],
        'updated_on': [ops.Greaterequal, ops.DateGreaterEqual, ops.DateEqual, ops.DateLesserEqual]
    }

    def has_read_permission(self, qs):
        if current_user.has_permission('view_brand'):
            return qs.filter(self.model.store_id.in_(current_user.store_ids))
        return qs.filter(false())

    def has_change_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and current_user.has_permission('change_brand')

    def has_delete_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and current_user.has_permission('remove_brand')

    def has_add_permission(self, objects):
        if not current_user.has_permission('create_brand'):
            return False
        for obj in objects:
            if not current_user.has_store_access(obj.store_id):
                return False
        return True


class TaxResource(ModelResource):
    model = Tax
    schema = TaxSchema

    auth_required = True
    optional = ('products', 'store')

    order_by = ['store_id', 'id', 'name']

    filters = {
        'name': [ops.Equal, ops.Contains],
        'store_id': [ops.Equal, ops.In],
        'created_on': [ops.DateLesserEqual, ops.DateEqual, ops.DateGreaterEqual],
        'updated_on': [ops.Greaterequal, ops.DateGreaterEqual, ops.DateEqual, ops.DateLesserEqual]
    }

    only = ()

    exclude = ()

    def has_read_permission(self, qs):
        if current_user.has_permission('view_tax'):
            return qs.filter(self.model.store_id.in_(current_user.store_ids))
        return qs.filter(false())

    def has_change_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and current_user.has_permission('change_tax')

    def has_delete_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and current_user.has_permission('remove_tax')

    def has_add_permission(self, objects):
        if not current_user.has_permission('create_tax'):
            return False
        for obj in objects:
            if not current_user.has_store_access(obj.store_id):
                return False
        return True


class SaltResource(ModelResource):
    model = Salt
    schema = SaltSchema

    auth_required = True

    max_limit = 500

    default_limit = 100

    optional = ('products', 'store', 'working', 'side_effects', 'usage')

    order_by = ['store_id', 'id', 'name']

    filters = {
        'name': [ops.Equal, ops.Contains],
        'store_id': [ops.Equal, ops.In],
        'created_on': [ops.DateLesserEqual, ops.DateEqual, ops.DateGreaterEqual],
        'updated_on': [ops.Greaterequal, ops.DateGreaterEqual, ops.DateEqual, ops.DateLesserEqual]
    }

    def has_read_permission(self, qs):
        if current_user.has_permission('view_salt'):
            return qs.filter(self.model.store_id.in_(current_user.store_ids))
        return qs.filter(false())

    def has_change_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and current_user.has_permission('change_salt')

    def has_delete_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and current_user.has_permission('remove_salt')

    def has_add_permission(self, objects):
        if not current_user.has_permission('create_salt'):
            return False
        for obj in objects:
            if not current_user.has_store_access(obj.store_id):
                return False
        return True


class ComboResource(ModelResource):
    model = Combo
    schema = ComboSchema

    auth_required = True

    optional = ('products', 'store')

    filters = {
        'name': [ops.Equal, ops.Contains],
        'store_id': [ops.Equal, ops.In],
        'created_on': [ops.DateLesserEqual, ops.DateEqual, ops.DateGreaterEqual],
        'updated_on': [ops.Greaterequal, ops.DateGreaterEqual, ops.DateEqual, ops.DateLesserEqual]
    }

    def has_read_permission(self, qs):
        if current_user.has_permission('view_combo'):
            return qs.filter(self.model.store_id.in_(current_user.store_ids))
        return qs.filter(false())

    def has_change_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and current_user.has_permission('change_combo')

    def has_delete_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and current_user.has_permission('remove_combo')

    def has_add_permission(self, objects):
        if not current_user.has_permission('create_combo'):
            return False
        for obj in objects:
            if not current_user.has_store_access(obj.store_id):
                return False
        return True


class ProductTagResource(AssociationModelResource):
    model = ProductTag

    schema = ProductTagSchema

    auth_required = True

    roles_accepted = ('admin',)

    optional = ('product', 'salt')

    def has_read_permission(self, qs):
        if current_user.has_permission('view_product_tag'):
            return qs.filter(self.model.store_id.in_(current_user.store_ids))
        return qs.filter(false())

    def has_change_permission(self, obj, data):
        return current_user.has_store_access(obj.store_id) and \
               current_user.has_permission('change_product_tag')

    def has_delete_permission(self, obj, data):
        return current_user.has_store_access(obj.store_id) and \
               current_user.has_permission('remove_product_tag')

    def has_add_permission(self, obj, data):

        if not current_user.has_permission('create_product_tag') or \
                not current_user.has_store_access(Product.query.with_entities(Product.store_id)
                                                         .filter(Product.id == obj.product_id).scalar()):
            return False
        return True


class ProductSaltResource(AssociationModelResource):
    model = ProductSalt

    schema = ProductSaltSchema

    auth_required = True

    default_limit = 100

    max_limit = 500

    roles_accepted = ('admin',)

    optional = ('product', 'salt', 'store_id')

    filters = {
        'updated_on': [ops.Greaterequal, ops.DateGreaterEqual, ops.DateEqual, ops.DateLesserEqual],
        'created_on': [ops.Greaterequal, ops.DateGreaterEqual, ops.DateEqual, ops.DateLesserEqual],
        'store_id': [ops.Equal, ops.In],
        'salt_id': [ops.Equal, ops.In]
    }

    def has_read_permission(self, qs):
        if current_user.has_permission('view_product_salt'):
            return qs.filter(self.model.store_id.in_(current_user.store_ids))
        return qs.filter(false())

    def has_change_permission(self, obj, data):
        return current_user.has_store_access(obj.store_id) and \
               current_user.has_permission('change_product_salt')

    def has_delete_permission(self, obj, data):
        return current_user.has_store_access(obj.store_id) and \
               current_user.has_permission('remove_product_salt')

    def has_add_permission(self, obj, data):
        if not current_user.has_permission('create_product_salt') or \
                not current_user.has_store_access(Product.query.with_entities(Product.store_id)
                                                         .filter(Product.id == obj.product_id).scalar()):
            return False
        return True


class ProductTaxResource(AssociationModelResource):
    model = ProductTax
    schema = ProductTaxSchema

    auth_required = True

    max_limit = 500

    def has_read_permission(self, qs):
        if current_user.has_permission('view_product_tax'):
            return qs.filter(self.model.store_id.in_(current_user.store_ids))
        return qs.filter(false())

    def has_change_permission(self, obj, data):
        return current_user.has_store_access(obj.store_id) and current_user.has_permission('change_product_tax')

    def has_delete_permission(self, obj, data):
        return current_user.has_store_access(obj.store_id) and current_user.has_permission('remove_product_tax')

    def has_add_permission(self, obj, data):
        if not current_user.has_permission('create_product_tax') or \
                not current_user.has_store_access(Product.query.with_entities(Product.store_id)
                                                         .filter(Product.id == obj.product_id).scalar()):
            return False
        return True
