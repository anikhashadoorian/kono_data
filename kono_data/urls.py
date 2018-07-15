"""kono_data URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.views.generic import RedirectView
from django.contrib.auth.views import login, logout

from kono_data import settings
from kono_data.views.dataset import index_dataset, export_dataset, update_or_create_dataset, \
    fetch_dataset_from_source, show_leaderboard
from kono_data.views.process import process
from kono_data.views.user import signup
from kono_data.views.index import IndexView

urlpatterns = [
                  url(r'^accounts/logout/$', logout, name='logout'),
                  url(r'^accounts/signup/$', signup, name='signup'),
                  path('signup/<str:invite_key>', signup, name='signup_with_invite'),
                  path('accounts/login/', login, {'template_name': 'admin/login.html'}, name='login'),
                  path('accounts/login/<str:invite_key>', login, {'template_name': 'admin/login.html'}, name='login'),
                  url(r'^accounts/profile/$', RedirectView.as_view(url=reverse_lazy('index'))),
                  url(r'^accounts/$', RedirectView.as_view(url='/')),
                  url(r'^admin_tools/', include('admin_tools.urls')),
                  path('admin/', admin.site.urls),
                  path('', IndexView.as_view(), name='index'),
                  path('process/<uuid:dataset>', process, name='process'),
                  path('dataset/create/', update_or_create_dataset, name='update_or_create_dataset'),
                  path('dataset/<uuid:dataset>', update_or_create_dataset, name='update_or_create_dataset'),
                  path('dataset/<uuid:dataset>/export', export_dataset, name='export_dataset'),
                  path('dataset/<uuid:dataset>/fetch', fetch_dataset_from_source, name='fetch_dataset'),
                  path('dataset/<uuid:dataset>/leaderboard', show_leaderboard, name='show_leaderboard'),
                  path('dataset/<str:type>', index_dataset, name='datasets'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
