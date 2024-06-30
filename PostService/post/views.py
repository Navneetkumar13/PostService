from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PostService.enums import ErrorResponseStatus, ReferenceTypes
from . models import Post
from user.models import User
from PostService.utils import (
    generate_unique_key, 
    save_file_to_s3_bucket,
    regenerate_url_for_key
)
from django.utils import timezone
from likes.models import Likes
from view.models import View

'''
API Type: POST
Description: API to create discussion post
'''
class CreateDiscussionPostAPI(APIView):
    def post(self, request):
        try:
            caption = request.data.get('caption',None)
            image = request.FILES.get('image',None)
            hashtags = request.data.get('hashtags',None)
            hashtags_list = []
            if ',' in hashtags:
                hashtags_list = hashtags.replace(' ','').split(',')
            else:
                hashtags_list = hashtags.replace(' ','').split()
            created_by = request.data.get('created_by',None)

            if created_by is None:
                return Response({'response':ErrorResponseStatus.INVALID_FIELD.value, 'code':'400', 'message':'Please provide valid username'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Checking if user exists or not in db
            created_by_user_q = User.objects.filter(username=created_by).first()
            if created_by_user_q is None:
                return Response({'response': ErrorResponseStatus.USER_NOT_FOUND.value, 'code':'404', 'message':'User not found'}, status=status.HTTP_404_NOT_FOUND)

            s3_image_key = None
            s3_image_url = None
            try:
                if image is not None:
                    s3_image_key = generate_unique_key( "images", image.name)
                    save_file_to_s3_bucket(s3_image_key, image)
                    s3_image_url = regenerate_url_for_key(s3_image_key)
            except Exception as boto_exception:
                return Response({'response':'Error', 'exception':boto_exception}, status=status.HTTP_400_BAD_REQUEST)
            
            now = timezone.now()

            post_obj = Post(
                caption = caption,
                image_s3_link = s3_image_url,
                image_s3_path = s3_image_key,
                hashtags = hashtags_list,
                created_by = created_by,
                created_at = now,
                updated_at = now
            )
            post_obj.save()

            data = {
                'post_id':post_obj.post_id,
                'caption': post_obj.caption,
                'image_s3_link': post_obj.image_s3_link,
                'hashtags':post_obj.hashtags,
                'created_by': created_by_user_q.name,
                'created_at': post_obj.created_at,
                'updated_at': post_obj.updated_at
            }
            return Response({'response':'Success', 'code':'201', 'message':'Discussion post created', 'data':data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print('Exception: ',e)
            return Response({'response': ErrorResponseStatus.INTERNAL_SERVER_ERROR.value, 'code':'500', 'message':'Error Occured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

'''
API Type: DELETE
Description: API to delete discussion post
'''
class DeleteDiscussionPostAPI(APIView):
    def delete(self, request):
        try:
            post_id = request.GET.get('post_id', None)
            if post_id is None:
                return Response({'response':ErrorResponseStatus.INVALID_FIELD.value, 'code':'400', 'message':'Please provide valid post id'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Checking if dicussion post exists or not
            post_q = Post.objects.filter(post_id=post_id).first()
            if post_q is None:
                return Response({'response':ErrorResponseStatus.DISCUSSION_NOT_FOUND.value, 'code':'404', 'message':'Discussion post not found'}, status=status.HTTP_404_NOT_FOUND)

            # Getting likes of the post to remove
            likes_q = Likes.objects.filter(reference_type = ReferenceTypes.POST_REFERENCE_TYPE.value, reference_id = post_id)

            post_q.delete()
            likes_q.delete()

            return Response({'response':'Success', 'code':'200', 'message':'Discussion post deleted'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'response': ErrorResponseStatus.INTERNAL_SERVER_ERROR.value, 'code':'500', 'message':'Error Occured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


'''
API Type: PUT
Description: API to update discussion post
'''
class UpdateDiscussionAPI(APIView):
    def put(self, request, post_id):
        try:
            if post_id is None:
                return Response({'response':ErrorResponseStatus.INVALID_FIELD.value, 'code':'400', 'message':'Please provide valid post id'}, status=status.HTTP_400_BAD_REQUEST)

            # Checking if post exists
            post_q = Post.objects.filter(post_id=post_id).first()
            if post_q is None:
                return Response({'response':ErrorResponseStatus.DISCUSSION_NOT_FOUND.value, 'code':'404', 'message':'Discussion post not found'}, status=status.HTTP_404_NOT_FOUND)

            caption = request.data.get('caption',None)
            if caption is not None:
                post_q.caption = caption

            image = request.FILES.get('image',None)
            if image is not None:
                s3_image_key = generate_unique_key( "images", image.name)
                save_file_to_s3_bucket(s3_image_key, image)
                s3_image_url = regenerate_url_for_key(s3_image_key)

                post_q.image_s3_link = s3_image_url
                post_q.image_s3_path = s3_image_key

            hashtags = request.data.get('hashtags',None)
            if hashtags is not None:
                hashtags_list = []
                if ',' in hashtags:
                    hashtags_list = hashtags.replace(' ','').split(',')
                else:
                    hashtags_list = hashtags.replace(' ','').split()
                post_q.hashtags = hashtags_list

            # For liking the post
            liked_by = request.data.get('liked_by',None)
            if liked_by is not None:
                # Checking if already liked then remove like, else add like
                like_check_q = Likes.objects.filter(liked_by = liked_by, reference_type = ReferenceTypes.POST_REFERENCE_TYPE.value, reference_id = post_id).first()
                if like_check_q is not None:
                    like_check_q.delete()
                else:
                    like_obj = Likes(
                        liked_by = liked_by,
                        reference_type = ReferenceTypes.POST_REFERENCE_TYPE.value,
                        reference_id = post_id
                    )
                    like_obj.save()
            
            post_q.updated_at = timezone.now()
            post_q.save()

            # Geetting likes count from like query
            likes_count = 0
            post_likes_count_q = Likes.objects.filter(reference_type = ReferenceTypes.POST_REFERENCE_TYPE.value, reference_id = post_id)
            likes_count = post_likes_count_q.count()
            liked_by_list = []
            for like_entry in post_likes_count_q:
                user_like_q = User.objects.filter(username = like_entry.liked_by).first()
                if user_like_q is not None:
                    liked_by_list.append({"username":user_like_q.username, "name":user_like_q.name})

            # Getting username from user table
            created_by = None
            created_by_user_q = User.objects.filter(username=post_q.created_by).first()
            if created_by_user_q is not None:
                created_by = created_by_user_q.name
            
            data = {
                'post_id':post_q.post_id,
                'caption': post_q.caption,
                'image_s3_link': post_q.image_s3_link,
                'hashtags':post_q.hashtags,
                'likes_count': likes_count,
                'liked_by': liked_by_list,
                'created_by': created_by,
                'created_at': post_q.created_at,
                'updated_at': post_q.updated_at
            }

            return Response({'response':'Success', 'code':'200', 'message':'Discussion post updated', 'data':data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'response': ErrorResponseStatus.INTERNAL_SERVER_ERROR.value, 'code':'500', 'message':'Error Occured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


'''
API Type: GET
Description: API to search discussions post by text
'''
class GetDiscussionPostByText(APIView):
    def get(self, request):
        try:
            curr_username = request.GET.get('curr_username', None)
            if curr_username is None:
                return Response({'response':ErrorResponseStatus.INVALID_FIELD.value, 'code':'400', 'message':'Please provide valid username'}, status=status.HTTP_400_BAD_REQUEST)
            text = request.GET.get('text', None)
            if text is None:
                return Response({'response':ErrorResponseStatus.INVALID_FIELD.value, 'code':'400', 'message':'Please provide valid text to search posts'}, status=status.HTTP_400_BAD_REQUEST)
            
            post_q = Post.objects.filter(caption__icontains=text)
            
            posts_list = []
            for post in post_q:

                # Geetting post likes count from like query
                likes_count = 0
                post_likes_count_q = Likes.objects.filter(reference_type = ReferenceTypes.POST_REFERENCE_TYPE.value, reference_id = post.post_id)
                likes_count = post_likes_count_q.count()
                liked_by_list = []
                for like_entry in post_likes_count_q:
                    user_like_q = User.objects.filter(username = like_entry.liked_by).first()
                    if user_like_q is not None:
                        liked_by_list.append({"username":user_like_q.username, "name":user_like_q.name})

                # Getting created by user details
                created_by = None
                created_by_user_q = User.objects.filter(username=post.created_by).first()
                if created_by_user_q is not None:
                    created_by = created_by_user_q.name
                
                # Getting view counts
                view_count = 0
                view_count_q = View.objects.filter(post_id = post.post_id)
                view_count = view_count_q.count()
                
                data = {
                    'post_id':post.post_id,
                    'caption': post.caption,
                    'image_s3_link': post.image_s3_link,
                    'hashtags':post.hashtags,
                    'likes_count': likes_count,
                    'liked_by': liked_by_list,
                    'view_count': view_count,
                    'created_by': created_by,
                    'created_at': post.created_at,
                    'updated_at': post.updated_at
                }
                posts_list.append(data)

                # Creating View Map for the post
                view_q = View.objects.filter(visited_by = curr_username, post_id = post.post_id).first()
                if view_q is None:
                    view_obj = View(
                        post_id = post.post_id,
                        visited_by = curr_username
                    )
                    view_obj.save()

            return Response({'response':'Success', 'code':'200', 'data':posts_list}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'response': ErrorResponseStatus.INTERNAL_SERVER_ERROR.value, 'code':'500', 'message':'Error Occured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

'''
API Type: GET
Description: API to search discussions post by hashtag
'''
class GetDiscussionPostByHashTags(APIView):
    def get(self, request):
        try:
            curr_username = request.GET.get('curr_username', None)
            if curr_username is None:
                return Response({'response':ErrorResponseStatus.INVALID_FIELD.value, 'code':'400', 'message':'Please provide valid username'}, status=status.HTTP_400_BAD_REQUEST)
            hashtags = request.GET.get('hashtags', None)
            if hashtags is None:
                return Response({'response':ErrorResponseStatus.INVALID_FIELD.value, 'code':'400', 'message':'Please provide valid text to search posts'}, status=status.HTTP_400_BAD_REQUEST)
            
            hashtags_list = []
            if ',' in hashtags:
                hashtags_list = hashtags.replace(' ','').split(',')
            else:
                hashtags_list = hashtags.replace(' ','').split()

            post_q = Post.objects.filter(hashtags__contains=hashtags_list)

            posts_list = []
            for post in post_q:

                # Geetting post likes count from like query
                likes_count = 0
                post_likes_count_q = Likes.objects.filter(reference_type = ReferenceTypes.POST_REFERENCE_TYPE.value, reference_id = post.post_id)
                likes_count = post_likes_count_q.count()
                liked_by_list = []
                for like_entry in post_likes_count_q:
                    user_like_q = User.objects.filter(username = like_entry.liked_by).first()
                    if user_like_q is not None:
                        liked_by_list.append({"username":user_like_q.username, "name":user_like_q.name})

                # Getting craeted by user details
                created_by = None
                created_by_user_q = User.objects.filter(username=post.created_by).first()
                if created_by_user_q is not None:
                    created_by = created_by_user_q.name

                # Getting view counts
                view_count = 0
                view_count_q = View.objects.filter(post_id = post.post_id)
                view_count = view_count_q.count()
                
                data = {
                    'post_id':post.post_id,
                    'caption': post.caption,
                    'image_s3_link': post.image_s3_link,
                    'hashtags':post.hashtags,
                    'likes_count': likes_count,
                    'liked_by': liked_by_list,
                    'view_count': view_count,
                    'created_by': created_by,
                    'created_at': post.created_at,
                    'updated_at': post.updated_at
                }
                posts_list.append(data)

                # Creating View Map for the post
                view_q = View.objects.filter(visited_by = curr_username, post_id = post.post_id).first()
                if view_q is None:
                    view_obj = View(
                        post_id = post.post_id,
                        visited_by = curr_username
                    )
                    view_obj.save()


            return Response({'response':'Success', 'code':'200', 'data':posts_list}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'response': ErrorResponseStatus.INTERNAL_SERVER_ERROR.value, 'code':'500', 'message':'Error Occured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     