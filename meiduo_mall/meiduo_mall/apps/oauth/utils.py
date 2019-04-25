from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer, BadData


def generate_access_token(openid):
    """将openid加密为access_token"""
    # 创建对象,第一个参数秘钥,第二个参数有效期(秒)
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=300)
    data = {'openid': openid}
    # 调用对象的dumps方法,传入字典类型,进行加密,返回bytes类型
    access_token = serializer.dumps(data)
    # 解码后返回
    return access_token.decode()


def check_access_token(access_token):
    """将access_token解密为openid"""
    # 创建对象,第一个参数秘钥,第二个参数有效期(秒)
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=300)
    try:
        # 调用对象的loads方法,传入access_token,进行解密,返回字典类型
        data = serializer.loads(access_token)
    # 如解密出错,说明access_token遭到破坏
    except BadData:
        return None
    # 如解密成功,则提取openid并返回
    else:
        openid = data.get('openid')
        return openid
