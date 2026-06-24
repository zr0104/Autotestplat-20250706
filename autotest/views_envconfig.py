# -*- coding:utf-8 -*-
############################################
#Auther:：Sen
#Version：Autotestplat-V6.0
#Module: Environment Configuration
############################################
import json, time, re, sys, traceback, random, hashlib, base64, datetime
from io import StringIO
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required


@login_required
def showEnvConfig(request):
    """显示环境配置主页面（重定向到Python方法库）"""
    return redirect('/autotest/envconfig/pythonfunc/')


@login_required
def showPythonFunc(request):
    """显示Python自定义方法库"""
    username = request.session.get('user', '')

    if not username:
        return redirect('/autotest/login/')

    user_obj = AuthUser.objects.filter(username=username).first()
    if not user_obj:
        return redirect('/autotest/login/')

    c = csrf(request)
    c.update({'username': username})

    product_name = request.session.get('product_name', '默认产品')
    product_alls = AutotestplatProduct.objects.all().order_by('id')

    c.update({
        'product_name': product_name,
        'product_alls': product_alls
    })

    return render(request, "python_func.html", c)


@login_required
def showGlobalVar(request):
    """显示全局常量变量库"""
    username = request.session.get('user', '')

    if not username:
        return redirect('/autotest/login/')

    user_obj = AuthUser.objects.filter(username=username).first()
    if not user_obj:
        return redirect('/autotest/login/')

    c = csrf(request)
    c.update({'username': username})

    product_name = request.session.get('product_name', '默认产品')
    product_alls = AutotestplatProduct.objects.all().order_by('id')

    c.update({
        'product_name': product_name,
        'product_alls': product_alls
    })

    return render(request, "global_var.html", c)


@csrf_exempt
@login_required
def addEnv(request):
    """新增环境"""
    try:
        env_name = request.POST.get('env_name', '').strip()

        if not env_name:
            return HttpResponse('环境名称不能为空')

        existing_envs = getEnvironments()
        if env_name in existing_envs:
            return HttpResponse(f'环境 [{env_name}] 已存在')

        existing_envs.append(env_name)

        with open('environments.json', 'w', encoding='utf-8') as f:
            json.dump(existing_envs, f, ensure_ascii=False, indent=2)

        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'添加失败: {str(e)}')


@csrf_exempt
@login_required
def getEnvs(request):
    """获取所有环境列表"""
    try:
        envs = getEnvironments()
        return JsonResponse({'envs': envs})
    except Exception as e:
        return JsonResponse({'envs': ['环境1'], 'error': str(e)})


def getEnvironments():
    """从文件读取环境列表"""
    import os

    env_file = os.path.join(os.path.dirname(__file__), '..', 'environments.json')

    if os.path.exists(env_file):
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass

    default_envs = ['环境1', '环境2', '环境3']

    with open(env_file, 'w', encoding='utf-8') as f:
        json.dump(default_envs, f, ensure_ascii=False, indent=2)

    return default_envs


@csrf_exempt
@login_required
def loadPythonFuncList(request):
    """加载Python自定义方法列表"""
    try:
        items = EnvPythonFunc.objects.all().order_by('-update_time').values()
        rst = []
        for item in items:
            arr = [
                item['func_id'],
                item['func_name'],
                item['func_desc'] or '',
                item['param_desc'] or '',
                item['return_type'],
                '启用' if item['is_enable'] == 1 else '禁用',
                item['create_user'] or '',
                item['update_time'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(item['update_time'], 'strftime') else str(item['update_time'])
            ]
            rst.append(arr)
        return JsonResponse({'data': rst})
    except Exception as e:
        return JsonResponse({'data': [], 'error': str(e)})


@csrf_exempt
@login_required
def addPythonFunc(request):
    """新增Python自定义方法"""
    try:
        func_name = request.POST.get('func_name', '').strip()
        func_desc = request.POST.get('func_desc', '').strip()
        param_desc = request.POST.get('param_desc', '').strip()
        return_type = request.POST.get('return_type', '字符串').strip()
        func_code = request.POST.get('func_code', '').strip()

        if not func_name:
            return HttpResponse('方法名称不能为空')

        if not re.match(r'^[a-zA-Z0-9_]+$', func_name):
            return HttpResponse('方法名仅允许字母、数字、下划线')

        if EnvPythonFunc.objects.filter(func_name=func_name).exists():
            return HttpResponse(f'方法名 [{func_name}] 已存在，请使用其他名称')

        syntax_error = validate_python_syntax(func_code)
        if syntax_error:
            return HttpResponse(f'语法错误: {syntax_error}')

        defined_func_name = extract_function_name_from_code(func_code)
        if defined_func_name and defined_func_name != func_name:
            return HttpResponse(f'方法名不匹配: 表单填写的是 "{func_name}",但代码中定义的是 "{defined_func_name}"')

        username = request.session.get('user', '')

        EnvPythonFunc.objects.create(
            func_name=func_name,
            func_desc=func_desc,
            param_desc=param_desc,
            return_type=return_type,
            func_code=func_code,
            is_enable=1,
            create_user=username
        )

        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'保存失败: {str(e)}')


@csrf_exempt
@login_required
def updatePythonFunc(request):
    """更新Python自定义方法"""
    try:
        func_id = request.POST.get('func_id')
        func_name = request.POST.get('func_name', '').strip()
        func_desc = request.POST.get('func_desc', '').strip()
        param_desc = request.POST.get('param_desc', '').strip()
        return_type = request.POST.get('return_type', '字符串').strip()
        func_code = request.POST.get('func_code', '').strip()

        if not func_name:
            return HttpResponse('方法名称不能为空')

        if not re.match(r'^[a-zA-Z0-9_]+$', func_name):
            return HttpResponse('方法名仅允许字母、数字、下划线')

        if EnvPythonFunc.objects.exclude(func_id=func_id).filter(func_name=func_name).exists():
            return HttpResponse(f'方法名 [{func_name}] 已被其他方法使用')

        syntax_error = validate_python_syntax(func_code)
        if syntax_error:
            return HttpResponse(f'语法错误: {syntax_error}')

        defined_func_name = extract_function_name_from_code(func_code)
        if defined_func_name and defined_func_name != func_name:
            return HttpResponse(f'方法名不匹配: 表单填写的是 "{func_name}",但代码中定义的是 "{defined_func_name}"')

        EnvPythonFunc.objects.filter(func_id=func_id).update(
            func_name=func_name,
            func_desc=func_desc,
            param_desc=param_desc,
            return_type=return_type,
            func_code=func_code
        )

        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'更新失败: {str(e)}')


@csrf_exempt
@login_required
def deletePythonFunc(request):
    """删除Python自定义方法"""
    try:
        func_id = request.POST.get('func_id')
        EnvPythonFunc.objects.filter(func_id=func_id).delete()
        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'删除失败: {str(e)}')


@csrf_exempt
@login_required
def togglePythonFuncStatus(request):
    """切换Python方法启用状态"""
    try:
        func_id = request.POST.get('func_id')
        func = EnvPythonFunc.objects.filter(func_id=func_id).first()
        if func:
            new_status = 0 if func.is_enable == 1 else 1
            EnvPythonFunc.objects.filter(func_id=func_id).update(is_enable=new_status)
            return HttpResponse('200')
        return HttpResponse('方法不存在')
    except Exception as e:
        return HttpResponse(f'操作失败: {str(e)}')


@csrf_exempt
@login_required
def getPythonFuncDetail(request):
    """获取Python方法详情"""
    try:
        func_id = request.POST.get('func_id')
        func = EnvPythonFunc.objects.filter(func_id=func_id).first()
        if func:
            data = {
                'func_id': func.func_id,
                'func_name': func.func_name,
                'func_desc': func.func_desc or '',
                'param_desc': func.param_desc or '',
                'return_type': func.return_type,
                'func_code': func.func_code,
                'is_enable': func.is_enable
            }
            return JsonResponse(data)
        return JsonResponse({'error': '方法不存在'})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@csrf_exempt
@login_required
def debugPythonFunc(request):
    """在线调试Python方法"""
    try:
        func_code = request.POST.get('func_code', '').strip()
        test_params = request.POST.get('test_params', '{}')

        try:
            test_params_dict = json.loads(test_params)
        except:
            return JsonResponse({'success': False, 'error': '测试参数格式错误，请使用JSON格式'})

        syntax_error = validate_python_syntax(func_code)
        if syntax_error:
            return JsonResponse({'success': False, 'error': f'语法错误: {syntax_error}'})

        old_stdout = sys.stdout
        redirected_output = StringIO()
        sys.stdout = redirected_output

        try:
            safe_builtins = __builtins__.copy()

            safe_modules = {
                'time': __import__('time'),
                'datetime': __import__('datetime'),
                'random': __import__('random'),
                'hashlib': __import__('hashlib'),
                'base64': __import__('base64'),
                're': __import__('re'),
                'json': __import__('json'),
                'math': __import__('math'),
            }

            def mock_db_query(db_name, sql):
                return [{'error': '调试模式不支持数据库查询'}]

            def mock_md5(text):
                return hashlib.md5(text.encode()).hexdigest()

            def mock_base64_encode(text):
                return base64.b64encode(text.encode()).decode()

            def mock_base64_decode(text):
                return base64.b64decode(text.encode()).decode()

            safe_globals = {
                '__builtins__': safe_builtins,
                'db_query': mock_db_query,
                'db_update': mock_db_query,
                'md5': mock_md5,
                'base64_encode': mock_base64_encode,
                'base64_decode': mock_base64_decode,
            }

            safe_globals.update({mod: safe_modules[mod] for mod in safe_modules})

            exec(func_code, safe_globals)

            func_names = [name for name in safe_globals.keys() if callable(safe_globals[name]) and not name.startswith('_')]

            result = None
            console_output = redirected_output.getvalue()

            if func_names:
                main_func_name = func_names[-1]
                main_func = safe_globals[main_func_name]

                args = []
                for key in sorted(test_params_dict.keys()):
                    args.append(test_params_dict[key])

                if args:
                    result = main_func(*args)
                else:
                    result = main_func()

            sys.stdout = old_stdout

            return JsonResponse({
                'success': True,
                'result': str(result),
                'console_output': console_output,
                'function_name': func_names[-1] if func_names else None
            })

        except Exception as e:
            sys.stdout = old_stdout
            error_traceback = traceback.format_exc()
            return JsonResponse({
                'success': False,
                'error': str(e),
                'traceback': error_traceback
            })

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'调试失败: {str(e)}'})


def validate_python_syntax(code):
    """验证Python代码语法"""
    try:
        compile(code, '<string>', 'exec')
        return None
    except SyntaxError as e:
        return f"第{e.lineno}行: {e.msg}"
    except Exception as e:
        return str(e)


class VariableResolver:
    """
    变量解析器 - 支持多级作用域变量插值

    作用域优先级（从高到低）：
    1. 单接口私有参数（仅当前接口步骤）
    2. 场景 Variables 临时变量（单条业务场景用例内部）
    3. 事务 backVariables（当前事务内部）
    4. Extract 全局提取变量（同项目下全部共享）
    5. SQL 脚本变量
    6. CSV 文件参数
    7. EnvGlobalVariables 环境配置全局常量
    8. Python自定义方法调用（特殊格式 ${方法名}）

    特殊变量：
    - backVariables: 结构化对象，必须链式取值 result.data.row.xxx
    - Hooks 局部变量: 仅钩子脚本执行阶段生效
    - ${方法名}: 调用Python自定义方法，如 ${get_now_time_stamp}
    """

    def __init__(self, private_params=None, scene_vars=None, transaction_backvars=None,
                 extract_vars=None, sql_vars=None, csv_vars=None, env_global_vars=None):
        self.private_params = private_params or {}
        self.scene_vars = scene_vars or {}
        self.transaction_backvars = transaction_backvars or {}
        self.extract_vars = extract_vars or {}
        self.sql_vars = sql_vars or {}
        self.csv_vars = csv_vars or {}
        self.env_global_vars = env_global_vars or {}

        self._method_cache = {}

    def resolve(self, text):
        """
        解析文本中的 ${variable_name} 占位符

        返回处理后的文本
        """
        import re

        if not text or '${' not in text:
            return text

        pattern = r'\$\{([^}]+)\}'

        def replace_var(match):
            var_name = match.group(1).strip()

            if '.' in var_name:
                return self._resolve_chain_var(var_name)
            else:
                is_python_method = self._check_if_python_method(var_name)
                if is_python_method:
                    return self._execute_python_method(var_name)
                else:
                    return self._resolve_simple_var(var_name)

        try:
            result = re.sub(pattern, replace_var, text)
            return result
        except Exception as e:
            return text

    def _check_if_python_method(self, var_name):
        """检查变量名是否是Python自定义方法"""
        if var_name in self._method_cache:
            return self._method_cache[var_name]

        method_obj = EnvPythonFunc.objects.filter(
            func_name=var_name,
            is_enable=1
        ).exists()

        self._method_cache[var_name] = method_obj
        return method_obj

    def _execute_python_method(self, var_name):
        """
        执行Python自定义方法

        格式: 方法名 或 方法名?param1=value1&param2=value2
        """
        params = {}
        method_name = var_name

        if '?' in var_name:
            method_name, query_string = var_name.split('?', 1)
            param_pairs = query_string.split('&')
            for pair in param_pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    params[key.strip()] = value.strip()

        method_name = method_name.strip()

        if not method_name:
            return f'${{{var_name}}}'

        result = execute_python_method(method_name, params)

        if result.startswith('ERROR:'):
            return f'[Python方法执行失败: {result}]'

        return result

    def _resolve_simple_var(self, var_name):
        """解析简单变量名，按优先级查找"""
        if var_name in self.private_params:
            return str(self.private_params[var_name])

        if var_name in self.scene_vars:
            return str(self.scene_vars[var_name])

        if var_name in self.transaction_backvars:
            return str(self.transaction_backvars[var_name])

        if var_name in self.extract_vars:
            return str(self.extract_vars[var_name])

        if var_name in self.sql_vars:
            return str(self.sql_vars[var_name])

        if var_name in self.csv_vars:
            return str(self.csv_vars[var_name])

        if var_name in self.env_global_vars:
            var_value = self.env_global_vars[var_name]

            if var_value and var_value.startswith('@method:'):
                method_name = var_value[8:]
                return self._execute_python_method(method_name)

            return str(var_value)

        return f'${{{var_name}}}'

    def _resolve_chain_var(self, chain_str):
        """解析链式变量路径，如 backVariables.result.data.row.name"""
        parts = chain_str.split('.')

        if len(parts) < 2:
            return f'${{{chain_str}}}'

        root_var = parts[0]

        if root_var == 'backVariables':
            current = self.transaction_backvars
        elif root_var == 'extractVariables':
            current = self.extract_vars
        elif root_var == 'sqlVariables':
            current = self.sql_vars
        elif root_var == 'csvVariables':
            current = self.csv_vars
        elif root_var == 'sceneVariables':
            current = self.scene_vars
        elif root_var == 'privateParams':
            current = self.private_params
        else:
            current = self.env_global_vars.get(root_var)

        if current is None:
            return f'${{{chain_str}}}'

        for part in parts[1:]:
            if isinstance(current, dict):
                if part in current:
                    current = current[part]
                else:
                    return f'${{{chain_str}}}'
            elif hasattr(current, part):
                current = getattr(current, part)
            else:
                return f'${{{chain_str}}}'

        return str(current) if current is not None else f'${{{chain_str}}}'

    def execute_extract(self, response_data, extract_config):
        """
        执行 Extract 提取操作

        Args:
            response_data: 接口响应数据（dict或JSON字符串）
            extract_config: Extract配置列表，如 [{"name": "extMsg", "expression": "content.extMsg"}]

        Returns:
            提取的变量字典
        """
        import json
        import jsonpath_ng

        extracted = {}

        if isinstance(response_data, str):
            try:
                response_data = json.loads(response_data)
            except:
                return extracted

        for item in extract_config:
            var_name = item.get('name', '').strip()
            expression = item.get('expression', '').strip()

            if not var_name or not expression:
                continue

            try:
                jsonpath_expr = jsonpath_ng.parse(expression)
                matches = jsonpath_expr.find(response_data)

                if matches:
                    value = matches[0].value
                    extracted[var_name] = value
            except Exception as e:
                extracted[var_name] = f'ERROR: {str(e)}'

        return extracted

    def merge_vars(self, other_resolver):
        """合并另一个 VariableResolver 的变量"""
        self.private_params.update(other_resolver.private_params)
        self.scene_vars.update(other_resolver.scene_vars)
        self.transaction_backvars.update(other_resolver.transaction_backvars)
        self.extract_vars.update(other_resolver.extract_vars)
        self.sql_vars.update(other_resolver.sql_vars)
        self.csv_vars.update(other_resolver.csv_vars)
        self.env_global_vars.update(other_resolver.env_global_vars)

@csrf_exempt
@login_required
def loadGlobalVarList(request):
    """加载全局常量变量列表（支持环境和分页）"""
    try:
        page = int(request.POST.get('page', 1))
        page_size = int(request.POST.get('page_size', 10))
        env_name = request.POST.get('env_name', '环境1')

        # 按 sort_order 正序排列（小的在前，大的在后）
        all_items = EnvGlobalVariables.objects.filter(
            Q(env_name=env_name) | Q(env_name__isnull=True)
        ).order_by('sort_order', 'var_id').values()

        total = all_items.count()

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        items = all_items[start_idx:end_idx]

        rst = []
        for item in items:
            arr = [
                item['var_id'],
                item['var_name'],
                item['var_value'] or '',
                item['var_category'],
                item['var_desc'] or '',
                '启用' if item['is_enable'] == 1 else '禁用',
                item['create_user'] or '',
                item['update_time'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(item['update_time'], 'strftime') else str(item['update_time']),
                item.get('env_name', '环境1')
            ]
            rst.append(arr)

        total_pages = (total + page_size - 1) // page_size

        return JsonResponse({
            'data': rst,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages
        })
    except Exception as e:
        return JsonResponse({'data': [], 'total': 0, 'error': str(e)})


@csrf_exempt
@login_required
def addGlobalVar(request):
    """新增全局常量变量"""
    try:
        var_name = request.POST.get('var_name', '').strip()
        var_value = request.POST.get('var_value', '').strip()
        var_category = request.POST.get('var_category', '业务常量').strip()
        var_desc = request.POST.get('var_desc', '').strip()
        env_name = request.POST.get('env_name', '环境1').strip()
        after_var_id = request.POST.get('after_var_id', '')  # 在哪一行后面插入

        print(f"DEBUG: 接收到参数 - var_name={var_name}, after_var_id={after_var_id}")

        if not var_name:
            return HttpResponse('变量名称不能为空')

        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var_name):
            return HttpResponse('变量名仅允许字母、数字、下划线，且不能以数字开头')

        if EnvGlobalVariables.objects.filter(var_name=var_name, env_name=env_name).exists():
            return HttpResponse(f'变量名 [{var_name}] 在 [{env_name}] 中已存在，请使用其他名称')

        username = request.session.get('user', '')

        # 计算新的 sort_order
        if after_var_id and after_var_id != '':
            print(f"DEBUG: 有指定插入位置 after_var_id={after_var_id}")
            # 有指定插入位置：找到 after_var 的 sort_order，然后让后面的都+1
            after_var = EnvGlobalVariables.objects.filter(var_id=after_var_id, env_name=env_name).first()
            if after_var:
                after_sort = after_var.sort_order
                print(f"DEBUG: after_var sort_order={after_sort}")

                # 将所有 sort_order > after_sort 的都+1（腾出位置）
                EnvGlobalVariables.objects.filter(env_name=env_name, sort_order__gt=after_sort).update(
                    sort_order=models.F('sort_order') + 1
                )

                # 新变量的 sort_order = after_sort + 1
                new_sort_order = after_sort + 1
                print(f"DEBUG: 新变量 sort_order={new_sort_order}")
            else:
                print(f"DEBUG: after_var不存在，当作普通新增")
                # after_var不存在，当作普通新增
                max_sort = EnvGlobalVariables.objects.filter(env_name=env_name).aggregate(
                    models.Max('sort_order')
                )['sort_order__max'] or 0
                new_sort_order = max_sort + 1
        else:
            print(f"DEBUG: 没有指定插入位置，放到最后")
            # 没有指定插入位置（顶部新增），放到最后
            max_sort = EnvGlobalVariables.objects.filter(env_name=env_name).aggregate(
                models.Max('sort_order')
            )['sort_order__max'] or 0
            new_sort_order = max_sort + 1

        new_var = EnvGlobalVariables.objects.create(
            var_name=var_name,
            var_value=var_value,
            var_category=var_category,
            var_desc=var_desc,
            is_enable=1,
            create_user=username,
            env_name=env_name,
            sort_order=new_sort_order
        )

        print(f"DEBUG: 新增变量 {var_name}, sort_order={new_sort_order}, after_var_id={after_var_id}")
        return HttpResponse(f'200:{new_var.var_id}:{new_sort_order}')
    except Exception as e:
        import traceback
        print(f"ERROR: {str(e)}")
        print(traceback.format_exc())
        return HttpResponse(f'保存失败: {str(e)}')


@csrf_exempt
@login_required
def updateGlobalVar(request):
    """更新全局常量变量"""
    try:
        var_id = request.POST.get('var_id')
        var_name = request.POST.get('var_name', '').strip()
        var_value = request.POST.get('var_value', '').strip()
        var_category = request.POST.get('var_category', '业务常量').strip()
        var_desc = request.POST.get('var_desc', '').strip()
        env_name = request.POST.get('env_name', '环境1').strip()

        if not var_name:
            return HttpResponse('变量名称不能为空')

        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var_name):
            return HttpResponse('变量名仅允许字母、数字、下划线，且不能以数字开头')

        if EnvGlobalVariables.objects.exclude(var_id=var_id).filter(var_name=var_name, env_name=env_name).exists():
            return HttpResponse(f'变量名 [{var_name}] 在 [{env_name}] 中已被其他变量使用')

        EnvGlobalVariables.objects.filter(var_id=var_id).update(
            var_name=var_name,
            var_value=var_value,
            var_category=var_category,
            var_desc=var_desc,
            env_name=env_name
        )

        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'更新失败: {str(e)}')


@csrf_exempt
@login_required
def deleteGlobalVar(request):
    """删除全局常量变量"""
    try:
        var_id = request.POST.get('var_id')
        EnvGlobalVariables.objects.filter(var_id=var_id).delete()
        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'删除失败: {str(e)}')


@csrf_exempt
@login_required
def toggleGlobalVarStatus(request):
    """切换全局变量启用状态"""
    try:
        var_id = request.POST.get('var_id')
        var = EnvGlobalVariables.objects.filter(var_id=var_id).first()
        if var:
            new_status = 0 if var.is_enable == 1 else 1
            EnvGlobalVariables.objects.filter(var_id=var_id).update(is_enable=new_status)
            return HttpResponse('200')
        return HttpResponse('变量不存在')
    except Exception as e:
        return HttpResponse(f'操作失败: {str(e)}')


@csrf_exempt
@login_required
def getGlobalVarDetail(request):
    """获取全局变量详情"""
    try:
        var_id = request.POST.get('var_id')
        var = EnvGlobalVariables.objects.filter(var_id=var_id).first()
        if var:
            data = {
                'var_id': var.var_id,
                'var_name': var.var_name,
                'var_value': var.var_value or '',
                'var_category': var.var_category,
                'var_desc': var.var_desc or '',
                'is_enable': var.is_enable,
                'env_name': var.env_name or '环境1'
            }
            return JsonResponse(data)
        return JsonResponse({'error': '变量不存在'})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@csrf_exempt
@login_required
def batchImportGlobalVars(request):
    """批量导入全局变量(CSV)"""
    try:
        csv_content = request.POST.get('csv_content', '').strip()
        if not csv_content:
            return HttpResponse('CSV内容为空')

        lines = csv_content.strip().split('\n')
        success_count = 0
        fail_count = 0
        errors = []

        username = request.session.get('user', '')

        for i, line in enumerate(lines, 1):
            try:
                parts = line.split(',')
                if len(parts) < 2:
                    errors.append(f'第{i}行: 格式错误')
                    fail_count += 1
                    continue

                var_name = parts[0].strip()
                var_value = ','.join(parts[1:-1]).strip() if len(parts) > 2 else parts[1].strip()
                var_category = parts[-1].strip() if len(parts) >= 3 else '业务常量'

                if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var_name):
                    errors.append(f'第{i}行: 变量名[{var_name}]格式不正确')
                    fail_count += 1
                    continue

                if EnvGlobalVariables.objects.filter(var_name=var_name).exists():
                    errors.append(f'第{i}行: 变量名[{var_name}]已存在')
                    fail_count += 1
                    continue

                EnvGlobalVariables.objects.create(
                    var_name=var_name,
                    var_value=var_value,
                    var_category=var_category,
                    var_desc=f'批量导入',
                    is_enable=1,
                    create_user=username
                )
                success_count += 1
            except Exception as e:
                errors.append(f'第{i}行: {str(e)}')
                fail_count += 1

        result_msg = f'导入完成: 成功{success_count}条，失败{fail_count}条'
        if errors:
            result_msg += '\n\n错误详情:\n' + '\n'.join(errors[:10])

        return HttpResponse(result_msg)
    except Exception as e:
        return HttpResponse(f'导入失败: {str(e)}')


@csrf_exempt
@login_required
def exportGlobalVars(request):
    """导出所有全局变量"""
    try:
        vars = EnvGlobalVariables.objects.all().values('var_name', 'var_value', 'var_category', 'var_desc')

        csv_lines = []
        for var in vars:
            value = var['var_value'] or ''
            if ',' in value or '\n' in value:
                value = f'"{value}"'
            csv_lines.append(f"{var['var_name']},{value},{var['var_category']},{var['var_desc']}")

        csv_content = '\n'.join(csv_lines)

        response = HttpResponse(csv_content, content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename=global_vars_{int(time.time())}.csv'
        return response
    except Exception as e:
        return HttpResponse(f'导出失败: {str(e)}')


@csrf_exempt
@login_required
def getGlobalVarCategories(request):
    """获取变量分类列表"""
    try:
        categories = EnvGlobalVariables.objects.values_list('var_category', flat=True).distinct()
        default_categories = ['账号密码', '域名地址', '业务常量', '鉴权Token', '环境标识']
        all_categories = list(set(list(categories) + default_categories))
        return JsonResponse(all_categories, safe=False)
    except Exception as e:
        return JsonResponse([], safe=False)


@csrf_exempt
@login_required
def getPythonMethodList(request):
    """获取所有启用的Python自定义方法列表（供全局变量选择）"""
    try:
        methods = EnvPythonFunc.objects.filter(
            is_enable=1
        ).order_by('func_name').values('func_name', 'func_desc', 'return_type')

        result = []
        for method in methods:
            result.append({
                'func_name': method['func_name'],
                'func_desc': method['func_desc'] or '',
                'return_type': method['return_type']
            })

        print(f"DEBUG: 返回 {len(result)} 个Python方法")
        return JsonResponse(result, safe=False)
    except Exception as e:
        import traceback
        print(f"ERROR: 获取Python方法列表失败: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse([], safe=False)


def execute_python_method(func_name, params=None):
    """
    执行Python自定义方法并返回结果

    Args:
        func_name: 方法名
        params: 参数字典（可选）

    Returns:
        方法执行结果或错误信息
    """
    if not params:
        params = {}

    try:
        func_obj = EnvPythonFunc.objects.filter(
            func_name=func_name,
            is_enable=1
        ).first()

        if not func_obj:
            return f'ERROR: 方法 [{func_name}] 不存在或已禁用'

        func_code = func_obj.func_code

        old_stdout = sys.stdout
        redirected_output = StringIO()
        sys.stdout = redirected_output

        try:
            safe_builtins = __builtins__.copy()

            safe_modules = {
                'time': __import__('time'),
                'datetime': __import__('datetime'),
                'random': __import__('random'),
                'hashlib': __import__('hashlib'),
                'base64': __import__('base64'),
                're': __import__('re'),
                'json': __import__('json'),
                'math': __import__('math'),
            }

            def mock_db_query(db_name, sql):
                return [{'error': '生产模式不支持数据库查询'}]

            def mock_md5(text):
                return hashlib.md5(text.encode()).hexdigest()

            def mock_base64_encode(text):
                return base64.b64encode(text.encode()).decode()

            def mock_base64_decode(text):
                return base64.b64decode(text.encode()).decode()

            safe_globals = {
                '__builtins__': safe_builtins,
                'db_query': mock_db_query,
                'db_update': mock_db_query,
                'md5': mock_md5,
                'base64_encode': mock_base64_encode,
                'base64_decode': mock_base64_decode,
            }

            safe_globals.update({mod: safe_modules[mod] for mod in safe_modules})

            exec(func_code, safe_globals)

            func_names = [name for name in safe_globals.keys() if callable(safe_globals[name]) and not name.startswith('_')]

            if func_names:
                main_func = safe_globals[func_names[-1]]

                args = []
                for key in sorted(params.keys()):
                    args.append(params[key])

                if args:
                    result = main_func(*args)
                else:
                    result = main_func()

                sys.stdout = old_stdout
                return str(result)
            else:
                sys.stdout = old_stdout
                return 'ERROR: 未找到可执行的函数'

        except Exception as e:
            sys.stdout = old_stdout
            error_traceback = traceback.format_exc()
            return f'ERROR: {str(e)}'

    except Exception as e:
        return f'ERROR: 执行失败 - {str(e)}'


def extract_function_name_from_code(code):
    """从代码中提取第一个函数定义的名称"""
    match = re.search(r'^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code, re.MULTILINE)
    if match:
        return match.group(1)
    return None


@csrf_exempt
@login_required
def swapGlobalVarOrder(request):
    """交换两个全局变量的顺序（使用原始SQL避免主键限制）"""
    try:
        from django.db import connection

        var_id_1 = request.POST.get('var_id_1')
        var_id_2 = request.POST.get('var_id_2')
        env_name = request.POST.get('env_name', '环境1')

        print(f"DEBUG: 交换变量 {var_id_1} 和 {var_id_2}, 环境: {env_name}")

        # 验证变量存在
        var1 = EnvGlobalVariables.objects.filter(var_id=var_id_1, env_name=env_name).first()
        var2 = EnvGlobalVariables.objects.filter(var_id=var_id_2, env_name=env_name).first()

        if not var1:
            print(f"DEBUG: 变量1不存在")
            return HttpResponse('变量1不存在')
        if not var2:
            print(f"DEBUG: 变量2不存在")
            return HttpResponse('变量2不存在')

        # 交换 sort_order 而不是 var_id
        temp_sort = var1.sort_order
        var1.sort_order = var2.sort_order
        var2.sort_order = temp_sort

        var1.save(update_fields=['sort_order'])
        var2.save(update_fields=['sort_order'])

        print(f"DEBUG: 交换成功，sort_order: {var1.sort_order}, {var2.sort_order}")
        return HttpResponse('200')
    except Exception as e:
        import traceback
        print(f"DEBUG: 交换失败: {str(e)}")
        print(traceback.format_exc())
        return HttpResponse(f'交换失败: {str(e)}')


# ==================== Header配置 CRUD ====================

@csrf_exempt
@login_required
def loadHeaderList(request):
    """加载Header列表"""
    try:
        page = int(request.POST.get('page', 1))
        page_size = int(request.POST.get('page_size', 10))
        env_name = request.POST.get('env_name', '环境1')
        
        all_items = EnvGlobalHeader.objects.filter(env_name=env_name).order_by('sort_order', 'id').values()
        total = all_items.count()
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        items = all_items[start_idx:end_idx]
        
        rst = []
        for item in items:
            arr = [
                item['id'],
                item['header_name'],
                item['header_value'] or '',
                item['description'] or '',
                '启用' if item['is_enable'] == 1 else '禁用',
                item['create_user'] or '',
                item['update_time'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(item['update_time'], 'strftime') else str(item['update_time']),
                item.get('env_name', '环境1')
            ]
            rst.append(arr)
        
        return JsonResponse({
            'data': rst,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        })
    except Exception as e:
        return JsonResponse({'data': [], 'total': 0, 'error': str(e)})


@csrf_exempt
@login_required
def addHeader(request):
    """新增Header"""
    try:
        header_name = request.POST.get('header_name', '').strip()
        header_value = request.POST.get('header_value', '').strip()
        description = request.POST.get('description', '').strip()
        env_name = request.POST.get('env_name', '环境1').strip()
        
        if not header_name:
            return HttpResponse('Header名称不能为空')
        
        if EnvGlobalHeader.objects.filter(header_name=header_name, env_name=env_name).exists():
            return HttpResponse(f'Header [{header_name}] 已存在')
        
        username = request.session.get('user', '')
        
        max_sort = EnvGlobalHeader.objects.filter(env_name=env_name).aggregate(
            models.Max('sort_order')
        )['sort_order__max'] or 0
        
        EnvGlobalHeader.objects.create(
            header_name=header_name,
            header_value=header_value,
            description=description,
            is_enable=1,
            create_user=username,
            env_name=env_name,
            sort_order=max_sort + 1
        )
        
        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'保存失败: {str(e)}')


@csrf_exempt
@login_required
def updateHeader(request):
    """更新Header"""
    try:
        id = request.POST.get('id')
        header_name = request.POST.get('header_name', '').strip()
        header_value = request.POST.get('header_value', '').strip()
        description = request.POST.get('description', '').strip()
        env_name = request.POST.get('env_name', '环境1').strip()
        
        if not header_name:
            return HttpResponse('Header名称不能为空')
        
        EnvGlobalHeader.objects.filter(id=id).update(
            header_name=header_name,
            header_value=header_value,
            description=description,
            env_name=env_name
        )
        
        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'更新失败: {str(e)}')


@csrf_exempt
@login_required
def deleteHeader(request):
    """删除Header"""
    try:
        id = request.POST.get('id')
        EnvGlobalHeader.objects.filter(id=id).delete()
        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'删除失败: {str(e)}')


# ==================== Request参数 CRUD ====================
# （类似Header的实现，此处省略以节省篇幅，实际开发时需要完整实现）

# ==================== Extract提取规则 CRUD ====================
# （类似Header的实现，此处省略以节省篇幅，实际开发时需要完整实现）

# ==================== Validate断言 CRUD ====================
# （类似Header的实现，此处省略以节省篇幅，实际开发时需要完整实现）

# ==================== Variables临时变量 CRUD ====================
# （类似Header的实现，此处省略以节省篇幅，实际开发时需要完整实现）

# ==================== backVariables结构化变量 CRUD ====================
# （类似Header的实现，此处省略以节省篇幅，实际开发时需要完整实现）

# ==================== Hooks钩子脚本 CRUD ====================
# （类似Header的实现，此处省略以节省篇幅，实际开发时需要完整实现）

# ... existing code ...

# ==================== Request参数 CRUD ====================

@csrf_exempt
@login_required
def loadRequestList(request):
    """加载Request参数列表"""
    try:
        page = int(request.POST.get('page', 1))
        page_size = int(request.POST.get('page_size', 10))
        env_name = request.POST.get('env_name', '环境1')

        all_items = EnvGlobalRequest.objects.filter(env_name=env_name).order_by('sort_order', 'id').values()
        total = all_items.count()

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        items = all_items[start_idx:end_idx]

        rst = []
        for item in items:
            arr = [
                item['id'],
                item['request_name'],
                item['request_value'] or '',
                item['description'] or '',
                '启用' if item['is_enable'] == 1 else '禁用',
                item['create_user'] or '',
                item['update_time'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(item['update_time'], 'strftime') else str(item['update_time']),
                item.get('env_name', '环境1')
            ]
            rst.append(arr)

        return JsonResponse({
            'data': rst,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        })
    except Exception as e:
        return JsonResponse({'data': [], 'total': 0, 'error': str(e)})


@csrf_exempt
@login_required
def addRequest(request):
    """新增Request参数"""
    try:
        request_name = request.POST.get('request_name', '').strip()
        request_value = request.POST.get('request_value', '').strip()
        description = request.POST.get('description', '').strip()
        env_name = request.POST.get('env_name', '环境1').strip()

        if not request_name:
            return HttpResponse('Request参数名不能为空')

        if EnvGlobalRequest.objects.filter(request_name=request_name, env_name=env_name).exists():
            return HttpResponse(f'Request参数 [{request_name}] 已存在')

        username = request.session.get('user', '')

        max_sort = EnvGlobalRequest.objects.filter(env_name=env_name).aggregate(
            models.Max('sort_order')
        )['sort_order__max'] or 0

        EnvGlobalRequest.objects.create(
            request_name=request_name,
            request_value=request_value,
            description=description,
            is_enable=1,
            create_user=username,
            env_name=env_name,
            sort_order=max_sort + 1
        )

        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'保存失败: {str(e)}')


@csrf_exempt
@login_required
def updateRequest(request):
    """更新Request参数"""
    try:
        id = request.POST.get('id')
        request_name = request.POST.get('request_name', '').strip()
        request_value = request.POST.get('request_value', '').strip()
        description = request.POST.get('description', '').strip()
        env_name = request.POST.get('env_name', '环境1').strip()

        if not request_name:
            return HttpResponse('Request参数名不能为空')

        EnvGlobalRequest.objects.filter(id=id).update(
            request_name=request_name,
            request_value=request_value,
            description=description,
            env_name=env_name
        )

        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'更新失败: {str(e)}')


@csrf_exempt
@login_required
def deleteRequest(request):
    """删除Request参数"""
    try:
        id = request.POST.get('id')
        EnvGlobalRequest.objects.filter(id=id).delete()
        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'删除失败: {str(e)}')


# ==================== Extract提取规则 CRUD ====================

@csrf_exempt
@login_required
def loadExtractList(request):
    """加载Extract提取规则列表"""
    try:
        page = int(request.POST.get('page', 1))
        page_size = int(request.POST.get('page_size', 10))
        env_name = request.POST.get('env_name', '环境1')

        all_items = EnvGlobalExtract.objects.filter(env_name=env_name).order_by('sort_order', 'id').values()
        total = all_items.count()

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        items = all_items[start_idx:end_idx]

        rst = []
        for item in items:
            arr = [
                item['id'],
                item['var_name'],
                item['json_path'],
                item['description'] or '',
                '启用' if item['is_enable'] == 1 else '禁用',
                item['create_user'] or '',
                item['update_time'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(item['update_time'], 'strftime') else str(item['update_time']),
                item.get('env_name', '环境1')
            ]
            rst.append(arr)

        return JsonResponse({
            'data': rst,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        })
    except Exception as e:
        return JsonResponse({'data': [], 'total': 0, 'error': str(e)})


@csrf_exempt
@login_required
def addExtract(request):
    """新增Extract提取规则"""
    try:
        var_name = request.POST.get('var_name', '').strip()
        json_path = request.POST.get('json_path', '').strip()
        description = request.POST.get('description', '').strip()
        env_name = request.POST.get('env_name', '环境1').strip()

        if not var_name:
            return HttpResponse('变量名不能为空')
        if not json_path:
            return HttpResponse('JsonPath表达式不能为空')

        if EnvGlobalExtract.objects.filter(var_name=var_name, env_name=env_name).exists():
            return HttpResponse(f'提取变量 [{var_name}] 已存在')

        username = request.session.get('user', '')

        max_sort = EnvGlobalExtract.objects.filter(env_name=env_name).aggregate(
            models.Max('sort_order')
        )['sort_order__max'] or 0

        EnvGlobalExtract.objects.create(
            var_name=var_name,
            json_path=json_path,
            description=description,
            is_enable=1,
            create_user=username,
            env_name=env_name,
            sort_order=max_sort + 1
        )

        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'保存失败: {str(e)}')


@csrf_exempt
@login_required
def updateExtract(request):
    """更新Extract提取规则"""
    try:
        id = request.POST.get('id')
        var_name = request.POST.get('var_name', '').strip()
        json_path = request.POST.get('json_path', '').strip()
        description = request.POST.get('description', '').strip()
        env_name = request.POST.get('env_name', '环境1').strip()

        if not var_name:
            return HttpResponse('变量名不能为空')
        if not json_path:
            return HttpResponse('JsonPath表达式不能为空')

        EnvGlobalExtract.objects.filter(id=id).update(
            var_name=var_name,
            json_path=json_path,
            description=description,
            env_name=env_name
        )

        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'更新失败: {str(e)}')


@csrf_exempt
@login_required
def deleteExtract(request):
    """删除Extract提取规则"""
    try:
        id = request.POST.get('id')
        EnvGlobalExtract.objects.filter(id=id).delete()
        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'删除失败: {str(e)}')


# ==================== Validate断言 CRUD ====================

@csrf_exempt
@login_required
def loadValidateList(request):
    """加载Validate断言列表"""
    try:
        page = int(request.POST.get('page', 1))
        page_size = int(request.POST.get('page_size', 10))
        env_name = request.POST.get('env_name', '环境1')

        all_items = EnvGlobalValidate.objects.filter(env_name=env_name).order_by('sort_order', 'id').values()
        total = all_items.count()

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        items = all_items[start_idx:end_idx]

        rst = []
        for item in items:
            arr = [
                item['id'],
                item['validate_name'],
                item['validate_expression'],
                item['expected_value'] or '',
                item['description'] or '',
                '启用' if item['is_enable'] == 1 else '禁用',
                item['create_user'] or '',
                item['update_time'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(item['update_time'], 'strftime') else str(item['update_time']),
                item.get('env_name', '环境1')
            ]
            rst.append(arr)

        return JsonResponse({
            'data': rst,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        })
    except Exception as e:
        return JsonResponse({'data': [], 'total': 0, 'error': str(e)})


@csrf_exempt
@login_required
def addValidate(request):
    """新增Validate断言"""
    try:
        validate_name = request.POST.get('validate_name', '').strip()
        validate_expression = request.POST.get('validate_expression', '').strip()
        expected_value = request.POST.get('expected_value', '').strip()
        description = request.POST.get('description', '').strip()
        env_name = request.POST.get('env_name', '环境1').strip()

        if not validate_name:
            return HttpResponse('断言名称不能为空')
        if not validate_expression:
            return HttpResponse('断言表达式不能为空')

        username = request.session.get('user', '')

        max_sort = EnvGlobalValidate.objects.filter(env_name=env_name).aggregate(
            models.Max('sort_order')
        )['sort_order__max'] or 0

        EnvGlobalValidate.objects.create(
            validate_name=validate_name,
            validate_expression=validate_expression,
            expected_value=expected_value,
            description=description,
            is_enable=1,
            create_user=username,
            env_name=env_name,
            sort_order=max_sort + 1
        )

        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'保存失败: {str(e)}')


@csrf_exempt
@login_required
def updateValidate(request):
    """更新Validate断言"""
    try:
        id = request.POST.get('id')
        validate_name = request.POST.get('validate_name', '').strip()
        validate_expression = request.POST.get('validate_expression', '').strip()
        expected_value = request.POST.get('expected_value', '').strip()
        description = request.POST.get('description', '').strip()
        env_name = request.POST.get('env_name', '环境1').strip()

        if not validate_name:
            return HttpResponse('断言名称不能为空')
        if not validate_expression:
            return HttpResponse('断言表达式不能为空')

        EnvGlobalValidate.objects.filter(id=id).update(
            validate_name=validate_name,
            validate_expression=validate_expression,
            expected_value=expected_value,
            description=description,
            env_name=env_name
        )

        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'更新失败: {str(e)}')


@csrf_exempt
@login_required
def deleteValidate(request):
    """删除Validate断言"""
    try:
        id = request.POST.get('id')
        EnvGlobalValidate.objects.filter(id=id).delete()
        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'删除失败: {str(e)}')


# ==================== Variables临时变量 CRUD ====================

@csrf_exempt
@login_required
def loadVariablesTempList(request):
    """加载Variables临时变量列表"""
    try:
        page = int(request.POST.get('page', 1))
        page_size = int(request.POST.get('page_size', 10))
        env_name = request.POST.get('env_name', '环境1')

        all_items = EnvGlobalVariablesTemp.objects.filter(env_name=env_name).order_by('sort_order', 'id').values()
        total = all_items.count()

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        items = all_items[start_idx:end_idx]

        rst = []
        for item in items:
            arr = [
                item['id'],
                item['var_name'],
                item['var_value'] or '',
                item['description'] or '',
                '启用' if item['is_enable'] == 1 else '禁用',
                item['create_user'] or '',
                item['update_time'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(item['update_time'], 'strftime') else str(item['update_time']),
                item.get('env_name', '环境1')
            ]
            rst.append(arr)

        return JsonResponse({
            'data': rst,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        })
    except Exception as e:
        return JsonResponse({'data': [], 'total': 0, 'error': str(e)})


@csrf_exempt
@login_required
def addVariablesTemp(request):
    """新增Variables临时变量"""
    try:
        var_name = request.POST.get('var_name', '').strip()
        var_value = request.POST.get('var_value', '').strip()
        description = request.POST.get('description', '').strip()
        env_name = request.POST.get('env_name', '环境1').strip()

        if not var_name:
            return HttpResponse('变量名不能为空')

        if EnvGlobalVariablesTemp.objects.filter(var_name=var_name, env_name=env_name).exists():
            return HttpResponse(f'临时变量 [{var_name}] 已存在')

        username = request.session.get('user', '')

        max_sort = EnvGlobalVariablesTemp.objects.filter(env_name=env_name).aggregate(
            models.Max('sort_order')
        )['sort_order__max'] or 0

        EnvGlobalVariablesTemp.objects.create(
            var_name=var_name,
            var_value=var_value,
            description=description,
            is_enable=1,
            create_user=username,
            env_name=env_name,
            sort_order=max_sort + 1
        )

        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'保存失败: {str(e)}')


@csrf_exempt
@login_required
def updateVariablesTemp(request):
    """更新Variables临时变量"""
    try:
        id = request.POST.get('id')
        var_name = request.POST.get('var_name', '').strip()
        var_value = request.POST.get('var_value', '').strip()
        description = request.POST.get('description', '').strip()
        env_name = request.POST.get('env_name', '环境1').strip()

        if not var_name:
            return HttpResponse('变量名不能为空')

        EnvGlobalVariablesTemp.objects.filter(id=id).update(
            var_name=var_name,
            var_value=var_value,
            description=description,
            env_name=env_name
        )

        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'更新失败: {str(e)}')


@csrf_exempt
@login_required
def deleteVariablesTemp(request):
    """删除Variables临时变量"""
    try:
        id = request.POST.get('id')
        EnvGlobalVariablesTemp.objects.filter(id=id).delete()
        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'删除失败: {str(e)}')


# ==================== backVariables结构化变量 CRUD ====================

@csrf_exempt
@login_required
def loadBackVariablesList(request):
    """加载backVariables结构化变量列表"""
    try:
        page = int(request.POST.get('page', 1))
        page_size = int(request.POST.get('page_size', 10))
        env_name = request.POST.get('env_name', '环境1')

        all_items = EnvGlobalBackVariables.objects.filter(env_name=env_name).order_by('sort_order', 'id').values()
        total = all_items.count()

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        items = all_items[start_idx:end_idx]

        rst = []
        for item in items:
            arr = [
                item['id'],
                item['var_name'],
                item['json_structure'] or '',
                item['description'] or '',
                '启用' if item['is_enable'] == 1 else '禁用',
                item['create_user'] or '',
                item['update_time'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(item['update_time'], 'strftime') else str(item['update_time']),
                item.get('env_name', '环境1')
            ]
            rst.append(arr)

        return JsonResponse({
            'data': rst,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        })
    except Exception as e:
        return JsonResponse({'data': [], 'total': 0, 'error': str(e)})


@csrf_exempt
@login_required
def addBackVariables(request):
    """新增backVariables结构化变量"""
    try:
        var_name = request.POST.get('var_name', '').strip()
        json_structure = request.POST.get('json_structure', '').strip()
        description = request.POST.get('description', '').strip()
        env_name = request.POST.get('env_name', '环境1').strip()

        if not var_name:
            return HttpResponse('变量名不能为空')

        if EnvGlobalBackVariables.objects.filter(var_name=var_name, env_name=env_name).exists():
            return HttpResponse(f'回写变量 [{var_name}] 已存在')

        username = request.session.get('user', '')

        max_sort = EnvGlobalBackVariables.objects.filter(env_name=env_name).aggregate(
            models.Max('sort_order')
        )['sort_order__max'] or 0

        EnvGlobalBackVariables.objects.create(
            var_name=var_name,
            json_structure=json_structure,
            description=description,
            is_enable=1,
            create_user=username,
            env_name=env_name,
            sort_order=max_sort + 1
        )

        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'保存失败: {str(e)}')


@csrf_exempt
@login_required
def updateBackVariables(request):
    """更新backVariables结构化变量"""
    try:
        id = request.POST.get('id')
        var_name = request.POST.get('var_name', '').strip()
        json_structure = request.POST.get('json_structure', '').strip()
        description = request.POST.get('description', '').strip()
        env_name = request.POST.get('env_name', '环境1').strip()

        if not var_name:
            return HttpResponse('变量名不能为空')

        EnvGlobalBackVariables.objects.filter(id=id).update(
            var_name=var_name,
            json_structure=json_structure,
            description=description,
            env_name=env_name
        )

        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'更新失败: {str(e)}')


@csrf_exempt
@login_required
def deleteBackVariables(request):
    """删除backVariables结构化变量"""
    try:
        id = request.POST.get('id')
        EnvGlobalBackVariables.objects.filter(id=id).delete()
        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'删除失败: {str(e)}')


# ==================== Hooks钩子脚本 CRUD ====================

@csrf_exempt
@login_required
def loadHooksList(request):
    """加载Hooks钩子脚本列表"""
    try:
        page = int(request.POST.get('page', 1))
        page_size = int(request.POST.get('page_size', 10))
        env_name = request.POST.get('env_name', '环境1')

        all_items = EnvGlobalHooks.objects.filter(env_name=env_name).order_by('sort_order', 'id').values()
        total = all_items.count()

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        items = all_items[start_idx:end_idx]

        rst = []
        for item in items:
            arr = [
                item['id'],
                item['hook_name'],
                item['hook_type'],
                item['hook_code'] or '',
                item['description'] or '',
                '启用' if item['is_enable'] == 1 else '禁用',
                item['create_user'] or '',
                item['update_time'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(item['update_time'], 'strftime') else str(item['update_time']),
                item.get('env_name', '环境1')
            ]
            rst.append(arr)

        return JsonResponse({
            'data': rst,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        })
    except Exception as e:
        return JsonResponse({'data': [], 'total': 0, 'error': str(e)})


@csrf_exempt
@login_required
def addHooks(request):
    """新增Hooks钩子脚本"""
    try:
        hook_name = request.POST.get('hook_name', '').strip()
        hook_type = request.POST.get('hook_type', 'pre').strip()
        hook_code = request.POST.get('hook_code', '').strip()
        description = request.POST.get('description', '').strip()
        env_name = request.POST.get('env_name', '环境1').strip()

        if not hook_name:
            return HttpResponse('钩子名称不能为空')

        if EnvGlobalHooks.objects.filter(hook_name=hook_name, env_name=env_name).exists():
            return HttpResponse(f'钩子 [{hook_name}] 已存在')

        username = request.session.get('user', '')

        max_sort = EnvGlobalHooks.objects.filter(env_name=env_name).aggregate(
            models.Max('sort_order')
        )['sort_order__max'] or 0

        EnvGlobalHooks.objects.create(
            hook_name=hook_name,
            hook_type=hook_type,
            hook_code=hook_code,
            description=description,
            is_enable=1,
            create_user=username,
            env_name=env_name,
            sort_order=max_sort + 1
        )

        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'保存失败: {str(e)}')


@csrf_exempt
@login_required
def updateHooks(request):
    """更新Hooks钩子脚本"""
    try:
        id = request.POST.get('id')
        hook_name = request.POST.get('hook_name', '').strip()
        hook_type = request.POST.get('hook_type', 'pre').strip()
        hook_code = request.POST.get('hook_code', '').strip()
        description = request.POST.get('description', '').strip()
        env_name = request.POST.get('env_name', '环境1').strip()

        if not hook_name:
            return HttpResponse('钩子名称不能为空')

        EnvGlobalHooks.objects.filter(id=id).update(
            hook_name=hook_name,
            hook_type=hook_type,
            hook_code=hook_code,
            description=description,
            env_name=env_name
        )

        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'更新失败: {str(e)}')


@csrf_exempt
@login_required
def deleteHooks(request):
    """删除Hooks钩子脚本"""
    try:
        id = request.POST.get('id')
        EnvGlobalHooks.objects.filter(id=id).delete()
        return HttpResponse('200')
    except Exception as e:
        return HttpResponse(f'删除失败: {str(e)}')

# ==================== Header配置 CRUD ====================
@csrf_exempt
@login_required
def initializeSortOrder(request):
    """初始化所有现有变量的 sort_order（按 var_id 正序）"""
    try:
        env_name = request.POST.get('env_name', '环境1')

        # 获取所有变量，按 var_id 正序排列
        vars = EnvGlobalVariables.objects.filter(env_name=env_name).order_by('var_id')

        for i, var in enumerate(vars, start=1):
            var.sort_order = i
            var.save(update_fields=['sort_order'])

        return HttpResponse(f'已初始化 {len(vars)} 个变量的 sort_order')
    except Exception as e:
        import traceback
        print(f"ERROR: {str(e)}")
        print(traceback.format_exc())
        return HttpResponse(f'初始化失败: {str(e)}')





