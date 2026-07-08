import time
import logging
import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from time import sleep
from .models import AutotestplatParameter

# 报告保存路径
report_path = os.path.join(os.path.dirname(__file__), 'report', 'test_report.html')

def get_email_config():
    """从数据库获取邮件配置"""
    try:
        # 获取邮件发送人配置 (格式: smtp服务器,邮箱地址,授权码)
        sender_config = AutotestplatParameter.objects.filter(keywords='email_sender').first()
        # 获取邮件接收人配置
        accepters_config = AutotestplatParameter.objects.filter(keywords='email_accepters').first()
        
        if not sender_config or not accepters_config:
            return None
        
        # 解析发送人配置
        sender_parts = sender_config.value.split(',')
        if len(sender_parts) != 3:
            logging.error(f"邮件发送人配置格式错误: {sender_config.value}")
            return None
        
        mail_host = sender_parts[0].strip()
        mail_user = sender_parts[1].strip()
        mail_pass = sender_parts[2].strip()
        email_accepters_value = accepters_config.value.strip()
        
        return {
            'mail_host': mail_host,
            'mail_user': mail_user,
            'mail_pass': mail_pass,
            'email_accepters_value': email_accepters_value
        }
    except Exception as e:
        logging.error(f"获取邮件配置失败: {str(e)}")
        return None

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
        table_rows.append(row.strip())  

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


def web_html_template(report_id, product, testcase_name, testcase_sum, testcase_pass, testcase_fail, testcase_ng, testcase_pass_per, testtime, webcases):
    """Web测试报告HTML模板"""
    table_rows = []
    for case in webcases:
        result_text = "通过" if case.get('result') == 'pass' else "失败"
        result_color = "green" if case.get('result') == 'pass' else "red"

        row = f"""
          <tr>
              <td>{case.get('step_number', 'N/A')}</td>
              <td>{case.get('step_name', 'N/A')}</td>
              <td>{case.get('find_method', 'N/A')}</td>
              <td>{case.get('element_value', 'N/A')}</td>
              <td>{case.get('operation', 'N/A')}</td>
              <td style="color:{result_color};font-weight:bold;">{result_text}</td>
              <td>{case.get('response_time', 'N/A')}</td>
              <td style="word-break:break-all;">{case.get('error_log', '')}</td>
          </tr>"""
        table_rows.append(row.strip())

    if not table_rows:
        table_rows = ["<tr><td colspan='8' style='text-align:center;'>暂无测试数据</td></tr>"]

    table_body_rows = "\n".join(table_rows)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Web自动化测试报告</title>
    </head>
    <body>
    
    <h1 style="font-size: 24px;color:green;text-align:center;">Web UI自动化测试报告</h1><br>
                <ul class="headline" style="margin-left: -20px">
                    <li>测试报告ID：<span style="font-size: 16px">{report_id} </span></li>
                </ul>
                <ul class="headline" style="margin-left: -20px">
                    <br>
                    <li>产品/项目：<span style="font-size: 16px">{product} </span></li>
                </ul>
                <ul class="headline" style="margin-left: -20px">
                    <br>
                    <li>测试用例：<span style="font-size: 16px">{testcase_name} </span></li>
                </ul>
                <ul class="headline" style="margin-left: -20px;">
                    <br>
                    <li>步骤总数： <span id="testcase_all_count" style="font-size: 16px"> {testcase_sum}</span>
                    &nbsp;&nbsp;通过： <span style="font-size: 16px;color: blue"> {testcase_pass}</span>
                    &nbsp;&nbsp;失败：<span style="font-size: 16px;color: red"> {testcase_fail}</span>
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
                <th>步骤序号</th>
                <th>步骤名称</th>
                <th>定位方式</th>
                <th>元素值</th>
                <th>操作方法</th>
                <th>执行结果</th>
                <th>响应时间</th>
                <th>错误日志</th>
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
        <title>Web UI自动化测试报告</title>
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
            width: 95%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            table-layout: fixed;
            border: 2px solid #666; 
        }}
        th, td {{
            padding: 8px 10px;
            text-align: left;
            border: 1px solid #666; 
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        th {{
            background-color: #d9edf7;
            font-weight: bold;
            border-bottom: 2px solid #666; 
        }}
        tr:hover {{
            background-color: #f5f5f5;
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

        <h1 style="font-size: 24px;color:green;text-align:center;">Web UI自动化测试报告</h1><br>
                  <ul class="headline" style="margin-left: -20px">
                    <li>测试报告ID：<span style="font-size: 16px">{report_id} </span></li>
                </ul>
                <ul class="headline" style="margin-left: -20px">
                    <br>
                    <li>产品/项目：<span style="font-size: 16px">{product} </span></li>
                </ul>
                <ul class="headline" style="margin-left: -20px">
                    <br>
                    <li>测试用例：<span style="font-size: 16px">{testcase_name} </span></li>
                </ul>
                <ul class="headline" style="margin-left: -20px;">
                    <br>
                    <li>步骤总数： <span id="testcase_all_count" style="font-size: 16px"> {testcase_sum}</span>
                    &nbsp;&nbsp;通过： <span style="font-size: 16px;color: blue"> {testcase_pass}</span>
                    &nbsp;&nbsp;失败：<span style="font-size: 16px;color: red"> {testcase_fail}</span>
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
                <th>步骤序号</th>
                <th>步骤名称</th>
                <th>定位方式</th>
                <th>元素值</th>
                <th>操作方法</th>
                <th>执行结果</th>
                <th>响应时间</th>
                <th>错误日志</th>
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
        
        email_config = get_email_config()
        if not email_config:
            return JsonResponse({
                "message": "邮件配置不存在或格式错误，请在系统设置中配置邮件信息"
            }, status=500)
        
        mail_host = email_config['mail_host']
        mail_user = email_config['mail_user']
        mail_pass = email_config['mail_pass']
        email_accepters_value = email_config['email_accepters_value']
        
        report_id = data.get('report_id')
        product = data.get('product')
        testcase = data.get('testcase')
        testplan = data.get('testplan')
        testcase_sum = data.get('testcase_sum')
        testcase_pass = data.get('testcase_pass')
        testcase_fail = data.get('testcase_fail')
        testcase_ng = data.get('testcase_ng')
        testcase_pass_per = data.get('testcase_pass_per')
        testtime = data.get('testtime')
        testcase_details = data.get('apicases')
        webcases = data.get('webcases')  

        print("Report ID:", report_id)
        print("Product:", product)
        print("Testcase:", testcase)
        print("Testplan:", testplan)
        print("Testcase Sum:", testcase_sum)
        print("Testcase Pass:", testcase_pass)
        print("Testcase Fail:", testcase_fail)
        print("Testcase NG:", testcase_ng)
        print("Testcase Pass Percentage:", testcase_pass_per)
        print("Test Time:", testtime)
        print("Mail Host:", mail_host)
        print("Mail User:", mail_user)
        print("Email Accepters:", email_accepters_value)
        if testcase_details:
            print("API Cases:",testcase_details)
        if webcases:
            print("Web Cases:", webcases)

        html_content = ''
        email_content = ""
        try:
            send_time = time.strftime("%Y-%m-%d %H:%M:%S")
            
            is_web_report = webcases is not None and len(webcases) > 0
            
            if is_web_report:
                report_filename = f"web_testreport_{report_id}.html"
                subject = f'Web UI自动化测试报告_{testcase}'
                html_content, email_content = web_html_template(report_id, product, testcase, testcase_sum, testcase_pass,
                                                            testcase_fail, testcase_ng, testcase_pass_per, testtime,
                                                            webcases)
            else:
                report_filename = f"api_testreport_{report_id}.html"
                subject = f'接口自动化测试报告_{testplan}'
                html_content, email_content = html_template(report_id, product, testplan, testcase_sum, testcase_pass,
                                                            testcase_fail, testcase_ng, testcase_pass_per, testtime,
                                                            testcase_details)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                logging.info("write content")
                print(send_time)
                f.write(html_content)
            logging.info('报告已写入成功，路径为:{}'.format(report_path))
        except Exception as e:
            logging.error('邮件内容拼接失败:{}!'.format(e))
            return JsonResponse({"message": f"邮件发送失败: {str(e)}"}, status=500)

        msg = MIMEMultipart('mixed')

        email_accepters = []
        if re.findall(',', email_accepters_value):
            accepters = str(email_accepters_value).split(',')
            for accepter in accepters:
                email_accepters.append(accepter)
            msg['To'] = ','.join(email_accepters)
        elif isinstance(email_accepters_value, str):
            msg['To'] = email_accepters_value
            email_accepters = email_accepters_value

        msg['From'] = mail_user
        msg['Subject'] = Header(subject, 'utf-8')
        msg.attach(MIMEText(email_content, 'html', 'utf-8'))
        
        try:
            with open(report_path, 'rb') as f:
                file_data = f.read()
            
            html_attachment = MIMEText(file_data.decode('utf-8'), 'html', 'utf-8')
            html_attachment.add_header('Content-Disposition', 'attachment', filename=report_filename)
            msg.attach(html_attachment)
        except Exception as e:
            logging.error(f'附件读取失败: {e}')
            return JsonResponse({"message": f"附件读取失败: {str(e)}"}, status=500)
        
        try:
            emailserver = smtplib.SMTP_SSL(mail_host, 465)
            logging.info("邮箱登录中...")
            emailserver.login(mail_user, mail_pass)
            sleep(3)
            emailserver.sendmail(mail_user, email_accepters, msg.as_string())
            sleep(3)
            emailserver.quit()
            logging.info("邮件已发送成功。")
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"邮件认证失败：请检查邮箱账号和授权码是否正确。错误详情: {str(e)}"
            logging.error(error_msg)
            return JsonResponse({"message": error_msg}, status=500)
        except smtplib.SMTPConnectError as e:
            error_msg = f"SMTP服务器连接失败：请检查SMTP服务器地址({mail_host})是否正确，或网络连接是否正常。错误详情: {str(e)}"
            logging.error(error_msg)
            return JsonResponse({"message": error_msg}, status=500)
        except Exception as e:
            error_msg = f"邮件发送失败: {str(e)}"
            logging.error(error_msg)
            try:
                emailserver.quit()
            except:
                pass
            return JsonResponse({"message": error_msg}, status=500)

    return JsonResponse({"message": "邮件发送成功!"})

