from django.db import models


class User(models.Model):
    class Meta:
        db_table = 'user'

    uuid = models.CharField(max_length=36, primary_key=True, verbose_name='uuid')

    nickname = models.CharField(max_length=25, verbose_name='昵称')

    public_key = models.CharField(max_length=1000, verbose_name='公钥')

