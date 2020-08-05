"""Analyze behavior activity"""
from datetime import datetime, timedelta
from collections import defaultdict
from flask import request, current_app, jsonify
from bson import ObjectId

from . import api
from app.model import get_tdb

def dedupe(items, key=None):
    """
        Remove duplicate values
    """
    seen = set()
    for item in items:
        val = item if key is None else key(item)
        if val not in seen:
            yield item
            seen.add(val)

def time_lowwer():
    """
        id_time_lowwer_bound
    """
    t_now = datetime.now().astimezone(current_app.config['TIMEZONE'])
    t_at_zero = t_now.replace(hour=0, minute=0, second=0, microsecond=0)
    id_lowwer_bound = ObjectId.from_datetime(t_at_zero)
    return id_lowwer_bound

def pt_time_lowwer(past_n):
    """
        pt_time_lowwer_bound
    """
    t_now = datetime.now().astimezone(current_app.config['TIMEZONE'])
    t_at_zero = t_now.replace(hour=0, minute=0, second=0, microsecond=0)
    id_lowwer_bound = ObjectId.from_datetime(
        t_at_zero - timedelta(days=past_n))
    return id_lowwer_bound

def pt_time_upper(past_n):
    """
        pt_time_upper_bound
    """
    t_now = datetime.now().astimezone(current_app.config['TIMEZONE'])
    t_at_zero = t_now.replace(hour=0, minute=0, second=0, microsecond=0)
    id_upper_bound = ObjectId.from_datetime(
        t_at_zero - timedelta(days=past_n-1))
    return id_upper_bound

def pt_value(pt_list):
    """
    The value of proportion and tendency
    """
    result = None
    for tem in pt_list:
        for behavior in tem.values():
            result = behavior
    return result

@api.route('/behavior/results', methods=['GET'])
def results():
    """
    oneday user activity
    """
    db_ = get_tdb()

    #注册用户总数
    all_users = len(list(db_.ActivitySessions.find({})))

    #日观看用户
    play_user_list = list(db_.playRecords.find({
        '_id': {'$gte': time_lowwer()},
    }, {
        'user': 1, '_id': 0
    }))
    play_user = len(list(dedupe(
        play_user_list,
        key=lambda play_user_list: (play_user_list['user'])
    )))

    #日评论用户
    comment_user_list = list(db_.Actions.find({
        '_id': {'$gte': time_lowwer()},
        'behavior': 5,
    }, {
        'user': 1, '_id': 0
    }))

    #日弹幕用户
    danmaku_user_list = list(db_.Actions.find({
        '_id': {'$gte': time_lowwer()},
        'behavior': 8,
    }, {
        'user': 1, '_id': 0
    }))

    #日收藏用户
    follow_user_list = list(db_.Actions.find({
        '_id': {'$gte': time_lowwer()},
        'behavior': 3,
    }, {
        'user': 1, '_id':0
    }))

    #日点赞用户
    preference_user_list = list(db_.Actions.find({
        '_id': {'$gte': time_lowwer()},
        'behavior': 9,
    }, {
        'user': 1, '_id': 0
    }))

    #日分享用户
    share_user_list = list(db_.Actions.find({
        '_id': {'$gte': time_lowwer()},
        'behavior': 6,
    }, {
        'user': 1, '_id': 0
    }))

    #日活跃用户（去重）
    oneday_active_users_list = play_user_list + \
                               comment_user_list + \
                               danmaku_user_list + \
                               follow_user_list + \
                               preference_user_list + \
                               share_user_list
    oneday_active_users = len(list(dedupe(
        oneday_active_users_list,
        key=lambda oneday_active_users_list: (oneday_active_users_list['user'])
    )))

    #日互动用户（去重，不包括观看）
    oneday_behave_users_list = comment_user_list + \
                               danmaku_user_list + \
                               follow_user_list + \
                               preference_user_list + \
                               share_user_list
    oneday_behave_users = len(list(dedupe(
        oneday_behave_users_list,
        key=lambda oneday_behave_users_list: (oneday_behave_users_list['user'])
    )))
    try:
        #日观看活跃度，日互动活跃度
        oneday_play_active = round(
            (play_user / oneday_active_users) * 100, 2)
        oneday_behave_active = round(float(
            oneday_behave_users / oneday_active_users) * 100, 2)

        return jsonify({
            'all_users':all_users,
            'oneday_active_users':oneday_active_users,
            'oneday_play_active':oneday_play_active,
            'oneday_behave_active':oneday_behave_active,
            })
    except ZeroDivisionError:
        return jsonify({"Error:": "division by zero"})

@api.route('/behavior/proportion', methods=['POST'])
def proportion_results():
    """
        user proportion activity
    """
    db_ = get_tdb()

    past_pro_n = request.get_json()['past_pro_n']
    video_types = set(request.get_json()['video_types'])

    if isinstance(past_pro_n, int) is False or past_pro_n < 0:
        return jsonify({"Error:": "TypeError"}), 500

    if 'programme' in video_types:
        video_types.remove('programme')
        video_types.add(0)
    if 'shortVideo' in video_types:
        video_types.remove('shortVideo')
        video_types.add(1)

    #观看
    pastpron_plays_list = list(db_.proportion.find({
        'behave_type': 0,
        'timestamp': {
            '$gte': pt_time_lowwer(past_pro_n),
            '$lt': pt_time_upper(past_pro_n)},
        'video_type': {'$in': list(video_types)}
    }, {
        'behave_ratio': 1, '_id': 0
    }))
    plays_pro_n = pt_value(pastpron_plays_list)

    #评论
    pastpron_comments_list = list(db_.proportion.find({
        'behave_type': 1,
        'timestamp': {
            '$gte': pt_time_lowwer(past_pro_n),
            '$lt': pt_time_upper(past_pro_n)},
        'video_type': {'$in': list(video_types)}
    }, {
        'behave_ratio': 1, '_id': 0
    }))
    comments_pro_n = pt_value(pastpron_comments_list)

    #弹幕
    pastpron_danmakus_list = list(db_.proportion.find({
        'behave_type': 2,
        'timestamp': {
            '$gte': pt_time_lowwer(past_pro_n),
            '$lt': pt_time_upper(past_pro_n)},
        'video_type': {'$in': list(video_types)}
    }, {
        'behave_ratio': 1, '_id': 0
    }))
    danmakus_pro_n = pt_value(pastpron_danmakus_list)

    #收藏
    pastpron_follows_list = list(db_.proportion.find({
        'behave_type': 3,
        'timestamp': {
            '$gte': pt_time_lowwer(past_pro_n),
            '$lt': pt_time_upper(past_pro_n)},
        'video_type': {'$in': list(video_types)}
    }, {
        'behave_ratio': 1, '_id': 0
    }))
    follows_pro_n = pt_value(pastpron_follows_list)

    #点赞
    pastpron_preferences_list = list(db_.proportion.find({
        'behave_type': 4,
        'timestamp': {
            '$gte': pt_time_lowwer(past_pro_n),
            '$lt': pt_time_upper(past_pro_n)},
        'video_type': {'$in': list(video_types)}
    }, {
        'behave_ratio': 1, '_id': 0
    }))
    preferences_pro_n = pt_value(pastpron_preferences_list)

    #分享
    pastpron_shares_list = list(db_.proportion.find({
        'behave_type': 5,
        'timestamp': {
            '$gte': pt_time_lowwer(past_pro_n),
            '$lt': pt_time_upper(past_pro_n)},
        'video_type': {'$in': list(video_types)}
    }, {
        'behave_ratio': 1, '_id': 0
    }))
    shares_pro_n = pt_value(pastpron_shares_list)

    return jsonify({
        'plays_pro_n': plays_pro_n,
        'comments_pro_n': comments_pro_n,
        'danmakus_pro_n': danmakus_pro_n,
        'follows_pro_n': follows_pro_n,
        'preferences_pro_n': preferences_pro_n,
        'shares_pro_n': shares_pro_n,
    })

@api.route('/behavior/tendency', methods=['POST'])
def tendency_results():
    """
        user tendency activity
    """
    db_ = get_tdb()

    past_n = request.get_json()['past_n']
    video_types = set(request.get_json()['video_types'])

    if isinstance(past_n, int) is False or past_n < 0:
        return jsonify({"Error:": "TypeError"}), 500

    if 'programme' in video_types:
        video_types.remove('programme')
        video_types.add(0)
    elif 'shortVideo' in video_types:
        video_types.remove('shortVideo')
        video_types.add(1)
    if past_n == 0:
        result = {
            '0':defaultdict(int)
            }
    elif past_n == 7:
        result = {
            '0':defaultdict(int),
            '1':defaultdict(int),
            '2':defaultdict(int),
            '3':defaultdict(int),
            '4':defaultdict(int),
            '5':defaultdict(int),
            '6':defaultdict(int),
            }
    elif past_n == 15:
        result = {
            '0':defaultdict(int),
            '1':defaultdict(int),
            '2':defaultdict(int),
            '3':defaultdict(int),
            '4':defaultdict(int),
            '5':defaultdict(int),
            '6':defaultdict(int),
            '7':defaultdict(int),
            '8':defaultdict(int),
            '9':defaultdict(int),
            '10':defaultdict(int),
            '11':defaultdict(int),
            '12':defaultdict(int),
            '13':defaultdict(int),
            '14':defaultdict(int),
            }
    else:
        result = {
            '0':defaultdict(int),
            '1':defaultdict(int),
            '2':defaultdict(int),
            '3':defaultdict(int),
            '4':defaultdict(int),
            '5':defaultdict(int),
            '6':defaultdict(int),
            '7':defaultdict(int),
            '8':defaultdict(int),
            '9':defaultdict(int),
            '10':defaultdict(int),
            '11':defaultdict(int),
            '12':defaultdict(int),
            '13':defaultdict(int),
            '14':defaultdict(int),
            '15':defaultdict(int),
            '16':defaultdict(int),
            '17':defaultdict(int),
            '18':defaultdict(int),
            '19':defaultdict(int),
            '20':defaultdict(int),
            '21':defaultdict(int),
            '22':defaultdict(int),
            '23':defaultdict(int),
            '24':defaultdict(int),
            '25':defaultdict(int),
            '26':defaultdict(int),
            '27':defaultdict(int),
            '28':defaultdict(int),
            '29':defaultdict(int),
            }

    for day in range(past_n):
        #观看
        pastn_plays_list = list(db_.tendency.find({
            'behave_type': 0,
            'timestamp': {
                '$gte': pt_time_lowwer(day),
                '$lt': pt_time_upper(day)},
            'video_type': {'$in': list(video_types)}
        }, {
            'behave_ratio': 1, '_id': 0
        }))
        result[str(day)]['plays'] = pt_value(pastn_plays_list)

        #评论
        pastn_comments_list = list(db_.tendency.find({
            'behave_type': 1,
            'timestamp': {
                '$gte': pt_time_lowwer(day),
                '$lt': pt_time_upper(day)},
            'video_type': {'$in': list(video_types)}
        }, {
            'behave_ratio': 1, '_id': 0
        }))
        result[str(day)]['comments'] = pt_value(pastn_comments_list)

        #弹幕
        pastn_danmakus_list = list(db_.tendency.find({
            'behave_type': 2,
            'timestamp': {
                '$gte': pt_time_lowwer(day),
                '$lt': pt_time_upper(day)},
            'video_type': {'$in': list(video_types)}
        }, {
            'behave_ratio': 1, '_id': 0
        }))
        result[str(day)]['danmakus'] = pt_value(pastn_danmakus_list)

        #收藏
        pastn_follows_list = list(db_.tendency.find({
            'behave_type': 3,
            'timestamp': {
                '$gte': pt_time_lowwer(day),
                '$lt': pt_time_upper(day)},
            'video_type': {'$in': list(video_types)}
        }, {
            'behave_ratio': 1, '_id': 0
        }))
        result[str(day)]['follows'] = pt_value(pastn_follows_list)

        #点赞
        pastn_preferences_list = list(db_.tendency.find({
            'behave_type': 4,
            'timestamp': {
                '$gte': pt_time_lowwer(day),
                '$lt': pt_time_upper(day)},
            'video_type': {'$in': list(video_types)}
        }, {
            'behave_ratio': 1, '_id': 0
        }))
        result[str(day)]['preferences'] = pt_value(pastn_preferences_list)

        #分享
        pastn_shares_list = list(db_.tendency.find({
            'behave_type': 5,
            'timestamp': {
                '$gte': pt_time_lowwer(day),
                '$lt': pt_time_upper(day)},
            'video_type': {'$in': list(video_types)}
        }, {
            'behave_ratio': 1, '_id': 0
        }))
        result[str(day)]['shares'] = pt_value(pastn_shares_list)

    return jsonify({'result': result})
