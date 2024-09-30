from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView
from .models import update, Learnings, MyLearningList
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from django.urls import reverse, reverse_lazy
from django.views import View
import re

# Create your views here.
class PostListView(ListView):
    model = update
    login_url='login'
    template_name ='home.html'
    context_object_name ='posts'
    ordering = ['-date']
    paginate_by = 4 
class PostCreateView(LoginRequiredMixin,CreateView):
    model = update
    login_url='login'
    fields =['title','content']
    template_name ='post_new.html'
    def form_valid(self , form):
        form.instance.author=self.request.user
        return super().form_valid(form)
class PostDetailView(DetailView):
    model = update
    template_name ='post_detail.html'

class UserPostListView(ListView):
    model = update
    template_name ='user_post.html'
    context_object_name ='posts'
    paginate_by = 4
    def get_queryset(self):
        user = get_object_or_404(User , username = self.kwargs.get('username'))
        return  update.objects.filter(author=user).order_by('-date')


class LearningsListView(ListView):
    model = Learnings
    template_name = 'learnings_list.html'
    context_object_name = 'learnings'
    paginate_by = 4

    def get_queryset(self):
        sort_by = self.request.GET.get('sort_by', 'date')
        subject_filter = self.request.GET.get('subject', None)
        
        queryset = Learnings.objects.select_related('author').only(
            'subject', 'hours_learned', 'learning_detail', 'author', 'date'
        )
        
        if sort_by == 'youtube':
            queryset = queryset.filter(links__icontains='youtube.com')
        
        if subject_filter:
            queryset = queryset.filter(subject=subject_filter)
        
        # Order by date and then by primary key (largest first)
        queryset = queryset.order_by('-date', '-pk')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['authors'] = User.objects.filter(learnings__in=context['learnings']).distinct()
        context['subjects'] = Learnings.objects.values_list('subject', flat=True).distinct()
        return context

class LearningsCreateView(LoginRequiredMixin, CreateView):
    model = Learnings
    login_url = 'login'
    fields = ['subject', 'date', 'hours_learned', 'learning_detail', 'links']  # Include new fields
    template_name = 'learnings_new.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        try:
            form.instance.clean()  # Call the clean method to validate the date
        except ValidationError as e:
            form.add_error('date', e)
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' in context:
            form = context['form']
            if form.instance.date:
                form.instance.date = form.instance.date.strftime('%d-%m-%Y')
        return context


class LearningsDetailView(LoginRequiredMixin, DetailView):
    model = Learnings
    template_name = 'learnings_detail.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video_id = self.extract_youtube_video_id(self.object.links)
        context['video_id'] = video_id
        context['is_author'] = self.object.author == self.request.user
        return context

    def extract_youtube_video_id(self, url):
        # Regular expression to extract the video ID from the YouTube URL
        match = re.search(r'v=([^&]+)', url)
        if match:
            return match.group(1)
        return None

    def post(self, request, *args, **kwargs):
        learning = self.get_object()
        # Check if the learning already exists in the user's MyLearningList
        if not MyLearningList.objects.filter(user=request.user, learning=learning).exists():
            MyLearningList.objects.create(user=request.user, learning=learning, status='pending')
        return redirect(reverse('my-learning-list'))


class LearningUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Learnings
    login_url = 'login'
    fields = ['subject', 'learning_detail', 'links', 'hours_learned']
    template_name = 'learning_update.html'
    success_url = reverse_lazy('learnings_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        learning = self.get_object()
        return self.request.user == learning.author
class LearningsDeleteView(LoginRequiredMixin, DeleteView):
    model = Learnings
    success_url = reverse_lazy('learning-create')
    template_name = 'learning_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        learning = self.get_object()
        if learning.author != self.request.user:
            raise PermissionDenied("You are not allowed to delete this learning.")
        return super().delete(request, *args, **kwargs)



class MyLearningListView(LoginRequiredMixin, ListView):
    model = MyLearningList
    login_url = 'login'
    template_name = 'my_learning_list.html'
    context_object_name = 'learnings'

    def get_queryset(self):
        queryset = MyLearningList.objects.filter(user=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = MyLearningList.STATUS_CHOICES
        context['learning_pks'] = [learnings.pk for learnings in context['learnings']]
        
        return context

    def post(self, request, *args, **kwargs):
        learning_id = request.POST.get('learning_id')
        new_status = request.POST.get('status')
        delete_learning = request.POST.get('delete_learning')

        if learning_id:
            try:
                learning_item = MyLearningList.objects.get(id=learning_id, user=request.user)
                if delete_learning:
                    learning_item.delete()
                elif new_status:
                    learning_item.status = new_status
                    learning_item.save()
                return redirect(reverse('my-learning-list'))
            except MyLearningList.DoesNotExist:
                return HttpResponseForbidden("You do not have permission to update this item.")
        
        return redirect(reverse('my-learning-list'))
class UserLearningListView(ListView):
    model = Learnings
    template_name = 'user_learnings.html'  # Replace with your desired template
    context_object_name = 'learnings'
    paginate_by = 4

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Learnings.objects.filter(author=user).order_by('-date')