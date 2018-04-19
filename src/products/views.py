from datetime import datetime

from flask import make_response, jsonify, request
from flask_restful import Resource
from flask_security import current_user, roles_accepted, auth_token_required
from sqlalchemy import func, cast, Date, Text, Integer

from src import BaseView, AssociationView
from src import api
from .models import Stock, DistributorBill
from .resources import BrandResource, DistributorBillResource, DistributorResource, ProductResource, \
    ProductTaxResource, StockResource, TaxResource, TagResource, ComboResource, SaltResource, \
    ProductTagResource, ProductSaltResource


@api.register()
class ProductView(BaseView):
    @classmethod
    def get_resource(cls):
        return ProductResource


@api.register()
class TagView(BaseView):
    @classmethod
    def get_resource(cls):
        return TagResource


@api.register()
class StockView(BaseView):
    @classmethod
    def get_resource(cls):
        return StockResource


@api.register()
class DistributorView(BaseView):
    @classmethod
    def get_resource(cls):
        return DistributorResource


@api.register()
class DistributorBillView(BaseView):
    @classmethod
    def get_resource(cls):
        return DistributorBillResource


@api.register()
class TaxView(BaseView):
    @classmethod
    def get_resource(cls):
        return TaxResource


@api.register()
class BrandView(BaseView):
    @classmethod
    def get_resource(cls):
        return BrandResource


@api.register()
class ComboView(BaseView):
    @classmethod
    def get_resource(cls):
        return ComboResource


@api.register()
class SaltView(BaseView):
    @classmethod
    def get_resource(cls):
        return SaltResource


@api.register()
class ProductTaxAssociationView(AssociationView):
    @classmethod
    def get_resource(cls):
        return ProductTaxResource


@api.register()
class ProductTagAssociationView(AssociationView):
    @classmethod
    def get_resource(cls):
        return ProductTagResource


@api.register()
class ProductSaltAssociationView(AssociationView):
    @classmethod
    def get_resource(cls):
        return ProductSaltResource


class StockStatResource(Resource):
    method_decorators = [roles_accepted('admin', 'owner', 'staff'), auth_token_required]

    model = Stock

    def get(self):
        shops = request.args.getlist('__retail_shop_id__in')
        for shop in shops:
            if not current_user.has_shop_access(shop):
                return make_response(jsonify({'message': 'Access Forbidden'}), 403)
        if len(shops) == 1:
            shops = shops[0].split(',')
        from_date = datetime.strptime(request.args['__created_on__gte'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
        to_date = datetime.strptime(request.args['__created_on__lte'], '%Y-%m-%dT%H:%M:%S.%fZ').date()

        days = (to_date - from_date).days

        collection_type = 'day'
        if days > 28:
            collection_type = 'week'
            if days > 360:
                collection_type = 'month'

        stock_metrics = Stock.query \
            .with_entities(cast(func.coalesce(func.Sum(self.model.purchase_amount * self.model.units_purchased), 0), Integer),
                           cast(func.coalesce(func.Sum(self.model.selling_amount * self.model.units_sold), 0), Integer),
                           cast(func.coalesce(
                               func.Sum((self.model.units_purchased - self.model.units_sold) * self.model.purchase_amount)
                               .filter(self.model.expired == True), 0), Integer),
                           func.cast(func.date_trunc(collection_type, func.cast(self.model.created_on, Date)), Text)
                           .label('dateWeek')) \
            .filter(self.model.created_on.between(from_date, to_date),
                    self.model.retail_shop_id.in_(shops)).order_by('dateWeek').group_by('dateWeek').limit(100).all()

        distributor_metrics = DistributorBill.query \
            .with_entities(cast(func.coalesce(func.Sum(DistributorBill.bill_amount), 0), Integer), DistributorBill.distributor_name,
                           ) \
            .filter(DistributorBill.created_on.between(from_date, to_date),
                    DistributorBill.retail_shop_id.in_(shops)) \
            .group_by(DistributorBill.distributor_id) \
            .limit(100).all()

        return make_response(jsonify(dict(stock_metrics=stock_metrics, distributor_metrics=distributor_metrics)), 200)


api.add_resource(StockStatResource, '/stock_stats/', endpoint='stock_stats')
