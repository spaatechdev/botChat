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
    context.update({'message': "User Details Fetched Successfully", 'userDetails': {'id': request.user.id, 'email': request.user.email, 'username': request.user.username, 'first_name': request.user.first_name, 'last_name': request.user.last_name, 'phone': request.user.phone}})
    return Response(context)


def find_maximum_substring(sentence, words):
    max_substring = ''
    max_length = 0
    for word in words:
        substring = longest_common_substring(sentence, word)
        if len(substring) > max_length:
            max_substring = substring
            max_length = len(substring)
    return max_substring


def longest_common_substring(str1, str2):
    m = len(str1)
    n = len(str2)
    lengths = [[0] * (n + 1) for _ in range(m + 1)]
    longest_substring_length = 0
    ending_index = 0

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                lengths[i][j] = lengths[i - 1][j - 1] + 1
                if lengths[i][j] > longest_substring_length:
                    longest_substring_length = lengths[i][j]
                    ending_index = i - 1
            else:
                lengths[i][j] = 0

    return str1[ending_index - longest_substring_length + 1:ending_index + 1]

def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def getResponse(request):
    if request.method == "POST":
        question = request.POST['question']
        result = list(models.QuestionAnswers.objects.filter(question__icontains=question).distinct().values('response', 'category', 'order', 'parent__question', 'parent__response'))
        # question_words = question.split(" ")
        # result = list(models.QuestionAnswers.objects.filter(question__in=question_words).distinct().values('response', 'category', 'order', 'parent__question', 'parent__response'))
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
            print(result)
            if (result['score'] < 0.03):
                responseText = random.choice(["Sorry I don't understand your query.", "Sorry! I can't find any relatable answers for your query."])
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
            # best_answers = find_maximum_substring(content, question_words)
            # print(best_answers)
            # pattern = fr'(.*?({"|".join(re.escape(word) for word in question_words)}).*?\.)'
            # match = re.search(pattern, content, re.DOTALL)
            # if match:
            #     sentence = match.group(1)
            #     print(sentence)
            # else:
            #     print("No matching sentence found.")
            # exit()
    else:
        return JsonResponse({
            'code': 501,
            'status': "ERROR",
            'message': "There should be ajax method."
        })
