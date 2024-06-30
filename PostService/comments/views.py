from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . models import Comments
from PostService.enums import ErrorResponseStatus, ReferenceTypes
from post.models import Post
from user.models import User
from likes.models import Likes
from django.utils import timezone

'''
API Type: POST
Description: API to add comment for a discussion post
'''
class AddCommentAPI(APIView):
    def post(self, request):
        try:
            base_comment_id = request.data.get('base_comment_id', None)
            comment = request.data.get('comment', None)
            is_reply = request.data.get('is_reply',False)

            post_id = request.data.get('post_id',None)
            if post_id is None:
                return Response({'response':ErrorResponseStatus.INVALID_FIELD.value, 'code':'400', 'message':'Please provide valid post id'}, status=status.HTTP_400_BAD_REQUEST)
            
            post_check_q = Post.objects.filter(post_id=post_id).first()
            if post_check_q is None:
                return Response({'response':ErrorResponseStatus.DISCUSSION_NOT_FOUND.value, 'code':'404', 'message':'Discussion post not found'}, status=status.HTTP_404_NOT_FOUND)

            created_by = request.data.get('created_by', None)
            if created_by is None:
                return Response({'response':ErrorResponseStatus.INVALID_FIELD.value, 'code':'400', 'message':'Please provide valid username'}, status=status.HTTP_400_BAD_REQUEST)
                        
            created_by_user_check_q = User.objects.filter(username=created_by).first()
            if created_by_user_check_q is None:
                return Response({'response':ErrorResponseStatus.USER_NOT_FOUND.value, 'code':'404', 'message':'User not found'}, status=status.HTTP_404_NOT_FOUND)

            now = timezone.now()

            comment_obj = Comments(
                base_comment_id = base_comment_id,
                comment = comment,
                is_reply = is_reply,
                post_id = post_id,
                created_by = created_by,
                created_at = now,
                updated_at = now
            )
            comment_obj.save()

            data = {
                'base_comment_id':comment_obj.base_comment_id,
                'comment_id': comment_obj.comment_id,
                'comment': comment_obj.comment,
                'is_reply':comment_obj.is_reply,
                'post_id':comment_obj.post_id,
                'created_by': created_by_user_check_q.name,
                'created_at': comment_obj.created_at,
                'updated_at': comment_obj.updated_at
            }
            return Response({'response':'Success', 'code':'201', 'message':'Comment Added Successfully', 'data':data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print('Exception: ',e)
            return Response({'response': ErrorResponseStatus.INTERNAL_SERVER_ERROR.value, 'code':'500', 'message':'Error Occured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

'''
API Type: DELETE
Description: API to delete comment
'''
class DeleteCommentAPI(APIView):
    def delete(self, request):
        try:
            comment_id = request.GET.get('comment_id', None)
            if comment_id is None:
                return Response({'response':ErrorResponseStatus.INVALID_FIELD.value, 'code':'400', 'message':'Please provide valid comment id'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Checking if comments exists or not
            comments_q = Comments.objects.filter(comment_id=comment_id)
            reply_q = Comments.objects.filter(base_comment_id = comment_id)
            reply_q.delete()

            if comments_q is None:
                return Response({'response':ErrorResponseStatus.COMMENT_NOT_FOUND.value, 'code':'404', 'message':'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

            comments_q.delete()
            return Response({'response':'Success', 'code':'200', 'message':'Discussion post deleted'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'response': ErrorResponseStatus.INTERNAL_SERVER_ERROR.value, 'code':'500', 'message':'Error Occured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

'''
API Type: PUT
Description: API to update comment
'''
class UpdateCommentAPI(APIView):
    def put(self, request, comment_id):
        try:
            if comment_id is None:
                return Response({'response':ErrorResponseStatus.INVALID_FIELD.value, 'code':'400', 'message':'Please provide valid comment id'}, status=status.HTTP_400_BAD_REQUEST)

            # Checking if comment exists
            comment_q = Comments.objects.filter(comment_id=comment_id).first()

            if comment_q is None:
                return Response({'response':ErrorResponseStatus.COMMENT_NOT_FOUND.value, 'code':'404', 'message':'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

            comment = request.data.get('comment',None)
            if comment is not None:
                comment_q.comment = comment

            # For liking the comment
            liked_by = request.data.get('liked_by',None)
            if liked_by is not None:
                # Checking if already liked then remove like, else add like
                like_check_q = Likes.objects.filter(liked_by = liked_by, reference_type = ReferenceTypes.COMMENT_REFERENCE_TYPE.value, reference_id = comment_id).first()
                if like_check_q is not None:
                    like_check_q.delete()
                else:
                    like_obj = Likes(
                        liked_by = liked_by,
                        reference_type = ReferenceTypes.COMMENT_REFERENCE_TYPE.value,
                        reference_id = comment_id
                    )
                    like_obj.save()

            comment_q.updated_at = timezone.now()
            comment_q.save()

            # Getting likes count from like query
            likes_count = 0
            comment_likes_count_q = Likes.objects.filter(reference_type = ReferenceTypes.COMMENT_REFERENCE_TYPE.value, reference_id = comment_id)
            likes_count = comment_likes_count_q.count()
            liked_by_list = []
            for like_entry in comment_likes_count_q:
                user_like_q = User.objects.filter(username = like_entry.liked_by).first()
                if user_like_q is not None:
                    liked_by_list.append({"username":user_like_q.username, "name":user_like_q.name})

            # Getting created by user details
            created_by = None
            created_by_user_q = User.objects.filter(username=comment_q.created_by).first()
            if created_by_user_q is not None:
                created_by = created_by_user_q.name
            
            data = {
                'base_comment_id':comment_q.base_comment_id,
                'comment_id': comment_q.comment_id,
                'comment': comment_q.comment,
                'is_reply':comment_q.is_reply,
                'post_id':comment_q.post_id,
                'likes_count': likes_count,
                'liked_by': liked_by_list,
                'created_by': created_by,
                'created_at': comment_q.created_at,
                'updated_at': comment_q.updated_at
            }

            return Response({'response':'Success', 'code':'200', 'message':'Comment updated', 'data':data}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Exception: ",e)
            return Response({'response': ErrorResponseStatus.INTERNAL_SERVER_ERROR.value, 'code':'500', 'message':'Error Occured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

'''
API Type: GET
Description: API to get Comments of a post
'''
class GetCommentByPostIdAPI(APIView):
    def get(self, request):
        try:
            post_id = request.GET.get('post_id', None)
            if post_id is None:
                return Response({'response':ErrorResponseStatus.INVALID_FIELD.value, 'code':'400', 'message':'Please provide valid post_id'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Checking if post exists or not
            post_q = Post.objects.filter(post_id=post_id).first()
            if post_q is None:
                return Response({'response': ErrorResponseStatus.DISCUSSION_NOT_FOUND.value, 'code':'404', 'message':'Post not found'}, status=status.HTTP_404_NOT_FOUND)
            
            comments_q = Comments.objects.filter(post_id=post_id, is_reply=False)
            
            comments_list = []
            for comment in comments_q:
                created_by = None
                created_by_user_q = User.objects.filter(username=comment.created_by).first()
                if created_by_user_q is not None:
                    created_by = created_by_user_q.name
                
                reply_q = Comments.objects.filter(base_comment_id = comment.comment_id, is_reply=True)

                replies = []
                for reply in reply_q:
                    reply_created_by = None
                    reply_created_by_user_q = User.objects.filter(username=reply.created_by).first()
                    if reply_created_by_user_q is not None:
                        reply_created_by = reply_created_by_user_q.name

                    # Geetting comment likes count from like query
                    reply_likes_count = 0
                    reply_likes_count_q = Likes.objects.filter(reference_type = ReferenceTypes.COMMENT_REFERENCE_TYPE.value, reference_id = reply.comment_id)
                    reply_likes_count = reply_likes_count_q.count()
                    reply_liked_by_list = []
                    for like_entry in reply_likes_count_q:
                        user_like_q = User.objects.filter(username = like_entry.liked_by).first()
                        if user_like_q is not None:
                            reply_liked_by_list.append({"username":user_like_q.username, "name":user_like_q.name})

                    reply_data = {
                        'base_comment_id':reply.base_comment_id,
                        'comment_id': reply.comment_id,
                        'comment': reply.comment,
                        'is_reply':reply.is_reply,
                        'post_id':reply.post_id,
                        'likes_count': reply_likes_count,
                        'liked_by': reply_liked_by_list,
                        'created_by': reply_created_by,
                        'created_at': reply.created_at,
                        'updated_at': reply.updated_at
                    }
                    replies.append(reply_data)

                # Geetting comment likes count from like query
                comment_likes_count = 0
                comment_likes_count_q = Likes.objects.filter(reference_type = ReferenceTypes.COMMENT_REFERENCE_TYPE.value, reference_id = comment.comment_id)
                comment_likes_count = comment_likes_count_q.count()
                comment_liked_by_list = []
                for like_entry in comment_likes_count_q:
                    user_like_q = User.objects.filter(username = like_entry.liked_by).first()
                    if user_like_q is not None:
                        comment_liked_by_list.append({"username":user_like_q.username, "name":user_like_q.name})

                comment_data = {
                    'base_comment_id':comment.base_comment_id,
                    'comment_id': comment.comment_id,
                    'comment': comment.comment,
                    'is_reply':comment.is_reply,
                    'post_id':comment.post_id,
                    'likes_count': comment_likes_count,
                    'liked_by': comment_liked_by_list,
                    'created_by': created_by,
                    'created_at': comment.created_at,
                    'updated_at': comment.updated_at,
                    'replies' : replies
                }
                comments_list.append(comment_data)

            return Response({'response':'Success', 'code':'200', 'data':comments_list}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'response': ErrorResponseStatus.INTERNAL_SERVER_ERROR.value, 'code':'500', 'message':'Error Occured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
