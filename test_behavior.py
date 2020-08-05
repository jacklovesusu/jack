from datetime import datetime, timedelta
import random

import pytest
import mongomock
import pymongo
from bson import ObjectId
from faker import Faker

from app import create_app

random.seed(datetime.now().timestamp())
f = Faker()
Faker.seed(datetime.now().timestamp())


@pytest.fixture
def client():
    app = create_app('testing')

    with app.test_client() as client:
        with app.app_context():
            pass
        yield client


class TestBehavior:

    @mongomock.patch()
    def test_results(self, client):
        db = pymongo.MongoClient().dataCenter
        now = datetime.now().astimezone(client.application.config['TIMEZONE'])
        dates = {
            f.date_time_between_dates(
                now.replace(hour=0, minute=0, second=0, microsecond=0),
                now
            ) for i in range(1000)
        }

        db.activitysessions.insert_many([
            {
                '_id': ObjectId.from_datetime(d),
                'user': ObjectId.from_datetime(d),
            } for d in dates
        ])

        db.playrecords.insert_many([
            {
                '_id': ObjectId.from_datetime(d),
                'user': ObjectId.from_datetime(d),
                'targetType': random.choice([0, 1]),
            } for d in dates
        ])

        db.actions.insert_many([
            {
                '_id': ObjectId.from_datetime(d),
                "user": ObjectId.from_datetime(d),
                "behavior": random.choice([5, 8, 3, 9, 6]),
                "type": random.choice([0, 1]),
            } for d in dates
        ])

        resp = client.get('/api/v1/behavior/results',
                          content_type='application/json')

        assert resp.status_code == 200  # 状态码200，服务器成功处理了请求
        assert resp.is_json

    @mongomock.patch()
    def test_proportion_flase_results(self, client):
        db = pymongo.MongoClient().dataCenter

        t_now = datetime.now().astimezone(client.application.config['TIMEZONE'])
        t_at_zero = t_now.replace(hour=0, minute=0, second=0, microsecond=0)

        past_pro_n = random.randint(0, 30)

        dates = {  # 时间范围
            f.date_time_between_dates(
                t_at_zero - timedelta(days=past_pro_n),
                t_at_zero - timedelta(days=past_pro_n - 1),
            ) for i in range(1000)
        }

        db.proportion.insert_many([
            {
                'type': random.choice([0, 1, 2, 3, 4, 5]),
                'video_type': random.choice([0, 1]),
                'timestamp': ObjectId.from_datetime(d),
                'behavior_type': random.randint(0, 100)
            } for d in dates
        ])

        resp = client.post('/api/v1/behavior/proportion',
                           json={
                               'past_pro_n': random.choice([-100, 25.1, "hello", "(2+5j)"]),
                               'video_types': ['programme', 'shortVideo']
                           })

        assert resp.status_code != 200
        assert resp.is_json

    @mongomock.patch()
    def test_tendency_false_results(self, client):
        db = pymongo.MongoClient().dataCenter

        t_now = datetime.now().astimezone(client.application.config['TIMEZONE'])

        t_at_zero = t_now.replace(hour=0, minute=0, second=0, microsecond=0)

        past_n = random.randint(0, 30)

        dates = {  # 时间范围
            f.date_time_between_dates(
                t_at_zero - timedelta(days=past_n),
                t_at_zero - timedelta(days=past_n - 1),
            ) for i in range(1000)
        }

        db.tendency.insert_many([
            {
                'type': random.choice([0, 1, 2, 3, 4, 5]),
                'video_type': random.choice([0, 1]),
                'timestamp': ObjectId.from_datetime(d),
                'behavior_type': random.randint(0, 100)
            } for d in dates
        ])

        resp = client.post('/api/v1/behavior/tendency',
                           json={
                               'past_n': random.choice([-100, 25.1, "hello", "(2+5j)"]),
                               'video_types': ['programme', 'shortVideo']
                           })

        assert resp.status_code != 200
        assert resp.is_json

    @mongomock.patch()
    def test_proportion_true_results(self, client):
        db = pymongo.MongoClient().dataCenter

        t_now = datetime.now().astimezone(client.application.config['TIMEZONE'])
        t_at_zero = t_now.replace(hour=0, minute=0, second=0, microsecond=0)

        past_pro_n = random.randint(0, 30)

        dates = {  # 时间范围
            f.date_time_between_dates(
                t_at_zero - timedelta(days=past_pro_n),
                t_at_zero - timedelta(days=past_pro_n - 1),
            ) for i in range(1000)
        }

        db.proportion.insert_many([
            {
                'type': random.choice([0, 1, 2, 3, 4, 5]),
                'video_type': random.choice([0, 1]),
                'timestamp': ObjectId.from_datetime(d),
                'behavior_type': random.randint(0, 100)
            } for d in dates
        ])

        resp = client.post('/api/v1/behavior/proportion',
                           json={
                               'past_pro_n': random.choice([0, 7, 15, 30]),
                               'video_types': ['programme', 'shortVideo']
                           })

        assert resp.status_code == 200
        assert resp.is_json

    @mongomock.patch()
    def test_tendency_true_results(self, client):
        db = pymongo.MongoClient().datCenter

        t_now = datetime.now().astimezone(client.application.config['TIMEZONE'])

        t_at_zero = t_now.replace(hour=0, minute=0, second=0, microsecond=0)

        past_n = random.randint(0, 30)

        dates = {  # 时间范围
            f.date_time_between_dates(
                t_at_zero - timedelta(days=past_n),
                t_at_zero - timedelta(days=past_n - 1),
            ) for i in range(1000)
        }

        db.tendency.insert_many([
            {
                'type': random.choice([0, 1, 2, 3, 4, 5]),
                'video_type': random.choice([0, 1]),
                'timestamp': ObjectId.from_datetime(d),
                'behavior_type': random.randint(0, 100)
            } for d in dates
        ])

        resp = client.post('/api/v1/behavior/tendency',
                           json={
                               'past_n': random.choice([0, 7, 15, 30]),
                               'video_types': ['programme', 'shortVideo']
                           })

        assert resp.status_code == 200