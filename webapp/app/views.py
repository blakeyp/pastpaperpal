from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.conf import settings
from django.http import HttpResponse

from django.core.files.storage import FileSystemStorage

from django.core.exceptions import ObjectDoesNotExist

from .forms import PaperForm, NotesForm
from .models import Paper, Question, Rubric, UserNotes

from scripts.paper_parser import get_details, extract_questions
from scripts.question_parser import get_marks
from scripts.similar import get_similar_qs
from scripts.merge_contds import merge

from django.contrib.auth import authenticate, login, logout

import json, os

from django.http import JsonResponse

from django.contrib import messages

from collections import Counter, namedtuple

# each function defines a 'view'
# views represent 'types' of web pages
# called when there is a URL match
# each returns either an HttpResponse or an exception

def index(request):

    # get all available modules according to uploaded paper's in db
    modules=[]
    for paper in Paper.objects.all():
        modules.append(paper.module_code.upper())  

    # split into 2 lists
    module_codes = []; count_papers = []

    for module, count in sorted(Counter(modules).items()):
        module_codes.append(module)
        count_papers.append(count)

    module_codes = json.dumps(list(module_codes))
    count_papers = json.dumps(list(count_papers))

    return render(request, 'index.html')


def sign_in(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)

    if user is not None:
        login(request, user)
    
    return redirect('app:index')


def sign_out(request):
    logout(request)
    return redirect('app:index')



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

            paper = Paper(module_code=module_code, year=year)
            paper.save()

            fs = FileSystemStorage()
            file_name = 'uploads/'+module_code+'_'+year+'.pdf'
            fs.save(file_name, file)

            num_qs, crop_sizes, sections = extract_questions(file_name, paper.pk)

            merge('media/papers/'+str(paper.pk)+'/')   # merge contds

            # now can remove uploaded file, don't need it anymore - not true!!!
            # instead, remove on deleting a paper from db
            #os.remove('media/'+file_name)

            # traverse questions in paper to populate questions records in db
            for i in range(num_qs):

                q_num = i+1

                total_marks, marks_breakdown = get_marks(paper.pk, q_num)
                marks_breakdown = json.dumps(marks_breakdown) if marks_breakdown else None

                new_section = sections.get(q_num)   # lookup if new section starts this question

                question = Question(paper=paper, q_num=q_num,
                    width=crop_sizes[i][0], height=crop_sizes[i][1],
                    total_marks=total_marks,
                    marks_breakdown=marks_breakdown,
                    new_section=new_section)
                question.save()

            rubric = Rubric(paper=paper, total_qs=num_qs, calcs_allowed=False)
            rubric.save()
            
            # message denoting upload sucess, with year
            messages.add_message(request, messages.SUCCESS, paper.year)
            
            return redirect('app:module', module=module_code)
    else:
        form = PaperForm()
    return render(request, 'upload.html', { 'form': form })

def module(request, module):
    storage = messages.get_messages(request)
    message = None
    for msg in storage:
        message = int(msg.message)
        break
    print message
    papers = get_list_or_404(Paper, module_code=module)
    return render(request, 'module.html', {'module': module,
        'papers': papers, 'message':message})

def paper(request, module, year):
    paper = get_object_or_404(Paper, module_code=module, year=year)
    other_years = []
    for o_paper in Paper.objects.filter(module_code=module).exclude(year=year):   # years of other papers available for this module in db
        other_years.append(o_paper.year)
    other_years.sort(reverse=True)
    rubric = Rubric.objects.get(paper=paper)
    questions = Question.objects.filter(paper=paper)
    q_width = questions[0].width
    print questions
    return render(request, 'paper.html', {'paper':paper, 'other_years':other_years, 'rubric':rubric, 'questions': questions, 'q_width':q_width})

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

def question(request, module, year, q_num):
    paper = get_object_or_404(Paper, module_code=module, year=year)
    question = get_object_or_404(Question, paper=paper, q_num=q_num)

    # use faux object type thing - maybe all this stuff better processed before db entry?
    Part = namedtuple('Part', ['part','marks','mins','percent'])

    marks_breakdown = json.loads(question.marks_breakdown)
    print marks_breakdown
    total_time = 120
    mins_per_mark = total_time/100.0
    total_marks = question.total_marks

    print total_marks

    q_time = int(round(total_marks*mins_per_mark)*60)
    q_mins = int(round(total_marks*mins_per_mark))

    parts = []
    for i in range(len(marks_breakdown)):
        part = chr(ord('a')+i)
        marks = marks_breakdown[i]
        mins = round((marks*mins_per_mark)*2)/2
        if mins.is_integer():
            mins = str(mins).split('.', 1)[0]
        else:
            mins = str(mins).split('.', 1)[0]+'&frac12;'

        percent = marks/float(total_marks)*100
        parts.append(Part(part, marks, mins, percent))

    user_notes = None
    user = request.user
    if user.is_authenticated:
        try:
            user_notes = UserNotes.objects.get(user=user, question=question).notes
            print 'found!', user_notes
        except ObjectDoesNotExist:
            print 'no user notes found'

    return render(request, 'question.html', {'paper':paper, 'question':question,
        'user_notes':user_notes, 'parts':parts, 'q_time':q_time, 'q_mins':q_mins})

def save_notes(request, module, year, q_num):
    if request.method == "POST":
        user = request.user
        if user.is_authenticated:
            q_id = request.POST['q_id']
            notes = request.POST['notes']
            UserNotes.objects.update_or_create(user=user, question=Question.objects.get(pk=q_id),
                defaults={'notes':notes})
            return HttpResponse(status=200)
    return HttpResponse(status=403)