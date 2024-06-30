from django.urls import path
from . import views

urlpatterns = [
    path('create_discussion/', views.CreateDiscussionPostAPI.as_view(), name='create-post'),
    path('delete_discussion/', views.DeleteDiscussionPostAPI.as_view(), name='delete-post'),
    path('get_discussions_by_hashtags/', views.GetDiscussionPostByHashTags.as_view(), name='get-post-by-tags'),
    path('get_discussions_by_text/', views.GetDiscussionPostByText.as_view(), name='get-post-by-text'),
    path('update_discussion/<str:post_id>/', views.UpdateDiscussionAPI.as_view(), name='update-post-detail'),
]
