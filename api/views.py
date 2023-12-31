from django.shortcuts import render

# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from superuser import models
from django.contrib.messages import get_messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from transformers import pipeline
import random
import re
import string
from django.db.models import Q
from functools import reduce
from operator import or_
from operator import itemgetter


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def loginUser(request):
    context = {}
    user = models.User.objects.get(pk=request.user.id)
    login(request, user)
    context.update({'message': "User Logged In Successfully"})
    return Response(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logoutUser(request):
    context = {}
    logout(request)
    try:
        del request.session
    except:
        pass
    try:
        storage = get_messages(request)
        for message in storage:
            message = ''
        storage.used = False
    except:
        pass
    context.update({'message': "Logged Out Successfully"})
    return Response(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserDetails(request):
    context = {}
    context.update({'message': "User Details Fetched Successfully", 'userDetails': {'id': request.user.id, 'email': request.user.email,
                   'username': request.user.username, 'first_name': request.user.first_name, 'last_name': request.user.last_name, 'phone': request.user.phone}})
    return Response(context)


def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def getResponse(request):
    if request.method == "POST":
        question = request.POST['question'].strip()
        pattern = r'^[^a-zA-Z0-9\s]+|[^a-zA-Z0-9\s]+$'
        # Use re.sub() to replace leading and trailing special characters with an empty string
        question = re.sub(pattern, '', question)
        # Remove any remaining leading and trailing whitespaces
        question = question.strip()
        # question = question.replace('Great Lake', 'GLTS')
        # question = question.replace('Great Lake Technology Service', 'GLTS')
        # question = question.replace('Great Lake Technology Services', 'GLTS')
        # question = question.replace('Great Lake Tech Service', 'GLTS')
        # question = question.replace('Great Lake Tech Services', 'GLTS')
        # question = question.replace('G L Tech Service', 'GLTS')
        # question = question.replace('G L T Service', 'GLTS')
        # question = question.replace('GL Tech Service', 'GLTS')
        # question = question.replace('GLT Service', 'GLTS')
        # question = question.replace('GLTech Service', 'GLTS')
        # question = question.replace('GL', 'GLTS')
        # question = question.replace('GLT', 'GLTS')
        # question = question.replace('G L', 'GLTS')
        # question = question.replace('G L T', 'GLTS')
        question = question.lower()

        result = list(models.QuestionAnswers.objects.filter(question__iexact=question).values('id', 'question', 'response', 'category', 'order', 'parent__question', 'parent__response'))

        if len(result) > 0:
            return JsonResponse({
                'code': 200,
                'status': "SUCCESS",
                'message': random.choice(result)['response']
            })
        else:
            result = list(models.QuestionAnswers.objects.filter(question__icontains=question).values(
                'id', 'question', 'response', 'category', 'order', 'parent__question', 'parent__response'))
            if len(result) > 0:
                return JsonResponse({
                    'code': 200,
                    'status': "SUCCESS",
                    'message': random.choice(result)['response']
                })
            else:
                # Split the search query into individual words
                # search_words = question.split()
                search_words = question.translate(str.maketrans('', '', string.punctuation)).split()
                q_object = reduce(or_, (Q(question__icontains=word) for word in search_words))

                # Filter the objects based on the number of matching words
                result = []
                max_match_count = 2
                for obj in models.QuestionAnswers.objects.filter(q_object).values('id', 'question', 'response', 'category', 'order', 'parent__question', 'parent__response'):
                    # obj_words = obj['question'].split()
                    obj_words = obj['question'].lower().translate(str.maketrans('', '', string.punctuation)).split()
                    obj['match_count'] = sum(1 for word in search_words if word in obj_words)
                    # match_count = 0
                    # for word in search_words:
                    #     if word in obj_words:
                    #         match_count += 1
                    if obj['match_count'] > max_match_count:
                        max_match_count = obj['match_count']
                        result = [obj]
                    elif obj['match_count'] == max_match_count:
                        result.append(obj)
                result = sorted(result, key=itemgetter('match_count'), reverse=True)
                length=len(result)
                if length > 3:
                    del result[length - 4:]
                if len(result) > 0:
                    return JsonResponse({
                        'code': 200,
                        'status': "SUCCESS",
                        'message': random.choice(result)['response']
                    })
                else:
                    file_path = "media/serviceTexts.txt"
                    f = open(file_path)
                    content = f.read()
                    f.close()
                    content = remove_html_tags(content)

                    # Load the pre-trained question answering model
                    nlp = pipeline("question-answering")

                    # The paragraph you want to extract answers from
                    paragraph = content

                    # The question you want to find an answer for
                    question = question

                    # Use the model to find the answer
                    result = nlp(question=question, context=paragraph)
                    if (result['score'] < 0.03):
                        responseText = random.choice(
                            ["Sorry I don't understand your query.", "Sorry! I can't find any relatable answers for your query."])
                        return JsonResponse({
                            'code': 200,
                            'status': "SUCCESS",
                            'message': responseText
                        })
                    else:
                        return JsonResponse({
                            'code': 200,
                            'status': "SUCCESS",
                            'message': result['answer']
                        })
    else:
        return JsonResponse({
            'code': 501,
            'status': "ERROR",
            'message': "There should be ajax method."
        })


def test_cors_view(request):
    data = {'message': 'CORS test successful!'}
    response = JsonResponse(data)
    response['Access-Control-Allow-Origin'] = '*'
    return response
