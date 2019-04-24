from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer


def generate_access_token(openid):
    """将openid加密为access_token"""
    # 创建对象,第一个参数秘钥,第二个参数有效期(秒)
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=300)
    data = {'openid': openid}
    # 调用对象的dumps方法,传入字典类型,进行加密,返回bytes类型
    access_token = serializer.dumps(data)
    # 解码后返回
    return access_token.decode()
