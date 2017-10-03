from django.conf.urls import include, url, static
from django.conf import settings
from django.views.generic import RedirectView
from django.urls import reverse

from django.contrib import admin
admin.autodiscover()

from registration.backends.simple.views import RegistrationView

from blog.views import ArticleList
from .settings import DEBUG

class MyRegistrationView(RegistrationView):
    def get_success_url(self, request, user):
        return "/profiles"

urlpatterns = [
    url(r'^$', ArticleList.as_view(), name='index'),
    url(r'^polls/', include('polls.urls', namespace='polls')),
    url(r'^blog/', include('blog.urls', namespace='blog')),
    url(r'^bicycle/', include('cycle_storage.urls', namespace='bicycle')),
    # url(r'^laundry/', RedirectView.as_view(url="http://stiralka.mipt.ru"), name="laundry"),
    # url(r'^print/', RedirectView.as_view(url="http://print.mipt.ru"), name="print"),
    url(r'^aid/', include('fin_aid.urls', namespace='fin_aid')),
    url(r'^senate/', include('senate.urls', namespace='senate')),
    url(r'^servertime/', include('servertime.urls', namespace='servertime')),
    url(r'^profiles/', include('profiles.urls', namespace='profiles')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/register/$', MyRegistrationView.as_view(), name='registration_register'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url('', include('social_django.urls', namespace='social')),
] 
if DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)