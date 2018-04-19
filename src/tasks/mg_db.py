from datetime import datetime, timedelta

import requests
import base64
from flask import json
import time
from sqlalchemy import func
from sqlalchemy.exc import InvalidRequestError, OperationalError, IntegrityError

from src.products.models import Product, Brand, Category, ProductCategory
from src import celery, db

URL = 'https://3yp0hp3wsh-dsn.algolia.net/1/indexes/nmsp01_default_products/query'

querystring = {"x-algolia-application-id":"3YP0HP3WSH","x-algolia-api-key":"M2Y3ZWQxOWU3YzY2ZGFhOWM5MmU1NzE0MWM0Mzk2YWM3NDJkMTk0Njk3NDVkZDQ0ZmIxYTIyODIxMjE2Y2RmYnRhZ0ZpbHRlcnM9"}

headers = {
    'Content-Type': "application/json",
    'Cache-Control': "no-cache",
    'Postman-Token': "664e9667-c46f-0f78-5bfa-66381f281cee"
    }

DATE = (datetime.now() + timedelta(days=365)).date()
session = requests.session()
session.proxies = []

payload = "\"params\":\"query={}&hitsPerPage={}&page={}\""

char_set = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
            'v', 'w', 'x', 'y', 'z']


def generate_tasks():

    for i in char_set[12:]:
        for x in char_set:
            for y in char_set:
                autocomplete.apply_async([i + x + y, 0])


@celery.task
def autocomplete(keyword, page=0):
    # resp = requests.request("POST", URL, data='{' + payload.format(keyword, 100, page) + '}', headers=headers, params=querystring)
    #
    # data = resp.json()
    #
    # result = data['hits']
    #
    # if page == 0:
    #     pages = data['nbPages']
    #     print(pages)
    #     if pages:
    #         for y in range(1, pages + 1):
    #             autocomplete.apply_async([keyword, y])
    params = {'productType': 'A', 'n': base64.encodebytes(bytes(keyword, "utf-8")).decode("utf-8"), 'rows': 1000}

    res = requests.request("GET", "https://www.medplusmart.com/ProductSearchAll.mart", params=params)

    if res.status_code == 200 and len(res.json()):
        print(keyword, len(res.json()))
        save_med_products.apply_async([res.json()])
    else:
        print(keyword, res.status_code, res.content)
    # save_products.apply_async([result])
    return True


@celery.task
def save_products(data):
    for i in data:
        try:
            if db.session.query(Product.query.filter(Product.name == i['name']).exists()).scalar():
                return
            b_id = Brand.query.with_entities(Brand.id).filter(Brand.name == i['manufacturer']).limit(1).scalar()
            try:
                if not b_id:
                    b = Brand()
                    b.name = i['manufacturer']
                    db.session.add(b)
                    db.session.commit()
                    b_id = b.id
            except (IntegrityError, OperationalError, InvalidRequestError) as e:
                db.session.rollback()
                print(e)

            product = Product()
            product.name = i['name']
            product.url = i['url']
            product.brand_id = b_id
            product.therapeutic_name = i['genericname']
            product.price = i['price']['INR']['default']
            product.drug_type = i['drug_type']
            product.formulation_types = i['formulation_types']
            product.dosage = i['dosage'] if 'dosage' in i else ""
            db.session.add(product)
            db.session.commit()

            if 'categories_without_path' and i['categories_without_path']:
                for x in i['categories_without_path']:
                    c_id = Category.query.with_entities(Category.id).filter(Category.name == x).limit(1).scalar()
                    try:
                        if not c_id:
                            c = Category()
                            c.name = x
                            db.session.add(c)
                            db.session.commit()
                            c_id = c.id
                        if c_id:
                            pc = ProductCategory()
                            pc.product_id = product.id
                            pc.category_id = c_id
                            db.session.add(pc)
                            db.session.commit()

                    except (IntegrityError, OperationalError, InvalidRequestError) as e:
                        db.session.rollback()
                        print(e)
        except (IntegrityError, OperationalError, InvalidRequestError) as e:
            db.session.rollback()
            print(e)
    pass


@celery.task
def save_med_products(data):
    for i in data:
        if 'productName' not in i:
            continue
        try:
            if db.session.query(Product.query.filter(func.lower(Product.name) == func.lower(i['productName'])).exists()).scalar():
                continue
            b_id = Brand.query.with_entities(Brand.id).filter(func.lower(Brand.name) == func.lower(i['manufacturer'])).limit(1).scalar()
            try:
                print(i['productName'])
                if not b_id:
                    b = Brand()
                    b.name = i['manufacturer']
                    db.session.add(b)
                    db.session.commit()
                    b_id = b.id
            except (IntegrityError, OperationalError, InvalidRequestError) as e:
                db.session.rollback()
                print(e)

            product = Product()
            product.name = i['productName']
            product.brand_id = b_id
            # product.therapeutic_name = i['genericname']
            product.price = i['packSizeMrp']
            # product.drug_type = i['drug_type']
            product.formulation_types = i['productFormName']
            # product.dosage = i['dosage'] if 'dosage' in i else ""
            db.session.add(product)
            db.session.commit()

        except (IntegrityError, OperationalError, InvalidRequestError) as e:
            db.session.rollback()
            print(e)
    pass