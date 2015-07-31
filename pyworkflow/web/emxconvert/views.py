# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from pyworkflow.web.app.views_util import getResourceCss, getResourceJs, getResourceIcon, getServiceManager


from models import Document
from forms import DocumentForm
import os

def list(request):
    url=''
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            file_new = request.FILES['docfile']
            print("file_new", type(file_new), file_new.name)
            newdoc = Document(docfile = file_new)
            request.session['newdoc']=newdoc
            request.session['file_new']=file_new
            #            emxFileName = (os.path.splitext(file_new.name)[0]+'.emx')
            newdoc.save()#saves doc

            # Redirect to the document list after POST
            #            return HttpResponseRedirect(reverse('myapp.views.list'))
            return HttpResponseRedirect(reverse('emxconvert.views.list'))
    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    if 'newdoc' in request.session:
        document = request.session['newdoc']
        file_new = request.session['file_new']
    else:
        document = None
        file_new = None
    #print("document",document.docfile.name)
    # Render list page with the documents and the form,

    return render_to_response(
        'emxconvert/list.html',
        {'document': document,
         'form': form,
         'file_new': file_new,
         'general_css': getResourceCss('general'),
         },
        context_instance=RequestContext(request)
    )


# Create your views here.
from django.http import HttpResponse

def index(request):
    return HttpResponse("Greeting from emxConvert")