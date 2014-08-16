from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse


def setup(request):
    return HttpResponse("setup")

def form(request):
    return HttpResponse("form")

def closed(request):
    return HttpResponse("closed")
