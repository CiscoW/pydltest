import json
# import requests
from urllib.parse import quote as urlquote
from django.contrib import messages
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.utils import quote
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django.contrib import admin
from testinstance.models import *
# from locusttest.testinstance import ApiTestInstance
# from locusttest.testinstance import SideTestInstance
# from locusttest.testdata import get_api_test_data
# from locusttest.testdata import get_side_test_data
# from locusttest.testdata import send_test_data
# from flaskservice.config import GET_LOCUST_SERVICE_STATE_URL
from flaskservice.config import INDEX_URL
# from locusttest.models import LocustTest

IS_POPUP_VAR = '_popup'
TO_FIELD_VAR = '_to_field'


# def get_locust_service_state(url):
#     response = requests.get(url=url)
#     state = json.loads(response.text)
#     return state


# Register your models here.
@admin.register(MicroServiceApiTestInstance)
class MicroServiceApiTestInstanceAdmin(admin.ModelAdmin):
    # fields = (('test_date', 'test_mode'), 'host', ('min_wait', 'max_wait'),
    #           ('locust_count', 'hatch_rate', 'run_time'),
    #           'test_content', 'describe')
    list_display = ['test_date', 'test_mode', 'host', 'locust_count', 'hatch_rate', 'max_wait', 'min_wait', 'run_time',
                    'describe', 'state']

    search_fields = ('test_mode__test_mode', 'host', 'describe')

    ordering = ('-test_date',)

    filter_horizontal = ('test_content',)
    fieldsets = (

        ("压力测试配置", {'fields': [('test_date', 'test_mode'), 'host', ('min_wait', 'max_wait'),
                               ('locust_count', 'hatch_rate', 'run_time'), 'test_content', 'describe']}),

        ("单点登录配置", {'fields': [('token_url', 'user', 'password'), 'token_params']})
    )

    def state(self, obj):
        # running = get_locust_service_state(GET_LOCUST_SERVICE_STATE_URL % obj.id)
        if obj.running_status:
            a_label = '<a href="%s" target="_blank" style="color: red">正在运行中 >>> </a>' % (INDEX_URL % obj.id)
        else:
            a_label = '<a href="%s" target="_blank" style="color: green">未运行 >>> </a>' % (INDEX_URL % obj.id)
        return format_html(a_label)

    state.short_description = "状态"

    # def save_model(self, request, obj, form, change):
    #     super().save_model(request, obj, form, change)
    #
    #     # 向flask 服务中发送数据 注: 因django中使用locust出现猴子补丁问题 所以用此方法比较合适
    #     test_instance = TestInstance(obj)
    #     send_test_data(test_instance)

    def response_add(self, request, obj, post_url_continue=None):
        """
        Determine the HttpResponse for the add_view stage.
        """
        opts = obj._meta
        preserved_filters = self.get_preserved_filters(request)
        obj_url = reverse(
            'admin:%s_%s_change' % (opts.app_label, opts.model_name),
            args=(quote(obj.pk),),
            current_app=self.admin_site.name,
        )
        # Add a link to the object's change form if the user can edit the obj.
        if self.has_change_permission(request, obj):
            obj_repr = format_html('<a href="{}">{}</a>', urlquote(obj_url), obj)
        else:
            obj_repr = str(obj)
        msg_dict = {
            'name': opts.verbose_name,
            'obj': obj_repr,
        }
        # Here, we distinguish between different save types by checking for
        # the presence of keys in request.POST.

        if IS_POPUP_VAR in request.POST:
            to_field = request.POST.get(TO_FIELD_VAR)
            if to_field:
                attr = str(to_field)
            else:
                attr = obj._meta.pk.attname
            value = obj.serializable_value(attr)
            popup_response_data = json.dumps({
                'value': str(value),
                'obj': str(obj),
            })
            return TemplateResponse(request, self.popup_response_template or [
                'admin/%s/%s/popup_response.html' % (opts.app_label, opts.model_name),
                'admin/%s/popup_response.html' % opts.app_label,
                'admin/popup_response.html',
            ], {
                                        'popup_response_data': popup_response_data,
                                    })

        elif "_continue" in request.POST or (
                # Redirecting after "Save as new".
                "_saveasnew" in request.POST and self.save_as_continue and
                self.has_change_permission(request, obj)
        ):
            msg = _('The {name} "{obj}" was added successfully.')
            if self.has_change_permission(request, obj):
                msg += ' ' + _('You may edit it again below.')
            self.message_user(request, format_html(msg, **msg_dict), messages.SUCCESS)
            if post_url_continue is None:
                post_url_continue = obj_url
            post_url_continue = add_preserved_filters(
                {'preserved_filters': preserved_filters, 'opts': opts},
                post_url_continue
            )
            return HttpResponseRedirect(post_url_continue)

        elif "_addanother" in request.POST:
            msg = format_html(
                _('The {name} "{obj}" was added successfully. You may add another {name} below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = request.path
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)

        else:
            msg = format_html(
                _('The {name} "{obj}" was added successfully.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)

            # 只能写在这里，不能写在save_model中，那边的obj中的数据是历史的
            # 向flask 服务中发送数据 注: 因django中使用locust出现猴子补丁问题 所以用此方法比较合适
            # 此方法禁用 改成动态获取更为合理
            # api_test_instance = ApiTestInstance(obj)
            # test_id, test_data = get_api_test_data(api_test_instance)
            # LocustTest.objects.create(id=test_id, test_data=test_data)
            return self.response_post_save_add(request, obj)

    def response_change(self, request, obj):
        """
        Determine the HttpResponse for the change_view stage.
        """

        if IS_POPUP_VAR in request.POST:
            opts = obj._meta
            to_field = request.POST.get(TO_FIELD_VAR)
            attr = str(to_field) if to_field else opts.pk.attname
            value = request.resolver_match.kwargs['object_id']
            new_value = obj.serializable_value(attr)
            popup_response_data = json.dumps({
                'action': 'change',
                'value': str(value),
                'obj': str(obj),
                'new_value': str(new_value),
            })
            return TemplateResponse(request, self.popup_response_template or [
                'admin/%s/%s/popup_response.html' % (opts.app_label, opts.model_name),
                'admin/%s/popup_response.html' % opts.app_label,
                'admin/popup_response.html',
            ], {
                                        'popup_response_data': popup_response_data,
                                    })

        opts = self.model._meta
        preserved_filters = self.get_preserved_filters(request)

        msg_dict = {
            'name': opts.verbose_name,
            'obj': format_html('<a href="{}">{}</a>', urlquote(request.path), obj),
        }
        if "_continue" in request.POST:
            msg = format_html(
                _('The {name} "{obj}" was changed successfully. You may edit it again below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = request.path
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)

        elif "_saveasnew" in request.POST:
            msg = format_html(
                _('The {name} "{obj}" was added successfully. You may edit it again below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = reverse('admin:%s_%s_change' %
                                   (opts.app_label, opts.model_name),
                                   args=(obj.pk,),
                                   current_app=self.admin_site.name)
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)

        elif "_addanother" in request.POST:
            msg = format_html(
                _('The {name} "{obj}" was changed successfully. You may add another {name} below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = reverse('admin:%s_%s_add' %
                                   (opts.app_label, opts.model_name),
                                   current_app=self.admin_site.name)
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)

        else:
            msg = format_html(
                _('The {name} "{obj}" was changed successfully.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            # 只能写在这里，不能写在save_model中，那边的obj中的数据是历史的
            # 向flask 服务中发送数据 注: 因django中使用locust出现猴子补丁问题 所以用此方法比较合适
            # 此方法禁用 改成动态获取更为合理
            # api_test_instance = ApiTestInstance(obj)
            # test_id, test_data = get_api_test_data(api_test_instance)
            # LocustTest.objects.filter(id=test_id).update(test_data=test_data)

            return self.response_post_save_change(request, obj)


@admin.register(SeleniumTestInstance)
class SeleniumTestInstanceAdmin(admin.ModelAdmin):
    list_display = ('test_date', 'test_mode', 'host', 'locust_count', 'hatch_rate', 'run_time',
                    'max_wait', 'min_wait', 'browser_mode', 'describe', 'state')

    fields = (('test_date', 'test_mode'), ('min_wait', 'max_wait'), ('locust_count', 'hatch_rate', 'run_time'),
              ('browser_mode', 'time_out'), 'side', 'describe')

    ordering = ('-test_date',)

    search_fields = ('host', 'describe')

    def state(self, obj):
        # running = get_locust_service_state(GET_LOCUST_SERVICE_STATE_URL % obj.id)
        if obj.running_status:
            a_label = '<a href="%s" target="_blank" style="color: red">正在运行中 >>> </a>' % (INDEX_URL % obj.id)
        else:
            a_label = '<a href="%s" target="_blank" style="color: green">未运行 >>> </a>' % (INDEX_URL % obj.id)
        return format_html(a_label)

    state.short_description = "状态"

    def response_add(self, request, obj, post_url_continue=None):
        """
        Determine the HttpResponse for the add_view stage.
        """
        opts = obj._meta
        preserved_filters = self.get_preserved_filters(request)
        obj_url = reverse(
            'admin:%s_%s_change' % (opts.app_label, opts.model_name),
            args=(quote(obj.pk),),
            current_app=self.admin_site.name,
        )
        # Add a link to the object's change form if the user can edit the obj.
        if self.has_change_permission(request, obj):
            obj_repr = format_html('<a href="{}">{}</a>', urlquote(obj_url), obj)
        else:
            obj_repr = str(obj)
        msg_dict = {
            'name': opts.verbose_name,
            'obj': obj_repr,
        }
        # Here, we distinguish between different save types by checking for
        # the presence of keys in request.POST.

        if IS_POPUP_VAR in request.POST:
            to_field = request.POST.get(TO_FIELD_VAR)
            if to_field:
                attr = str(to_field)
            else:
                attr = obj._meta.pk.attname
            value = obj.serializable_value(attr)
            popup_response_data = json.dumps({
                'value': str(value),
                'obj': str(obj),
            })
            return TemplateResponse(request, self.popup_response_template or [
                'admin/%s/%s/popup_response.html' % (opts.app_label, opts.model_name),
                'admin/%s/popup_response.html' % opts.app_label,
                'admin/popup_response.html',
            ], {
                                        'popup_response_data': popup_response_data,
                                    })

        elif "_continue" in request.POST or (
                # Redirecting after "Save as new".
                "_saveasnew" in request.POST and self.save_as_continue and
                self.has_change_permission(request, obj)
        ):
            msg = _('The {name} "{obj}" was added successfully.')
            if self.has_change_permission(request, obj):
                msg += ' ' + _('You may edit it again below.')
            self.message_user(request, format_html(msg, **msg_dict), messages.SUCCESS)
            if post_url_continue is None:
                post_url_continue = obj_url
            post_url_continue = add_preserved_filters(
                {'preserved_filters': preserved_filters, 'opts': opts},
                post_url_continue
            )
            return HttpResponseRedirect(post_url_continue)

        elif "_addanother" in request.POST:
            msg = format_html(
                _('The {name} "{obj}" was added successfully. You may add another {name} below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = request.path
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)

        else:
            msg = format_html(
                _('The {name} "{obj}" was added successfully.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)

            # 只能写在这里，不能写在save_model中，那边的obj中的数据是历史的
            # 向flask 服务中发送数据 注: 因django中使用locust出现猴子补丁问题 所以用此方法比较合适
            # 此方法禁用 改成动态获取更为合理
            # side_test_instance = SideTestInstance(obj)
            # test_id, test_data = get_side_test_data(side_test_instance)
            # LocustTest.objects.create(id=test_id, test_data=test_data)
            return self.response_post_save_add(request, obj)

    def response_change(self, request, obj):
        """
        Determine the HttpResponse for the change_view stage.
        """

        if IS_POPUP_VAR in request.POST:
            opts = obj._meta
            to_field = request.POST.get(TO_FIELD_VAR)
            attr = str(to_field) if to_field else opts.pk.attname
            value = request.resolver_match.kwargs['object_id']
            new_value = obj.serializable_value(attr)
            popup_response_data = json.dumps({
                'action': 'change',
                'value': str(value),
                'obj': str(obj),
                'new_value': str(new_value),
            })
            return TemplateResponse(request, self.popup_response_template or [
                'admin/%s/%s/popup_response.html' % (opts.app_label, opts.model_name),
                'admin/%s/popup_response.html' % opts.app_label,
                'admin/popup_response.html',
            ], {
                                        'popup_response_data': popup_response_data,
                                    })

        opts = self.model._meta
        preserved_filters = self.get_preserved_filters(request)

        msg_dict = {
            'name': opts.verbose_name,
            'obj': format_html('<a href="{}">{}</a>', urlquote(request.path), obj),
        }
        if "_continue" in request.POST:
            msg = format_html(
                _('The {name} "{obj}" was changed successfully. You may edit it again below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = request.path
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)

        elif "_saveasnew" in request.POST:
            msg = format_html(
                _('The {name} "{obj}" was added successfully. You may edit it again below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = reverse('admin:%s_%s_change' %
                                   (opts.app_label, opts.model_name),
                                   args=(obj.pk,),
                                   current_app=self.admin_site.name)
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)

        elif "_addanother" in request.POST:
            msg = format_html(
                _('The {name} "{obj}" was changed successfully. You may add another {name} below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = reverse('admin:%s_%s_add' %
                                   (opts.app_label, opts.model_name),
                                   current_app=self.admin_site.name)
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)

        else:
            msg = format_html(
                _('The {name} "{obj}" was changed successfully.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            # 只能写在这里，不能写在save_model中，那边的obj中的数据是历史的
            # 向flask 服务中发送数据 注: 因django中使用locust出现猴子补丁问题 所以用此方法比较合适
            # 此方法禁用 改成动态获取更为合理
            # side_test_instance = SideTestInstance(obj)
            # test_id, test_data = get_side_test_data(side_test_instance)
            # LocustTest.objects.filter(id=test_id).update(test_data=test_data)

            return self.response_post_save_change(request, obj)
