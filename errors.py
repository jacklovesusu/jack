"""
    The errors of client
"""
import re
from collections import defaultdict, Counter
from datetime import datetime
from flask import jsonify, current_app, request
from bson import ObjectId

from app.model import get_ldb
from app.exceptions import InvalidData, NotImplemented
from . import api


@api.errorhandler(InvalidData)
def invalid_data_handler(e):
    response = jsonify({'error': 'invalid data', 'message': e.args[0]})
    response.status_code = 400

    return response


@api.errorhandler(NotImplemented)
def not_implemented_handler(e):
    response = jsonify({'message': 'interface not implemented'})
    response.status_code = 400

    return response


@api.route('/error/client/count', methods=['post'])
def client_count():
    """
        The errors of client:
        equal is count play_errors and init_errors
    """
    db_ = get_ldb()

    start_date = request.get_json()['start_date']
    end_date = request.get_json()['end_date']
    typ = request.get_json()['typ']

    start_time = datetime.fromisoformat(start_date).astimezone(
        current_app.config['TIMEZONE'])
    end_time = datetime.fromisoformat(end_date).astimezone(
        current_app.config['TIMEZONE'])

    play_error_count = db_.playrecords.count_documents({
        '_id': {'$gte': ObjectId.from_datetime(start_time),
                '$lte': ObjectId.from_datetime(end_time)},
        'loadingDatas.playType': 5,
        'platform': typ,
        'isBenchData': {'$ne': True},
        })

    init_error_list = list(db_.initrecords.find({
        '_id': {'$gte': ObjectId.from_datetime(start_time),
                '$lte': ObjectId.from_datetime(end_time)},
        'type': {'$exists': True},
        }, {
            'userAgent': 1, '_id':0
            }))

    init_error_count = 0
    for init in init_error_list:
        if re.split('[/ ]', init['userAgent'].strip())[2] == typ:
            init_error_count += 1


    result = play_error_count + init_error_count

    return jsonify({
        'count':result
    })

@api.route('/error/client/device', methods=['post'])
def client_device():
    """
        The errors of client device(Android, iOS...):
        equal is count play_errors and init_errors
    """
    db_ = get_ldb()

    params = request.get_json()
    current_app.logger.warning(params)
    start_date = params['start_date']
    end_date = params['end_date']
    lim_n = params['lim_n']

    start_time = datetime.fromisoformat(start_date).astimezone(
        current_app.config['TIMEZONE'])
    end_time = datetime.fromisoformat(end_date).astimezone(
        current_app.config['TIMEZONE'])

    play_error_list = list(db_.playrecords.find({
        '_id': {'$gte': ObjectId.from_datetime(start_time),
                '$lte': ObjectId.from_datetime(end_time)},
        'loadingDatas.playType': 5,
        'userAgent': {'$ne': True},
        'isBenchData': {'$ne': True},
        }, {
            'userAgent': 1, '_id':0
            }))
    play_result = []
    play_error_result = [re.split('[/ ]', pl['userAgent'].strip()) for pl in play_error_list]
    for pr_ in play_error_result:
        if len(pr_) == 4:
            play_result.append('Window/'+pr_[-1])
        else:
            play_result.append(pr_[-1])

    init_error_list = list(db_.initrecords.find({
        '_id': {'$gte': ObjectId.from_datetime(start_time),
                '$lte': ObjectId.from_datetime(end_time)},
        'userAgent': {'$ne': True},
        'type': {'$exists': True},
        }, {
            'userAgent': 1, '_id':0
            }))

    init_result = []
    init_error_result = [re.split('[/ ]', init['userAgent'].strip()) for init in init_error_list]
    for ini in init_error_result:
        if len(ini) == 4:
            play_result.append('Window/'+ini[-1])
        else:
            play_result.append(ini[-1])

    result_list = play_result + init_result

    str_list = Counter([re.split('[- /]', k.strip())[0] for k in result_list])

    res = sorted(str_list.items(), key=lambda kv: kv[1], reverse=True)[:lim_n]

    result = defaultdict(dict)
    for r in res:
        result[r[0]] = r[1]

    return jsonify(result)

@api.route('/error/client/ios', methods=['post'])
def client_ios():
    """
        The errors of iOS:
        equal is count play_errors and init_errors
    """
    db_ = get_ldb()

    params = request.get_json()
    start_date = params['start_date']
    end_date = params['end_date']
    lim_n = params['lim_n']

    start_time = datetime.fromisoformat(start_date).astimezone(
        current_app.config['TIMEZONE'])
    end_time = datetime.fromisoformat(end_date).astimezone(
        current_app.config['TIMEZONE'])

    play_error_list = list(db_.playrecords.find({
        '_id': {'$gte': ObjectId.from_datetime(start_time),
                '$lte': ObjectId.from_datetime(end_time)},
        'loadingDatas.playType': 5,
        'platform': 'iOS',
        'isBenchData': {'$ne': True},
        }, {
            'userAgent': 1, '_id': 0
            }))
    play_error_result = [re.split('[/ ]', pl['userAgent'].strip())[3] for pl in play_error_list]

    init_error_list = list(db_.initrecords.find({
        '_id': {'$gte': ObjectId.from_datetime(start_time),
                '$lte': ObjectId.from_datetime(end_time)},
        'type': {'$exists': True},
        }, {
            'userAgent': 1, '_id':0
            }))
    init_error_result = []
    for init in init_error_list:
        if re.split('[/ ]', init['userAgent'].strip())[2] == 'iOS':
            init_error_result.append(re.split('[/ ]', init['userAgent'].strip())[3])

    result_list = Counter(play_error_result + init_error_result)

    res = sorted(result_list.items(), key=lambda kv: kv[1], reverse=True)[:lim_n]

    result = defaultdict(dict)
    for r in res:
        result[r[0]] = r[1]

    return jsonify(result)

@api.route('/error/client/Android', methods=['post'])
def client_android():
    """
        The errors of Android:
        equal is count play_errors and init_errors
    """
    db_ = get_ldb()

    params = request.get_json()
    start_date = params['start_date']
    end_date = params['end_date']
    lim_n = params['lim_n']

    start_time = datetime.fromisoformat(start_date).astimezone(
        current_app.config['TIMEZONE'])
    end_time = datetime.fromisoformat(end_date).astimezone(
        current_app.config['TIMEZONE'])

    play_error_list = list(db_.playrecords.find({
        '_id': {'$gte': ObjectId.from_datetime(start_time),
                '$lte': ObjectId.from_datetime(end_time)},
        'loadingDatas.playType': 5,
        'platform': 'Android',
        'isBenchData': {'$ne': True},
        }, {
            'userAgent': 1, '_id': 0
            }))
    play_error_result = [re.split('[/ ]', pl['userAgent'].strip())[3] for pl in play_error_list]

    init_error_list = list(db_.initrecords.find({
        '_id': {'$gte': ObjectId.from_datetime(start_time),
                '$lte': ObjectId.from_datetime(end_time)},
        'type': {'$exists': True},
        }, {
            'userAgent': 1, '_id':0
            }))
    init_error_result = []
    for init in init_error_list:
        if re.split('[/ ]', init['userAgent'].strip())[2] == 'Android':
            init_error_result.append(re.split('[/ ]', init['userAgent'].strip())[3])

    result_list = play_error_result + init_error_result
    str_list = Counter([k.split('.')[0] for k in result_list])

    res = sorted(str_list.items(), key=lambda kv: kv[1], reverse=True)[:lim_n]

    result = defaultdict(dict)
    for r in res:
        result[r[0]] = r[1]

    return jsonify(result)

@api.route('/error/client/PC', methods=['post'])
def client_pc():
    """
        The errors of PC:
        equal is count play_errors and init_errors
    """
    db_ = get_ldb()

    params = request.get_json()
    start_date = params['start_date']
    end_date = params['end_date']
    lim_n = params['lim_n']

    start_time = datetime.fromisoformat(start_date).astimezone(
        current_app.config['TIMEZONE'])
    end_time = datetime.fromisoformat(end_date).astimezone(
        current_app.config['TIMEZONE'])

    play_error_list = list(db_.playrecords.find({
        '_id': {'$gte': ObjectId.from_datetime(start_time),
                '$lte': ObjectId.from_datetime(end_time)},
        'loadingDatas.playType': 5,
        'platform': 'desktop',
        'isBenchData': {'$ne': True},
        }, {
            'userAgent': 1, '_id': 0
            }))
    play_error_result = [re.split('[/ ]', pl['userAgent'].strip())[3] for pl in play_error_list]

    init_error_list = list(db_.initrecords.find({
        '_id': {'$gte': ObjectId.from_datetime(start_time),
                '$lte': ObjectId.from_datetime(end_time)},
        'type': {'$exists': True},
        }, {
            'userAgent': 1, '_id':0
            }))
    init_error_result = []
    for init in init_error_list:
        if re.split('[/ ]', init['userAgent'].strip())[2] == 'Window':
            init_error_result.append(re.split('[/ ]', init['userAgent'].strip())[3])

    result_list = Counter(play_error_result + init_error_result)
    res = sorted(result_list.items(), key=lambda kv: kv[1], reverse=True)[:lim_n]

    result = defaultdict(dict)
    for r in res:
        result[r[0]] = r[1]

    return jsonify(result)

@api.route('/error/client/errtype', methods=['post'])
def client_errtype():
    """
        The errors of errtype:
        errtype is play_errors and init_errors
    """
    db_ = get_ldb()

    start_date = request.get_json()['start_date']
    end_date = request.get_json()['end_date']

    start_time = datetime.fromisoformat(start_date).astimezone(
        current_app.config['TIMEZONE'])
    end_time = datetime.fromisoformat(end_date).astimezone(
        current_app.config['TIMEZONE'])

    play_error_count = db_.playrecords.count_documents({
        '_id': {'$gte': ObjectId.from_datetime(start_time),
                '$lte': ObjectId.from_datetime(end_time)},
        'loadingDatas.playType': 5,
        'isBenchData': {'$ne': True},
        })

    init_error_count = db_.initrecords.count_documents({
        '_id': {'$gte': ObjectId.from_datetime(start_time),
                '$lte': ObjectId.from_datetime(end_time)},
        'type': {'$exists': True},
        })

    return jsonify({
        '播放失败':play_error_count,
        '初始化失败':init_error_count
    })

@api.route('/error/client/network', methods=['post'])
def client_network():
    """
        The errors of network:
        network is wifi,4G,5G...
    """
    db_ = get_ldb()

    start_date = request.get_json()['start_date']
    end_date = request.get_json()['end_date']

    start_time = datetime.fromisoformat(start_date).astimezone(
        current_app.config['TIMEZONE'])
    end_time = datetime.fromisoformat(end_date).astimezone(
        current_app.config['TIMEZONE'])

    play_error_list = list(db_.playrecords.find({
        '_id': {'$gte': ObjectId.from_datetime(start_time),
                '$lte': ObjectId.from_datetime(end_time)},
        'loadingDatas.playType': 5,
        'network': {'$exists': True},
        'isBenchData': {'$ne': True},
        }, {
            'network': 1, '_id': 0
            }))
    play_error = [pl['network'] for pl in play_error_list]

    error_count = Counter(play_error )
    error_count['unknown'] = error_count['NONE'] + error_count['UNKNOWN']
    del error_count['NONE']
    del error_count['UNKNOWN']

    return jsonify(error_count)

@api.route('/error/client/area', methods=['post'])
def client_area():
    """
        The errors of area:
        area is 北京、广州、和田、深圳
    """
    db_ = get_ldb()

    params = request.get_json()
    start_date = params['start_date']
    end_date = params['end_date']
    lim_n = params['lim_n']

    start_time = datetime.fromisoformat(start_date).astimezone(
        current_app.config['TIMEZONE'])
    end_time = datetime.fromisoformat(end_date).astimezone(
        current_app.config['TIMEZONE'])

    play_error_list = list(db_.playrecords.aggregate([
        {'$match': {
            '_id': {'$gte': ObjectId.from_datetime(start_time),
                    '$lte': ObjectId.from_datetime(end_time)},
            'loadingDatas.playType': 5,
            'location': {'$exists': True},
            'isBenchData': {'$ne': True},
        }}, {'$project': {
                'location': 1, '_id': 0}
        }, {'$group': {
                '_id':'$location',
                'count': {'$sum': 1}
        }}, {'$sort':{'count': -1}},
            {'$limit': int(lim_n+1)}
        ]))

    result_dict = defaultdict(dict)
    for play in play_error_list:
        result_dict[play['_id'][6:]] = play['count']
    result_dict['中国'] = result_dict['']
    del result_dict['']

    res = sorted(result_dict.items(), key=lambda kv: kv[1], reverse=True)[:lim_n]

    result = defaultdict(dict)
    for r in res:
        result[r[0]] = r[1]

    return jsonify(result)

@api.route('/error/client/details', methods=['post'])
def client_details():
    """
        The errors of details:
        details is device_id,device_model,ip,network,
        devoce_os,location,protocol,platform
    """
    db_ = get_ldb()

    start_date = request.get_json()['start_date']
    end_date = request.get_json()['end_date']
    index = request.get_json()['index']
    count = request.get_json()['count']
    error_type = request.get_json()['error_type']
    network = request.get_json()['network']
    protocol = request.get_json()['protocol']
    platform = request.get_json()['platform']

    start_time = datetime.fromisoformat(start_date).astimezone(
        current_app.config['TIMEZONE'])
    end_time = datetime.fromisoformat(end_date).astimezone(
        current_app.config['TIMEZONE'])

    if 'play' in error_type:
        play_error_list = list(db_.playrecords.find({
            '_id': {'$gte': ObjectId.from_datetime(start_time),
                    '$lte': ObjectId.from_datetime(end_time)},
            'loadingDatas.playType': 5,
            'network':{'$in':network},
            'protocol': {'$in': protocol},
            'platform': {'$in': platform},
            'location': {'$exists': True},
            'isBenchData': {'$ne': True},
            }, {
                'deviceId': 1,
                'userAgent': 1,
                'IP': 1,
                'network': 1,
                'location': 1,
                'platform': 1,
                'protocol': 1,
                '_id': 0
            }))
        for play in play_error_list:
            play['error_type'] = 'play'
            play['device_model'] = re.split('[/ ]', play['userAgent'].strip())[-1]
            play['device_os'] = re.split('[/ ]', play['userAgent'].strip())[3]
            del play['userAgent']

    if 'initial' in error_type:
        init_error_list = list(db_.initrecords.find({
            '_id': {'$gte': ObjectId.from_datetime(start_time),
                    '$lte': ObjectId.from_datetime(end_time)},
            'type': {'$exists': True},
        }, {
            'guid': 1,
            'deviceId': 1,
            'userAgent': 1,
            'location': 1,
            'network': 1,
            '_id': 0
        }))

        guid_ip_list = list(db_.activitysessions.find({
            'guid': {'$exists': True},
            'location': {'$exists': True}
        }, {
            'guid': 1,
            'IP': 1,
            '_id': 0
        }))
        guid_ip = defaultdict(dict)

        for guid in guid_ip_list:
            guid_ip[guid['guid']] = guid['IP']

        for init in init_error_list:
            init['error_type'] = 'initial'
            init['device_model'] = re.split('[/ ]', init['userAgent'].strip())[-1]
            init['device_os'] = re.split('[/ ]', init['userAgent'].strip())[3]
            init['platform'] = re.split('[/ ]', init['userAgent'].strip())[2]
            init['IP'] = guid_ip[init['guid']]

            del init['userAgent']

    if 'play' in error_type and 'initial' not in error_type:
        result_list = play_error_list
    if 'play' not in error_type and 'initial' in error_type:
        result_list = init_error_list
    if 'play' in error_type and 'initial' in error_type:
        result_list = play_error_list + init_error_list

    result_list = result_list[index * count: index * count + count]

    return jsonify(result_list)

@api.route('/error/client/details/count', methods=['post'])
def client_details_count():
    """
        The errors of details count
    """
    db_ = get_ldb()

    start_date = request.get_json()['start_date']
    end_date = request.get_json()['end_date']
    error_type = request.get_json()['error_type']
    network = request.get_json()['network']
    protocol = request.get_json()['protocol']
    platform = request.get_json()['platform']

    start_time = datetime.fromisoformat(start_date).astimezone(
        current_app.config['TIMEZONE'])
    end_time = datetime.fromisoformat(end_date).astimezone(
        current_app.config['TIMEZONE'])

    if 'play' in error_type:
        play_error_count = db_.playrecords.count_documents({
            '_id': {'$gte': ObjectId.from_datetime(start_time),
                    '$lte': ObjectId.from_datetime(end_time)},
            'loadingDatas.playType': 5,
            'network':{'$in':network, '$exists': True},
            'protocol': {'$in': protocol},
            'platform': {'$in': platform},
            'location': {'$exists': True},
            'isBenchData': {'$ne': True},
            })

    init_error_count = 0
    if 'initial' in error_type:
        init_error_list = list(db_.initrecords.find({
            '_id': {'$gte': ObjectId.from_datetime(start_time),
                    '$lte': ObjectId.from_datetime(end_time)},
            'type': {'$exists': True},
        }, {
            'userAgent': 1,
            '_id': 0
        }))
        for init in init_error_list:
            if re.split('[/ ]', init['userAgent'].strip())[2] in platform:
                init_error_count += 1

    if 'play' in error_type and 'initial' not in error_type:
        error_count = play_error_count
    if 'play' not in error_type and 'initial' in error_type:
        error_count = init_error_count
    if 'play' in error_type and 'initial' in error_type:
        error_count = play_error_count + init_error_count

    return jsonify({
        'count':error_count
    })
