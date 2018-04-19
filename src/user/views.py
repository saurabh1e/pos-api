from datetime import datetime

from flask import request, jsonify, make_response, redirect
from flask_restful import Resource
from flask_security.utils import verify_and_update_password, login_user
from flask_security import auth_token_required, roles_accepted, current_user
from sqlalchemy import func, and_, cast, Date, Text, Float

from src import BaseView, AssociationView
from src import api
from src.orders.models import Order
from src.utils.methods import List
from .models import User, Customer, CustomerTransaction
from .resources import UserResource, UserRoleResource, RoleResource, \
    OrganisationResource, StoreResource, UserStoreResource, CustomerResource, AddressResource, \
    LocalityResource, CityResource, CustomerAddressResource, CustomerTransactionResource, \
    UserPermissionResource, PermissionResource, PrinterConfigResource, RegistrationDetailResource


@api.register()
class UserView(BaseView):
    @classmethod
    def get_resource(cls):
        return UserResource


@api.register()
class RoleView(BaseView):
    api_methods = [List]

    @classmethod
    def get_resource(cls):
        return RoleResource


@api.register()
class PermissionView(BaseView):
    api_methods = [List]

    @classmethod
    def get_resource(cls):
        return PermissionResource


@api.register()
class UserRoleAssociationView(AssociationView):
    @classmethod
    def get_resource(cls):
        return UserRoleResource


@api.register()
class UserPermissionAssociationView(AssociationView):
    @classmethod
    def get_resource(cls):
        return UserPermissionResource


@api.register()
class StoreView(BaseView):
    @classmethod
    def get_resource(cls):
        return StoreResource


@api.register()
class OrganisationView(BaseView):
    @classmethod
    def get_resource(cls):
        return OrganisationResource


@api.register()
class UserStoreAssociationView(AssociationView):
    @classmethod
    def get_resource(cls):
        return UserStoreResource


class UserLoginResource(Resource):
    model = User

    def post(self):

        if request.json:
            data = request.json

            user = self.model.query.filter(self.model.email == data['email']).first()
            if user and verify_and_update_password(data['password'], user) and login_user(user):

                return jsonify({'id': user.id, 'authentication_token': user.get_auth_token()})
            else:
                return make_response(jsonify({'meta': {'code': 403}}), 403)

        else:
            data = request.form
            user = self.model.query.filter(self.model.email == data['email']).first()
            if user and verify_and_update_password(data['password'], user) and login_user(user):
                return make_response(redirect('/admin/', 302))
            else:
                return make_response(redirect('/api/v1/login', 403))


api.add_resource(UserLoginResource, '/login/', endpoint='login')


@api.register()
class CustomerView(BaseView):
    @classmethod
    def get_resource(cls):
        return CustomerResource


@api.register()
class AddressView(BaseView):
    @classmethod
    def get_resource(cls):
        return AddressResource


@api.register()
class LocalityView(BaseView):
    @classmethod
    def get_resource(cls):
        return LocalityResource


@api.register()
class CityView(BaseView):
    @classmethod
    def get_resource(cls):
        return CityResource


@api.register()
class CustomerAddressView(AssociationView):
    @classmethod
    def get_resource(cls):
        return CustomerAddressResource


@api.register()
class CustomerTransactionView(BaseView):
    @classmethod
    def get_resource(cls):
        return CustomerTransactionResource


@api.register()
class PrinterConfigView(BaseView):
    @classmethod
    def get_resource(cls):
        return PrinterConfigResource


@api.register()
class RegistrationDetailView(BaseView):
    @classmethod
    def get_resource(cls):
        return RegistrationDetailResource


class CustomerStatResource(Resource):
    method_decorators = [roles_accepted('admin', 'owner', 'staff'), auth_token_required]

    model = Customer

    def get(self):

        shops = request.args.getlist('__retail_shop_id__in')
        for shop in shops:
            if not current_user.has_shop_access(shop):
                return make_response(jsonify({'message': 'Access Forbidden'}), 403)

        brand_id = request.args.get('__retail_brand_id__equal')
        if len(shops) == 1:
            shops = shops[0].split(',')
        from_date = datetime.strptime(request.args['__created_on__gte'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
        to_date = datetime.strptime(request.args['__created_on__lte'], '%Y-%m-%dT%H:%M:%S.%fZ').date()

        days = (to_date - from_date).days

        collection_type = 'day'
        if days > 56:
            collection_type = 'week'
            if days > 360:
                collection_type = 'month'

        new_customers = self.model.query.join(Order, and_(Order.customer_id == self.model.id)) \
            .with_entities(func.Count(func.Distinct(Order.customer_id)), func.Sum(Order.total), func.avg(Order.total),
                           func.cast(func.date_trunc(collection_type, func.cast(self.model.created_on, Date)), Text)
                           .label('dateWeek')
                           ) \
            .filter(and_(self.model.created_on.between(from_date, to_date), Order.created_on.between(from_date, to_date),
                    Order.retail_shop_id.in_(shops))).group_by('dateWeek').order_by('dateWeek')\
            .having(func.Count(func.Distinct(Order.id)) > 0).all()

        return_customers = self.model.query.join(Order, and_(Order.customer_id == self.model.id)) \
            .with_entities(func.Count(func.Distinct(Order.customer_id)), func.Sum(Order.total), func.avg(Order.total),
                           func.cast(func.date_trunc(collection_type, func.cast(self.model.created_on, Date)), Text)
                           .label('dateWeek')
                           ) \
            .filter(and_(self.model.created_on.between(from_date, to_date), Order.created_on.between(from_date, to_date))) \
            .having(func.Count(func.Distinct(Order.id)) > 1).group_by('dateWeek').order_by('dateWeek').all()

        old_customers = Order.query.join(Customer, and_(Customer.id == Order.customer_id)) \
            .with_entities(func.Count(func.Distinct(Order.customer_id)), func.Sum(Order.total), func.avg(Order.total),
                           func.cast(func.date_trunc(collection_type, func.cast(Order.created_on, Date)), Text)
                           .label('dateWeek')
                           ) \
            .filter(and_(Customer.created_on <= from_date, Order.created_on.between(from_date, to_date),
                    Order.retail_shop_id.in_(shops), Customer.retail_brand_id == brand_id))\
            .group_by('dateWeek').order_by('dateWeek') \
            .having(func.Count(func.Distinct(Order.id)) > 0).all()

        total_due = self.model.query.outerjoin(Order, and_(Order.customer_id == self.model.id)) \
            .outerjoin(CustomerTransaction, and_(CustomerTransaction.customer_id == self.model.id)) \
            .with_entities(func.coalesce(cast(func.Sum(Order.total), Float), 0.0) -
                           func.coalesce(cast(func.Sum(Order.amount_paid), Float), 0.0)
                           - func.coalesce(cast(func.Sum(CustomerTransaction.amount), Float), 0.0)) \
            .filter(self.model.retail_brand_id == brand_id).scalar()

        top_customers = self.model.query.outerjoin(Order, and_(Order.customer_id == self.model.id)) \
            .with_entities(func.Count(func.Distinct(Order.id)), self.model.name) \
            .filter(self.model.retail_brand_id == brand_id, Order.created_on.between(from_date, to_date),
                    Order.retail_shop_id.in_(shops)).group_by(Order.customer_id, self.model.name) \
            .order_by(-func.Count(func.Distinct(Order.id))).limit(10).all()

        top_billed_customers = self.model.query.outerjoin(Order, and_(Order.customer_id == self.model.id)) \
            .with_entities(func.Sum(Order.total), self.model.name) \
            .filter(self.model.retail_brand_id == brand_id, Order.created_on.between(from_date, to_date),
                    Order.retail_shop_id.in_(shops)).group_by(Order.customer_id, self.model.name) \
            .order_by(-func.Sum(Order.total)).limit(10).all()

        return make_response(jsonify(dict(new_customers=new_customers, return_customers=return_customers,
                                          old_customers=old_customers, top_billed_customers=top_billed_customers,
                                          total_due=total_due, top_customers=top_customers)), 200)


api.add_resource(CustomerStatResource, '/customer_stats/', endpoint='customer_stats')
