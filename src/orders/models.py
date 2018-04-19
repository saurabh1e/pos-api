from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func, select
from src import db, BaseMixin, ReprMixin


class OrderStatus(BaseMixin, db.Model, ReprMixin):
    __repr_fields__ = ['order_id', 'status_id']

    order_id = db.Column(db.ForeignKey('order.id'), nullable=False, index=True)
    status_id = db.Column(db.ForeignKey('status.id'), nullable=False, index=True)

    order = db.relationship('Order', foreign_keys=[order_id])
    status = db.relationship('Status', foreign_keys=[status_id])


class Status(BaseMixin, db.Model, ReprMixin):

    name = db.Column(db.String(20), unique=True, nullable=False)
    code = db.Column(db.SmallInteger, unique=True, nullable=False)


class Order(BaseMixin, db.Model, ReprMixin):

    __repr_fields__ = ['id', 'invoice_number']

    is_draft = db.Column(db.Boolean(), default=True)
    sub_total = db.Column(db.Float(precision=2), default=0, nullable=True)
    total = db.Column(db.Float(precision=2), default=0, nullable=True)
    amount_paid = db.Column(db.Float(precision=2), default=0, nullable=True)
    auto_discount = db.Column(db.Float(precision=2), default=0, nullable=True)
    is_void = db.Column(db.Boolean(), default=False)
    invoice_number = db.Column(db.Integer)
    reference_number = db.Column(db.String(12), nullable=True)

    customer_id = db.Column(db.ForeignKey('customer.id'), nullable=True, index=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=True, index=True)
    address_id = db.Column(db.ForeignKey('address.id'), nullable=True, index=True)
    store_id = db.Column(db.ForeignKey('store.id'), nullable=True, index=True)

    items = db.relationship('Item', uselist=True, back_populates='order', lazy='dynamic', cascade='all, delete-orphan')
    customer = db.relationship('Customer', foreign_keys=[customer_id], lazy='subquery')
    created_by = db.relationship('User', foreign_keys=[user_id], lazy='subquery')
    address = db.relationship('Address', foreign_keys=[address_id], lazy='subquery')
    store = db.relationship('Store', foreign_keys=[store_id], lazy='subquery')
    time_line = db.relationship('Status', secondary='order_status')

    @hybrid_property
    def total_discount(self):
        return sum([discount.value if discount.type == 'VALUE' else float(self.total*discount/100)
                    for discount in self.discounts])

    @hybrid_property
    def items_count(self):
        return self.items.with_entities(func.Count(Item.id)).scalar()

    @items_count.expression
    def items_count(cls):
        return select([func.Count(Item.id)]).where(Item.order_id == cls.id).as_scalar()

    @hybrid_property
    def amount_due(self):
        if self.total and self.amount_paid:
            return self.total - self.amount_paid
        return self.total


class Item(BaseMixin, db.Model, ReprMixin):

    __repr_fields__ = ['id', 'order_id', 'product_id']

    name = db.Column(db.String(55))
    unit_price = db.Column(db.Float(precision=2))
    quantity = db.Column(db.Float(precision=2))
    discount = db.Column(db.FLOAT(precision=2), default=0, nullable=False)
    stock_adjust = db.Column(db.Boolean(), default=False)

    order_id = db.Column(db.ForeignKey('order.id'), nullable=True, index=True)
    stock_id = db.Column(db.ForeignKey('stock.id'), nullable=True, index=True)

    order = db.relationship('Order', foreign_keys=[order_id], single_parent=True, back_populates='items',
                            cascade="all, delete-orphan")
    taxes = db.relationship('ItemTax', uselist=True, cascade='all, delete-orphan',
                            back_populates='item')

    stock = db.relationship('Stock', foreign_keys=[stock_id], single_parent=True, back_populates='order_items')

    @hybrid_property
    def total_price(self):
        return float(self.unit_price * self.quantity)

    @hybrid_property
    def discounted_total_price(self):
        return float(self.discounted_unit_price * self.quantity)

    @hybrid_property
    def discounted_unit_price(self):
        return float(self.unit_price-(self.unit_price * self.discount)/100)

    @hybrid_property
    def discount_amount(self):
        return float((self.total_price*self.discount)/100)

    @hybrid_property
    def is_combo(self):
        return self.combo_id is not None

    @hybrid_property
    def store_id(self):
        return self.order.store_id

    @store_id.expression
    def store_id(self):
        return select([Order.store_id]).where(Order.id == self.order_id).as_scalar()


class ItemTax(BaseMixin, db.Model):

    tax_value = db.Column(db.Float(precision=2))
    tax_amount = db.Column(db.Float(precision=2))
    item_id = db.Column(db.ForeignKey('item.id'), index=True)
    tax_id = db.Column(db.ForeignKey('tax.id'), index=True)

    tax = db.relationship('Tax', foreign_keys=[tax_id])
    item = db.relationship('Item', back_populates='taxes', foreign_keys=[item_id])
