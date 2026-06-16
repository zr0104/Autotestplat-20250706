# -*- coding:utf-8 -*-
############################################
#Auther:：Sen
#Version：Autotestplat-V6.0
############################################
import re,time,random,json
from .models import *
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.template.context_processors import csrf
from django.shortcuts import render
from .views_user import *
from django.contrib.auth import get_user_model

def testReportView(request):
    user_name = request.session.get('user', '')
    product_all = AutotestplatProduct.objects.filter(delete_flag='N')
    product_id = AuthUser.objects.filter(username=user_name).first().last_name
    product_name = AutotestplatProduct.objects.filter(id=product_id).first().product_name
    c = csrf(request)
    c.update({"product_name":product_name,"product_alls":product_all})
    return render(request,"report.html",c)

@csrf_exempt
def loadTestReport(request):
    items = AutotestplatTestReport.objects.exclude(delete_flag='Y').values_list().order_by('id')
    rst = []
    for item in items:
        arr = []
        for j in item:
            arr.append(j)
        rst.append(arr)
    realRst = {'data': rst}
    print(realRst)
    return JsonResponse(realRst)

@csrf_exempt
def addTestReport(request):
    iteration_version = request.POST.get('iteration_version')
    progress = request.POST.get('progress')
    result = request.POST.get('result')
    creator = request.session.get('user', '')
    delete_flag = 'N'
    iteration_version_exist = AutotestplatTestReport.objects.filter(iteration_version=iteration_version).first()
    if iteration_version_exist:
        return HttpResponse(f'产品”{iteration_version}“已存在，请重新填写')
    AutotestplatTestReport.objects.create(iteration_version=iteration_version, progress=progress, result=result,creator=creator,delete_flag=delete_flag)
    return HttpResponse('200')

@csrf_exempt
def deleteTestReport(request):
    id = request.POST.get('id')
    delete_flag = 'Y'
    sn = AuthUser.objects.filter(last_name=id)
    if sn:
        return HttpResponse(f'在用户设置中，有人设置了默认正使用该产品，不能删除！')
    AutotestplatTestReport.objects.filter(id=id).update(delete_flag=delete_flag)
    return HttpResponse('200')

@csrf_exempt
def updateTestReport(request):
    id = request.POST.get('id')
    iteration_version = request.POST.get('iteration_version')
    progress = request.POST.get('progress')
    result = request.POST.get('result')
    if AutotestplatTestReport.objects.exclude(id=id).filter(iteration_version=iteration_version).exists():
        return HttpResponse(f'产品”{iteration_version}“重复，请重新填写')
    AutotestplatTestReport.objects.filter(testreport_id=id).update(testreport_id=id,iteration_version=iteration_version,progress=progress,result=result)
    return HttpResponse('200')


@csrf_exempt
def getTestReportDetail(request,testreport_id):
    items = AutotestplatTestReport.objects.filter(id=testreport_id).all().order_by('id')
    testreport_id = testreport_id
    iteration_version = items.first().iteration_version
    product_id = items.first().product_id
    require_nums = items.first().require_nums
    testcase_nums = ''
    bug_nums = ''
    progress = ''
    result = 'pass'
    create_time = items.first().create_time
    return render(request, "report_detail.html",{"test_result": items,"id":testreport_id,"iteration_version":iteration_version,"require_nums":require_nums,"testcase_nums":testcase_nums,"bug_nums":bug_nums,"progress":progress,"result":result,"create_time":create_time,'product_name':product_id})


