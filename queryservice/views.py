from django.apps import apps
from django.http import HttpResponse
from django.views.generic import View
from queryservice.view_functions import introspect_entity_action, get_contents, read_entity_action
from queryservice.Qresponse import Response
import json


# Create your views here.

class IntrospectEntityAction(View):
    @staticmethod
    def get(request):
        content = get_contents(request)
        resp = Response()
        payload = []
        if content:
            app_name = content.get('appName', None)
            entity_name = content.get('entityName', None)
            if app_name and entity_name:
                payload = introspect_entity_action(app_name, entity_name)
                resp.passed()
                resp.add_param('properties', payload)

        return HttpResponse(resp.get_response(), content_type="application/json")


class ReadEntityAction(View):

    @staticmethod
    def get(request):
        content = get_contents(request)
        resp = Response()
        payload = []
        if content:
            _appName = content.get('appName', None)
            _entityName = content.get('entityName', None)
            _fields = content.get('properties', [])
            _pageSize = content.get('pageSize', 10)
            _pageIndex = content.get('pageIndex', 1)
            _filter = content.get('filters', [])
            _sort = content.get('sort', None)

            if len(_fields) > 0 and _appName and _entityName:
                read_entity_action(app_name=_appName, entity_name=_entityName, properties=_fields, resp=resp,
                                   pageSize=_pageSize, pageIndex=_pageIndex, filter=_filter, sort=_sort)
            else:
                resp.failed()
                resp.add_message('Incomplete Read request parameters')
        else:
            resp.failed()
            resp.add_message('Missing Read request parameters.')

        return HttpResponse(resp.get_response(), content_type="application/json")

    @staticmethod
    def post(request):
        content = get_contents(request)
        resp = Response()
        payload = []
        if content:
            _appName = content.get('appName', None)
            _entityName = content.get('entityName', None)
            _fields = content.get('properties', [])
            _pageSize = content.get('pageSize', 10)
            _pageIndex = content.get('pageIndex', 1)
            _filter = content.get('filters', [])
            _sort = content.get('sort', None)

            if len(_fields) > 0 and _appName and _entityName:
                read_entity_action(app_name=_appName, entity_name=_entityName, properties=_fields, resp=resp,
                                   pageSize=_pageSize, pageIndex=_pageIndex, filter=_filter, sort=_sort)
            else:
                resp.failed()
                resp.add_message('Incomplete Read request parameters')
        else:
            resp.failed()
            resp.add_message('Missing Read request parameters.')

        return HttpResponse(resp.get_response(), content_type="application/json")


class UpdateEntityAction(View):

    @staticmethod
    def post(request):
        pass


class CreateEntityAction(View):

    @staticmethod
    def post(request):
        pass


class DeleteEntityAction(View):

    @staticmethod
    def post(request):
        content = get_contents(request)
        resp = Response()
        if content:
            _appName = content.get('appName', None)
            _entityName = content.get('entityName', None)
            _entity_id = content.get('entityId', None)

            if _appName and _entity_id and _entityName:

                query_model = apps.get_model(_appName, _entityName)
                if query_model:
                    try:
                        record = query_model.objects.get(id=_entity_id)
                        record.active = False
                        record.save()

                        resp.passed()
                        resp.add_message('Record deleted Successfully')
                    except Exception as err:
                        resp.failed()
                        resp.add_message(str(err))

                else:
                    resp.failed()
                    resp.add_message('Undefined Entity Specification')

            else:
                resp.failed()
                resp.add_message('Missing parameters')

        return HttpResponse(resp.get_response(), content_type="application/json")
