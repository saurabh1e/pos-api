from datetime import datetime
import re
from sqlalchemy import and_, func, select, or_
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import NUMERIC
from sqlalchemy.ext.hybrid import hybrid_property

from src import db, BaseMixin, ReprMixin
from src.orders.models import Item
from src.user.models import Store


class Brand(BaseMixin, db.Model, ReprMixin):
    name = db.Column(db.String(55), nullable=False, index=True, unique=True)
    products = db.relationship('Product', uselist=True, back_populates='brand')


class ProductTax(BaseMixin, db.Model, ReprMixin):
    tax_id = db.Column(db.ForeignKey('tax.id'), index=True)
    product_id = db.Column(db.ForeignKey('product.id'), index=True)

    tax = db.relationship('Tax', foreign_keys=[tax_id])
    product = db.relationship('Product', foreign_keys=[product_id])

    UniqueConstraint(tax_id, product_id)

    @hybrid_property
    def store_id(self):
        return self.product.store_id

    @store_id.expression
    def store_id(self):
        return select([Product.store_id]).where(Product.id == self.product_id).as_scalar()


class Tax(BaseMixin, db.Model, ReprMixin):
    name = db.Column(db.String(25), nullable=False, index=True)
    value = db.Column(db.Float(precision=2), nullable=False)
    is_disabled = db.Column(db.Boolean(), default=False)

    store_id = db.Column(db.ForeignKey('store.id', ondelete='CASCADE'), index=True, nullable=False)

    store = db.relationship('Store', foreign_keys=[store_id], uselist=False, backref='taxes')
    products = db.relationship('Product', back_populates='taxes', secondary='product_tax', lazy='dynamic')

    UniqueConstraint(name, store_id)


class Distributor(BaseMixin, db.Model, ReprMixin):
    name = db.Column(db.String(127), nullable=False, index=True)
    phone_numbers = db.Column(db.JSON)
    emails = db.Column(db.JSON)

    store_id = db.Column(db.ForeignKey('store.id', ondelete='CASCADE'), index=True, nullable=False)

    store = db.relationship('Store', foreign_keys=[store_id], uselist=False, backref='distributors')

    UniqueConstraint(name, store_id)

    @hybrid_property
    def store_name(self):
        return self.store.name

    @store_name.expression
    def store_name(self):
        return select([Store.name]).where(Store.id == self.store_id).as_scalar()


class DistributorBill(BaseMixin, db.Model, ReprMixin):
    __repr_fields__ = ['id', 'distributor_id']

    purchase_date = db.Column(db.Date, nullable=False)
    reference_number = db.Column(db.String(55), nullable=True)
    distributor_id = db.Column(db.ForeignKey('distributor.id'), nullable=False, index=True)

    distributor = db.relationship('Distributor', single_parent=True,)
    purchased_items = db.relationship('Stock', uselist=True, back_populates='distributor_bill', lazy='dynamic')

    @hybrid_property
    def bill_amount(self):
        return self.purchased_items.with_entities(func.Sum(Stock.purchase_amount * Stock.units_purchased)).scalar()

    @bill_amount.expression
    def bill_amount(cls):
        return select([func.Sum(Stock.units_purchased * Stock.purchase_amount)]) \
            .where(Stock.distributor_bill_id == cls.id).as_scalar()

    @hybrid_property
    def total_items(self):
        return self.purchased_items.with_entities(func.Count(Stock.id)).scalar()

    @total_items.expression
    def total_items(cls):
        return select([func.Count(func.Distinct(Stock.id))]).where(Stock.distributor_bill_id == cls.id).as_scalar()

    @hybrid_property
    def store_id(self):
        return self.distributor.store_id

    @store_id.expression
    def store_id(self):
        return select([Distributor.store_id]).where(Distributor.id == self.distributor_id).as_scalar()

    @hybrid_property
    def store_name(self):
        return self.distributor.store.name

    @store_name.expression
    def store_name(self):
        return select([Distributor.store_name]).where(Distributor.id == self.distributor_id).as_scalar()

    @hybrid_property
    def distributor_name(self):
        return self.distributor.name

    @distributor_name.expression
    def distributor_name(self):
        return select([Distributor.name]).where(Distributor.id == self.distributor_id).as_scalar()


class ProductType(BaseMixin, db.Model, ReprMixin):
    name = db.Column(db.String(80), unique=True, index=True)
    description = db.Column(db.TEXT())
    store_id = db.Column(db.ForeignKey('store.id', ondelete='CASCADE'), index=True)


class Tag(BaseMixin, db.Model, ReprMixin):
    name = db.Column(db.String(55), unique=False, nullable=False, index=True)
    store_id = db.Column(db.ForeignKey('store.id', ondelete='CASCADE'), index=True, nullable=False)

    products = db.relationship('Product', back_populates='tags', secondary='product_tag')
    store = db.relationship('Store', foreign_keys=[store_id], uselist=False, backref='tags')

    UniqueConstraint(name, store_id)


class ProductTag(BaseMixin, db.Model, ReprMixin):
    __repr_fields__ = ['tag_id', 'product_id']

    tag_id = db.Column(db.ForeignKey('tag.id'), index=True)
    product_id = db.Column(db.ForeignKey('product.id'), index=True)

    tag = db.relationship('Tag', foreign_keys=[tag_id])
    product = db.relationship('Product', foreign_keys=[product_id])

    UniqueConstraint(tag_id, product_id)

    @hybrid_property
    def store_id(self):
        return self.product.store_id

    @store_id.expression
    def store_id(self):
        return select([Product.store_id]).where(Product.id == self.product_id).as_scalar()


class Product(BaseMixin, db.Model, ReprMixin):
    name = db.Column(db.String(127), unique=True, nullable=False, index=True)

    description = db.Column(db.JSON(), nullable=True)
    sub_description = db.Column(db.Text(), nullable=True)
    is_disabled = db.Column(db.Boolean(), default=False)
    url = db.Column(db.Text())

    drug_schedule = db.Column(db.String(55))
    drug_type = db.Column(db.String(55))
    dosage = db.Column(db.String(55))
    formulation_types = db.Column(db.String(55))

    price = db.Column(NUMERIC(8, 2), default=0)

    prescription_required = db.Column(db.Boolean(), default=False)

    therapeutic_name = db.Column(db.String(255), nullable=True)

    is_loose = db.Column(db.Boolean(), default=False)
    barcode = db.Column(db.String(13), nullable=True, unique=True)

    brand_id = db.Column(db.ForeignKey('brand.id'), index=True, nullable=False)

    taxes = db.relationship('Tax', back_populates='products', secondary='product_tax')
    tags = db.relationship('Tag', back_populates='products', secondary='product_tag')
    brand = db.relationship('Brand', foreign_keys=[brand_id], uselist=False, back_populates='products')

    stocks = db.relationship('Stock', uselist=True, cascade="all, delete-orphan", lazy='dynamic')
    # distributors = db.relationship('Distributor', back_populates='products', secondary='product_distributor')
    combos = db.relationship('Combo', back_populates='products', secondary='combo_product', lazy='dynamic')
    salts = db.relationship('Salt', back_populates='products', secondary='product_salt', lazy='dynamic')
    product_salts = db.relationship('ProductSalt', lazy='dynamic', back_populates='product')

    @hybrid_property
    def short_code(self):
        return re.sub(r'[AEIOU ]', '', self.name, flags=re.IGNORECASE)[:5]

    @hybrid_property
    def brand_name(self):
        return self.brand.name

    @brand_name.expression
    def brand_name(self):
        return select([Brand.name]).where(Brand.id == self.brand_id).as_scalar()


class Salt(BaseMixin, db.Model, ReprMixin):
    name = db.Column(db.String(127), nullable=False, index=True)
    prescription_required = db.Column(db.Boolean(), default=True)
    usage = db.Column(db.Text(), nullable=True)
    working = db.Column(db.Text(), nullable=True)
    side_effects = db.Column(db.Text(), nullable=True)

    store_id = db.Column(db.ForeignKey('store.id', ondelete='CASCADE'), index=True, nullable=False)

    products = db.relationship('Product', back_populates='salts', secondary='product_salt')
    store = db.relationship('Store', foreign_keys=[store_id], uselist=False)

    UniqueConstraint(name, store_id)


class ProductSalt(BaseMixin, db.Model, ReprMixin):
    __repr_fields__ = ['salt_id', 'product_id']

    unit = db.Column(db.String(25), nullable=True)
    value = db.Column(db.String(25), nullable=True)
    salt_id = db.Column(db.ForeignKey('salt.id'), index=True, nullable=False)
    product_id = db.Column(db.ForeignKey('product.id'), index=True, nullable=False)

    salt = db.relationship('Salt', foreign_keys=[salt_id])
    product = db.relationship('Product', foreign_keys=[product_id])

    UniqueConstraint(salt_id, product_id)

    @hybrid_property
    def store_id(self):
        return self.product.store_id

    @store_id.expression
    def store_id(self):
        return select([Product.store_id]).where(Product.id == self.product_id).as_scalar()


class Stock(BaseMixin, db.Model, ReprMixin):
    __repr_fields__ = ['id', 'purchase_date']

    purchase_amount = db.Column(db.Float(precision=2), nullable=False, default=0)
    selling_amount = db.Column(db.Float(precision=2), nullable=False, default=0)
    units_purchased = db.Column(db.SmallInteger, nullable=False, default=1)
    batch_number = db.Column(db.String(25), nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    is_sold = db.Column(db.Boolean(), default=False, index=True)
    default_stock = db.Column(db.Boolean, default=False, nullable=True)

    distributor_bill_id = db.Column(db.ForeignKey('distributor_bill.id'), nullable=True, index=True)
    product_id = db.Column(db.ForeignKey('product.id'), nullable=False, index=True)
    store_id = db.Column(db.ForeignKey('store.id'), nullable=False, index=True)

    distributor_bill = db.relationship('DistributorBill', single_parent=True, back_populates='purchased_items')
    product = db.relationship('Product', single_parent=True, foreign_keys=[product_id], back_populates='stocks')
    order_items = db.relationship('Item', uselist=True, back_populates='stock', lazy='dynamic')
    store = db.relationship('Store', uselist=False, foreign_keys=[store_id])

    @hybrid_property
    def units_sold(self):

        total_sold = self.order_items.with_entities(func.Sum(Item.quantity)) \
            .filter(Item.stock_id == self.id, Item.stock_adjust.isnot(True)).scalar()
        if total_sold:
            if total_sold >= self.units_purchased and not self.is_sold:
                self.is_sold = True
                db.session.commit()
            return total_sold
        else:
            return 0

    @units_sold.expression
    def units_sold(cls):
        return select([func.coalesce(func.Sum(Item.quantity), 0)])\
            .where(and_(Item.stock_id == cls.id, Item.stock_adjust.isnot(True))).as_scalar()

    @hybrid_property
    def product_name(self):
        return self.product.name

    @product_name.expression
    def product_name(self):
        return select([Product.name]).where(Product.id == self.product_id).as_scalar()

    @hybrid_property
    def expired(self):
        return self.expiry_date is not None and self.expiry_date < datetime.now().date()

    @expired.expression
    def expired(self):
        return and_(or_(self.is_sold.isnot(True)), func.coalesce(self.expiry_date, datetime.now().date())
                    < datetime.now().date()).label('expired')

    @hybrid_property
    def distributor_id(self):
        return self.distributor_bill.distributor_id

    @distributor_id.expression
    def distributor_id(self):
        return select([DistributorBill.distributor_id]).where(
            DistributorBill.id == self.distributor_bill_id).as_scalar()

    @hybrid_property
    def distributor_name(self):
        return self.distributor_bill.distributor.name

    @distributor_name.expression
    def distributor_name(self):
        return select([Distributor.name]).where(and_(DistributorBill.id == self.distributor_bill_id,
                                                     Distributor.id == DistributorBill.distributor_id)).as_scalar()

    @hybrid_property
    def purchase_date(self):
        if self.distributor_bill_id:
            return self.distributor_bill.purchase_date
        return self.created_on

    @purchase_date.expression
    def purchase_date(cls):
        return select([DistributorBill.purchase_date]).where(DistributorBill.id == cls.distributor_bill_id).as_scalar()

    @hybrid_property
    def brand_name(self):
        return self.product.brand.name

    @brand_name.expression
    def brand_name(self):
        return select([Brand.name]).where(and_(Product.id == self.product_id,
                                               Brand.id == Product.brand_id)).as_scalar()


class Combo(BaseMixin, db.Model, ReprMixin):
    name = db.Column(db.String(55), nullable=False, index=True)
    products = db.relationship('Product', back_populates='combos', secondary='combo_product')


class ComboProduct(BaseMixin, db.Model, ReprMixin):
    __repr_fields__ = ['combo_id', 'product_id']

    combo_id = db.Column(db.ForeignKey('combo.id'), index=True)
    product_id = db.Column(db.ForeignKey('product.id'), index=True)

    combo = db.relationship('Combo', foreign_keys=[combo_id])
    product = db.relationship('Product', foreign_keys=[product_id])


class Category(BaseMixin, db.Model, ReprMixin):

    name = db.Column(db.String(55), nullable=False, unique=True)


class ProductCategory(BaseMixin, db.Model):

    product_id = db.Column(db.ForeignKey('product.id'), nullable=False)
    category_id = db.Column(db.ForeignKey('category.id'), nullable=False)

    UniqueConstraint(product_id, category_id)