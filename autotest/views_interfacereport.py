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
    # 关键修复：DataTables通过POST发送数据，必须用request.POST读取
    product_filter = request.POST.get('product_filter', '') or request.GET.get('product_filter', '')
    
    print(f"[DEBUG] loadReport - username: {username}, product_filter: '{product_filter}'")
    
    # 检查用户是否登录
    if not username:
        return JsonResponse({'data': []})
    
    user_obj = AuthUser.objects.filter(username=username).first()
    if not user_obj:
        return JsonResponse({'data': []})
    
    if user_obj.is_superuser == 1:
        if product_filter and product_filter != '':
            print(f"[DEBUG] 超级管理员 - 过滤产品: {product_filter}")
            items = AutotestplatTestplanInterfaceResult.objects.filter(product_name=product_filter).values_list(
                'report_id','product_id','product_name', 'suit_name', 'date_time',
                'task_mode').annotate(Count('id')).order_by('-date_time')
        else:
            print(f"[DEBUG] 超级管理员 - 显示所有产品")
            items = AutotestplatTestplanInterfaceResult.objects.all().values_list(
                'report_id','product_id','product_name', 'suit_name', 'date_time',
                'task_mode').annotate(Count('id')).order_by('-date_time')
    else:
        product_id = user_obj.last_name
        print(f"[DEBUG] 普通用户 - product_id: {product_id}")
        items = []
        result = AutotestplatTestplanInterfaceResult.objects.filter(
            product_id=product_id).values_list(
            'report_id','product_id','product_name', 'suit_name', 'date_time',
            'task_mode').annotate(Count('id')).order_by('-date_time')
        if result:
            items +=result
    
    rst = []
    for item in items:
        report_id = item[0]
        product_id_db = item[1]
        product_name = item[2]
        suit_name = item[3]
        date_time = item[4]
        task_mode = item[5]
        
        total_count = item[6]
        pass_count = AutotestplatTestplanInterfaceResult.objects.filter(
            report_id=report_id, result=0).count()
        
        if total_count > 0:
            pass_pers = '{:.0%}'.format(pass_count / total_count)
        else:
            pass_pers = '0%'
        
        arr = [report_id, product_name, date_time, total_count, pass_pers]
        rst.append(arr)
    
    print(f"[DEBUG] 返回报告数量: {len(rst)}")
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

