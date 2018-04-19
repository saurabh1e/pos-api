from marshmallow import pre_load
from flask_security import current_user

from src import ma, BaseSchema
from src.user.models import Customer
from .models import Order, Item, ItemTax, Status


class OrderSchema(BaseSchema):
    class Meta:
        model = Order

    sub_total = ma.Float(precision=2)
    total = ma.Float(precision=2)

    store_id = ma.Integer(load=True, allow_none=True)

    customer_id = ma.Integer(load=True, required=False, allow_none=True)
    address_id = ma.Integer(load=True, required=False, partial=True, allow_none=True)
    discount_id = ma.Integer()
    items_count = ma.Integer(dump_only=True)
    amount_due = ma.Integer(dump_only=True)

    items = ma.Nested('ItemSchema', many=True, exclude=('order', 'order_id'), load=True)
    retail_shop = ma.Nested('RetailShopSchema', many=False, only=('id', 'name'))
    customer = ma.Nested('CustomerSchema', many=False, load=True, only=['id', 'name', 'number'])
    address = ma.Nested('AddressSchema', many=False, dump_only=True, only=['id', 'name'])
    discounts = ma.Nested('DiscountSchema', many=True, load=True)

    @pre_load()
    def save(self, data):
        if 'customer' in data and (data['customer']['name'] or data['customer']['number']):
            customer_id = Customer.query.with_entities(Customer.id)\
                .filter(Customer.organisation_id == current_user.organisation_id,
                        Customer.name == data['customer']['name'],
                        Customer.number == data['customer']['number']).limit(1).scalar()
            if customer_id:
                data['customer_id'] = customer_id
                data.pop('customer')


class ItemSchema(BaseSchema):
    class Meta:
        model = Item
        exclude = ('created_on', 'updated_on')

    id = ma.Integer(dump_only=True)
    product_id = ma.Integer(load=False, dump_only=True)
    unit_price = ma.Float(precision=2)
    quantity = ma.Float(precision=2)
    order_id = ma.Integer()
    stock_id = ma.Integer()
    discount = ma.Float()
    discounted_total_price = ma.Float(dump_only=True)
    discounted_unit_price = ma.Float(dump_only=True)
    total_price = ma.Float(dump_only=True)
    discount_amount = ma.Float(dump_only=True)

    taxes = ma.Nested('ItemTaxSchema', many=True, exclude=('item',))


class ItemTaxSchema(BaseSchema):
    class Meta:
        model = ItemTax
        exclude = ('created_on', 'updated_on')

    tax_value = ma.Float(precision=2)
    id = ma.Integer(dump_only=True)
    item_id = ma.Integer(load=True)
    tax_id = ma.Integer(load=True)

    tax = ma.Nested('TaxSchema', many=False, only=('id', 'name'), dump_only=True)
    item = ma.Nested('ItemSchema', many=False, dump_only=True)


class StatusSchema(BaseSchema):
    class Meta:
        model = Status
        exclude = ('created_on', 'updated_on')

    name = ma.String()
    amount = ma.Float(precision=2)
