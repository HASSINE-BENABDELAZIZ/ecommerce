"""xmlfeed URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import PasswordResetConfirmView, \
    PasswordResetDoneView, \
    PasswordResetCompleteView
from django.urls import include, path, re_path
from rest_framework.documentation import include_docs_urls

from accounts.views import RegistrationView

from . import settings
from .views import LoginPage, logout_view, \
    generate_xml, PasswordResetView, IndexView, TrackList, TrackDetail

app_name = 'xmlfeed'

urlpatterns = [
    path('docs/', include_docs_urls(title='STORELINKERS', public=False)),
    path('api/', include('orders.api_urls')),

    path('api/products/', include('products.api_url')),
    path('marketplace/', include('marketplace.urls')),
    path('admin/', admin.site.urls),
    path('login/', LoginPage.as_view(), name="login"),
    path('register/', RegistrationView.as_view(), name="register"),
    path('logout/', logout_view, name="logout"),
    path('', IndexView.as_view(), name="index"),
    path('track/', TrackList.as_view(), name="track"),
    path('track/<str:slug>', TrackDetail.as_view(), name="track_detail"),
    path('user/', include('accounts.urls')),
    path('product/', include('products.urls')),
    path('order/', include('orders.urls')),
    path('password_reset/',
         PasswordResetView.as_view(),
         name='password_reset'),
    path("reset/<uidb64>/<token>/",
         PasswordResetConfirmView.as_view(),
         name="password_reset_confirm"),
    path("reset_password_sent/",
         PasswordResetDoneView.as_view(),
         name="password_reset_done"),
    path("reset_password_done/",
         PasswordResetCompleteView.as_view(),
         name="password_reset_complete"),

    re_path(r'^productsfeed.xml$',
            generate_xml, name="generate_xml"),
    path('test/', include('frontend.urls')),
    path('stat/', include('stats.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]
