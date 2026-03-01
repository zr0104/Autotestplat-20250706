#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import os
import re
import smtplib
import time
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from time import sleep
from django.http import JsonResponse
from autotest.models import AutotestplatParameter


email_sender_value = AutotestplatParameter.objects.filter(keywords='email_sender').first().value
email_accepters_value = AutotestplatParameter.objects.filter(keywords='email_accepters').first().value
# print(email_sender_value)
# print(email_accepters_value)

mail_host = email_sender_value.split(",")[0]   #"smtp.qq.com"
mail_user = email_sender_value.split(",")[1]   #"7980068@qq.com"
mail_pass=email_sender_value.split(",")[2]   #"rhdxglwjrznbbihj"


# 修改邮件发送地址
# report_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
report_dir = os.getcwd()
# report_dir = Path(__file__).parent.resolve()
# report_dir = Path.cwd()
report_path = os.path.join(report_dir,"/autotest/report", "/report_{}.html".format(time.strftime("%Y%m%d%H%M%S")))


def html_template(report_id,product,testplan,testcase_sum,testcase_pass,testcase_fail,testcase_ng,testcase_pass_per,testtime,testcase_details):
    print(testcase_details)
    table_rows = []
    for case in testcase_details:
        result_text = "通过" if case.get('result') == 0 else "不通过"
        result_color = "green" if case.get('result') == 0 else "red"

        row = f"""
          <tr>
              <td>{case.get('name', 'N/A')}</td>
              <td>{case.get('method', 'N/A')}</td>
              <td style="word-break:break-all;">{case.get('url', 'N/A')}</td>
              <td style="color:{result_color};font-weight:bold;">{result_text}</td>
              <td>{case.get('response_time', 'N/A')}</td>
          </tr>"""
        table_rows.append(row.strip())  #

    if not table_rows:
        table_rows = ["<tr><td colspan='5' style='text-align:center;'>暂无测试数据</td></tr>"]

    table_body_rows = "\n".join(table_rows)


    html_content = f"""
   <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>apiautotest</title>
    
    </head>
    <body>
    
    <h1 style="font-size: 24px;color:green;text-align:center;">接口自动化测试报告</h1><br>
                <ul class="headline" style="margin-left: -20px">
                    <li>测试报告ID：<span style="font-size: 16px">{report_id} </span></li>
                </ul>
                <ul class="headline" style="margin-left: -20px">
                    <br>
                    <li>产品/项目：<span style="font-size: 16px">{product} </span></li>
                </ul>
                <ul class="headline" style="margin-left: -20px">
                    <br>
                    <li>测试计划：<span style="font-size: 16px">{testplan} </span></li>
                </ul>
                <ul class="headline" style="margin-left: -20px;">
                    <br>
                    <li>用例总数： <span id="testcase_all_count" style="font-size: 16px"> {testcase_sum}</span>
                    &nbsp;&nbsp;通过： <span style="font-size: 16px;color: blue"> {testcase_pass}</span>
                    &nbsp;&nbsp;不通过：<span style="font-size: 16px;color: red"> {testcase_fail}</span>
                   &nbsp;&nbsp;未执行： <span style="font-size: 16px;color: lightgrey"> {testcase_ng}</span>
                    &nbsp;&nbsp;成功率： <span style="font-size: 16px"> {testcase_pass_per}</span></li>
                </ul>
                <ul class="headline" style="margin-left: -20px">
                    <br>
                    <li>测试时间： <span style="font-size: 14px;font-weight: normal"> {testtime}</span></li>
                </ul>
    <br>
    <br>
    <table border="1" style="width:100%; text-align:left;">
        <thead>
            <tr>
                <th>接口名称</th>
                <th>请求方法</th>
                <th>接口URL</th>
                <th>测试结果</th>
                <th>响应时间</th>
            </tr>
        </thead>
        <tbody>
            {table_body_rows}
           
        </tbody>
    </table>
    <br>
    <br>

</body>
</html>
    """

    email_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>接口自动化测试报告</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 20px;
            color: #333;
        }}
        h1 {{
            text-align: center;
        }}
        table {{
            width: 80%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            table-layout: fixed;
            border: 2px solid #666; 
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border: 1px solid #666; 
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            width: 1%;
        }}
        th {{
            background-color: #d9edf7;
            font-weight: bold;
            border-bottom: 2px solid #666; 
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .pass-row {{
            background-color: #dff0d8; 
        }}
        .fail-row {{
            background-color: #f2dede; 
        }}
        .unknown-row {{
            background-color: #f0f0f0; 
        }}
        .blue {{
                color: blue;
                font-weight: bold;
        }}
        .green {{
                color: green;
                font-weight: bold;
        }}
        .red {{
                color: red;
                font-weight: bold;
        }}
        .gray {{
                color: gray;
                font-weight: bold;
        }}
        
    </style>
    </head>
    <body>
   
    <br>

        <h1 style="font-size: 24px;color:green;text-align:center;">接口自动化测试报告</h1><br>
                  <ul class="headline" style="margin-left: -20px">
                    <li>测试报告ID：<span style="font-size: 16px">{report_id} </span></li>
                </ul>
                <ul class="headline" style="margin-left: -20px">
                    <br>
                    <li>产品/项目：<span style="font-size: 16px">{product} </span></li>
                </ul>
                <ul class="headline" style="margin-left: -20px">
                    <br>
                    <li>测试计划：<span style="font-size: 16px">{testplan} </span></li>
                </ul>
                <ul class="headline" style="margin-left: -20px;">
                    <br>
                    <li>用例总数： <span id="testcase_all_count" style="font-size: 16px"> {testcase_sum}</span>
                    &nbsp;&nbsp;通过： <span style="font-size: 16px;color: blue"> {testcase_pass}</span>
                    &nbsp;&nbsp;不通过：<span style="font-size: 16px;color: red"> {testcase_fail}</span>
                   &nbsp;&nbsp;未执行： <span style="font-size: 16px;color: lightgrey"> {testcase_ng}</span>
                    &nbsp;&nbsp;成功率： <span style="font-size: 16px"> {testcase_pass_per}</span></li>
                </ul>
                <ul class="headline" style="margin-left: -20px">
                    <br>
                    <li>测试时间： <span style="font-size: 14px;font-weight: normal"> {testtime}</span></li>
                </ul>
                    <br>

    <table border="1" style="width:100%; text-align:left;">
        <thead>
            <tr>
                <th>接口名称</th>
                <th>请求方法</th>
                <th>接口URL</th>
                <th>测试结果</th>
                <th>响应时间</th>
            </tr>
        </thead>
        <tbody>
            {table_body_rows}
        </tbody>
    </table>
    <br>
    <br>
 
    </body>
    </html>
            """

    return html_content, email_content



def sendReportToEmail(request):

    user_name=request.user.username
    print("username is ",user_name)

    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        print(data)
        report_id = data.get('report_id')
        product = data.get('product')
        testplan = data.get('testplan')
        testcase_sum = data.get('testcase_sum')
        testcase_pass = data.get('testcase_pass')
        testcase_fail = data.get('testcase_fail')
        testcase_ng = data.get('testcase_ng')
        testcase_pass_per = data.get('testcase_pass_per')
        testtime = data.get('testtime')
        testcase_details = data.get('apicases')

        print("Report ID:", report_id)
        print("Product:", product)
        print("Testplan:", testplan)
        print("Testcase Sum:", testcase_sum)
        print("Testcase Pass:", testcase_pass)
        print("Testcase Fail:", testcase_fail)
        print("Testcase NG:", testcase_ng)
        print("Testcase Pass Percentage:", testcase_pass_per)
        print("Test Time:", testtime)
        print("apicases:",testcase_details)

        html_content = ''
        email_content = ""
        try:
            send_time = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(report_path, 'w', encoding='utf-8') as f:
                logging.info("write content")
                print(send_time)
                html_content, email_content = html_template(report_id, product, testplan, testcase_sum, testcase_pass,
                                                            testcase_fail, testcase_ng, testcase_pass_per, testtime,
                                                            testcase_details)
                f.write(html_content)
            logging.info('报告已写入成功，路径为:{}'.format(report_path))
        except Exception as e:
            logging.error('邮件内容拼接失败:{}!'.format(e))

        msg = MIMEMultipart('mixed')

        email_accepters = []
        if re.findall(',', email_accepters_value):
            accepters = str(email_accepters_value).split(',')
            for accepter in accepters:
                email_accepters.append(accepter)
            msg['To'] = ','.join(email_accepters)
            # return newlist
        elif isinstance(email_accepters_value, str):
            msg['To'] = email_accepters_value
            email_accepters = email_accepters_value
            # return accepters

        # receivers = format_accepters(email_accepters_value, msg)
        msg['From'] = mail_user
        subject = '接口自动化测试报告_{}'.format(testplan)
        msg['Subject'] = Header(subject, 'utf-8')
        msg.attach(MIMEText(email_content, 'html', 'utf-8'))
        with open(report_path, 'r', encoding='utf-8') as f:
            html_attachment = MIMEApplication(f.read().encode('utf-8'), _subtype='html', _charset='utf-8')
        html_attachment.add_header('Content-Disposition', 'attachment', filename="apitestreport_project.html")
        msg.attach(html_attachment)
        try:
            emailserver = smtplib.SMTP_SSL(mail_host, 465)
            logging.info("邮箱登录中...")
            emailserver.login(mail_user, mail_pass)
            sleep(3)
            emailserver.sendmail(mail_user, email_accepters, msg.as_string())
            sleep(3)
            emailserver.quit()
            logging.info("邮件已发送成功。")
        except Exception as e:
            emailserver.quit()
            logging.info("邮件发送失败。" + '\n' + '异常信息:{}'.format(e))

    return JsonResponse({"message": "邮件发送成功!"})

