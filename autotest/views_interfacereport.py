# -*- coding:utf-8 -*-
############################################
#Auther:：Sen
#Version：Autotestplat-V2.6
############################################
import re,time,random,json,os
from .models import *
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .views_user import *
from django.contrib.auth import get_user_model
from django.db.models import Count
#from djcelery.models import PeriodicTask
from django.conf import settings
from django.http import StreamingHttpResponse
from django.template.context_processors import csrf
from django.shortcuts import render
from pdfkit import from_url
import pdfkit
def reportView(request):
    user_name = request.session.get('user', '')
    
    # 检查用户是否登录
    if not user_name:
        return redirect('/autotest/login/')
    
    # 查询用户对象并判空
    user_obj = AuthUser.objects.filter(username=user_name).first()
    if not user_obj:
        return redirect('/autotest/login/')
    
    product_all = AutotestplatProduct.objects.filter(delete_flag='N')
    product_id = user_obj.last_name
    
    # 判空处理
    if not product_id:
        product_name = ''
    else:
        product_obj = AutotestplatProduct.objects.filter(id=product_id).first()
        product_name = product_obj.product_name if product_obj else ''
    
    c = csrf(request)
    c.update({"product_name":product_name,"product_alls":product_all})
    return render(request,"interface_report.html",c)

@csrf_exempt
def loadReport(request):
    username = request.session.get('user', '')
    product_filter = request.POST.get('product_filter', '') or request.GET.get('product_filter', '')
    report_id_search = request.POST.get('report_id_search', '').strip()
    suit_name_search = request.POST.get('suit_name_search', '').strip()
    date_time_search = request.POST.get('date_time_search', '').strip()
    
    if not username:
        return JsonResponse({'data': []})
    
    user_obj = AuthUser.objects.filter(username=username).first()
    if not user_obj:
        return JsonResponse({'data': []})
    
    if user_obj.is_superuser == 1:
        qs = AutotestplatTestplanInterfaceResult.objects.all()
        if product_filter and product_filter != '':
            qs = qs.filter(product_name=product_filter)
    else:
        product_id = user_obj.last_name
        qs = AutotestplatTestplanInterfaceResult.objects.filter(product_id=product_id)
    
    items = qs.values_list(
        'report_id','product_id','product_name', 'suit_name', 'date_time',
        'task_mode').annotate(Count('id')).order_by('-date_time')
    
    rst = []
    for item in items:
        report_id = item[0]
        product_name = item[2]
        suit_name = item[3]
        date_time = item[4]
        total_count = item[6]
        
        print(f"[DEBUG] suit_name_search='{suit_name_search}', suit_name='{suit_name}', suit_name_repr={repr(suit_name)}")
        
        if report_id_search and report_id_search not in str(report_id):
            continue
        if suit_name_search and suit_name_search not in (suit_name or ''):
            print(f"[DEBUG] 过滤掉: suit_name='{suit_name}' 不包含 '{suit_name_search}'")
            continue
        if date_time_search and date_time_search not in (date_time or ''):
            continue
        
        pass_count = AutotestplatTestplanInterfaceResult.objects.filter(
            report_id=report_id, result=0).count()
        
        if total_count > 0:
            pass_pers = '{:.0%}'.format(pass_count / total_count)
        else:
            pass_pers = '0%'
        
        arr = [report_id, product_name, date_time, total_count, pass_pers]
        rst.append(arr)
    
    realRst = {'data': rst}
    return JsonResponse(realRst)

@csrf_exempt
def getReportDetail(request,report_id):
    items = AutotestplatTestplanInterfaceResult.objects.filter(report_id=report_id).all().order_by('id')
    testreport_id = report_id
    testplan_name = items.first().suit_name
    testplan_time = items.first().date_time
    product_name = items.first().product_name
    testcase_all_count = len(AutotestplatTestplanInterfaceResult.objects.filter(report_id=report_id).all().order_by('id'))
    testcase_pass_count = len(AutotestplatTestplanInterfaceResult.objects.filter(report_id=report_id).filter(result=0).order_by('id'))
    testcase_fail_count = len(AutotestplatTestplanInterfaceResult.objects.filter(report_id=report_id).filter(result=1).order_by('id'))
    testcase_norun_count = testcase_all_count-testcase_pass_count-testcase_fail_count
    testcase_pass_pers = '{:.0%}'.format(testcase_pass_count / testcase_all_count)
    return render(request, "interface_report_detail.html",{"test_result": items,"report_id":testreport_id,"testplan_name":testplan_name,"testcase_all_count":testcase_all_count,"testcase_pass_count":testcase_pass_count,"testcase_fail_count":testcase_fail_count,"testcase_norun_count":testcase_norun_count,"testcase_pass_pers":testcase_pass_pers,"testplan_time":testplan_time,'product_name':product_name})

@csrf_exempt
def deleteReport(request):
    id = request.POST.get('report_id')
    AutotestplatTestplanInterfaceResult.objects.filter(report_id=id).delete()
    return HttpResponse('200')

