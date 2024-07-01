from django.shortcuts import render
from django.http import HttpResponse


def login_page(request):
    return HttpResponse('Login Endpoint')


def register_page(request):
    return HttpResponse('Register Endpoint')


def user_page(request):
    return HttpResponse('User Endpoint')
