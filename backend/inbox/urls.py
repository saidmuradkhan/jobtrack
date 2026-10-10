from django.urls import path

from . import views

urlpatterns = [
    path("inbox/", views.inbox, name="inbox"),
    path("inbox/receive/", views.receive, name="inbox-receive"),
    path("inbox/emails/<int:pk>/accept/", views.accept, name="inbox-accept"),
    path("inbox/emails/<int:pk>/dismiss/", views.dismiss, name="inbox-dismiss"),
]
