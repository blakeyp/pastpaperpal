from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .forms import PaperForm
from .models import Paper, Question, Rubric, UserNotes, UserCompletedQuestion

from scripts.paper_parser import get_details, extract_questions
from scripts.question_parser import get_marks
from scripts.rubric_parser import get_rubric
from scripts.similar import get_similar_qs
from scripts.merge_contds import merge

from collections import Counter, namedtuple
import json

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
    
    prev_page = request.GET['previous']
    return redirect(prev_page)

def sign_out(request):
    logout(request)
    prev_page = request.GET['previous']
    return redirect(prev_page)

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

            # merge text of questions that continue over pages
            merge('media/papers/'+str(paper.pk)+'/')

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

            time, calcs_allowed, choice_choose, choice_outof, choice_text = get_rubric(paper.pk)

            rubric = Rubric(paper=paper, total_qs=num_qs, time_mins=time, calcs_allowed=calcs_allowed, 
                choice_choose=choice_choose, choice_text=choice_text)
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

    papers = Paper.objects.filter(module_code=module).order_by('-year')
    latest_paper = papers.first()
    rubric = Rubric.objects.get(paper=latest_paper)

    total_mins = rubric.time_mins
    time_hrs = total_mins/60
    time_mins = total_mins % 60

    for p in papers:

        completed_qs = 0
        p.total_qs = Rubric.objects.get(paper=p).total_qs

        user = request.user
        if user.is_authenticated:
            for q in Question.objects.filter(paper=p):
                try:
                    UserCompletedQuestion.objects.get(user=user,question=q)
                    completed_qs += 1
                except ObjectDoesNotExist:
                    print 'user not done this question'

        p.completed_qs = completed_qs
        p.completed_percent = float(p.completed_qs)/p.total_qs * 100


    return render(request, 'module.html', {'module':module,
        'papers':papers, 'latest_paper':latest_paper, 'rubric':rubric, 
        'time_hrs':time_hrs, 'time_mins':time_mins, 'message':message })

def paper(request, module, year):
    paper = get_object_or_404(Paper, module_code=module, year=year)
    other_years = []   # years of other papers available for this module in db
    for o_paper in Paper.objects.filter(module_code=module):
        other_years.append(o_paper.year)
    other_years.sort(reverse=True)
    rubric = Rubric.objects.get(paper=paper)
    questions = Question.objects.filter(paper=paper)
    q_width = questions[0].width

    user = request.user
    if user.is_authenticated:
        for q in questions:
            try:
                q.completed = UserCompletedQuestion.objects.get(user=user,question=q)
            except ObjectDoesNotExist:
                pass   # user has not done this question, continue

    print questions
    return render(request, 'paper.html', {'paper':paper, 'other_years':other_years, 
    	'rubric':rubric, 'questions': questions, 'q_width':q_width})

def similar_qs(request, module, year, q_num):
    # get paper object for paper of question being compared to
    paper = get_object_or_404(Paper, module_code=module, year=year)
    
    # get all other available papers
    # for this module (excluding this year's)
    other_papers = [p.pk for p in Paper.objects.filter(module_code=module).exclude(year=year)]

    if not other_papers:
        return HttpResponse('Sorry, no available papers to compare to!')
    else: get_top = 3   # top number of questions to return

    sim_qs = get_similar_qs(paper.pk, q_num, other_papers, get_top)
    # returns paper_id, q_num pairs

    similar_qs = []
    q_width = 0
    # get paper object from paper_id
    # so that can label questions by year
    # and question object from q_num
    for q in sim_qs:
        question = Question.objects.get(paper=q[0],q_num=q[1])
        question.paper = Paper.objects.get(pk=q[0])
        similar_qs.append(question)
        if question.width > q_width:
            q_width = question.width

    return render(request, 'similar_qs.html', {'similar_qs':similar_qs,
    	'get_top':get_top, 'q_width':q_width})

def question(request, module, year, q_num):
    paper = get_object_or_404(Paper, module_code=module, year=year)
    question = get_object_or_404(Question, paper=paper, q_num=q_num)
    other_questions = [q for q in Question.objects.filter(paper=paper)]

    total_time = Rubric.objects.get(paper=paper).time_mins
    mins_per_mark = total_time/100.0
    total_marks = question.total_marks

    q_time = int(round(total_marks*mins_per_mark)*60)
    q_mins = int(round(total_marks*mins_per_mark))

    Part = namedtuple('Part', ['part','marks','mins','percent', 'cumul_percent'])
    parts = []

    if question.marks_breakdown:
        marks_breakdown = json.loads(question.marks_breakdown)       
        cumul_percent = 0
        for i in range(len(marks_breakdown)):
            part = chr(ord('a')+i)
            marks = marks_breakdown[i]
            mins = round((marks*mins_per_mark)*2)/2
            if mins.is_integer():
                mins = str(mins).split('.', 1)[0]
            else:
                mins = str(mins).split('.', 1)[0]+'&frac12;'
            if mins == '0' or mins == '0&frac12;':
                mins = '&frac12;'
            percent = marks/float(total_marks)*100
            cumul_percent += percent
            parts.append(Part(part, marks, mins, percent, cumul_percent))

    user_notes = None
    completed_q = None
    user = request.user
    if user.is_authenticated:
        try:
            user_notes = UserNotes.objects.get(user=user, question=question).notes
        except ObjectDoesNotExist:
            pass
        try:
            completed_q = UserCompletedQuestion.objects.filter(user=user, question=question)
        except ObjectDoesNotExist:
            pass

    return render(request, 'question.html', {'paper':paper, 'question':question, 'other_questions':other_questions,
        'user_notes':user_notes, 'parts':parts, 'q_time':q_time, 'q_mins':q_mins, 'completed_q':completed_q})

# ajax views

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

def set_completed(request, module, year, q_num):
    if request.method == "POST":
        user = request.user
        if user.is_authenticated:
            q_id = request.POST['q_id']
            completed = request.POST['completed']

            if completed == 'set':
                completed_q = UserCompletedQuestion(user=user, question=Question.objects.get(pk=q_id))
                completed_q.save()
            elif completed == 'delete':
                UserCompletedQuestion.objects.filter(user=user, question=Question.objects.get(pk=q_id)).delete()

            return HttpResponse(status=200)
    return HttpResponse(status=403)