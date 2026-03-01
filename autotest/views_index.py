from django.shortcuts import render
from django.http import HttpResponseRedirect


def indexView(request):
    return render(request, "index.html")


def aiPage(request):
    # return HttpResponseRedirect("http://127.0.0.1:8080")
    return render(request, "ai.html")

def aiTestcase(request):
    # return HttpResponseRedirect("http://127.0.0.1:8080")
    return render(request, "ai_testcase.html")

