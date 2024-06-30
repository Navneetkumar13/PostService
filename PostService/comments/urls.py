from django.urls import path
from . import views

urlpatterns = [
    path('add_comment/', views.AddCommentAPI.as_view(), name='add-comment'),
    path('update_comment/<str:comment_id>/', views.UpdateCommentAPI.as_view(), name='update-comment'),
    path('get_comments_by_post_id/', views.GetCommentByPostIdAPI.as_view(), name='get-comments-by-post-id'),
    path('delete_comment/', views.DeleteCommentAPI.as_view(), name='delete-comment'),
]
