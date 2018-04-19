from datetime import datetime

from flask import make_response, jsonify, request
from flask_restful import Resource
from flask_security import auth_token_required, roles_accepted, current_user
from sqlalchemy import func, and_, Date, Text

from src import BaseView, api
from src.products.models import Product, Stock
from .models import Order, Item
from .resources import ItemResource, OrderResource, ItemTaxResource, StatusResource


@api.register()
class OrderView(BaseView):
    @classmethod
    def get_resource(cls):
        return OrderResource


@api.register()
class ItemView(BaseView):
    @classmethod
    def get_resource(cls):
        return ItemResource


@api.register()
class ItemTaxView(BaseView):
    @classmethod
    def get_resource(cls):
        return ItemTaxResource


@api.register()
class StatusView(BaseView):
    @classmethod
    def get_resource(cls):
        return StatusResource


class OrderStatResource(Resource):
    method_decorators = [roles_accepted('admin', 'owner', 'staff'), auth_token_required]

    model = Order

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

        orders = self.model.query.join(Item, and_(Item.order_id == self.model.id)) \
            .filter(self.model.retail_shop_id.in_(shops), self.model.created_on.between(from_date, to_date))

        total_orders, total_sales, total_items, total_quantity, total_due = \
            orders.with_entities(func.Count(func.Distinct(self.model.id)), func.sum(self.model.total),
                                 func.Count(func.Distinct(Item.product_id)), func.sum(Item.quantity),
                                 func.Sum(self.model.amount_due)).all()[0]

        orders = self.model.query\
            .with_entities(func.count(func.Distinct(self.model.id)), func.sum(self.model.total),
                           func.avg(self.model.total),
                           func.cast(func.date_trunc(collection_type, func.cast(self.model.created_on, Date)), Text)
                           .label('dateWeek')) \
            .filter(self.model.created_on.between(from_date, to_date), self.model.retail_shop_id.in_(shops)) \
            .group_by('dateWeek').order_by('dateWeek').all()

        items = Item.query.join(self.model, and_(self.model.id == Item.order_id)) \
            .filter(self.model.retail_shop_id.in_(shops))

        max_sold_items = items.join(Product, and_(Product.id == Item.product_id)) \
            .with_entities(func.Sum(Item.quantity), Product.name, ) \
            .filter(self.model.created_on.between(from_date, to_date)) \
            .group_by(Item.product_id, Product.name).order_by(-func.Sum(Item.quantity)).limit(10).all()

        max_profitable_items = items.join(Product, and_(Product.id == Item.product_id)) \
            .join(Stock, and_(Stock.id == Item.stock_id)) \
            .with_entities(func.Sum((Item.unit_price - Stock.purchase_amount) * Item.quantity), Product.name, ) \
            .filter(self.model.created_on.between(from_date, to_date)) \
            .group_by(Item.product_id, Product.name) \
            .order_by(-func.Sum((Item.unit_price - Stock.purchase_amount) * Item.quantity)) \
            .limit(10).all()

        return make_response(jsonify(dict(total_orders=total_orders, total_sales=total_sales,
                                          total_quantity=total_quantity, max_sold_items=max_sold_items,
                                          max_profitable_items=max_profitable_items,
                                          total_items=str(total_items), orders=orders)), 200)


api.add_resource(OrderStatResource, '/order_stats/', endpoint='order_stats')
