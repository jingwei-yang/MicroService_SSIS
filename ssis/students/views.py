from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from students.models import Student
from students.models import Enrollment
from students.serializers import StudentSerializer
from students.serializers import EnrollSerializer


# Import Libs for changing Schema 
from django.db import models
from django.db import connection, DatabaseError, IntegrityError
from django.db.models.fields import IntegerField, TextField, CharField, SlugField



class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)



@csrf_exempt
def student_list(request):
	"""
   	List all code students, or create a new students.
	"""
	if request.method == 'GET':
		students = Student.objects.all()
		serializer = StudentSerializer(students, many=True)
		print serializer.data
		return JSONResponse(serializer.data)
		
	elif request.method == 'POST':
		data = JSONParser().parse(request)
		serializer = StudentSerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			return JSONResponse(serializer.data, status=201)
		return JSONResponse(serializer.errors, status=400)



@csrf_exempt
def student_detail(request, sID):
	"""
	Retrieve, update or delete a code snippet.
	"""
	try:
		student = Student.objects.get(studentID=sID)
	except Student.DoesNotExist:
		return HttpResponse(status=404)

	if request.method == 'GET':
		serializer = StudentSerializer(student)
		return JSONResponse(serializer.data)

	elif request.method == 'PUT':
		data = JSONParser().parse(request)
		serializer = StudentSerializer(student, data=data)
		if serializer.is_valid():
			serializer.save()
			return JSONResponse(serializer.data)
		return JSONResponse(serializer.errors, status=400)

	elif request.method == 'DELETE':
		student.delete()
		return HttpResponse(status=204)



@csrf_exempt
def enroll_list(request):
	"""
   	List all enrollments, or create a new enrollment.
	"""
	if request.method == 'GET':
		enroll = Enrollment.objects.all()
		serializer = EnrollSerializer(enroll, many=True)
		print serializer.data
		return JSONResponse(serializer.data)
		
	elif request.method == 'POST':
		data = JSONParser().parse(request)
		serializer = EnrollSerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			return JSONResponse(serializer.data, status=201)
		return JSONResponse(serializer.errors, status=400)



@csrf_exempt
def enroll_student_detail(request, sID):
	"""
	Retrieve, update or delete a enrollment.
	"""
	try:
		enroll = Enrollment.objects.get(studentID=sID)
		serializer = EnrollSerializer(enroll)
	except Enrollment.DoesNotExist:
		return HttpResponse(status=404)

	if request.method == 'GET':
		serializer = EnrollSerializer(enroll)
		return JSONResponse(serializer.data)

	elif request.method == 'DELETE':
		enroll.delete()
		return HttpResponse(status=204)



@csrf_exempt
def enroll_detail(request, sID, cID):
	"""
	Retrieve, update or delete a enrollment.
	"""
	try:
		enroll = Enrollment.objects.filter(studentID=sID).filter(courseID=cID)
		serializer = EnrollSerializer(enroll)
	except Enrollment.DoesNotExist:
		return HttpResponse(status=404)

	if request.method == 'GET':
		serializer = EnrollSerializer(enroll)
		return JSONResponse(serializer.data)

	elif request.method == 'PUT':
		data = JSONParser().parse(request)
		serializer = EnrollSerializer(enroll, data=data)
		if serializer.is_valid():
			serializer.save()
			return JSONResponse(serializer.data)
		return JSONResponse(serializer.errors, status=400)
	elif request.method == 'DELETE':
		enroll.delete()
		return HttpResponse(status=204)



@csrf_exempt
def schema_operations(request):
	"""
	add column into the schema
	"""
	if request.method == 'POST':
		data = JSONParser().parse(request)
		field_name = data["field_name"]
		field_type = data["field_type"]
		default_value = data["default_value"]
		if field_type == "IntegerField" :
			field = models.IntegerField(default = default_value)
		elif field_type == "TextField" :
			field = models.TextField(default = default_value)
		elif field_type == "SlugField" :
			field = models.SlugField(default = default_value)
		else :
			field = models.CharField(max_length=50, default = default_value)
		field.set_attributes_from_name(field_name)
		try:
			with connection.schema_editor() as schema_editor:
				schema_editor.add_field(Student, field)
		except Student.DoesNotExist:
			return HttpResponse(status=404)
		return HttpResponse(status=200)