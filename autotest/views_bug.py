# -*- coding:utf-8 -*-
############################################
#Auther:：Sen
#Version：Autotestplat-V2.6
############################################
import re,time,random,json

from django.db.models import Q

from .models import *
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.template.context_processors import csrf
from django.shortcuts import render
from .views_user import *
from django.contrib.auth import get_user_model

def bugView(request):
    user_name = request.session.get('user', '')
    product_all = AutotestplatProduct.objects.filter(delete_flag='N')
    product_id = AuthUser.objects.filter(username=user_name).first().last_name
    product_name = AutotestplatProduct.objects.filter(id=product_id).first().product_name
    c = csrf(request)
    c.update({"product_name":product_name,"product_alls":product_all})
    return render(request,"bug.html",c)

@csrf_exempt
def loadBug(request):
    username = request.session.get('user', '')
    if AuthUser.objects.filter(username=username).first().is_superuser == 1:
        items = AutotestplatBug.objects.exclude(delete_flag='Y').values_list().order_by('id')
    else:
        user_product_id = AuthUser.objects.filter(username=username).first().last_name
        if user_product_id:
            items = AutotestplatBug.objects.filter(Q(product_id=user_product_id)).exclude(delete_flag='Y').values_list().order_by('id')
        else:
            items = AutotestplatBug.objects.exclude(delete_flag='Y').values_list().order_by('id')
    rst = []
    for item in items:
        arr = []
        for j in item:
            arr.append(j)
        rst.append(arr)
    realRst = {'data': rst}
    return JsonResponse(realRst)

@csrf_exempt
def addBug(request):
    bug_name = request.POST.get('bug_name')
    level = request.POST.get('level')
    bug_description = request.POST.get('bug_description')
    assigned_to = request.POST.get('assigned_to')
    status = '新建'
    create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    charger = request.session.get('user', '')
    product_id = AuthUser.objects.filter(username=charger).first().last_name
    delete_flag = 'N'
    bug_name_exist = AutotestplatBug.objects.filter(bug_name=bug_name).first()
    if bug_name_exist:
        return HttpResponse(f'产品”{bug_name}“已存在，请重新填写')
    AutotestplatBug.objects.create(bug_name=bug_name, level=level, bug_description=bug_description,assigned_to=assigned_to,status=status,charger=charger,product_id=product_id,create_time=create_time,delete_flag=delete_flag)
    return HttpResponse('200')

@csrf_exempt
def deleteBug(request):
    id = request.POST.get('id')
    delete_flag = 'Y'
    sn = AuthUser.objects.filter(last_name=id)
    if sn:
        return HttpResponse(f'在用户设置中，有人设置了默认正使用该产品，不能删除！')
    AutotestplatBug.objects.filter(id=id).update(delete_flag=delete_flag)
    return HttpResponse('200')

@csrf_exempt
def updateBug(request):
    id = request.POST.get('id')
    bug_name = request.POST.get('bug_name')
    level = request.POST.get('level')
    bug_description = request.POST.get('bug_description')
    assigned_to = request.POST.get('assigned_to')
    status = request.POST.get('status')
    if AutotestplatBug.objects.exclude(id=id).filter(bug_name=bug_name).exists():
        return HttpResponse(f'产品”{bug_name}“重复，请重新填写')
    AutotestplatBug.objects.filter(id=id).update(id=id,bug_name=bug_name,level=level,bug_description=bug_description,assigned_to=assigned_to,status=status)
    return HttpResponse('200')
