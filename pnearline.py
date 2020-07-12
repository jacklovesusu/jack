from flask import request, current_app, jsonify, render_template
from datetime import datetime, timedelta
from bson import ObjectId
from collections import defaultdict

from . import api
from app.model import get_db


@api.route('/test/tendency', methods=['GET'])
def test_tendency():
    db = get_db()['invitationCat']
    
    result = {
        '0': defaultdict(int),
        '1': defaultdict(int),
        '2': defaultdict(int),
        '3': defaultdict(int),
        '4': defaultdict(int),
        '5': defaultdict(int),
        '6': defaultdict(int),
        '7': defaultdict(int),
        '8': defaultdict(int),
        '9': defaultdict(int),
        '10': defaultdict(int),
        '11': defaultdict(int),
        '12': defaultdict(int),
        '13': defaultdict(int),
        '14': defaultdict(int),
        '15': defaultdict(int),
        '16': defaultdict(int),
        '17': defaultdict(int),
        '18': defaultdict(int),
        '19': defaultdict(int),
        '20': defaultdict(int),
        '21': defaultdict(int),
        '22': defaultdict(int),
        '23': defaultdict(int),
        '24': defaultdict(int),
        '25': defaultdict(int),
        '26': defaultdict(int),
        '27': defaultdict(int),
        '28': defaultdict(int),
        '29': defaultdict(int),
    }
    
    t_now = datetime.now().astimezone(current_app.config['TIMEZONE'])
    t_at_zero = t_now.replace(hour=3, minute=0, second=0, microsecond=0)
    
    for day in range(30):
        days_ago = str(day)
        
        id_lowwer_bound = ObjectId.from_datetime(
            t_at_zero - timedelta(days=day)
        )
        id_upper_bound = ObjectId.from_datetime(
            t_at_zero - timedelta(days=day - 1)
        )
        
        if day == 0:
            id_upper_bound = ObjectId.from_datetime(t_now)
        
        # 观看
        for behave in range(3):
            if behave == 0:
                video_pl_flag = 0
                video_com_flag = '0'
                video_dan_flag = '0'
                video_fol_flag = 0
                video_pre_flag = 0
                video_sha_flag = 0
            if behave == 1:
                video_play_flag = 1
                video_comment_flag = '2'
                video_dan_flag = '1'
                video_fol_flag = 3
                video_pre_flag = 3
                video_sha_flag = 1
            if behave == 2:
                video_pl_flag = {'$in': [0, 1]}
                video_com_flag = {'$in': ['0', '2']}
                video_dan_flag = {'$in': ['0', '1']}
                video_fol_flag = {'$in': [1, 3]}
                video_pre_flag = {'$in': [0, 3]}
                video_sha_flag = {'$in': [0, 1]}
            
            # 观看
            users_cur = db.users.find({'userType': 'entity'},
                                      {'_id': 1})
            pastn_user_plays_list = list(db.actions.find({
                'user': {'$in': [u['_id'] for u in users_cur]},
                '_id': {'$gte': id_lowwer_bound, '$lte': id_upper_bound},
                'behavior': 0,
                'type': video_pl_flag,
                'deletable': {'$ne': True},
            }, {
                'user': 1
            }))
            result[days_ago]['plays'] = len(set([str(p['user']) for p in pastn_user_plays_list]))
            
            # 评论
            users_cur = db.users.find({'userType': 'entity'},
                                      {'_id': 1})
            pastn_user_comments_list = list(db.comments.find({
                'user': {'$in': [u['_id'] for u in users_cur]},
                '_id': {'$gte': id_lowwer_bound, '$lte': id_upper_bound},
                'status': '1',
                'type': video_com_flag,
            }, {
                'user': 1
            }))
            result[days_ago]['comments'] = len(set([str(c['user']) for c in pastn_user_comments_list]))
            
            # 弹幕
            users_cur = db.users.find({'userType': 'entity'},
                                      {'_id': 1})
            pastn_user_danmakus_list = list(db.danmakus.find({
                'user': {'$in': [u['_id'] for u in users_cur]},
                '_id': {'$gte': id_lowwer_bound, '$lte': id_upper_bound},
                'status': '1',
                'type': video_dan_flag,
            }, {
                'user': 1
            }))
            result[days_ago]['danmakus'] = len(set([str(d['user']) for d in pastn_user_danmakus_list]))
            
            # 收藏
            users_cur = db.users.find({'userType': 'entity'},
                                      {'_id': 1})
            pastn_user_follows_list = list(db.follows.find({
                'user': {'$in': [u['_id'] for u in users_cur]},
                '_id': {'$gte': id_lowwer_bound, '$lte': id_upper_bound},
                'state': 1,
                'type': video_fol_flag,
            }, {
                'user': 1
            }))
            result[days_ago]['follows'] = len(set([str(f['user']) for f in pastn_user_follows_list]))
            
            # 点赞
            users_cur = db.users.find({'userType': 'entity'},
                                      {'_id': 1})
            pastn_user_preferences_list = list(db.preferences.find({
                'user': {'$in': [u['_id'] for u in users_cur]},
                '_id': {'$gte': id_lowwer_bound, '$lte': id_upper_bound},
                'state': 1,
                'type': video_pre_flag,
            }, {
                'user': 1
            }))
            result[days_ago]['preferences'] = len(set([str(pr['user']) for pr in pastn_user_preferences_list]))
            
            # 分享
            users_cur = db.users.find({'userType': 'entity'},
                                      {'_id': 1})
            pastn_user_shares_list = list(db.actions.find({
                'user': {'$in': [u['_id'] for u in users_cur]},
                '_id': {'$gte': id_lowwer_bound, '$lte': id_upper_bound},
                'behavior': 6,
                'type': video_sha_flag,
                'deletable': {'$ne': True},
            }, {
                'user': 1
            }))
            result[days_ago]['shares'] = len(set([str(s['user']) for s in pastn_user_shares_list]))
            
            if behave == 0:
                all_user_list = pastn_user_plays_list + pastn_user_comments_list + pastn_user_danmakus_list + \
                                pastn_user_follows_list + pastn_user_preferences_list + pastn_user_shares_list
                result[days_ago]['programme'] = len(set([str(u['user']) for u in all_user_list]))
                if result[days_ago]['programme'] != 0:
                    result[days_ago]['pastn_play_programme'] = round(
                        float(result[days_ago]['plays'] / result[days_ago]['programme']) * 100, 2)
                    result[days_ago]['pastn_comment_programme'] = round(
                        float(result[days_ago]['comments'] / result[days_ago]['programme']) * 100, 2)
                    result[days_ago]['pastn_danmaku_programme'] = round(
                        float(result[days_ago]['danmakus'] / result[days_ago]['programme']) * 100, 2)
                    result[days_ago]['pastn_follow_programme'] = round(
                        float(result[days_ago]['follows'] / result[days_ago]['programme']) * 100, 2)
                    result[days_ago]['pastn_preference_programme'] = round(
                        float(result[days_ago]['preferences'] / result[days_ago]['programme']) * 100, 2)
                    result[days_ago]['pastn_share_programme'] = round(
                        float(result[days_ago]['shares'] / result[days_ago]['programme']) * 100, 2)
                else:
                    result[days_ago]['pastn_play_programme'] = 0
                    result[days_ago]['pastn_comment_programme'] = 0
                    result[days_ago]['pastn_danmaku_programme'] = 0
                    result[days_ago]['pastn_follow_programme'] = 0
                    result[days_ago]['pastn_preference_programme'] = 0
                    result[days_ago]['pastn_share_programme'] = 0
            if behave == 1:
                all_user_list = pastn_user_plays_list + pastn_user_comments_list + pastn_user_danmakus_list + \
                                pastn_user_follows_list + pastn_user_preferences_list + pastn_user_shares_list
                result[days_ago]['shortvideo'] = len(set([str(u['user']) for u in all_user_list]))
                if result[days_ago]['shortvideo'] != 0:
                    result[days_ago]['pastn_play_shortVideo'] = round(
                        float(result[days_ago]['plays'] / result[days_ago]['shortvideo']) * 100, 2)
                    result[days_ago]['pastn_comment_shortVideo'] = round(
                        float(result[days_ago]['comments'] / result[days_ago]['shortvideo']) * 100, 2)
                    result[days_ago]['pastn_danmaku_shortVideo'] = round(
                        float(result[days_ago]['danmakus'] / result[days_ago]['shortvideo']) * 100, 2)
                    result[days_ago]['pastn_follow_shortVideo'] = round(
                        float(result[days_ago]['follows'] / result[days_ago]['shortvideo']) * 100, 2)
                    result[days_ago]['pastn_preference_shortVideo'] = round(
                        float(result[days_ago]['preferences'] / result[days_ago]['shortvideo']) * 100, 2)
                    result[days_ago]['pastn_share_shortVideo'] = round(
                        float(result[days_ago]['shares'] / result[days_ago]['shortvideo']) * 100, 2)
                else:
                    result[days_ago]['pastn_play_shortVideo'] = 0
                    result[days_ago]['pastn_comment_shortVideo'] = 0
                    result[days_ago]['pastn_danmaku_shortVideo'] = 0
                    result[days_ago]['pastn_follow_shortVideo'] = 0
                    result[days_ago]['pastn_preference_shortVideo'] = 0
                    result[days_ago]['pastn_share_shortVideo'] = 0
            if behave == 2:
                all_user_list = pastn_user_plays_list + pastn_user_comments_list + pastn_user_danmakus_list + \
                                pastn_user_follows_list + pastn_user_preferences_list + pastn_user_shares_list
                result[days_ago]['all'] = len(set([str(u['user']) for u in all_user_list]))
                if result[days_ago]['all'] != 0:
                    result[days_ago]['pastn_play_all'] = round(
                        float(result[days_ago]['plays'] / result[days_ago]['all']) * 100, 2)
                    result[days_ago]['pastn_comment_all'] = round(
                        float(result[days_ago]['comments'] / result[days_ago]['all']) * 100, 2)
                    result[days_ago]['pastn_danmaku_all'] = round(
                        float(result[days_ago]['danmakus'] / result[days_ago]['all']) * 100, 2)
                    result[days_ago]['pastn_follow_all'] = round(
                        float(result[days_ago]['follows'] / result[days_ago]['all']) * 100, 2)
                    result[days_ago]['pastn_preference_all'] = round(
                        float(result[days_ago]['preferences'] / result[days_ago]['all']) * 100, 2)
                    result[days_ago]['pastn_share_all'] = round(
                        float(result[days_ago]['shares'] / result[days_ago]['all']) * 100, 2)
                else:
                    result[days_ago]['pastn_play_all'] = 0
                    result[days_ago]['pastn_comment_all'] = 0
                    result[days_ago]['pastn_danmaku_all'] = 0
                    result[days_ago]['pastn_follow_all'] = 0
                    result[days_ago]['pastn_preference_all'] = 0
                    result[days_ago]['pastn_share_all'] = 0
    
    db.tendency.remove({})
    
    for day in range(30):
        for type in range(6):
            for video_type in range(3):
                days_ago = str(day)
                if type == 0 and video_type == 0:
                    db.tendency.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 0 and video_type == 1:
                    db.tendency.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 0 and video_type == 2:
                    db.tendency.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 1 and video_type == 0:
                    db.tendency.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 1 and video_type == 1:
                    db.tendency.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 1 and video_type == 2:
                    db.tendency.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 2 and video_type == 0:
                    db.tendency.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 2 and video_type == 1:
                    db.tendency.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 2 and video_type == 2:
                    db.tendency.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 3 and video_type == 0:
                    db.tendency.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 3 and video_type == 1:
                    db.tendency.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 3 and video_type == 2:
                    db.tendency.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 4 and video_type == 0:
                    db.tendency.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 4 and video_type == 1:
                    db.tendency.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 4 and video_type == 2:
                    db.tendency.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 5 and video_type == 0:
                    db.tendency.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 5 and video_type == 1:
                    db.tendency.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 5 and video_type == 2:
                    db.tendency.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
    
    return jsonify({"result": result})


@api.route('/test/proportion', methods=['GET'])
def test_proportion():
    db = get_db()['invitationCat']
    
    result = {
        '0': defaultdict(int),
        '7': defaultdict(int),
        '15': defaultdict(int),
        '30': defaultdict(int),
    }
    
    t_now = datetime.now().astimezone(current_app.config['TIMEZONE'])
    t_at_zero = t_now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    for day in [0, 7, 15, 30]:
        days_ago = str(day)
        
        id_lowwer_bound = ObjectId.from_datetime(
            t_at_zero - timedelta(days=day)
        )
        
        if day == 0:
            id_lowwer_bound = ObjectId.from_datetime(t_at_zero)
        
        # 观看
        for behave in range(3):
            if behave == 0:
                video_pl_flag = 0
                video_com_flag = '0'
                video_dan_flag = '0'
                video_fol_flag = 0
                video_pre_flag = 0
                video_sha_flag = 0
            if behave == 1:
                video_play_flag = 1
                video_comment_flag = '2'
                video_dan_flag = '1'
                video_fol_flag = 3
                video_pre_flag = 3
                video_sha_flag = 1
            if behave == 2:
                video_pl_flag = {'$in': [0, 1]}
                video_com_flag = {'$in': ['0', '2']}
                video_dan_flag = {'$in': ['0', '1']}
                video_fol_flag = {'$in': [1, 3]}
                video_pre_flag = {'$in': [0, 3]}
                video_sha_flag = {'$in': [0, 1]}
            
            # 观看
            users_cur = db.users.find({'userType': 'entity'},
                                      {'_id': 1})
            pastn_user_plays_list = list(db.actions.find({
                'user': {'$in': [u['_id'] for u in users_cur]},
                '_id': {'$gte': id_lowwer_bound},
                'behavior': 0,
                'type': video_pl_flag,
                'deletable': {'$ne': True},
            }, {
                'user': 1
            }))
            result[days_ago]['plays'] = len(set([str(p['user']) for p in pastn_user_plays_list]))
            
            # 评论
            users_cur = db.users.find({'userType': 'entity'},
                                      {'_id': 1})
            pastn_user_comments_list = list(db.comments.find({
                'user': {'$in': [u['_id'] for u in users_cur]},
                '_id': {'$gte': id_lowwer_bound},
                'status': '1',
                'type': video_com_flag,
            }, {
                'user': 1
            }))
            result[days_ago]['comments'] = len(set([str(c['user']) for c in pastn_user_comments_list]))
            
            # 弹幕
            users_cur = db.users.find({'userType': 'entity'},
                                      {'_id': 1})
            pastn_user_danmakus_list = list(db.danmakus.find({
                'user': {'$in': [u['_id'] for u in users_cur]},
                '_id': {'$gte': id_lowwer_bound},
                'status': '1',
                'type': video_dan_flag,
            }, {
                'user': 1
            }))
            result[days_ago]['danmakus'] = len(set([str(d['user']) for d in pastn_user_danmakus_list]))
            
            # 收藏
            users_cur = db.users.find({'userType': 'entity'},
                                      {'_id': 1})
            pastn_user_follows_list = list(db.follows.find({
                'user': {'$in': [u['_id'] for u in users_cur]},
                '_id': {'$gte': id_lowwer_bound},
                'state': 1,
                'type': video_fol_flag,
            }, {
                'user': 1
            }))
            result[days_ago]['follows'] = len(set([str(f['user']) for f in pastn_user_follows_list]))
            
            # 点赞
            users_cur = db.users.find({'userType': 'entity'},
                                      {'_id': 1})
            pastn_user_preferences_list = list(db.preferences.find({
                'user': {'$in': [u['_id'] for u in users_cur]},
                '_id': {'$gte': id_lowwer_bound},
                'state': 1,
                'type': video_pre_flag,
            }, {
                'user': 1
            }))
            result[days_ago]['preferences'] = len(set([str(pr['user']) for pr in pastn_user_preferences_list]))
            
            # 分享
            users_cur = db.users.find({'userType': 'entity'},
                                      {'_id': 1})
            pastn_user_shares_list = list(db.actions.find({
                'user': {'$in': [u['_id'] for u in users_cur]},
                '_id': {'$gte': id_lowwer_bound},
                'behavior': 6,
                'type': video_sha_flag,
                'deletable': {'$ne': True},
            }, {
                'user': 1
            }))
            result[days_ago]['shares'] = len(set([str(s['user']) for s in pastn_user_shares_list]))
            
            if behave == 0:
                all_user_list = pastn_user_plays_list + pastn_user_comments_list + pastn_user_danmakus_list + \
                                pastn_user_follows_list + pastn_user_preferences_list + pastn_user_shares_list
                result[days_ago]['programme'] = len(set([str(u['user']) for u in all_user_list]))
                if result[days_ago]['programme'] != 0:
                    result[days_ago]['pastn_play_programme'] = round(
                        float(result[days_ago]['plays'] / result[days_ago]['programme']) * 100, 2)
                    result[days_ago]['pastn_comment_programme'] = round(
                        float(result[days_ago]['comments'] / result[days_ago]['programme']) * 100, 2)
                    result[days_ago]['pastn_danmaku_programme'] = round(
                        float(result[days_ago]['danmakus'] / result[days_ago]['programme']) * 100, 2)
                    result[days_ago]['pastn_follow_programme'] = round(
                        float(result[days_ago]['follows'] / result[days_ago]['programme']) * 100, 2)
                    result[days_ago]['pastn_preference_programme'] = round(
                        float(result[days_ago]['preferences'] / result[days_ago]['programme']) * 100, 2)
                    result[days_ago]['pastn_share_programme'] = round(
                        float(result[days_ago]['shares'] / result[days_ago]['programme']) * 100, 2)
                else:
                    result[days_ago]['pastn_play_programme'] = 0
                    result[days_ago]['pastn_comment_programme'] = 0
                    result[days_ago]['pastn_danmaku_programme'] = 0
                    result[days_ago]['pastn_follow_programme'] = 0
                    result[days_ago]['pastn_preference_programme'] = 0
                    result[days_ago]['pastn_share_programme'] = 0
            if behave == 1:
                all_user_list = pastn_user_plays_list + pastn_user_comments_list + pastn_user_danmakus_list + \
                                pastn_user_follows_list + pastn_user_preferences_list + pastn_user_shares_list
                result[days_ago]['shortvideo'] = len(set([str(u['user']) for u in all_user_list]))
                if result[days_ago]['shortvideo'] != 0:
                    result[days_ago]['pastn_play_shortVideo'] = round(
                        float(result[days_ago]['plays'] / result[days_ago]['shortvideo']) * 100, 2)
                    result[days_ago]['pastn_comment_shortVideo'] = round(
                        float(result[days_ago]['comments'] / result[days_ago]['shortvideo']) * 100, 2)
                    result[days_ago]['pastn_danmaku_shortVideo'] = round(
                        float(result[days_ago]['danmakus'] / result[days_ago]['shortvideo']) * 100, 2)
                    result[days_ago]['pastn_follow_shortVideo'] = round(
                        float(result[days_ago]['follows'] / result[days_ago]['shortvideo']) * 100, 2)
                    result[days_ago]['pastn_preference_shortVideo'] = round(
                        float(result[days_ago]['preferences'] / result[days_ago]['shortvideo']) * 100, 2)
                    result[days_ago]['pastn_share_shortVideo'] = round(
                        float(result[days_ago]['shares'] / result[days_ago]['shortvideo']) * 100, 2)
                else:
                    result[days_ago]['pastn_play_shortVideo'] = 0
                    result[days_ago]['pastn_comment_shortVideo'] = 0
                    result[days_ago]['pastn_danmaku_shortVideo'] = 0
                    result[days_ago]['pastn_follow_shortVideo'] = 0
                    result[days_ago]['pastn_preference_shortVideo'] = 0
                    result[days_ago]['pastn_share_shortVideo'] = 0
            if behave == 2:
                all_user_list = pastn_user_plays_list + pastn_user_comments_list + pastn_user_danmakus_list + \
                                pastn_user_follows_list + pastn_user_preferences_list + pastn_user_shares_list
                result[days_ago]['all'] = len(set([str(u['user']) for u in all_user_list]))
                if result[days_ago]['all'] != 0:
                    result[days_ago]['pastn_play_all'] = round(
                        float(result[days_ago]['plays'] / result[days_ago]['all']) * 100, 2)
                    result[days_ago]['pastn_comment_all'] = round(
                        float(result[days_ago]['comments'] / result[days_ago]['all']) * 100, 2)
                    result[days_ago]['pastn_danmaku_all'] = round(
                        float(result[days_ago]['danmakus'] / result[days_ago]['all']) * 100, 2)
                    result[days_ago]['pastn_follow_all'] = round(
                        float(result[days_ago]['follows'] / result[days_ago]['all']) * 100, 2)
                    result[days_ago]['pastn_preference_all'] = round(
                        float(result[days_ago]['preferences'] / result[days_ago]['all']) * 100, 2)
                    result[days_ago]['pastn_share_all'] = round(
                        float(result[days_ago]['shares'] / result[days_ago]['all']) * 100, 2)
                else:
                    result[days_ago]['pastn_play_all'] = 0
                    result[days_ago]['pastn_comment_all'] = 0
                    result[days_ago]['pastn_danmaku_all'] = 0
                    result[days_ago]['pastn_follow_all'] = 0
                    result[days_ago]['pastn_preference_all'] = 0
                    result[days_ago]['pastn_share_all'] = 0
    
    db.proportion.remove({})
    
    for day in [0, 7, 15, 30]:
        for type in range(6):
            for video_type in range(3):
                days_ago = str(day)
                
                if type == 0 and video_type == 0:
                    db.proportion.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 0 and video_type == 1:
                    db.proportion.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_shortVideo'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 0 and video_type == 2:
                    db.proportion.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_play_all'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 1 and video_type == 0:
                    db.proportion.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_comment_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 1 and video_type == 1:
                    db.proportion.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_comment_shortVideo'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 1 and video_type == 2:
                    db.proportion.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_comment_all'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 2 and video_type == 0:
                    db.proportion.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_danmaku_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 2 and video_type == 1:
                    db.proportion.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_danmaku_shortVideo'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 2 and video_type == 2:
                    db.proportion.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_danmaku_all'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 3 and video_type == 0:
                    db.proportion.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_follow_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 3 and video_type == 1:
                    db.proportion.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_follow_shortVideo'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 3 and video_type == 2:
                    db.proportion.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_follow_all'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                
                if type == 4 and video_type == 0:
                    db.proportion.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_preference_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 4 and video_type == 1:
                    db.proportion.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_preference_shortVideo'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 4 and video_type == 2:
                    db.proportion.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_preference_all'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 5 and video_type == 0:
                    db.proportion.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_share_programme'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 5 and video_type == 1:
                    db.proportion.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_share_shortVideo'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
                if type == 5 and video_type == 2:
                    db.proportion.insert_many([{
                        'type': type,
                        'video_type': video_type,
                        'behave_ratio': result[days_ago]['pastn_share_all'],
                        'timestamp': ObjectId.from_datetime(t_now - timedelta(days=day))
                    }])
    
    return jsonify({"result": result})


