from __future__ import unicode_literals

from django.db import models
from django.dispatch import receiver

from django.contrib.auth.models import User

import os, shutil

# to reset database (i.e. delete all records and tables),
# delete contents of migrations folder (apart from
# '__init__.py') then run 'python manage.py flush'
# might also need to clear 'django_migrations' in db!

class Paper(models.Model):
	module_code = models.CharField(max_length=5)
	year = models.PositiveSmallIntegerField()

	def __str__(self):
		return str(self.pk) + ': ' + self.module_code + ', ' + str(self.year)

# deletes past paper's directory on 'post_delete'
@receiver(models.signals.post_delete, sender=Paper)
def delete_paper_dir(sender, instance, *args, **kwargs):
    print 'deleting: ', instance
    paper_file = 'media/uploads/'+instance.module_code+'_'+str(instance.year)+'.pdf'
    if os.path.isfile(paper_file):
    	os.remove(paper_file)
    paper_dir = 'media/papers/'+str(instance.pk)
    if os.path.isdir(paper_dir):
        shutil.rmtree(paper_dir)

class Rubric(models.Model):
	paper = models.ForeignKey(Paper,on_delete=models.CASCADE)
	total_qs = models.PositiveSmallIntegerField()
	time_mins = models.PositiveSmallIntegerField(null=True)
	calcs_allowed = models.NullBooleanField(null=True)
	choice_choose = models.PositiveSmallIntegerField(null=True)
	choice_text = models.CharField(max_length=100,null=True)

	def __str__(self):
		return str(self.paper.pk) + ', ' + str(self.time_mins) + ', ' + str(self.calcs_allowed) + ', ' + str(self.choice_choose) + ', ' + str(self.choice_text)

	# class Meta:
	# 	unique_together = ('module_code', 'year')

class Question(models.Model):
	paper = models.ForeignKey(Paper,on_delete=models.CASCADE)
	q_num = models.PositiveSmallIntegerField()
	width = models.PositiveSmallIntegerField()
	height = models.PositiveSmallIntegerField()
	total_marks = models.PositiveSmallIntegerField()
	marks_breakdown = models.CharField(max_length=200,null=True)
	new_section = models.CharField(max_length=2,null=True)

	def __str__(self):
		return str(self.paper.pk) + ', ' + str(self.q_num) + ', ' + str(self.width) + ', ' + str(self.height) + ', ' + str(self.total_marks) + ', ' + str(self.marks_breakdown) + ', ' + str(self.new_section)

class UserNotes(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	question = models.ForeignKey(Question,on_delete=models.CASCADE)
	notes = models.TextField()

	def __str__(self):
		return str(self.user.pk) + ', ' + str(self.question.pk) + ', ' + str(self.notes)

class UserCompletedQuestion(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	question = models.ForeignKey(Question,on_delete=models.CASCADE)

	def __str__(self):
		return str(self.user.pk) + ', ' + str(self.question.pk)