from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import AutotestplatProduct, AuthUser
from django.template.context_processors import csrf


def indexView(request):
    return render(request, "index.html")


def aiPage(request):
    user_name = request.session.get('user', '')
    
    # 获取当前用户信息
    if not user_name:
        return render(request, "login.html")
    
    user_obj = AuthUser.objects.filter(username=user_name).first()
    if not user_obj:
        return render(request, "login.html")
    
    # 获取产品列表
    product_all = AutotestplatProduct.objects.filter(delete_flag='N')
    product_id = user_obj.last_name
    
    if product_id:
        product_name = AutotestplatProduct.objects.filter(id=product_id).first().product_name
    else:
        product_name = ''
    
    c = csrf(request)
    c.update({"product_name": product_name, "product_alls": product_all})
    
    return render(request, "ai.html", c)

def aiTestcase(request):
    # return HttpResponseRedirect("http://127.0.0.1:8080")
    return render(request, "ai_testcase.html")

