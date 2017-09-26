from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

from hashlib import md5
from datetime import datetime, date
from PIL import Image
import pandas as pd

class Category(models.Model):
    name = models.CharField("Название", max_length=100)
    reason = models.CharField("Причина (для заявления)", max_length=100)
    max_sum = models.IntegerField("Макс. сумма", default=20000)
    max_quantity = models.IntegerField("Макс. раз за семестр", default=1)
    notifications = models.BooleanField("Уведомления о новых заявлениях", default=True)

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return self.name


def is_image(file):
    try:
        trial_image = Image.open(file)
        trial_image.verify()  # raises exception if there are errors
        return True
    except Exception:
        return False


# TODO add_dttm changes EVERY time when model is saved, so instead of setting it as auto_now_add=True it's better to set im manually
class AidRequest(models.Model):
    WAITING = 1
    ACCEPTED = 2
    DECLINED = 3
    INFO_NEEDED = 4

    AID_REQUEST_STATUS = (
        (WAITING, "Заявление рассматривается"),
        (ACCEPTED, "Заявление одобрено"),
        (DECLINED, "В заявлении отказано"),
        (INFO_NEEDED, "Необходимо уточнить данные"),
    )

    applicant = models.ForeignKey(User, blank=True, null=True)  # find out how to add applicant to form before validation
    category = models.ForeignKey(Category)
    reason = models.TextField("Причина", max_length=1024)
    req_sum = models.FloatField("Запрошенная сумма", blank=True, null=True)
    urgent = models.BooleanField("Срочно", default=False)
    accepted_sum = models.FloatField("Одобренная сумма", blank=True, null=True)
    status = models.IntegerField("Статус заявления", choices=AID_REQUEST_STATUS, default=WAITING)
    add_dttm = models.DateTimeField("Дата подачи", auto_now_add=True)
    examination_dttm = models.DateTimeField("Дата рассмотрения", blank=True, null=True)
    payment_dt = models.DateField("Дата выплаты", blank=True, null=True)
    examination_comment = models.TextField("Комментарий комиссии", blank=True, null=True)
    submitted_paper = models.BooleanField("Принес заявление", default=False)
    paid_with_cash = models.BooleanField("заплатили наличными", default=False)

    def can_view(self, user):
        if not user.is_authenticated:
            return False
        if self.applicant == user \
            or user.userprofile.student_info and self.applicant.userprofile.student_info == user.userprofile.student_info \
                or user.groups.filter(name="finance").exists() or user.is_superuser:
            return True
        return False

    # returns links to images, related to this aidrequest
    # TODO rewrite using new AidDocument.is_image field?
    def images_tags(self):
        html = ""
        files = self.aiddocument_set.all()
        for file in files:
            if is_image(file.file):
                html += '<img class="aiddocument" style="max-width:100%;" src={}>'.format(file.file.url)
        return html
    images_tags.allow_tags = True
    images_tags.short_description = "Приложенные изображения"

    # creates csv with all accepted applications for this month
    @staticmethod	
    def to_csv(filename):
        df = pd.DataFrame(columns=["FIO", "group", "req_sum", "Исх. сумма", "Реал. сумма", "За что", "заявление",
                                "Комментарии", "e-mail", "text"])
        for request in AidRequest.objects.filter(status=AidRequest.ACCEPTED,
                                                 payment_dt__month=date.today().month,
                                                 paid_with_cash=False).order_by('category'):
            dct = {
                "req_sum": request.req_sum,
                "Исх. сумма": int(request.accepted_sum/0.86) if request.accepted_sum != 0 else 0,
                "Реал. сумма": int(request.accepted_sum),
                "За что": request.category.name,
                "Комментарии": request.examination_comment,
                "text": "",
            }
            student_info = request.applicant.userprofile.student_info
            if student_info:
                dct.update({
                    "FIO": student_info.fio,
                    "group": student_info.group,
                    "e-mail": student_info.phystech,
                })
            else:
                fio = request.applicant.last_name + request.applicant.first_name + request.applicant.userprofile.middlename
                if fio:
                    dct.update({"FIO": fio})
                else:
                    dct.update({"FIO": request.applicant.username})
            if request.submitted_paper:
                dct.update({"заявление":"+"})
            df = df.append(dct, ignore_index=True)
        df.to_csv(filename)

    def get_absolute_url(self):
        return reverse('fin_aid:aid_request_detail', args=[self.id])

    def __str__(self):
        return "{}: заявление от {} по категории {} на сумму {}".format(self.applicant, self.add_dttm.date(), self.category, self.req_sum)

    class Meta:
        verbose_name = "заявление на матпомощь"
        verbose_name_plural = "заявления на матпомощь"


# separate function as it's used in create_paper
def user_hash(user):
    secret = md5(str(user.id).encode("utf-8")).hexdigest()
    secret = md5((secret + user.username).encode("utf-8")).hexdigest()
    return secret


def document_path(instance, filename):
    return "aid_docs/user_{}/{}".format(user_hash(instance.request.applicant), filename)


# TODO if user can harm us with custom filename we should replace user-given filename
class AidDocument(models.Model):
    file = models.FileField("Документ", upload_to=document_path)
    # filename = models.CharField("Имя файла", max_length=100)
    request = models.ForeignKey(AidRequest)
    is_application_paper = models.BooleanField("Заявление на матпомощь", default=False)
    is_image = models.BooleanField("Является изображением", default=False)

    class Meta:
        verbose_name = "потверждающий документ"
        verbose_name_plural = "подтверждающие документы"

    def __str__(self):
        return "Документ {} к заявлению {}".format(self.file.name, self.request)


def _get_next_date_naive(dt=None, t='payment'):
    if not dt:
        dt = date.today()
    pay_day = 28
    edge_day = 14
    if t == 'payment':
        day = pay_day
    elif t == 'deadline':
        day = edge_day
    else:
        raise ValueError

    year = dt.year
    if dt.day <= edge_day:
        month = dt.month
    else:
        if dt.month < 12:
            month = dt.month + 1
        else:
            month = 1
            year = dt.year + 1
    result_dt = date(year, month, day)
    return result_dt


def _get_default_year():
    return date.today().year
def _get_default_month():
    return date.today().month
def _get_default_payment_dt():
    return date(datetime.now().year, datetime.now().month, 28)
def _get_default_deadline_dt():
    return date(datetime.now().year, datetime.now().month, 14)


class MonthlyData(models.Model):
    MONTH = [
        (1, "Январь"), (2, "Февраль"), (3, "Март"), (4, "Апрель"), (5, "Май"), (6, "Июнь"),
        (7, "Июль"), (8, "Август"), (9, "Сентябрь"), (10, "Октябрь"), (11, "Ноябрь"), (12, "Декабрь"),
    ]
    year = models.IntegerField("Год", default=_get_default_year)
    month = models.IntegerField("Месяц", default=_get_default_month, choices=MONTH)
    limit = models.FloatField("Лимит")
    deadline_dt = models.DateField("Дэдлайн по заявлениям", default=_get_default_deadline_dt)
    payment_dt = models.DateField("Дата выплаты матпомощи", default=_get_default_payment_dt)

    def __str__(self):
        return "{} {}".format(self.get_month_display(), self.year)

    class Meta:
        verbose_name = "Информация о месяце"
        verbose_name_plural = "Лимиты по месяцам"

    @classmethod
    def current(cls):
        deadline = get_next_date(date.today(), 'deadline')
        return cls.objects.get(year=deadline.year, month=deadline.month)

    @property
    def sum_used(self):
        requests = AidRequest.objects.filter(status=AidRequest.ACCEPTED, payment_dt__year=self.year,
                                             payment_dt__month=self.month)
        return requests.aggregate(sum=models.Sum('accepted_sum'))["sum"]


def _get_next_date_db(dt=None, t='payment'):
    if not dt:
        dt = date.today()
    next_month = MonthlyData.objects.filter(deadline_dt__gte=dt).order_by('payment_dt').first()
    if next_month:
        if t == 'payment':
            return next_month.payment_dt
        elif t == 'deadline':
            return next_month.deadline_dt
        else:
            raise ValueError
    else:
        return None


def get_next_date(dt=None, t='payment'):
    payment_dt = _get_next_date_db(dt, t)
    if not payment_dt:
        payment_dt = _get_next_date_naive(dt, t)
    return payment_dt


"""def sum_by_month(year, month):
    requests = AidRequest.objects.filter(status=AidRequest.ACCEPTED, payment_dt__year=year, payment_dt__month=month)
    return requests.aggregate(sum=models.Sum('accepted_sum'))["sum"]"""

