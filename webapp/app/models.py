from __future__ import unicode_literals

from django.db import models

# to reset database (i.e. delete all records and tables),
# delete contents of migrations folder (apart from
# '__init__.py') then run 'python manage.py flush'
# might also need to clear 'django_migrations' in db!

def file_path(instance, filename):
	return 'uploads/{0}_{1}.pdf'.format(instance.module_code, instance.year)

# def file_path(instance, filename):
# 	return 'uploads/paper_{0}.pdf'.format(instance.id)

class Paper(models.Model):
	module_code = models.CharField(max_length=5)
	year = models.PositiveSmallIntegerField()
	# file = models.FileField(upload_to=file_path)

	def __str__(self):
		return str(self.pk) + ', ' + self.module_code + ', ' + str(self.year)

class Rubric(models.Model):
	paper = models.ForeignKey(Paper,on_delete=models.CASCADE)
	total_qs = models.PositiveSmallIntegerField()
	calcs_allowed = models.BooleanField()

	def __str__(self):
		return str(self.paper.pk) + ', ' + str(self.calcs_allowed)

	#paper_id = models.ForeignKey(Paper,on_delete=models.CASCADE)

	# class Meta:
	# 	unique_together = ('module_code', 'year')

#class PDF(models.Model):
	#paper = models.ForeignKey(Paper,on_delete=models.CASCADE)
	#file = models.FileField(upload_to='documents/')