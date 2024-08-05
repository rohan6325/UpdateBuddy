from django.urls import path
from .views import PostListView, PostCreateView , PostDetailView , UserPostListView , LearningsCreateView , LearningsDetailView, LearningsListView
from .views import LearningsDeleteView,MyLearningListView, LearningUpdateView , UserLearningListView
urlpatterns = [
     path("posts", PostListView.as_view(), name="home"),
     path("posts/new/", PostCreateView.as_view(), name="post-create"),
     path("post/<int:pk>/", PostDetailView.as_view(), name="post-detail"),
     path("userpost/<str:username>", UserPostListView.as_view(), name="User-posts"),
     path("learning/new/", LearningsCreateView.as_view(), name="learning-create"),
     path("learning/<int:pk>/", LearningsDetailView.as_view(), name="learning-detail"),
     path('', LearningsListView.as_view(), name='learnings_list'),
     path('learnings/<int:pk>/delete/', LearningsDeleteView.as_view(), name='learning-delete'),
     path('mylearnings/', MyLearningListView.as_view(), name='my-learning-list'),
     path('learning/<int:pk>/update/', LearningUpdateView.as_view(), name='learning-update'),
     path('user/<str:username>/learnings/', UserLearningListView.as_view(), name='user-learnings'),

]

