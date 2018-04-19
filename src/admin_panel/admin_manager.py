from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from flask_admin_impexp.admin_impexp import AdminImportExport
from flask_security import current_user
from src import admin, db
from src.user.models import User, Role, Permission, UserRole, Organisation, Store, \
    Address, Locality, City, Customer, RegistrationDetail, CustomerAddress, CustomerTransaction, PrinterConfig
from src.orders.models import Status, Item, Order, ItemTax, OrderStatus
from src.products.models import ProductTax, Tax, Product, ProductType, Stock, Distributor,\
    DistributorBill, Tag, Brand, Salt, Combo, ProductSalt, ProductTag, ProductCategory, Category


class MyModel(AdminImportExport):
    page_size = 100
    can_set_page_size = True
    can_view_details = True

    def is_accessible(self):
        return current_user.has_role('admin')


class StoreAdmin(MyModel):

    column_filters = ('name',)
    form_excluded_columns = ('orders',)

    form_ajax_refs = {
        'registration_details': QueryAjaxModelLoader('registration_details', db.session, RegistrationDetail,
                                                     fields=['name'], page_size=10),
        'printer_config': QueryAjaxModelLoader('printer_config', db.session, PrinterConfig, fields=['id'], page_size=10),
        'users': QueryAjaxModelLoader('users', db.session, User, fields=['name'], page_size=10),
        'orders': QueryAjaxModelLoader('orders', db.session, Order, fields=['id'], page_size=10),
        'organisation': QueryAjaxModelLoader('organisation', db.session, Organisation, fields=['name'], page_size=10),
        'tags': QueryAjaxModelLoader('tags', db.session, Tag, fields=['name'], page_size=10),
        'salts': QueryAjaxModelLoader('salts', db.session, Salt, fields=['name'], page_size=10),
        'taxes': QueryAjaxModelLoader('taxes', db.session, Tax, fields=['name'], page_size=10),
        'distributors': QueryAjaxModelLoader('distributors', db.session, Distributor, fields=['name'], page_size=10),

    }


class DistributorBillAdmin(MyModel):

    column_searchable_list = ('id',  'purchase_date', 'reference_number')
    column_filters = ('distributor.name', 'distributor', 'purchase_date', 'reference_number')

    form_ajax_refs = {
        'distributor': QueryAjaxModelLoader('distributor', db.session, Distributor, fields=['name'], page_size=10),
        'purchased_items':  QueryAjaxModelLoader('purchased_items', db.session, Stock, fields=['product_name'],
                                                 page_size=10),
    }


class ProductAdmin(MyModel):

    # column_filters = ('brand', 'tags', 'taxes', 'salts')

    column_sortable_list = ('created_on',)
    column_default_sort = 'created_on'
    column_searchable_list = ('name',)
    column_editable_list = ('name', 'sub_description',
                            'is_loose', 'is_disabled', 'barcode')

    form_ajax_refs = {
        'brand': QueryAjaxModelLoader('brand', db.session, Brand, fields=['name'], page_size=10),
        'stocks': QueryAjaxModelLoader('stocks', db.session, Stock, fields=['product_name'], page_size=10),
        'tags': QueryAjaxModelLoader('tags', db.session, Tag, fields=['name'], page_size=10),
        'salts': QueryAjaxModelLoader('salts', db.session, Salt, fields=['name'], page_size=10),
        'taxes': QueryAjaxModelLoader('taxes', db.session, Tax, fields=['name'], page_size=10),
    }

    inline_models = (Tag, Tax, Salt)


class DistributorAdmin(MyModel):

    column_editable_list = ('name',)
    column_filters = ('store',)
    form_ajax_refs = {    }


class TaxAdmin(MyModel):

    column_sortable_list = ('name',)
    column_searchable_list = ('id', 'store_id', 'name')
    column_editable_list = ('name', 'store_id')
    column_filters = ('products.name', 'store')

    form_ajax_refs = {
        'products': QueryAjaxModelLoader('products', db.session, Product, fields=['name'], page_size=10),
        'store': QueryAjaxModelLoader('store', db.session, Store, fields=['name'], page_size=10),
    }


class SaltAdmin(MyModel):
    column_sortable_list = ('name',)
    column_searchable_list = ('id', 'store_id', 'name')
    column_editable_list = ('name', 'store_id')
    column_filters = ('products.name', 'store')

    form_ajax_refs = {
        'products': QueryAjaxModelLoader('products', db.session, Product, fields=['name'], page_size=10),
        'store': QueryAjaxModelLoader('store', db.session, Store, fields=['name'], page_size=10),
    }


class TagAdmin(MyModel):
    column_sortable_list = ('name',)
    column_searchable_list = ('id', 'store_id', 'name')
    column_editable_list = ('name', 'store_id')
    column_filters = ('products.name', 'store')

    form_ajax_refs = {
        'product': QueryAjaxModelLoader('product', db.session, Product, fields=['name'], page_size=10),
        'store': QueryAjaxModelLoader('store', db.session, Store, fields=['name'], page_size=10),
    }


class BrandAdmin(MyModel):

    column_sortable_list = ('name',)
    column_searchable_list = ('id', 'name')
    column_editable_list = ('name',)
    column_filters = ('products.name',)

    form_ajax_refs = {
        'products': QueryAjaxModelLoader('products', db.session, Product, fields=['name'], page_size=10),
    }


class BrandDistributorAdmin(MyModel):

    column_searchable_list = ('id', 'brand_id', 'distributor_id')


class StockAdmin(MyModel):

    column_filters = ('product.name', 'product')
    column_editable_list = ('selling_amount', 'purchase_amount', 'batch_number', 'expiry_date',
                            'is_sold', 'default_stock', 'units_purchased')

    form_ajax_refs = {
        'product': QueryAjaxModelLoader('product', db.session, Product, fields=['name'], page_size=10),
        'distributor_bill': QueryAjaxModelLoader('distributor_bill', db.session, DistributorBill,
                                                 fields=['distributor_name'], page_size=10)
    }


class ProductTaxAdmin(MyModel):
    column_filters = ('product.name', 'tax')
    column_searchable_list = ('product.name', 'product_id')
    form_ajax_refs = {
        'tax': QueryAjaxModelLoader('tax', db.session, Tax, fields=['name'], page_size=10),
        'products': QueryAjaxModelLoader('products', db.session, Product, fields=['name'], page_size=10),
    }


class ProductSaltAdmin(MyModel):
    column_filters = ('product.name', 'salt', 'unit', 'value')
    column_searchable_list = ('product.name', 'salt.id',
                              'salt.name', 'product.id')

    form_ajax_refs = {
        'salt': QueryAjaxModelLoader('salt', db.session, Salt, fields=['name'], page_size=10),
        'product': QueryAjaxModelLoader('product', db.session, Product, fields=['name'], page_size=10),
    }


class ProductTagAdmin(MyModel):
    column_filters = ('product.name', 'tag')
    column_searchable_list = ('product.name', 'product_id', 'product.name')

    form_ajax_refs = {
        'tag': QueryAjaxModelLoader('tag', db.session, Tag, fields=['name'], page_size=10),
        'product': QueryAjaxModelLoader('product', db.session, Product, fields=['name'], page_size=10),
    }


class RoleAdmin(MyModel):
    column_filters = ('users.name', 'name')
    column_searchable_list = ('id',)


class PermissionAdmin(MyModel):
    column_filters = ('users.name', 'name')
    column_searchable_list = ('id',)


class CustomerAdmin(MyModel):
    column_filters = ('email', 'name', 'number', 'organisation', 'orders')
    form_excluded_columns = ('orders', 'transactions')
    column_searchable_list = ('id', 'name', 'number')


admin.add_view(MyModel(User, session=db.session))
admin.add_view(CustomerAdmin(Customer, session=db.session))
admin.add_view(MyModel(CustomerTransaction, session=db.session))
admin.add_view(RoleAdmin(Role, session=db.session))
admin.add_view(MyModel(UserRole, session=db.session))
admin.add_view(PermissionAdmin(Permission, session=db.session))

admin.add_view(StoreAdmin(Store, session=db.session))
admin.add_view(MyModel(Organisation, session=db.session))
admin.add_view(MyModel(RegistrationDetail, session=db.session))
admin.add_view(MyModel(PrinterConfig, session=db.session))
admin.add_view(MyModel(Address, session=db.session))
admin.add_view(MyModel(CustomerAddress, session=db.session))
admin.add_view(MyModel(Locality, session=db.session))
admin.add_view(MyModel(City, session=db.session))


admin.add_view(ProductAdmin(Product, session=db.session))
admin.add_view(MyModel(Category, session=db.session))
admin.add_view(MyModel(ProductCategory, session=db.session))

admin.add_view(TagAdmin(Tag, session=db.session))
admin.add_view(SaltAdmin(Salt, session=db.session))
admin.add_view(BrandAdmin(Brand, session=db.session))
admin.add_view(StockAdmin(Stock, session=db.session))
admin.add_view(DistributorAdmin(Distributor, session=db.session))
admin.add_view(TaxAdmin(Tax, session=db.session))

admin.add_view(ProductTaxAdmin(ProductTax, session=db.session))
admin.add_view(ProductSaltAdmin(ProductSalt, session=db.session))
admin.add_view(ProductTagAdmin(ProductTag, session=db.session))
admin.add_view(MyModel(Combo, session=db.session))
admin.add_view(MyModel(ProductType, session=db.session))
admin.add_view(DistributorBillAdmin(DistributorBill, session=db.session))


admin.add_view(MyModel(Order, session=db.session))
admin.add_view(MyModel(OrderStatus, session=db.session))
admin.add_view(MyModel(Item, session=db.session))
admin.add_view(MyModel(ItemTax, session=db.session))
admin.add_view(MyModel(Status, session=db.session))
