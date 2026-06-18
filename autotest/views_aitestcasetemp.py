# -*- coding:utf-8 -*-
############################################
#Auther:：Sen
#Version：Autotestplat-V6.0
############################################
import time,json,os,re
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
    return render(request,"ai_testcase_temp.html",c)

@csrf_exempt
def loadAiTestcaseTable(request):
    username = request.session.get('user', '')
    
    print(f"========== 加载AI测试用例列表 ==========")
    print(f"用户名: {username}")
    
    # 获取所有唯一的 ai_testcase_code（按最新时间排序）
    if AuthUser.objects.filter(username=username).first().is_superuser == 1:
        print("用户是超级管理员")
        # 先按 create_time 降序排列，然后按 ai_testcase_code 分组取第一条
        from django.db.models import Max
        latest_ids = AutotestplatAiTestcaseTemp.objects.values('ai_testcase_code').annotate(
            max_id=Max('id')
        ).values_list('max_id', flat=True)
        items = AutotestplatAiTestcaseTemp.objects.filter(id__in=latest_ids).values_list(
            'ai_testcase_code','ai_testcase_name','ai_testcase_result','creator','create_time','product_id','requirements_id'
        ).order_by('-create_time')
        print(f"查询到 {len(items)} 条记录")
    else:
        user_product_id = AuthUser.objects.filter(username=username).first().last_name
        print(f"用户产品ID: {user_product_id}")
        if user_product_id:
            from django.db.models import Max
            latest_ids = AutotestplatAiTestcaseTemp.objects.filter(product_id=user_product_id).values('ai_testcase_code').annotate(
                max_id=Max('id')
            ).values_list('max_id', flat=True)
            items = AutotestplatAiTestcaseTemp.objects.filter(id__in=latest_ids).values_list(
                'ai_testcase_code','ai_testcase_name','ai_testcase_result','creator','create_time','product_id','requirements_id'
            ).order_by('-create_time')
            print(f"按产品ID过滤后查询到 {len(items)} 条记录")
        else:
            from django.db.models import Max
            latest_ids = AutotestplatAiTestcaseTemp.objects.values('ai_testcase_code').annotate(
                max_id=Max('id')
            ).values_list('max_id', flat=True)
            items = AutotestplatAiTestcaseTemp.objects.filter(id__in=latest_ids).values_list(
                'ai_testcase_code','ai_testcase_name','ai_testcase_result','creator','create_time','product_id','requirements_id'
            ).order_by('-create_time')
            print(f"无产品ID过滤，查询到 {len(items)} 条记录")

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
    print(f"返回 {len(rst)} 条记录给前端")
    print(f"========== 加载完成 ==========")
    return JsonResponse(realRst)


def loadretoAiTestcaseTable(request,require_id):
    username = request.session.get('user', '')
    if AuthUser.objects.filter(username=username).first().is_superuser == 1:
        items = AutotestplatAiTestcaseTemp.objects.all().values_list('id','testcase_title','testcase_step','expect_result','result','charger','create_time','product_id').annotate(Count('id')).order_by('id')
    else:
        user_product_id = AuthUser.objects.filter(username=username).first().last_name
        if user_product_id:
            items = AutotestplatAiTestcaseTemp.objects.filter(Q(product_id=user_product_id)).filter(requirements_id=require_id).values_list('id','testcase_title','testcase_step','expect_result','result','charger','create_time','product_id').annotate(Count('id')).order_by('id')
        else:
            items = AutotestplatAiTestcaseTemp.objects.filter(requirements_id=require_id).values_list('id','testcase_title','testcase_step','expect_result','result','charger','create_time','product_id').annotate(Count('id')).order_by('id')

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
       AutotestplatAiTestcaseTemp.objects.create(id=id, ai_testcase_code=ai_testcase_code,ai_testcase_name=ai_testcase_name,ai_testcase_result=ai_testcase_result,creator=username,product_id=product_id,ai_testcase_step=aitestcase_step,ai_testcase_stepname=aitestcase_stepname,ai_testcase_expect_value=aitestcase_expect_value,ai_testcase_real_value=aitestcase_real_value,ai_testcase_step_result=aitestcase_step_result,create_time=create_time,delete_flag=delete_flag)
    return HttpResponse('200')

@csrf_exempt
def saveAiTestcaseFromChat(request):
    """从AI对话保存测试用例到临时表"""
    import json
    import re
    import uuid
    
    try:
        # 获取参数
        ai_testcase_code = request.POST.get('ai_testcase_code', str(int(time.time())))
        ai_testcase_name = request.POST.get('ai_testcase_name', '')
        ai_testcase_result = request.POST.get('ai_testcase_result', '')
        requirements_id = request.POST.get('requirements_id', '')
        product_id = request.POST.get('product_id', '')
        
        username = request.session.get('user', '')
        if not username:
            return HttpResponse('用户未登录', status=401)
        
        # 处理 product_id
        if AuthUser.objects.filter(username=username).first().is_superuser == 1:
            product_id = ''  # 超级管理员不需要 product_id
        else:
            if not product_id:
                user_product_id = AuthUser.objects.filter(username=username).first().last_name
                product_id = user_product_id if user_product_id else ''
        
        create_time = str(time.strftime("%Y-%m-%d %H:%M:%S"))
        delete_flag = 'N'
        
        # 处理 requirements_id
        req_id_value = None
        if requirements_id and requirements_id.strip() != '':
            try:
                req_id_value = int(requirements_id)
            except ValueError:
                req_id_value = None
        
        print(f"========== 保存AI测试用例 ==========")
        print(f"用例编码: {ai_testcase_code}")
        print(f"用例名称: {ai_testcase_name}")
        print(f"用户名: {username}")
        print(f"产品ID: {product_id}")
        print(f"需求ID: {req_id_value}")
        print(f"步骤文本:\n{ai_testcase_result}")
        
        # 解析步骤和预期结果（支持前端实际发送的格式）
        steps = []
        expected_results = []
        lines = ai_testcase_result.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 匹配 "步骤X：" 或 "步骤X:"
            step_match = re.search(r'^步骤\d+[:：]\s*(.+)$', line)
            if step_match:
                steps.append(step_match.group(1).strip())
            
            # 匹配 "预期结果X：" 或 "预期结果X:"
            expected_match = re.search(r'^预期结果\d+[:：]\s*(.+)$', line)
            if expected_match:
                expected_results.append(expected_match.group(1).strip())
        
        min_len = min(len(steps), len(expected_results))
        print(f"解析到 {len(steps)} 个步骤，{len(expected_results)} 个预期结果")
        print(f"将保存 {min_len} 条记录")
        
        created_count = 0
        for i in range(min_len):
            # 使用 UUID 确保唯一性
            unique_id = str(uuid.uuid4()).replace('-', '')[:16]
            id = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{unique_id}_{i}"
            
            # 提取步骤名称（取步骤内容的前20个字符作为步骤名称）
            step_content = steps[i]
            step_name = step_content[:20] if len(step_content) > 20 else step_content
            
            obj = AutotestplatAiTestcaseTemp.objects.create(
                id=id,
                ai_testcase_code=ai_testcase_code,
                ai_testcase_name=ai_testcase_name,
                ai_testcase_result='未执行',
                creator=username,
                product_id=product_id if product_id else None,
                ai_testcase_step=step_content,  # 完整步骤内容
                ai_testcase_stepname=step_name,  # 步骤名称（简短描述）
                ai_testcase_expect_value=expected_results[i],
                ai_testcase_real_value='',
                ai_testcase_step_result='',
                requirements_id=req_id_value,
                create_time=create_time,
                delete_flag=delete_flag
            )
            created_count += 1
            print(f"创建记录 {i+1}: ID={id}, 步骤名={step_name}, 步骤={step_content[:30]}...")
        
        print(f"========== 成功创建 {created_count} 条记录 ==========")
        return HttpResponse('200')
    
    except Exception as e:
        print(f"保存AI测试用例失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f'保存失败：{str(e)}', status=500)

@csrf_exempt
def loadAiOptions(request):
    aicase_result = []
    results = AutotestplatAiTestcaseTemp.objects.values('ai_testcase_result').distinct()
    for re in results:
        aicase_result.append(re['ai_testcase_result'])
    rst = [aicase_result]
    return JsonResponse(rst, safe=False)

@csrf_exempt
def deleteAitestcase(request):
    ai_testcase_code = request.POST.get('ai_testcase_code')
    AutotestplatAiTestcaseTemp.objects.filter(ai_testcase_code=ai_testcase_code).delete()
    return HttpResponse('200')

def showModAiTestcase(request):
    if request.method == "POST":
        raw_data = request.body
        raw_data = json.loads(raw_data)
        id = raw_data['id1']
        name = raw_data['name1']
        requirements_id = raw_data['requirements_id1']
        case_infos = AutotestplatAiTestcaseTemp.objects.filter(ai_testcase_code=id)
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
        result = AutotestplatAiTestcaseTemp.objects.filter(ai_testcase_code=id).first().ai_testcase_result

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
        AutotestplatAiTestcaseTemp.objects.filter(ai_testcase_code=ai_testcase_code).delete()
        time.sleep(1)
        
        modcaseStepList = raw_data['moddataObj']['modcaseStepList']
        modcaseStepList_objname = raw_data['moddataObj']['modcaseStepList_objname']
        modcaseStepList_findmethod = raw_data['moddataObj']['modcaseStepList_findmethod']
        
        min_length = min(len(modcaseStepList), len(modcaseStepList_objname), len(modcaseStepList_findmethod))
        
        for i in range(min_length):
            id = str(datetime.now().strftime("%Y%m%d%H%M%S%f"))
            testcase_step = modcaseStepList[i]
            testcase_objname = modcaseStepList_objname[i] if i < len(modcaseStepList_objname) else ''
            testcase_findmethod = modcaseStepList_findmethod[i] if i < len(modcaseStepList_findmethod) else ''
            
            if not testcase_objname or not testcase_findmethod:
                continue
                
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
        
        copycaseStepList = raw_data['copydataObj']['copycaseStepList']
        copycaseStepList_objname = raw_data['copydataObj']['copycaseStepList_objname']
        copycaseStepList_findmethod = raw_data['copydataObj']['copycaseStepList_findmethod']
        
        min_length = min(len(copycaseStepList), len(copycaseStepList_objname), len(copycaseStepList_findmethod))
        
        for i in range(min_length):
            id = str(datetime.now().strftime("%Y%m%d%H%M%S%f"))
            testcase_step = copycaseStepList[i]
            testcase_objname = copycaseStepList_objname[i] if i < len(copycaseStepList_objname) else ''
            testcase_findmethod = copycaseStepList_findmethod[i] if i < len(copycaseStepList_findmethod) else ''
            
            if not testcase_objname or not testcase_findmethod:
                continue
                
            time.sleep(1)
            copyAiTestcase = AutotestplatAiTestcaseTemp(id=id,ai_testcase_code=ai_testcase_code,ai_testcase_name=ai_testcase_name,
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
    AutotestplatAiTestcaseTemp.objects.filter(ai_testcase_code=ai_testcase_code).update(ai_testcase_result=ai_testcase_result)
    return HttpResponse('200')


