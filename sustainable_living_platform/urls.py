from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Redirect default admin to our custom professional dashboard
    path('admin/', RedirectView.as_view(url='/management/', permanent=True)),
    path('', include('core.urls')),
]
