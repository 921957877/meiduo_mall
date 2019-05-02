from django.conf import settings
from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client


class FastDFSStorage(Storage):
    # name:用户选择上传文件的名称
    # content:含有上传内容的一个File对象
    # 我们可以通过content.read()获得上传文件的内容
    def save(self, name, content, max_length=None):
        """重写上传文件的函数"""
        # 创建客户端对象
        client = Fdfs_client(settings.FDFS_CLIENT_CONF)
        # 调用上传函数,根据文件内容进行上传
        result = client.upload_by_buffer(content.read())
        # 判断是否上传成功
        if result.get('Status') != 'Upload successed.':
            raise Exception('上传失败')
        # 上传成功,返回file_id
        file_id = result.get('Remote file_id')
        return file_id

    def exists(self, name):
        """上传之前判断文件名是否冲突"""
        # 由于fdfs中的文件名是随机生成的,所以不存在文件名冲突的情况
        return False

    def url(self, name):
        """返回访问到文件的完整url地址"""
        return settings.FDFS_URL + name
