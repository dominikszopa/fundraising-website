from django.http import HttpResponse
from django.views import View


class IndexView(View):
    # Just an empty page, instead of an error

    def get(self, request):
        return HttpResponse('')
