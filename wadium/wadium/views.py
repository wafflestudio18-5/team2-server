from django.http import HttpResponse


def ping(request):
    return HttpResponse("Hi, this is wadium backend.")
