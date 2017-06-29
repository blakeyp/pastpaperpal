from .models import Paper
from collections import Counter
import json

def get_modules(request):
  
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

  return {'module_codes':module_codes, 'count_papers':count_papers}