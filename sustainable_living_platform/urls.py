from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', RedirectView.as_view(url='/management/', permanent=True)),
    path('', include('core.urls')),
]
