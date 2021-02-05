from django.urls import path
from queryservice.views import ReadEntityAction, IntrospectEntityAction, DeleteEntityAction
from party_base.views import ReadCustomerAccounts, UpdateCustomerAccounts

urlpatterns = [

    path('introspect/', IntrospectEntityAction.as_view()),
    path('read/', ReadEntityAction.as_view()),
    path('delete/', DeleteEntityAction.as_view()),

    # Custom CRUD Endpoints
    path('read/clients/', ReadCustomerAccounts.as_view(), {'account_type': 'pod'}),
    path('read/fforwarders/', ReadCustomerAccounts.as_view(), {'account_type': 'streamz'}),
    path('update/clients/', UpdateCustomerAccounts.as_view()),
    path('update/fforwarders/', UpdateCustomerAccounts.as_view())

]