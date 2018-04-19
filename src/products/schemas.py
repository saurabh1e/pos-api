from marshmallow import post_load
from src import ma, BaseSchema
from .models import Brand, Distributor, DistributorBill, Product, Tag, Stock, ProductTax, Tax, \
    Combo, Salt, ProductSalt, ProductTag


class BrandSchema(BaseSchema):
    class Meta:
        model = Brand
        exclude = ('created_on', 'updated_on')

    name = ma.String()
    store_id = ma.Integer()
    store = ma.Nested('StoreSchema', many=False, dump_only=True, only=('id', 'name'))
    distributors = ma.Nested('DistributorSchema', many=True, dump_only=True, only=('id', 'name'))
    products = ma.Nested('ProductSchema', many=True, dump_only=True, only=('id', 'name'))


class TagSchema(BaseSchema):
    class Meta:
        model = Tag
        exclude = ('created_on', 'updated_on')

    id = ma.Integer()
    name = ma.String()
    store_id = ma.Integer()
    store = ma.Nested('StoreSchema', many=False, dump_only=True, only=('id', 'name'))


class ProductTaxSchema(BaseSchema):
    class Meta:
        model = ProductTax
        exclude = ('created_on', 'updated_on')
        fields = ('tax_id', 'product_id')

    tax_id = ma.Integer(load=True)
    product_id = ma.Integer(load=True)


class TaxSchema(BaseSchema):
    class Meta:
        model = Tax
        exclude = ('created_on', 'updated_on')

    name = ma.String(load=True)
    value = ma.Float(precision=2, load=True)
    store_id = ma.Integer(load=True)
    store = ma.Nested('StoreSchema', many=False, dump_only=True, only=('id', 'name'))


class DistributorSchema(BaseSchema):
    class Meta:
        model = Distributor
        exclude = ('created_on', 'updated_on')

    id = ma.Integer()
    name = ma.String()
    phone_numbers = ma.List(ma.Integer())
    emails = ma.List(ma.Email())
    store_id = ma.Integer()
    products = ma.Nested('ProductSchema', many=True, dump_only=True, only=('id', 'name', 'last_selling_amount',
                                                                           'barcode', 'last_purchase_amount',
                                                                           'stock_required', 'quantity_label'))

    store = ma.Nested('StoreSchema', many=False, dump_only=True, only=('id', 'name'))
    bills = ma.Nested('DistributorBillSchema', many=True, exclude=('distributor', 'distributor_id'))


class DistributorBillSchema(BaseSchema):
    class Meta:
        model = DistributorBill
        exclude = ('created_on', 'updated_on')

    purchase_date = ma.Date(load=True)
    distributor_id = ma.Integer(load=True)
    total_items = ma.Integer(dump_only=True)
    bill_amount = ma.Integer(dump_only=True)

    distributor = ma.Nested('DistributorSchema', many=False, only=('id', 'name', 'store'))
    purchased_items = ma.Nested('StockSchema', many=True, exclude=('distributor_bill', 'order_items', 'product'),
                                load=True)


class ProductSchema(BaseSchema):
    class Meta:
        model = Product
        exclude = ('created_on', 'updated_on')

    name = ma.String()
    description = ma.List(ma.Dict(), allow_none=True)
    sub_description = ma.String(allow_none=True)
    brand_id = ma.Integer()
    store_id = ma.Integer()
    default_quantity = ma.Float(precision=2, partila=True)
    quantity_label = ma.String(load=True, allow_none=True)
    is_loose = ma.Boolean(load=True, allow_none=True)
    mrp = ma.Integer(dump_only=True)
    available_stock = ma.Integer(dump_only=True)
    barcode = ma.String(max_length=13, min_length=8, load=True, allow_none=True)
    prescription_required = ma.Boolean(dump_only=True)
    last_selling_amount = ma.Float(precision=2, dump_only=True)
    last_purchase_amount = ma.Float(precision=2, dump_only=True)
    stock_required = ma.Integer(dump_only=True)
    is_short = ma.Boolean(dump_only=True)
    distributors = ma.Nested('DistributorSchema', many=True, dump_only=True, only=('id', 'name'))
    brand = ma.Nested('BrandSchema', many=False, dump_only=True, only=('id', 'name'))
    packaging_form = ma.String(dump_only=True, allow_none=True)
    packaging_size = ma.String(dump_only=True, allow_none=True)
    similar_products = ma.List(ma.Integer)
    store = ma.Nested('StoreSchema', many=False, dump_only=True, only=('id', 'name'))
    tags = ma.Nested('TagSchema', many=True, only=('id', 'name'), dump_only=True)
    salts = ma.Nested('SaltSchema', many=True, only=('id', 'name'), dump_only=True)
    product_salts = ma.Nested('ProductSaltSchema', many=True, only=('salt_id', 'unit', 'value'),
                              dump_only=True,
                              exclude=('product', 'store', 'store_id', 'salt', 'product_id'))

    _links = ma.Hyperlinks(
        {
            'distributor': ma.URLFor('pos.distributor_view', __product_id__exact='<id>'),
            'store': ma.URLFor('pos.store_view', slug='<store_id>'),
            'brand': ma.URLFor('pos.brand_view', slug='<brand_id>'),
            'stocks': ma.URLFor('pos.stock_view', __product_id__exact='<id>')
        }
    )

    stocks = ma.Nested('StockSchema', many=True, only=('purchase_amount', 'selling_amount', 'units_purchased',
                                                       'units_sold', 'expiry_date', 'purchase_date', 'id'))
    taxes = ma.Nested('TaxSchema', many=True, dump_only=True, only=('id', 'name', 'value'))
    available_stocks = ma.Nested('StockSchema', many=True, dump_only=True,
                                 only=('purchase_amount', 'selling_amount', 'units_purchased', 'batch_number',
                                       'units_sold', 'expiry_date', 'purchase_date', 'id', 'default_stock'))

    @post_load
    def save_data(self, obj):
        return obj


class StockSchema(BaseSchema):
    class Meta:
        model = Stock
        exclude = ('order_items', 'created_on', 'updated_on')

    purchase_amount = ma.Float(precision=2)
    selling_amount = ma.Float(precision=2)
    units_purchased = ma.Integer()
    batch_number = ma.String(load=True)
    expiry_date = ma.Date(load=True)
    store_id = ma.Integer(load=True, allow_none=False)
    product_name = ma.String()
    product_id = ma.Integer(load=True)
    distributor_bill_id = ma.Integer(allow_none=True)
    units_sold = ma.Integer(dump_only=True, load=False)
    expired = ma.Boolean(dump_only=True)
    brand_name = ma.String(dump_only=True)
    quantity_label = ma.String(dump_only=True)
    default_stock = ma.Boolean(load=True, allow_none=True)

    distributor_bill = ma.Nested('DistributorBillSchema', many=False, dump_only=True, only=('id', 'distributor',
                                                                                            'reference_number'))
    product = ma.Nested('ProductSchema', many=False, only=('id', 'name', 'store'), dump_only=True)

    @post_load
    def index_stock(self, data):
        return data


class SaltSchema(BaseSchema):
    class Meta:
        model = Salt
        exclude = ('created_on', 'updated_on')

    store_id = ma.Integer()
    store = ma.Nested('StoreSchema', many=False, dump_only=True, only=('id', 'name'))


class SaltElasticSchema(BaseSchema):
    class Meta:
        model = Salt
        exclude = ('created_on', 'updated_on', 'store', 'products', 'prescription_required', 'store_id')

    id = ma.Integer()


class ComboSchema(BaseSchema):
    class Meta:
        model = Combo
        exclude = ('created_on', 'updated_on')
    store_id = ma.Integer()


class ProductSaltSchema(BaseSchema):

    class Meta:
        model = ProductSalt
        exclude = ('created_on', 'updated_on', 'salt', 'store', 'product')

    salt_id = ma.Integer(load=True, required=True, allow_none=False)
    product_id = ma.Integer(load=True, required=True, allow_none=False)
    store_id = ma.Integer(dump_only=True)

    @post_load
    def save_data(self, obj):
        # index_product_salts(*[obj.id])
        return obj


class ProductTagSchema(BaseSchema):

    class Meta:
        model = ProductTag
        exclude = ('created_on', 'updated_on')

    tag_id = ma.Integer(load=True)
    product_id = ma.Integer(load=True)

    @post_load
    def index_product(self, data):
        return data


class ProductElasticSchema(BaseSchema):

    class Meta:
        model = Product
        exclude = ('created_on', 'updated_on', 'store', 'last_selling_amount',
                   'last_purchase_amount', 'stock_required', 'is_short', 'distributors',
                   '_links', 'stocks', 'min_stock', 'combos', 'add_ons')

    name = ma.String()
    short_code = ma.String()
    description = ma.List(ma.Dict(), allow_none=True)
    sub_description = ma.String(allow_none=True)
    brand_id = ma.Integer()
    brand = ma.Nested('BrandSchema', many=False, only=('name',))
    salts = ma.Nested('SaltElasticSchema', many=True, only=('id', 'name'))
    taxes = ma.Nested('TaxSchema', many=True, dump_only=True, only=('id', 'name', 'value'))
    is_disabled = ma.Boolean()
    store_id = ma.Integer()
    quantity_label = ma.String(dump_only=True, allow_none=True)
    default_quantity = ma.Float(precision=2, partila=True)
    packaging_form = ma.String(dump_only=True, allow_none=True)
    packaging_size = ma.String(dump_only=True, allow_none=True)
    is_loose = ma.Boolean(dump_only=True, allow_none=True)
    mrp = ma.Integer(dump_only=True)
    min_stock = ma.Float(dump_only=True)
    auto_discount = ma.Float(dump_only=True)
    available_stock = ma.Integer(dump_only=True)
    similar_products = ma.List(ma.Integer)
    product_salts = ma.Nested('ProductSaltSchema', many=True, only=('salt_id', 'unit', 'value'))
    barcode = ma.String(max_length=13, min_length=8, dump_onl=True, allow_none=False)
    available_stocks = ma.Nested('StockSchema', many=True, dump_only=True,
                                 only=('purchase_amount', 'selling_amount', 'units_purchased', 'batch_number',
                                       'units_sold', 'expiry_date', 'purchase_date', 'id', 'default_stock'))

