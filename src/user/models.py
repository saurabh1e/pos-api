from datetime import datetime

from flask_security import RoleMixin, UserMixin
from sqlalchemy import UniqueConstraint, func, select
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

from src import db, BaseMixin, ReprMixin
from src.orders.models import Order


class UserStore(BaseMixin, db.Model):
    user_id = db.Column(db.ForeignKey('user.id', ondelete='CASCADE'), index=True, nullable=False)
    store_id = db.Column(db.ForeignKey('store.id', ondelete='CASCADE'), index=True, nullable=False)

    user = db.relationship('User', foreign_keys=[user_id])
    store = db.relationship('Store', foreign_keys=[store_id])

    UniqueConstraint(user_id, store_id)


class CustomerAddress(BaseMixin, db.Model, ReprMixin):
    customer_id = db.Column(db.ForeignKey('customer.id'), index=True)
    address_id = db.Column(db.ForeignKey('address.id'), unique=True)

    customer = db.relationship('Customer', foreign_keys=[customer_id])
    address = db.relationship('Address', foreign_keys=[address_id])

    UniqueConstraint(customer_id, address_id)


class Organisation(BaseMixin, db.Model, ReprMixin):
    name = db.Column(db.String(80), unique=True)

    stores = db.relationship('Store', back_populates='organisation', uselist=True,
                             cascade='all, delete-orphan')
    users = db.relationship('User', back_populates='organisation', uselist=True, cascade='all, delete-orphan')


class RegistrationDetail(BaseMixin, db.Model, ReprMixin):
    name = db.Column(db.String(55), nullable=False)
    value = db.Column(db.String(20), nullable=False)

    store_id = db.Column(db.ForeignKey('store.id', ondelete='CASCADE'), index=True)
    store = db.relationship('Store', foreign_keys=[store_id], back_populates='registration_details')


class Store(BaseMixin, db.Model, ReprMixin):
    name = db.Column(db.String(80), unique=False)
    identity = db.Column(db.String(80), unique=False)

    organisation_id = db.Column(db.ForeignKey('organisation.id'), index=True)
    address_id = db.Column(db.ForeignKey('address.id'), unique=True, index=True)
    invoice_number = db.Column(db.Integer, default=0, nullable=False)
    separate_offline_billing = db.Column(db.Boolean, default=False)

    organisation = db.relationship('Organisation', foreign_keys=[organisation_id], back_populates='stores')
    users = db.relationship('User', back_populates='stores', secondary='user_store', lazy='dynamic')
    orders = db.relationship('Order', uselist=True, back_populates='store', lazy='dynamic')
    address = db.relationship('Address', foreign_keys=[address_id], uselist=False)

    registration_details = db.relationship('RegistrationDetail', uselist=True, lazy='dynamic')
    printer_config = db.relationship('PrinterConfig', uselist=False)

    @hybrid_property
    def total_sales(self):
        data = self.orders.with_entities(func.Sum(Order.total), func.Count(Order.id), func.Sum(Order.items_count)) \
            .filter(Order.store_id == self.id, Order.created_on >= datetime.now().date()).all()[0]

        return {'total_sales': data[0], 'total_orders': data[1], 'total_items': str(data[2])}


class UserRole(BaseMixin, db.Model):
    user_id = db.Column(db.ForeignKey('user.id', ondelete='CASCADE'), index=True)
    role_id = db.Column(db.ForeignKey('role.id', ondelete='CASCADE'), index=True)

    user = db.relationship('User', foreign_keys=[user_id])
    role = db.relationship('Role', foreign_keys=[role_id])

    UniqueConstraint(user_id, role_id)


class UserPermission(BaseMixin, db.Model):
    user_id = db.Column(db.ForeignKey('user.id', ondelete='CASCADE'), index=True)
    permission_id = db.Column(db.ForeignKey('permission.id', ondelete='CASCADE'), index=True)

    user = db.relationship('User', foreign_keys=[user_id])
    permission = db.relationship('Permission', foreign_keys=[permission_id])

    UniqueConstraint(user_id, permission_id)


class Role(BaseMixin, RoleMixin, ReprMixin, db.Model):
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    is_hidden = db.Column(db.Boolean(), default=False)

    permissions = db.relationship('Permission', uselist=True, lazy='dynamic', back_populates='role')
    users = db.relationship('User', back_populates='roles', secondary='user_role')


class User(BaseMixin, UserMixin, ReprMixin, db.Model):
    email = db.Column(db.String(127), unique=True, nullable=False)
    password = db.Column(db.String(255), default='', nullable=False)
    name = db.Column(db.String(55), nullable=False)
    mobile_number = db.Column(db.String(20), unique=True, nullable=False)

    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())

    last_login_ip = db.Column(db.String(45))
    current_login_ip = db.Column(db.String(45))
    login_count = db.Column(db.Integer)

    organisation_id = db.Column(db.ForeignKey('organisation.id'), index=True)

    organisation = db.relationship('Organisation', foreign_keys=[organisation_id], back_populates='users')
    roles = db.relationship('Role', back_populates='users', secondary='user_role')
    permissions = db.relationship('Permission', back_populates='users', secondary='user_permission', lazy='dynamic')
    stores = db.relationship('Store', back_populates='users', secondary='user_store', lazy='dynamic')

    @hybrid_property
    def store_ids(self):
        return [i[0] for i in self.stores.with_entities(Store.id).all()]

    @store_ids.expression
    def store_ids(self):
        return select([UserStore.store_id]).where(UserStore.user_id == self.id).label('store_ids').limit(1)

    @hybrid_method
    def has_shop_access(self, shop_id):
        return db.session.query(UserStore.query.filter(UserStore.store_id == shop_id,
                                                       UserStore.user_id == self.id).exists()).scalar()

    @hybrid_method
    def has_permission(self, permission):
        return db.session.query(self.permissions.filter(Permission.name == permission).exists()).scalar()

    @hybrid_property
    def is_owner(self):
        return self.has_role('owner')


class Permission(BaseMixin, db.Model, ReprMixin):
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    type = db.Column(db.String(15), nullable=True)
    is_hidden = db.Column(db.Boolean(), default=False)
    role_id = db.Column(db.ForeignKey('role.id'), nullable=True)

    role = db.relationship('Role', back_populates='permissions', uselist=False)
    users = db.relationship('User', back_populates='permissions', secondary='user_permission')


class Customer(BaseMixin, db.Model, ReprMixin):
    email = db.Column(db.String(55), nullable=True)
    name = db.Column(db.String(55), nullable=False)
    active = db.Column(db.Boolean())
    number = db.Column(db.String(20), nullable=False)
    loyalty_points = db.Column(db.Integer, default=0)
    organisation_id = db.Column(db.ForeignKey('organisation.id'), index=True)

    organisation = db.relationship('Organisation', foreign_keys=[organisation_id])
    addresses = db.relationship('Address', secondary='customer_address')
    orders = db.relationship('Order', uselist=True, lazy='dynamic')
    transactions = db.relationship('CustomerTransaction', uselist=True, lazy='dynamic')

    UniqueConstraint(number, name, organisation_id)

    @hybrid_property
    def total_orders(self):
        return self.orders.with_entities(func.coalesce(func.Count(Order.id), 0)).scalar()

    @hybrid_property
    def total_billing(self):
        return self.orders.with_entities(func.coalesce(func.Sum(Order.total), 0)).scalar()

    @hybrid_property
    def amount_due(self):
        return self.orders.with_entities(func.coalesce(func.Sum(Order.total), 0) -
                                         func.coalesce(func.Sum(Order.amount_paid), 0)).scalar() - \
               self.transactions.with_entities(func.coalesce(func.Sum(CustomerTransaction.amount), 0)).scalar()


class CustomerTransaction(BaseMixin, db.Model, ReprMixin):
    amount = db.Column(db.Float(precision=2), nullable=False, default=0)
    customer_id = db.Column(db.ForeignKey('customer.id'), nullable=False, index=True)
    customer = db.relationship('Customer', foreign_keys=[customer_id])


class Address(BaseMixin, db.Model, ReprMixin):
    name = db.Column(db.Text, nullable=False)
    locality_id = db.Column(db.ForeignKey('locality.id'), index=True)
    locality = db.relationship('Locality', uselist=False)


class Locality(BaseMixin, db.Model, ReprMixin):
    name = db.Column(db.Text, nullable=False)
    city_id = db.Column(db.ForeignKey('city.id'), index=True)

    city = db.relationship('City', uselist=False)

    UniqueConstraint(city_id, name)


class City(BaseMixin, db.Model, ReprMixin):
    name = db.Column(db.Text, nullable=False, unique=True)


class PrinterConfig(BaseMixin, db.Model, ReprMixin):
    header = db.Column(db.Text, nullable=True)
    footer = db.Column(db.Text, nullable=True)

    bill_template = db.Column(db.Text, nullable=True)
    receipt_template = db.Column(db.Text, nullable=True)

    bill_printer_type = db.Column(db.Enum('thermal', 'dot_matrix', 'laser', name='varchar'))
    receipt_printer_type = db.Column(db.Enum('thermal', 'dot_matrix', 'laser', name='varchar'))
    label_printer_type = db.Column(db.Enum('1x1', '2x1', '3x1', '4x1', name='varchar'))

    have_receipt_printer = db.Column(db.Boolean(), default=False)
    have_bill_printer = db.Column(db.Boolean(), default=False)

    store_id = db.Column(db.ForeignKey('store.id'))

    stores = db.relationship('Store', back_populates='printer_config',
                             foreign_keys=[store_id])
