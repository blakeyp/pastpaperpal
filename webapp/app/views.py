from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.conf import settings
from django.http import HttpResponse

from django.core.files.storage import FileSystemStorage


from .forms import PaperForm
from .models import Paper
from .models import Rubric

from paper import get_details, extract_questions
from similar import get_similar_qs

import json

from django.http import JsonResponse

# each function defines a 'view'
# views represent 'types' of web pages
# called when there is a URL match
# each returns either an HttpResponse or an exception

def index(request):
    # get all available modules according to uploaded paper's in db
    modules=[]
    for paper in Paper.objects.all():
        modules.append(paper.module_code.upper())
    modules = set(modules)
    module_codes = json.dumps(list(modules))
    return render(request, 'index.html', {'module_codes':module_codes})

# ajax view that gets module codes of all papers in db
def get_modules(request):
    #json_response = 
    return JsonResponse({'modules': ['cs118', 'cs126', 'cs241']})

def upload(request):
    if request.method == 'POST' and request.FILES['file']:
        form = PaperForm(request.POST,request.FILES)   # populate form
        if form.is_valid():
            
            file=request.FILES['file']
            module_code, year = get_details(file)

            if Paper.objects.filter(module_code=module_code, 
                    year=year).exists():
                raise Exception('this paper already exists in db!')
            
            fs = FileSystemStorage()
            file_name = 'uploads/'+module_code+'_'+year+'.pdf'
            fs.save(file_name, file)

            paper = Paper(module_code=module_code,
                year=year)
            paper.save()

            num_qs = extract_questions(file_name, paper.pk)

            rubric = Rubric(paper=paper, total_qs=num_qs, calcs_allowed=False)
            rubric.save()

            return redirect('app:module', module_code)
    else:
        form = PaperForm()
    return render(request, 'upload.html', { 'form': form })

def module(request, module):
    papers = get_list_or_404(Paper, module_code=module)
    return render(request, 'module.html', {'module': module,
        'papers': papers})

def paper(request, module, year):
    paper = get_object_or_404(Paper, module_code=module, year=year)
    rubric = Rubric.objects.get(paper=paper)
    return render(request, 'paper.html', {'paper':paper, 'rubric':rubric, 'q_range': range(1,rubric.total_qs+1)})

def similar_qs(request, module, year, q_num):
    # get paper object for paper of question being compared to
    paper = get_object_or_404(Paper, module_code=module, year=year)
    
    # get all other available papers
    # for this module (excluding this year's)
    other_papers = [p.pk for p in Paper.objects.filter(module_code=module).exclude(year=year)]

    if not other_papers:
        return HttpResponse('sorry, no available papers to compare to!')
    else: get_top = len(other_papers)*2+1   # determine top number of questions to return

    similar_qs = get_similar_qs(paper.pk, q_num, other_papers, get_top)

    # get paper object from paper_id
    # so that can label questions by year
    for q in similar_qs: q[0] = Paper.objects.get(pk=q[0])

    return render(request, 'similar_qs.html', { 'similar_qs':similar_qs, 'get_top':get_top })