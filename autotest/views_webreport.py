"""
Create by on 2026/7/7
"""
__author__ = 'Sen'
# -*- coding:utf-8 -*-
############################################
#Version：Autotestplat-V6.0
############################################
import time, json, os
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
from .models import *
from django.template.context_processors import csrf


def getWebReportView(request):
    """Web测试报告列表页"""
    user_name = request.session.get('user', '')
    product_all = AutotestplatProduct.objects.filter(delete_flag='N')
    product_id = AuthUser.objects.filter(username=user_name).first().last_name
    product_name = AutotestplatProduct.objects.filter(id=product_id).first().product_name
    c = csrf(request)
    c.update({"product_name": product_name, "product_alls": product_all})
    return render(request, "web_report.html", c)


@csrf_exempt
def loadWebReport(request):
    """加载Web测试报告列表数据"""
    username = request.session.get('user', '')
    
    if AuthUser.objects.filter(username=username).first().is_superuser == 1:
        # 获取所有唯一的 report_id
        unique_reports = AutotestplatWebTestResult.objects.values_list('report_id', flat=True).distinct()
        
        rst = []
        for report_id in unique_reports:
            # 获取该报告的第一条记录作为代表
            first_record = AutotestplatWebTestResult.objects.filter(report_id=report_id).first()
            if first_record:
                # 统计该报告的步骤数量
                step_count = AutotestplatWebTestResult.objects.filter(report_id=report_id).count()
                rst.append([
                    first_record.report_id,
                    first_record.product_id,
                    first_record.product_name,
                    first_record.testcase_name,
                    first_record.date_time,
                    first_record.result,
                    step_count
                ])
        
        # 按执行时间排序
        rst.sort(key=lambda x: x[4] or '', reverse=True)
    else:
        product_id_filter = AuthUser.objects.filter(username=username).first().last_name
        
        # 获取该产品的所有唯一 report_id
        unique_reports = AutotestplatWebTestResult.objects.filter(product_id=product_id_filter).values_list('report_id', flat=True).distinct()
        
        rst = []
        for report_id in unique_reports:
            first_record = AutotestplatWebTestResult.objects.filter(report_id=report_id, product_id=product_id_filter).first()
            if first_record:
                step_count = AutotestplatWebTestResult.objects.filter(report_id=report_id, product_id=product_id_filter).count()
                rst.append([
                    first_record.report_id,
                    first_record.product_id,
                    first_record.product_name,
                    first_record.testcase_name,
                    first_record.date_time,
                    first_record.result,
                    step_count
                ])
        
        rst.sort(key=lambda x: x[4] or '', reverse=True)
    
    realRst = {'data': rst}
    return JsonResponse(realRst)


@csrf_exempt
def getWebReportDetail(request, report_id):
    """获取Web测试报告详情"""
    items = AutotestplatWebTestResult.objects.filter(report_id=report_id).all().order_by('step_number')
    testreport_id = report_id
    testcase_name = items.first().testcase_name if items.exists() else ''
    testplan_time = items.first().date_time if items.exists() else ''
    product_name = items.first().product_name if items.exists() else ''

    testcase_all_count = len(AutotestplatWebTestResult.objects.filter(report_id=report_id).all())
    testcase_pass_count = len(AutotestplatWebTestResult.objects.filter(report_id=report_id).filter(result='pass').order_by('id'))
    testcase_fail_count = len(AutotestplatWebTestResult.objects.filter(report_id=report_id).filter(result='fail').order_by('id'))
    testcase_norun_count = testcase_all_count - testcase_pass_count - testcase_fail_count

    if testcase_all_count > 0:
        testcase_pass_pers = '{:.0%}'.format(testcase_pass_count / testcase_all_count)
    else:
        testcase_pass_pers = '0%'

    return render(request, "web_report_detail.html", {
        "test_result": items,
        "report_id": testreport_id,
        "testcase_name": testcase_name,
        "testcase_all_count": testcase_all_count,
        "testcase_pass_count": testcase_pass_count,
        "testcase_fail_count": testcase_fail_count,
        "testcase_norun_count": testcase_norun_count,
        "testcase_pass_pers": testcase_pass_pers,
        "testplan_time": testplan_time,
        'product_name': product_name
    })


@csrf_exempt
def deleteWebReport(request):
    """删除Web测试报告"""
    id = request.POST.get('report_id')
    AutotestplatWebTestResult.objects.filter(report_id=id).delete()
    return HttpResponse('200')
