# -*- coding:utf-8 -*-
############################################
#Auther:：Sen
#Version：Autotestplat-V6.0
############################################
import re,time,random,json

from django.db.models import Count, Q

from .models import *
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.template.context_processors import csrf
from django.shortcuts import render
from .views_user import *
from django.contrib.auth import get_user_model

def IterationView(request):
    user_name = request.session.get('user', '')
    product_all = AutotestplatProduct.objects.filter(delete_flag='N')
    product_id = AuthUser.objects.filter(username=user_name).first().last_name
    product_name = AutotestplatProduct.objects.filter(id=product_id).first().product_name
    c = csrf(request)
    c.update({"product_name":product_name,"product_alls":product_all})
    return render(request,"iteration.html",c)

@csrf_exempt
def loadIteration(request):
    username = request.session.get('user', '')
    if AuthUser.objects.filter(username=username).first().is_superuser == 1:
        items = AutotestplatAiIteration.objects.exclude(delete_flag='Y').values_list().order_by('id')
    else:
        user_product_id = AuthUser.objects.filter(username=username).first().last_name
        if user_product_id:
            items = AutotestplatAiIteration.objects.filter(Q(product_id=user_product_id)).exclude(delete_flag='Y').values_list().order_by('id')
        else:
            items = AutotestplatAiIteration.objects.exclude(delete_flag='Y').values_list().order_by('id')
    rst = []
    for item in items:
        arr = []
        for j in item:
            arr.append(j)
        rst.append(arr)
    realRst = {'data': rst}
    return JsonResponse(realRst)

@csrf_exempt
def addIteration(request):
    iteration_version = request.POST.get('iteration_version')
    start_time = request.POST.get('start_time')
    except_end_time = request.POST.get('except_end_time')
    end_time = ''
    progress = request.POST.get('progress')
    status = '未开始'
    creator = request.session.get('user', '')
    product_id = AuthUser.objects.filter(username=creator).first().last_name
    delete_flag = 'N'
    iteration_version_exist = AutotestplatAiIteration.objects.filter(iteration_version=iteration_version).first()
    if iteration_version_exist:
        return HttpResponse(f'产品”{iteration_version}“已存在，请重新填写')
    AutotestplatAiIteration.objects.create(iteration_version=iteration_version, start_time=start_time, except_end_time=except_end_time,end_time=end_time, creator=creator,progress=progress,status=status,product_id=product_id,delete_flag=delete_flag)
    return HttpResponse('200')

@csrf_exempt
def deleteIteration(request):
    id = request.POST.get('id')
    delete_flag = 'Y'
    sn = AuthUser.objects.filter(last_name=id)
    if sn:
        return HttpResponse(f'在用户设置中，有人设置了默认正使用该产品，不能删除！')
    AutotestplatAiIteration.objects.filter(id=id).update(delete_flag=delete_flag)
    return HttpResponse('200')

@csrf_exempt
def updateIteration(request):
    id = request.POST.get('id')
    iteration_version = request.POST.get('iteration_version')
    if AutotestplatAiIteration.objects.exclude(id=id).filter(iteration_version=iteration_version).exists():
        return HttpResponse(f'产品”{iteration_version}“重复，请重新填写')
    AutotestplatAiIteration.objects.filter(id=id).update(id=id,iteration_version=iteration_version)
    return HttpResponse('200')

@csrf_exempt
def reportIteration(request):
    report_id = str(datetime.now().strftime("%Y%m%d%H%M%S%f"))
    iteration_id = request.POST.get('id')
    iteration_version = request.POST.get('iteration_version')
    user_name = request.session.get('user', '')
    product_id = AuthUser.objects.filter(username=user_name).first().last_name
    require_nums=AutotestplatRequirements.objects.filter(iteration_version_id=iteration_id).count()
    # bug_nums=AutotestplatBug.objects.filter()
    # test_case_nums=AutotestplatAiTestcase.objects.filter()
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    if AutotestplatTestReport.objects.exclude(id=id).filter(iteration_version=iteration_version,delete_flag='N').exists():
        return HttpResponse(f'产品”{iteration_version}“重复，请重新填写')
    AutotestplatTestReport.objects.create(id=report_id,iteration_version=iteration_version,product_id=product_id,creator=user_name,create_time=now,require_nums=require_nums)
    return HttpResponse('200')


@csrf_exempt
def getReToCaseDetail(request,require_id):
    items = AutotestplatAiTestcase.objects.filter(requirements_id=require_id).values_list('ai_testcase_code','ai_testcase_name','ai_testcase_result','tester','create_time','product_id','requirements_id', named=True).annotate(Count('id'))
    reToCase_id = require_id
    for item in items:
        testcase_name = item.ai_testcase_name
        expect_result = item.ai_testcase_result
        charger = item.tester
        create_time = item.create_time
        product_id = item.product_id
    return render(request, "iteration.html",{"reToCase_result": items,"requirements_id":require_id,"testcase_name":testcase_name,"charger":charger,"create_time":create_time,"product_id":product_id})

