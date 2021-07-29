from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    # OneToOne Field will create a unique index, making sure no multiple UserProfile pointing to the same User
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    # Django also provides an ImageField, which better to avoid to make things easier.
    # FileField will have the same effect as the ImageField, because avatar is saved in the form of file and load via url
    avatar = models.FileField(null=True)
    # when a user is created, an UserProfile instance will be constructed
    # the nickname will set to null initially until the user changes it.
    nickname = models.CharField(null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {}'.format(self.user, self.nickname)

# 定义一个 profile 的 property 方法，植入到 User 这个 model 里
# 这样当我们通过 user 的一个实例化对象访问 profile 的时候，即 user_instance.profile
# 就会在 UserProfile 中进行 get_or_create 来获得对应的 profile 的 object
# 这种写法实际上是一个利用 Python 的灵活性进行 hack 的方法，这样会方便我们通过 user 快速
# 访问到对应的 profile 信息。
def get_profile(user):
    if hasattr(user, '_cached_user_profile'):
        return getattr(user, '_cached_user_profile')

    profile, _ = UserProfile.objects.get_or_create(user=user)
    # 使用 user 对象的属性进行缓存(cache)，避免多次调用同一个 user 的 profile 时
    # 重复的对数据库进行查询
    setattr(user, '_cached_user_profile', profile)
    return profile

# 给 User Model 增加了一个 profile 的 property 方法用于快捷访问
User.profile = property(get_profile)