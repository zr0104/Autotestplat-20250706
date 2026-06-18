# -*- coding:utf-8 -*-
############################################
#Auther:：Sen
#Version：Autotestplat-V6.0
############################################

from django.db.models import Count, Q
from .views_user import *


def RequirementsView(request):
    user_name = request.session.get('user', '')
    product_all = AutotestplatProduct.objects.filter(delete_flag='N')
    product_id = AuthUser.objects.filter(username=user_name).first().last_name
    product_name = AutotestplatProduct.objects.filter(id=product_id).first().product_name
    iteration_all=AutotestplatAiIteration.objects.filter(delete_flag='N',product_id=product_id)
    iteration = AutotestplatAiIteration.objects.filter(product_id=product_id).first()
    if iteration is None:
        iteration_version_id=''
    else:
        user_iteration_version_id = AuthUser.objects.filter(username=user_name).first().first_name
        iv=AutotestplatAiIteration.objects.filter(product_id=product_id).values_list('id',flat=True)
        if user_iteration_version_id and user_iteration_version_id.strip():
            try:
                if int(user_iteration_version_id) in list(iv):
                    iteration_version_id=user_iteration_version_id
                else:
                    iteration_version_id=''
            except (ValueError, TypeError):
                iteration_version_id=''
        else:
            iteration_version_id=''
    if iteration_version_id=='':
        iteration_version=''
    else:
        iteration_version = AutotestplatAiIteration.objects.filter(id=iteration_version_id).first().iteration_version
    c = csrf(request)
    c.update({"product_name":product_name,"product_alls":product_all,"iteration_version":iteration_version,"iteration_alls":iteration_all})
    return render(request,"requirements.html",c)

@csrf_exempt
def loadRequirements(request):
    username = request.session.get('user', '')
    
    # 获取用户信息，如果不存在则返回空列表
    user_obj = AuthUser.objects.filter(username=username).first()
    if not user_obj:
        return JsonResponse({'data': []})
    
    user_product_id = user_obj.last_name
    
    # 如果用户有产品ID，只返回该产品的需求；否则返回所有需求
    if user_product_id:
        try:
            items = AutotestplatRequirements.objects.filter(
                Q(product_id=user_product_id) | Q(product_id__isnull=True)
            ).exclude(delete_flag='Y').values_list().order_by('-id')
        except:
            items = AutotestplatRequirements.objects.exclude(delete_flag='Y').values_list().order_by('-id')
    else:
        items = AutotestplatRequirements.objects.exclude(delete_flag='Y').values_list().order_by('-id')

    rst = []
    for item in items:
        arr = []
        for j in item:
            arr.append(j)
        rst.append(arr)
    realRst = {'data': rst}
    return JsonResponse(realRst)

@csrf_exempt
def addRequirements(request):
    print("=" * 50)
    print("接收到添加需求请求")
    print("POST 数据:", request.POST)
    
    iteration_version = request.POST.get('iteration_version')
    requirements_name = request.POST.get('requirements_name')
    requirements_type = request.POST.get('requirements_type')
    
    print(f"迭代版本: {iteration_version}")
    print(f"需求名称: {requirements_name}")
    print(f"需求类型: {requirements_type}")
    
    # 检查必填字段
    if not iteration_version or iteration_version.strip() == '' or iteration_version == '------':
        return HttpResponse('迭代版本不能为空！')
    if not requirements_name or requirements_name.strip() == '':
        return HttpResponse('需求描述不能为空！')
    if not requirements_type or requirements_type.strip() == '':
        return HttpResponse('需求类型不能为空！')
    
    # 检查迭代版本是否存在
    iteration_obj = AutotestplatAiIteration.objects.filter(iteration_version=iteration_version).first()
    print(f"查询迭代版本对象: {iteration_obj}")
    
    if not iteration_obj:
        # 列出所有存在的迭代版本
        all_iterations = AutotestplatAiIteration.objects.all().values_list('iteration_version', flat=True)
        print(f"数据库中存在的迭代版本: {list(all_iterations)}")
        return HttpResponse(f'迭代版本"{iteration_version}"不存在！请先在【功能测试】→【迭代版本】中创建该版本。当前可用版本：{", ".join(list(all_iterations))}')
    
    iteration_version_id = iteration_obj.id
    create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    charger = request.session.get('user', '')
    product_id = AuthUser.objects.filter(username=charger).first().last_name
    delete_flag = 'N'
    
    # 检查需求是否已存在
    requirements_name_exist = AutotestplatRequirements.objects.filter(requirements_name=requirements_name).first()
    if requirements_name_exist:
        return HttpResponse(f'需求"{requirements_name}"已存在，请重新填写')
    
    # 创建需求
    try:
        AutotestplatRequirements.objects.create(
            iteration_version_id=iteration_version_id,
            requirements_name=requirements_name, 
            requirements_type=requirements_type,
            product_id=product_id,
            charger=charger,
            create_time=create_time,
            delete_flag=delete_flag
        )
        print("需求创建成功！")
        return HttpResponse('200')
    except Exception as e:
        print(f"创建需求失败: {str(e)}")
        return HttpResponse(f'创建需求失败：{str(e)}')

@csrf_exempt
def deleteRequirements(request):
    id = request.POST.get('id')
    delete_flag = 'Y'
    sn = AuthUser.objects.filter(last_name=id)
    if sn:
        return HttpResponse(f'在用户设置中，有人设置了默认正使用该产品，不能删除！')
    AutotestplatRequirements.objects.filter(id=id).update(delete_flag=delete_flag)
    return HttpResponse('200')

@csrf_exempt
def updateRequirements(request):
    id = request.POST.get('id')
    requirements_name = request.POST.get('requirements_name')
    assigned_to = request.POST.get('assigned_to')
    print(requirements_name)
    print(assigned_to)
    if AutotestplatRequirements.objects.exclude(id=id).filter(requirements_name=requirements_name).exists():
        return HttpResponse(f'产品”{requirements_name}“重复，请重新填写')
    AutotestplatRequirements.objects.filter(id=id).update(id=id,requirements_name=requirements_name,assigned_to=assigned_to)
    return HttpResponse('200')

@csrf_exempt
def getReToCaseDetail(request,require_id):
    items = AutotestplatAiTestcase.objects.filter(requirements_id=require_id).values_list('ai_testcase_code','ai_testcase_name','ai_testcase_result','creator','create_time','product_id','requirements_id', named=True).annotate(Count('id'))
    # print(list(items))
    reToCase_id = require_id

    testcase_name = ""
    charger = ""
    create_time = ""
    user_name = request.session.get('user', '')
    product_id = AuthUser.objects.filter(username=user_name).first().last_name

    for item in items:
        testcase_name = item.ai_testcase_name
        expect_result = item.ai_testcase_result
        charger = item.creator
        create_time = item.create_time
        product_id = item.product_id
    return render(request, "requirements_to_testcase.html",{"reToCase_result": items,"requirements_id":require_id,"ai_testcase_name":testcase_name,"creator":charger,"create_time":create_time,"product_id":product_id})


import time,re
from ollama import Client

def requireTotestcase(request):
    print("to case ...")
    requirements_id = request.POST.get('id')
    requirements_name = request.POST.get('requirements_name')
    user_name = request.session.get('user', '')
    product_id = AuthUser.objects.filter(username=user_name).first().last_name
    print(requirements_name)
    client = Client(
        host='http://127.0.0.1:11434',
        headers={'x-some-header': 'some-value'}
    )

    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    deepseek_version=AutotestplatParameter.objects.filter(keywords='deepseek').first().value
    print(deepseek_version)

    prompt_value = AutotestplatParameter.objects.filter(keywords='prompt').first().value
    print(prompt_value)

    forexample="用户将提供给你一段功能需求内容，你是一个资深软件测试工程师，请你分析需求，并以等价类、边界值，错误猜测法等方法生成2到6个功能测试用例" \
               "每个功能测试用例都以 JSON 的形式输出，严格遵守以下的格式：\n\n" \
               "{" \
                    "\n \"用例标题\": <用例标题，格式为中文>," \
                    "\n \"步聚1\": <操作步聚>," \
                    "\n \"预期结果1\": <预期结果1>," \
                    "\n \"步聚2\": <操作步聚>," \
                    "\n \"预期结果2\": <预期结果2>," \
                    "\n \"步聚3\": <操作步聚>," \
                    "\n \"预期结果3\": <预期结果3>" \
                    "},"\
                    "\n{" "\n \"用例标题\": <用例标题，格式为中文>," \
                    "\n \"步聚1\": <操作步聚>," \
                    "\n \"预期结果1\": <预期结果>," \
                    "\n \"步聚2\": <操作步聚>," \
                    "\n \"预期结果2\": <预期结果>," \
                    "\n \"步聚3\": <操作步聚>," \
                    "\n \"预期结果3\": <预期结果3>" \
                "}"


    response = client.chat(model=deepseek_version,
                           messages=[
                               {
                                   "role": "system",
                                   "content": prompt_value
                               },
                               {
                                   "role": "user",
                                   "content": requirements_name
                               }
                           ]
                           )

    text = response.message.content

    answ=text.split('</think>')[1]
    answ = re.sub(r'\[|\]', '', answ)

    print(answ)

    matchs = re.findall(r'\{([^{}]*)\}', answ)
    print(matchs)
    for match in matchs:
        data="{"+match+"}"
        print(data)

        case_title_pattern = r'"用例标题"\s*:\s*"([^"\n]+)"[^,]*'
        case_title_match = re.search(case_title_pattern, data)
        if case_title_match:
            case_title = case_title_match.group(1)
        else:
            case_title=''
            print("未找到用例标题内容")

        step1_pattern = r'"步聚1"\s*:\s*"([^"\n]+)"[^,]*'
        step1_match = re.search(step1_pattern, data)
        if step1_match:
            step1 = step1_match.group(1)
        else:
            step1=''
            print("未找到步聚1内容")

        step1_result_pattern = r'"预期结果1"\s*:\s*"([^"\n]+)"[^,]*'
        step1_result_match = re.search(step1_result_pattern, data)
        if step1_result_match:
            step1_result = step1_result_match.group(1)
        else:
            step1_result=''
            print("未找到预期结果1内容")

        step2_pattern = r'"步聚2"\s*:\s*"([^"\n]+)"[^,]*'
        step2_match = re.search(step2_pattern, data)
        if step2_match:
            step2 = step2_match.group(1)
        else:
            step2=''
            print("未找到步聚2内容")

        step2_result_pattern = r'"预期结果2"\s*:\s*"([^"\n]+)"[^,]*'
        step2_result_match = re.search(step2_result_pattern, data)
        if step2_result_match:
            step2_result = step2_result_match.group(1)
        else:
            step2_result=''
            print("未找到预期结果2内容")

        step3_pattern = r'"步聚3"\s*:\s*"([^"\n]+)"[^,]*'
        step3_match = re.search(step3_pattern, data)
        if step3_match:
            step3 = step3_match.group(1)
        else:
            step3=''
            print("未找到步聚3内容")

        step3_result_pattern = r'"预期结果3"\s*:\s*"([^"\n]+)"[^,]*'
        step3_result_match = re.search(step3_result_pattern, data)
        if step3_result_match:
            step3_result = step3_result_match.group(1)
        else:
            step3_result=''
            print("未找到预期结果3内容")


        print("用例标题:", case_title)
        print("步聚1:", step1)
        print("预期结果1:", step1_result)
        print("步聚2:", step2)
        print("预期结果2:", step2_result)
        print("步聚3:", step3)
        print("预期结果3:", step3_result)

        steplist=[(step1,step1_result),(step2,step2_result),(step3,step3_result)]
        addRequirementsToTestcase(case_title,user_name,product_id,requirements_id,steplist)
        print("add ai testcase\n")
    # except:
    #     print("转换成正确json格式如下")


    return HttpResponse('200')


def addRequirementsToTestcase(case_title,user_name,product_id,requirements_id,steplist):
    ai_testcase_code = str(int(time.time()))
    testcase_name = case_title
    ai_testcase_result = ''
    creator = user_name
    product_id=product_id
    requirements_id=requirements_id
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    create_time = now
    testcase_name_exist = AutotestplatAiTestcaseTemp.objects.filter(ai_testcase_name=testcase_name).first()
    if testcase_name_exist:
        return HttpResponse(f'产品”{testcase_name}“已存在，请重新填写')
    i=0
    for step in steplist:
        id = str(datetime.now().strftime("%Y%m%d%H%M%S%f"))
        i=i+1
        ai_testcase_step="第"+str(i)+"步"
        time.sleep(2)
        AutotestplatAiTestcaseTemp.objects.create(id=id,ai_testcase_code=ai_testcase_code,ai_testcase_name=testcase_name, ai_testcase_step=ai_testcase_step, ai_testcase_stepname=step[0],ai_testcase_expect_value=step[1],ai_testcase_result=ai_testcase_result,creator=creator,create_time=create_time,product_id=product_id,requirements_id=requirements_id)
