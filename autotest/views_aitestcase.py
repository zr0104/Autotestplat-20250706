# -*- coding:utf-8 -*-
############################################
#Auther:：Sen
#Version：Autotestplat-V6.0
############################################
import time,json,os
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
from django.db.models import Q
from django.template.context_processors import csrf
from django.shortcuts import render
from .models import *
current_dir = os.getcwd()


def getAiView(request):
    user_name = request.session.get('user', '')
    product_all = AutotestplatProduct.objects.filter(delete_flag='N')
    product_id = AuthUser.objects.filter(username=user_name).first().last_name
    product_name = AutotestplatProduct.objects.filter(id=product_id).first().product_name
    c = csrf(request)
    c.update({"product_name":product_name,"product_alls":product_all})
    return render(request,"ai_testcase.html",c)

@csrf_exempt
def loadAiTestcaseTable(request):
    username = request.session.get('user', '')
    if AuthUser.objects.filter(username=username).first().is_superuser == 1:
        items = AutotestplatAiTestcase.objects.all().values_list('ai_testcase_code','ai_testcase_name','ai_testcase_result','creator','create_time','product_id','requirements_id').annotate(Count('id'))
    else:
        user_product_id = AuthUser.objects.filter(username=username).first().last_name
        if user_product_id:
            items = AutotestplatAiTestcase.objects.filter(Q(product_id=user_product_id)).values_list('ai_testcase_code','ai_testcase_name','ai_testcase_result','creator','create_time','product_id','requirements_id').annotate(Count('id'))
        else:
            items = AutotestplatAiTestcase.objects.all().values_list('ai_testcase_code','ai_testcase_name','ai_testcase_result','creator','create_time','product_id','requirements_id').annotate(Count('id'))

    rst = []
    for item in items:
        arr = []
        tmp_ids = AutotestplatProduct.objects.all().values_list().order_by('id')
        tmp = []
        for tmp_id in tmp_ids:
            tmp.append(tmp_id[0])
        
        product_id_value = item[5]
        if product_id_value is None or product_id_value == '':
            count = 0
        else:
            try:
                count = tmp.count(int(product_id_value))
            except (ValueError, TypeError):
                count = 0
        
        if count > 0:
            try:
                product_name = AutotestplatProduct.objects.filter(id=int(product_id_value)).first().product_name
                item_list = list(item)
                item_list[5] = product_name
                item = tuple(item_list)
            except (ValueError, TypeError):
                pass
        
        for j in item:
            arr.append(j)
        rst.append(arr)
    realRst = {'data': rst}
    return JsonResponse(realRst)


def loadretoAiTestcaseTable(request,require_id):
    username = request.session.get('user', '')
    if AuthUser.objects.filter(username=username).first().is_superuser == 1:
        items = AutotestplatAiTestcase.objects.all().values_list('id','testcase_title','testcase_step','expect_result','result','charger','create_time','product_id').annotate(Count('id')).order_by('id')
    else:
        user_product_id = AuthUser.objects.filter(username=username).first().last_name
        if user_product_id:
            items = AutotestplatAiTestcase.objects.filter(Q(product_id=user_product_id)).filter(requirements_id=require_id).values_list('id','testcase_title','testcase_step','expect_result','result','charger','create_time','product_id').annotate(Count('id')).order_by('id')
        else:
            items = AutotestplatAiTestcase.objects.filter(requirements_id=require_id).values_list('id','testcase_title','testcase_step','expect_result','result','charger','create_time','product_id').annotate(Count('id')).order_by('id')

    rst = []
    for item in items:
        arr = []
        tmp_ids = AutotestplatProduct.objects.all().values_list().order_by('id')
        tmp = []
        for tmp_id in tmp_ids:
            tmp.append(tmp_id[0])
        if (item[5] == None):
            count = 0
        else:
            count = tmp.count(int(item[5]))
        if count > 0:
            product_name = AutotestplatProduct.objects.filter(id=int(item[5])).first().product_name
            item_list = list(item)
            item_list[5] = product_name
            item = tuple(item_list)
        for j in item:
            arr.append(j)
        rst.append(arr)
    realRst = {'data': rst}
    return JsonResponse(realRst)

@csrf_exempt
def addAitestcase(request):
    ai_testcase_code = str(int(time.time()))
    username = request.session.get('user', '')
    if AuthUser.objects.filter(username=username).first().is_superuser == 1:
        product_id = ''
    else:
        product_id = AuthUser.objects.filter(username=username).first().last_name
    ai_testcase_result = '未执行'
    create_time = str(time.strftime("%Y-%m-%d %H:%M:%S"))
    ai_testcase_name = request.POST.get('ai_testcase_name')
    ai_testcase_step = request.POST.getlist('caseStepList[]')
    ai_testcase_stepname = request.POST.getlist('caseStepList_objname[]')
    ai_testcase_expect_value = request.POST.getlist('caseStepList_findmethod[]')
    delete_flag = 'N'
    for i in range(len(ai_testcase_step)):
       id = str(datetime.now().strftime("%Y%m%d%H%M%S%f"))
       aitestcase_step = ai_testcase_step[i]
       aitestcase_stepname = ai_testcase_stepname[i]
       aitestcase_expect_value = ai_testcase_expect_value[i]
       aitestcase_real_value = ''
       aitestcase_step_result=''
       time.sleep(2)
       AutotestplatAiTestcase.objects.create(id=id, ai_testcase_code=ai_testcase_code,ai_testcase_name=ai_testcase_name,ai_testcase_result=ai_testcase_result,creator=username,product_id=product_id,ai_testcase_step=aitestcase_step,ai_testcase_stepname=aitestcase_stepname,ai_testcase_expect_value=aitestcase_expect_value,ai_testcase_real_value=aitestcase_real_value,ai_testcase_step_result=aitestcase_step_result,create_time=create_time,delete_flag=delete_flag)
    return HttpResponse('200')

@csrf_exempt
def loadAiOptions(request):
    aicase_result = []
    results = AutotestplatAiTestcase.objects.values('ai_testcase_result').distinct()
    for re in results:
        aicase_result.append(re['ai_testcase_result'])
    rst = [aicase_result]
    return JsonResponse(rst, safe=False)

@csrf_exempt
def deleteAitestcase(request):
    ai_testcase_code = request.POST.get('ai_testcase_code')
    AutotestplatAiTestcase.objects.filter(ai_testcase_code=ai_testcase_code).delete()
    return HttpResponse('200')

def showModAiTestcase(request):
    if request.method == "POST":
        raw_data = request.body
        raw_data = json.loads(raw_data)
        id = raw_data['id1']
        name = raw_data['name1']
        requirements_id = raw_data['requirements_id1']
        case_infos = AutotestplatAiTestcase.objects.filter(ai_testcase_code=id)
        case_step_list = ''
        objname = ''
        findmethod = ''
        for index, case in enumerate(case_infos):
            if index == len(case_infos) - 1:
                case_step_list += case.ai_testcase_step
                objname +=case.ai_testcase_stepname
                findmethod +=case.ai_testcase_expect_value
            else:
                case_step_list += case.ai_testcase_step + ','
                objname += case.ai_testcase_stepname + ','
                findmethod += case.ai_testcase_expect_value + ','
        case_info = {'id': id,
                     'name': name,
                     'requirements_id':requirements_id,
                     'case_step_list':case_step_list,
                     'objname':objname,
                     'findmethod': findmethod,
                    }
        return HttpResponse(json.dumps(case_info), content_type='application/json')


def showRunAiTestcase(request):
    if request.method == "POST":
        raw_data = request.body
        raw_data = json.loads(raw_data)
        id = raw_data['id1']
        name = raw_data['name1']
        requirements_id = raw_data['requirements_id1']
        result = AutotestplatAiTestcase.objects.filter(ai_testcase_code=id).first().ai_testcase_result

        case_info = {'id': id,
                     'name': name,
                     'requirements_id':requirements_id,
                    }
        return HttpResponse(json.dumps(case_info), content_type='application/json')


def showCopyAiTestcase(request):
    if request.method == "POST":
        raw_data = request.body
        raw_data = json.loads(raw_data)
        id = raw_data['id1']
        name = raw_data['name1']
        case_infos = AutotestplatAiTestcase.objects.filter(ai_testcase_code=id)
        case_step_list = ''
        objname = ''
        findmethod = ''
        for index, case in enumerate(case_infos):
            if index == len(case_infos) - 1:
                case_step_list += case.ai_testcase_step
                objname +=case.ai_testcase_stepname
                findmethod +=case.ai_testcase_expect_value
            else:
                case_step_list += case.ai_testcase_step + ','
                objname += case.ai_testcase_stepname + ','
                findmethod += case.ai_testcase_expect_value + ','

        case_info = {'id': id,
                     'name': name,
                     'case_step_list':case_step_list,
                     'objname':objname,
                     'findmethod': findmethod,
                    }
        return HttpResponse(json.dumps(case_info), content_type='application/json')


@csrf_exempt
def modAitestcase(request):
    if request.method == "POST":
        raw_data = request.body
        raw_data = json.loads(raw_data)
        print(raw_data)
        id = raw_data['moddataObj']['id1']
        ai_testcase_code = id
        username = request.session.get('user', '')
        if AuthUser.objects.filter(username=username).first().is_superuser == 1:
            product_id = ''
        else:
            product_id = AuthUser.objects.filter(username=username).first().last_name
        ai_testcase_result = '未执行'
        create_time = str(time.strftime("%Y-%m-%d %H:%M:%S"))
        ai_testcase_name = raw_data['moddataObj']['ai_testcase_name']
        requirements_id = raw_data['moddataObj']['requirements_id']
        print(ai_testcase_name)
        delete_flag = 'N'
        AutotestplatAiTestcase.objects.filter(ai_testcase_code=ai_testcase_code).delete()
        time.sleep(1)
        for i in range(len(raw_data['moddataObj']['modcaseStepList'])):
            id = str(datetime.now().strftime("%Y%m%d%H%M%S%f"))
            testcase_step = raw_data['moddataObj']['modcaseStepList'][i]
            testcase_objname = raw_data['moddataObj']['modcaseStepList_objname'][i]
            testcase_findmethod = raw_data['moddataObj']['modcaseStepList_findmethod'][i]
            time.sleep(1)
            modAiTestcase = AutotestplatAiTestcase(id=id,ai_testcase_code=ai_testcase_code,ai_testcase_name=ai_testcase_name,
                                               ai_testcase_result=ai_testcase_result, creator=username,create_time=create_time,
                                               product_id=product_id, ai_testcase_step=testcase_step,
                                               ai_testcase_stepname=testcase_objname,
                                               ai_testcase_expect_value=testcase_findmethod,
                                               requirements_id=requirements_id,
                                               delete_flag=delete_flag)
            modAiTestcase.save()
        return HttpResponse('200')


@csrf_exempt
def copyAitestcase(request):
    if request.method == "POST":
        raw_data = request.body
        raw_data = json.loads(raw_data)
        ai_testcase_code = str(int(time.time()))
        username = request.session.get('user', '')
        if AuthUser.objects.filter(username=username).first().is_superuser == 1:
            product_id = ''
        else:
            product_id = AuthUser.objects.filter(username=username).first().last_name
        ai_testcase_result = '未执行'
        create_time = str(time.strftime("%Y-%m-%d %H:%M:%S"))
        ai_testcase_name = raw_data['copydataObj']['ai_testcase_name']
        delete_flag = 'N'
        time.sleep(1)
        for i in range(len(raw_data['copydataObj']['copycaseStepList'])):
            id = str(datetime.now().strftime("%Y%m%d%H%M%S%f"))
            testcase_step = raw_data['copydataObj']['copycaseStepList'][i]
            testcase_objname = raw_data['copydataObj']['copycaseStepList_objname'][i]
            testcase_findmethod = raw_data['copydataObj']['copycaseStepList_findmethod'][i]
            time.sleep(1)
            copyAiTestcase = AutotestplatAiTestcase(id=id,ai_testcase_code=ai_testcase_code,ai_testcase_name=ai_testcase_name,
                                               ai_testcase_result=ai_testcase_result, creator=username,create_time=create_time,
                                               product_id=product_id, ai_testcase_step=testcase_step,
                                               ai_testcase_stepname=testcase_objname,
                                               ai_testcase_expect_value=testcase_findmethod,
                                               delete_flag=delete_flag)
            copyAiTestcase.save()
        return HttpResponse('200')

@csrf_exempt
def runAitestcase(request):
    raw_data = request.body
    raw_data = json.loads(raw_data)
    ai_testcase_code = raw_data['rundataObj']['id1']
    ai_testcase_result = raw_data['rundataObj']['ai_testcase_result']
    time.sleep(1)
    AutotestplatAiTestcase.objects.filter(ai_testcase_code=ai_testcase_code).update(ai_testcase_result=ai_testcase_result)
    return HttpResponse('200')


