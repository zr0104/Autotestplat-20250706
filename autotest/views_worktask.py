# -*- coding:utf-8 -*-
############################################
#Auther:：Fin
#Version：Autotestplat-V6.0
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

def worktaskView(request):
    user_name = request.session.get('user', '')
    product_all = AutotestplatProduct.objects.filter(delete_flag='N')
    product_id = AuthUser.objects.filter(username=user_name).first().last_name
    product_name = AutotestplatProduct.objects.filter(id=product_id).first().product_name
    weeks_all = AutotestplatParameter.objects.filter(keywords__contains="week").order_by("-id")
    week = AutotestplatParameter.objects.filter(keywords__contains="week").last()
    if week is None:
        value = ''
    else:
        value = week.name +":"+ week.value
    c = csrf(request)
    c.update({"product_name": product_name, "product_alls": product_all, "value": value,
              "weeks_alls": weeks_all})
    return render(request, "worktask.html", c)

@csrf_exempt
def loadWroktask(request):
    username = request.session.get('user', '')
    user_product_id = AuthUser.objects.filter(username=username).first().last_name
    this_week_no = AutotestplatParameter.objects.filter(keywords__contains="week").values_list("name", flat=True).last()
    this_week_date = AutotestplatParameter.objects.filter(keywords__contains="week").values_list("value",flat=True).last()
    this_week=this_week_no+":"+this_week_date
    items = WorkTask.objects.filter(product_id=user_product_id,wt_datetime=this_week).values_list().order_by('-id')
    rst = []
    for item in items:
        arr = []
        for j in item:
            arr.append(j)
        rst.append(arr)
    realRst = {'data': rst}
    return JsonResponse(realRst)

@csrf_exempt
def addWroktask(request):
    wt_datetime = request.POST.get('wt_datetime')
    wt_thisweek = request.POST.get('wt_thisweek')
    wt_nextweek = request.POST.get('wt_nextweek')
    question = request.POST.get('question')
    creator = request.session.get('user', '')
    product_id = AuthUser.objects.filter(username=creator).first().last_name

    thisweek_exist = WorkTask.objects.filter(wt_datetime=wt_datetime,creator=creator,product_id=product_id).first()
    if thisweek_exist:
        return HttpResponse(f'您本周”{wt_datetime}“周报已提交，不可重复提交')
    WorkTask.objects.create(wt_datetime=wt_datetime, wt_thisweek=wt_thisweek, wt_nextweek=wt_nextweek,question=question,creator=creator,product_id=product_id)
    return HttpResponse('200')

@csrf_exempt
def deleteWorktask(request):
    id = request.POST.get('id')
    delete_flag = 'Y'
    sn = AuthUser.objects.filter(last_name=id)
    if sn:
        return HttpResponse(f'在用户设置中，有人设置了默认正使用该产品，不能删除！')
    WorkTask.objects.filter(id=id).update(delete_flag=delete_flag)
    return HttpResponse('200')

@csrf_exempt
def updateWorktask(request):
    creator = request.POST.get('creator')
    wt_datetime = request.POST.get('wt_datetime')
    wt_thisweek = request.POST.get('wt_thisweek')
    wt_nextweek = request.POST.get('wt_nextweek')
    question = request.POST.get('question')
    creator = request.session.get('user', '')
    product_id = AuthUser.objects.filter(username=creator).first().last_name
    id=request.POST.get('id')
    if WorkTask.objects.exclude(id=id).filter(creator=creator,product_id=product_id).exists():
        return HttpResponse(f'您不能修改同事的周报，请重新填写')
    WorkTask.objects.filter(id=id).update(id=id,wt_datetime=wt_datetime,wt_thisweek=wt_thisweek,wt_nextweek=wt_nextweek,question=question)
    return HttpResponse('200')

@csrf_exempt
def loadOptions(request):
    week = []
    week_alls = AutotestplatParameter.objects.filter(keywords__contains="week").values('name','value').order_by("-id")
    for wk in week_alls:
        w=wk['name']+":"+wk['value']
        week.append(w)
    rst = [week]
    return JsonResponse(rst, safe=False)

@csrf_exempt
def loadWeekSearch(request):
    week = []
    week_alls = AutotestplatParameter.objects.filter(keywords__contains="week").values('name','value').order_by("-id")
    for wk in week_alls:
        w = wk['name'] + ":" + wk['value']
        week.append(w)
    rst = [week]
    return JsonResponse(rst, safe=False)