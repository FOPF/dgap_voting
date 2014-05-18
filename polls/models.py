from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

#TODO необходимые методы в моделях
#TODO метод approve_user и модели для базы поселения

class Poll(models.Model):
    name = models.CharField('Название опроса', max_length=50)
    question = models.CharField('Вопрос', max_length=200)
    begin_date = models.DateTimeField('Начало голосования')
    end_date = models.DateTimeField('Конец голосования')
    target_room = models.CharField('Целевая комната', max_length=10) #предполагается использование регулярных выражений
    target_group = models.CharField('Целевая группа', max_length=10) #TODO значения по умолчанию для target, покрывающие все комнаты/группы
    public = models.BooleanField('Открытое голосование', default = True)
    ONE = 'ONE'
    MANY = 'MANY'
    OWN = 'OWN'
    ANSWER_TYPE_CHOICES = (
        (ONE , 'Выбор одного варианта'),
        (MANY , 'Выбор нескольких вариантов'),
        (OWN , 'Свой вариант'),
    )
    answer_type = models.CharField('Тип ответа', max_length=10, choices = ANSWER_TYPE_CHOICES, default = ONE)
    voted_users = models.ManyToManyField(User)
    def __str__(self):
        return self.name


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField("Текст ответа", max_length=200)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text

class UserHash(models.Model):
    value = models.BigIntegerField()#для очень старых опросов планируется удалять хэши, оставляя результаты в виде файла
    choice = models.ForeignKey(Choice)
    user = models.ForeignKey(User, null=True, blank=True, default = None)#при анонимном голосовании не заполнять это поле

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    middlename = models.CharField('Отчество', max_length=20)
    group = models.CharField('Номер группы', max_length=5)
    room = models.CharField('Номер комнаты', max_length=4)
    approval = models.BooleanField('Пользователь подтверждён', default = False)
    def __str__(self):  
        return "Профиль для %s" % self.user 

def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
        profile, created = UserProfile.objects.get_or_create(user=instance) 

post_save.connect(create_user_profile, sender=User)
