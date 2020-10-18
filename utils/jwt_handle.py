def jwt_response_payload_handler(token, user=None, request=None):
    """
    对返回数据重写，添加用户信息
    :param token:
    :param user:
    :param request:
    :return:
    """
    return {
        'user_id': user.id,
        'username': user.username,
        'token': token
    }
