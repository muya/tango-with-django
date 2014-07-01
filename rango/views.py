from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

def index(request):
	context = RequestContext(request)
	context_dict = {'boldmessage': "I am bold font from the context"}
	return render_to_response('rango/index.html', context_dict, context)

def about(request):
	page_content = "<a href='/rango/'>Home</a><br>Rango Says: Here is the about page"
	return HttpResponse(page_content)
