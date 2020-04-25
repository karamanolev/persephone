import json

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView


class APILogin(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            return Response({})

        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({})
        return Response({}, status=status.HTTP_403_FORBIDDEN)


class APILogout(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        logout(request)
        return Response({})


def react_host(request):
    if request.path.startswith('/api/v1'):
        return HttpResponse(
            json.dumps({
                'error': 'You requested an API view that does not exist.',
            }),
            status=status.HTTP_404_NOT_FOUND,
        )
    if request.method != 'GET':
        return HttpResponse('Status not allowed.', status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return render(request, 'react_host.html')
