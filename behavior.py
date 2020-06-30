用户行为分析
from flask import request, current_app, jsonify, render_template,redirect,url_for
from datetime import datetime, timedelta
from bson import ObjectId
from collections import defaultdict

from . import api
from app.model import get_db


@api.route('/behavior/results', methods=['GET'])
def results():

    db = get_db()['invitationCat']

    t_now = datetime.now().astimezone(current_app.config['TIMEZONE'])
    t_at_zero = t_now.replace(hour=0, minute=0, second=0, microsecond=0)

    id_lowwer_bound = ObjectId.from_datetime(t_at_zero)
    id_upper_bound = ObjectId.from_datetime(t_now)

    #用户总数
    all_users = len(list(db.users.aggregate([
        {'$match':{'userType':{'$in':['entity','other']}}}
])))

    #观看
    play_user_list = list(db.actions.aggregate([
            {'$match': {'behavior': 0,
                        'deletable':{'$ne':True},
                        '_id': {
                                '$gte': id_lowwer_bound,
                                '$lte': id_upper_bound},
                                }},
            {'$project': {'user': 1}}
        ]))
    play_user = len(set([str(pl['user']) for pl in play_user_list]))


    #分享
    share_user_list = list(db.actions.aggregate([
            {'$match': {'behavior': 6,
                        'deletable':{'$ne':True},
                      '_id': {
                                '$gte': id_lowwer_bound,
                                '$lte': id_upper_bound},
                                }},
            {'$project': {'user': 1}},
        ]))
    share_user = len(set([str(sh['user']) for sh in share_user_list]))


    #评论
    comment_user_list = list(db.comments.aggregate([
            {'$match': {'status': '1',
                        '_id': {
                            '$gte': id_lowwer_bound,
                            '$lte': id_upper_bound }
                            }},
            {'$project': {'user': 1}},
        ]))
    comment_user = len(set([str(c['user']) for c in comment_user_list]))


    #弹幕
    danmaku_user_list = list(db.danmakus.aggregate([
            {'$match': {'status': '1',
                        '_id': {
                            '$gte': id_lowwer_bound,
                            '$lte': id_upper_bound}}},
            {'$project': {'user': 1}},
        ]))
    danmaku_user = len(set([str(d['user']) for d in danmaku_user_list]))


    #收藏
    follow_user_list = list(db.follows.aggregate([
            {'$match': {'type': {'$in': [1, 2, 3]},
                        '_id': {
                            '$gte': id_lowwer_bound,
                            '$lte': id_upper_bound}}},
            {'$project': {'user': 1}},
        ]))
    follow_user = len(set([str(f['user']) for f in follow_user_list]))


    #点赞
    preference_user_list = list(db.preferences.aggregate([
            {'$match': {'state': 1,
                        '_id': {
                            '$gte': id_lowwer_bound,
                            '$lte': id_upper_bound}}},
            {'$project': {'user': 1}},
        ]))
    preference_user = len(set([str(pr['user']) for pr in preference_user_list]))


    #日活跃用户
    oneday_active_users_list = play_user_list + comment_user_list + danmaku_user_list + \
                            follow_user_list + preference_user_list + share_user_list
    oneday_active_users = len(set([str(one['user']) for one in oneday_active_users_list]))


    try:
        oneday_play_active = round((play_user / oneday_active_users) * 100, 2)
        oneday_active = round(float((oneday_active_users - play_play) / oneday_active_users) * 100, 2)

        return jsonify({
            'all_users':all_users,
            'oneday_active_users':oneday_active_users,
            'oneday_play_active':oneday_play_active,
            'oneday_active':oneday_active
            })
    except:
        return jsonify({"Error:": "division by zero"})



@api.route('/behavior/proportion_results', methods=['POST'])
def proportion_results():

    params = request.get_json()
    past_pro_n = params['past_pro_n']#必选
    video_type = params['video_type']

    video_types = ['programme', 'shortVideo', 'all']

    #异常输入数据检测
    if type(past_pro_n) != int or past_pro_n < 0:
        return jsonify({"Error:": "TypeError"}), 500
    if video_type not in video_types:
        return jsonify({"Error": "video_type_Error"}), 500

    db = get_db()['invitationCat']
    t_now = datetime.now().astimezone(current_app.config['TIMEZONE'])
    t_at_zero = t_now.replace(hour=0, minute=0, second=0, microsecond=0)

    if past_pro_n > 0:
        id_lowwer_bound = ObjectId.from_datetime(
            t_at_zero - timedelta(days=int(past_pro_n)+100))
        id_upper_bound = ObjectId.from_datetime(t_at_zero)
    else:
        id_lowwer_bound = ObjectId.from_datetime(t_at_zero)
        id_upper_bound = ObjectId.from_datetime(t_now)


    if video_type == 'programme':
        video_play_flag = 0
        video_comment_flag = '0'
        video_dan_flag = '0'
        video_fol_flag = 0
        video_pre_flag = 0
        video_share_flag = 0
    elif video_type == 'shortVideo':
        video_play_flag = 1
        video_comment_flag = '2'
        video_dan_flag = '1'
        video_fol_flag = 3
        video_pre_flag = 3
        video_share_flag = 1

    else:
        video_play_flag = {'$in':[0,1]}
        video_comment_flag = {'$in':['0','2']}
        video_dan_flag = {'$in':['0','1']}
        video_fol_flag = {'$in':[1,3]}
        video_pre_flag = {'$in':[0,3]}
        video_share_flag = {'$in':[0,1]}


    pastpron_user_plays_list = list(db.actions.aggregate([
            {'$match': {'behavior': 0,
                        'type':video_play_flag,
                        'deletable':{'$ne':True},
                        '_id': {
                                '$gte': id_lowwer_bound,
                                '$lte': id_upper_bound},
                                }},
            {'$project': {'user': 1}}
        ]))
    pastpron_user_plays = len(set([str(p['user']) for p in pastpron_user_plays_list]))
        # 过去n天观看


    pastpron_user_danmakus_list = list(db.danmakus.aggregate([
            {'$match': {'status': '1',
                        'type':video_dan_flag,
                        '_id': {
                                '$gte': id_lowwer_bound,
                                '$lte': id_upper_bound}}},
            {'$project': {'user': 1}}
        ]))
    pastpron_user_danmakus = len(set([str(d['user']) for d in pastpron_user_danmakus_list]))
          # 过去n天弹幕


    pastpron_user_shares_list = list(db.actions.aggregate([
            {'$match': {'behavior': 6,
                        'type':video_share_flag,
                        'deletable':{'$ne':True},
                        '_id': {
                                '$gte': id_lowwer_bound,
                                '$lte': id_upper_bound},
                                }},
            {'$project': {'user': 1}}
        ]))
    pastpron_user_shares = len(set([str(s['user']) for s in pastpron_user_shares_list]))
        # 过去n天分享


    pastpron_user_comments_list = list(db.comments.aggregate([
            {'$match': {'status': '1',
                        'type':video_comment_flag,
                        '_id': {
                                '$gte': id_lowwer_bound,
                                '$lte': id_upper_bound}}},
            {'$project': {'user': 1}}
        ]))
    pastpron_user_comments = len(set([str(c['user']) for c in pastpron_user_comments_list]))
        # 过去n天评论


    pastpron_user_follows_list = list(db.follows.aggregate([
            {'$match': {'state': 1,
                        'type':video_fol_flag,
                        '_id': {
                                '$gte': id_lowwer_bound,
                                '$lte': id_upper_bound}}},
            {'$project': {'user': 1}}
        ]))
    pastpron_user_follows = len(set([str(f['user']) for f in pastpron_user_follows_list]))
        # 过去n天收藏


    pastpron_user_preferences_list = list(db.preferences.aggregate([
            {'$match': {'state': 1,
                        'type':video_pre_flag,
                        '_id': {
                                '$gte': id_lowwer_bound,
                                '$lte': id_upper_bound}}},
            {'$project': {'user': 1}}
        ]))
    pastpron_user_preferences = len(set([str(pr['user']) for pr in pastpron_user_preferences_list]))
        # 过去n天点赞


    all_pro_nums_list = pastpron_user_plays_list + pastpron_user_comments_list + pastpron_user_danmakus_list + \
                    pastpron_user_follows_list + pastpron_user_preferences_list + pastpron_user_shares_list


    all_pro_nums = len(set([str(a['user']) for a in all_pro_nums_list]))

    try:
        plays_pro_n = round(float(pastpron_user_plays / all_pro_nums) * 100, 2)
        comments_pro_n = round(float(pastpron_user_comments / all_pro_nums) * 100, 2)
        danmakus_pro_n = round(float(pastpron_user_danmakus / all_pro_nums) * 100, 2)
        follows_pro_n = round(float(pastpron_user_follows / all_pro_nums) * 100, 2)
        preferences_pro_n = round(float(pastpron_user_preferences / all_pro_nums) * 100, 2)
        shares_pro_n = round(float(pastpron_user_shares / all_pro_nums) * 100, 2)

        return jsonify({
            'plays_pro_n': plays_pro_n,
            'comments_pro_n': comments_pro_n,
            'danmakus_pro_n': danmakus_pro_n,
            'follows_pro_n': follows_pro_n,
            'preferences_pro_n': preferences_pro_n,
            'shares_pro_n': shares_pro_n
        })

    except:
        return jsonify({"Error:":"division by zero"})


@api.route('/behavior/tendency_results',  methods=['POST'])
def tendency_results():

    params = request.get_json()
    past_n = params['past_n']
    video_type = params['video_type']

    video_types = ['programme', 'shortVideo', 'all']

    if type(past_n) != int or past_n <= 0:
        return jsonify({"Error:": "TypeError"}), 500
    if video_type not in video_types:
        return jsonify({"Error": "video_type_Error"}), 500

    if video_type == 'programme':
        video_play_flag = 0
        video_comment_flag = '0'
        video_dan_flag = '0'
        video_fol_flag = 0
        video_pre_flag = 0
        video_share_flag = 0
    elif video_type == 'shortVideo':
        video_play_flag = 1
        video_comment_flag = '2'
        video_dan_flag = '1'
        video_fol_flag = 3
        video_pre_flag = 3
        video_share_flag = 1
    else:
        video_play_flag = {'$in':[0,1]}
        video_comment_flag = {'$in':['0','2']}
        video_dan_flag = {'$in':['0','1']}
        video_fol_flag = {'$in':[1,3]}
        video_pre_flag = {'$in':[0,3]}
        video_share_flag = {'$in':[0,1]}


    db = get_db()['invitationCat']
    t_now = datetime.now().astimezone(current_app.config['TIMEZONE'])
    t_at_zero = t_now.replace(hour=0, minute=0, second=0, microsecond=0)

    res_play = dict()
    res_comment = dict()
    res_danmaku = dict()
    res_follow = dict()
    res_preference = dict()
    res_share = dict()
    res_all_tend = dict()
    result = defaultdict(int)

    for days_ago in range(int(past_n)):
        pastn_user_plays_list = list(db.actions.aggregate([
                {'$match': {'behavior': 0,
                            'type':video_play_flag,
                            'deletable':{'$ne':True},
                            '_id': {
                                    '$gte': ObjectId.from_datetime(
                                                t_at_zero - timedelta(days=int(past_n)+100)),
                                    '$lte': ObjectId.from_datetime(
                                                t_at_zero - timedelta(days=int(past_n-1)))},
                                    }},
                {'$project': {'user': 1}}
            ]))
        res_play[days_ago] = len(set([str(p['user']) for p in pastn_user_plays_list]))
        # 过去第n天观看


        pastn_user_comments_list = list(db.comments.aggregate([
                {'$match': {'status': '1',
                            'type':video_comment_flag,
                            '_id': {
                                    '$gte': ObjectId.from_datetime(
                                                t_at_zero - timedelta(days=int(past_n))),
                                    '$lte': ObjectId.from_datetime(
                                                t_at_zero - timedelta(days=int(past_n-1)))},
                                                }},
                {'$project': {'user': 1}},
            ]))
        res_comment[days_ago] = len(set([str(c['user']) for c in pastn_user_comments_list]))
        # 过去第n天评论


        pastn_user_danmakus_list = list(db.danmakus.aggregate([
                {'$match': {'status': '1',
                            'type':video_dan_flag,
                            '_id': {
                                    '$gte': ObjectId.from_datetime(
                                                t_at_zero - timedelta(days=int(past_n))),
                                    '$lte': ObjectId.from_datetime(
                                                t_at_zero - timedelta(days=int(past_n-1)))},
                                                }},
                {'$project': {'user': 1}}
            ]))
        res_danmaku[days_ago] = len(set([str(d['user']) for d in pastn_user_danmakus_list]))
        # 过去第n天弹幕


        pastn_user_follows_list = list(db.follows.aggregate([
                {'$match': {'state': 1,
                            'type':video_fol_flag,
                            '_id': {
                                    '$gte': ObjectId.from_datetime(
                                                t_at_zero - timedelta(days=int(past_n))),
                                    '$lte': ObjectId.from_datetime(
                                                t_at_zero - timedelta(days=int(past_n-1)))},
                                                }},
                {'$project': {'user': 1}}
            ]))
        res_follow[days_ago] = len(set([str(f['user']) for f in pastn_user_follows_list]))
        # 过去第n天收藏


        pastn_user_preferences_list = list(db.preferences.aggregate([
                {'$match': {'state': 1,
                                'type':video_pre_flag,
                            '_id': {
                                    '$gte': ObjectId.from_datetime(
                                                t_at_zero - timedelta(days=int(past_n))),
                                    '$lte': ObjectId.from_datetime(
                                                t_at_zero - timedelta(days=int(past_n-1)))},
                                                }},
                {'$project': {'user': 1}},
            ]))
        res_preference[days_ago] = len(set([str(pr['user']) for pr in pastn_user_preferences_list]))
        # 过去第n天点赞


        pastn_user_shares_list = list(db.actions.aggregate([
                {'$match': {'behavior': 6,
                            'type':video_share_flag,
                            'deletable':{'$ne':True},
                            '_id': {
                                    '$gte': ObjectId.from_datetime(
                                                t_at_zero - timedelta(days=int(past_n))),
                                    '$lte': ObjectId.from_datetime(
                                                t_at_zero - timedelta(days=int(past_n-1)))},
                                                }},
                {'$project': {'user': 1}}
            ]))
        res_share[days_ago] = len(set([str(s['user']) for s in pastn_user_shares_list]))
        # 过去第n天分享


        all_tend_nums_list = pastn_user_plays_list + pastn_user_comments_list + pastn_user_danmakus_list +\
         pastn_user_follows_list + pastn_user_preferences_list + pastn_user_shares_list

        res_all_tend[days_ago] = len(set([str(al['user']) for al in pastn_user_plays_list]))


        try:
            plays_n = round(float(res_play[days_ago] / res_all_tend[days_ago]) * 100, 2)
            comments_n = round(float(res_comment[days_ago] / res_all_tend[days_ago]) * 100, 2)
            danmakus_n = round(float(res_danmaku[days_ago] / res_all_tend[days_ago]) * 100, 2)
            follows_n = round(float(res_follow[days_ago] / res_all_tend[days_ago]) * 100, 2)
            preferences_n = round(float(res_preference[days_ago] / res_all_tend[days_ago]) * 100, 2)
            shares_n = round(float(res_share[days_ago] / res_all_tend[days_ago]) * 100, 2)

            result[days_ago][plays_n] = plays_n
            result[days_ago][comments_n] = comments_n
            result[days_ago][danmakus_n] = danmakus_n
            result[days_ago][follows_n] = follows_n
            result[days_ago][preferences_n] = preferences_n
            result[days_ago][shares_n] = shares_n

        except:
            return jsonify({"Error:":"division by zero"})

    for days_ago in range(int(past_n)):
        return jsonif({
            'plays_n':result[days_ago][plays_n],
            'comments_n':result[days_ago][comments_n],
            'danmakus_n':result[days_ago][danmakus_n],
            'follows_n':result[days_ago][follows_n],
            'preferences_n':result[days_ago][preferences_n],
            'shares_n':result[days_ago][shares_n],
        })
