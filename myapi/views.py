from django.shortcuts import render
from .models import Domain
from .serializers import DomainSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import socket


'''
This REST API has two end points

1. /postip
2. /getip?domain=...

1. this endpoint takes json as request and post it to postgres database
2. takes query parameters from request url and searches for domain in database and returns ip if present
   other wise does ip look and adds to the database and also returns the ip 

'''


@api_view(['POST'])
def postIP(request):
    if Domain.objects.filter(domain=request.data['domain']).exists():
        Domain.objects.filter(domain=request.data['domain']).update(ip=request.data['ip'])
        return Response(
            {
                'success':True,
                'status':'updated'
            },status.HTTP_200_OK
        )

    else:
        serializer=DomainSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
            {
                'success':True,
                'status':'created'
            },status.HTTP_201_CREATED
        )
    return Response({'success':False,'status': 'error'},status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['GET'])
def getIP(request):
    domain = request.GET.get('domain')

    if Domain.objects.filter(domain=domain).exists():
        try:
            ip = Domain.objects.get(domain=domain).ip
            return Response(
                {
                    'success':True,
                    'data':{
                        'ip': ip 
                    }      
                },status.HTTP_200_OK)
        except Domain.DoesNotExist:
            return Response(
                {
                    'success':False,
                    'data':{
                        'ip':"none"
                    }      
                },status.HTTP_404_NOT_FOUND)

    else:
        try:
            ip = socket.gethostbyname(domain)
        except:
            return Response({
                'success':False,
                'data':{
                    'ip': "none" 
                }      
            },status.HTTP_404_NOT_FOUND)
        serializer = DomainSerializer(data={'domain': domain, 'ip': ip})
        if serializer.is_valid():
            serializer.save()
            return Response(
            {
                'success':True,
                'data':{
                    'ip': ip 
                }      
            },status.HTTP_201_CREATED)
    return Response({
        'success':False, 
        'data':{
            'ip':"none"
        }
    },status.HTTP_503_SERVICE_UNAVAILABLE)
    

