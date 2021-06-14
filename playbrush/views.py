from django.views.generic import ListView, CreateView  # new
from .models import Files
from .forms import FilesForm  # new
from django.urls import reverse_lazy  # new
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from playbrush.data_process import DataProc
from django.template.response import TemplateResponse


from django.views.generic import ListView


class HomePageView(ListView):
    model = Files
    template_name = 'home.html'


class CreatePostView(CreateView):  # new
    model = Files
    form_class = FilesForm
    template_name = 'post.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # user = self.request.user
        context["data"] = ""
        return context


class ResoultView(ListView):
    def retrieve(self, fileid, * args, **kwargs):

        f = Files.objects.get(pk=fileid)
        d = DataProc()
        task1csv, task21, task22, task23, task24 = d.process(f.csv1.path, f.csv2.path)
        html = ""

        html += task1csv.to_html()
        html += str(task21)
        html += task22.to_html()
        html += task23.to_html()
        html += task24.to_html()

        return TemplateResponse(self, 'results.html', {"t1": task1csv.to_html(classes="table"), "t21": str(task21), "t22": task22.to_html(classes="table"), "t23": task23.to_html(classes="table"), "t24": task24.to_html(classes="table")})
