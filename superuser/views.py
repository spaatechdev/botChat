from django.shortcuts import render
from chatBot.decorators import login_required
from django.contrib import messages
import pathlib

import environ
env = environ.Env()
environ.Env.read_env()

context = {}
context['project_name'] = env("PROJECT_NAME")
context['client_name'] = env("CLIENT_NAME")

# Create your views here.
@login_required
def dashboard(request):
    return render(request, 'portal/dashboard.html', context)


@login_required
def serviceTexts(request):
    file_path = "media/serviceTexts.txt"
    if request.method == "POST":
        editorText = request.POST['editor']
        f = open(file_path,"w+")
        content = editorText
        f.write(content)
        f.close()
        messages.success(request, 'Service Information Updated Successfully.')
    f = open(file_path)
    content = f.read()
    f.close()
    context.update({
        'content' : content
    })
    return render(request, 'portal/serviceTexts.html', context)