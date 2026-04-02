from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import random
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from app.post.models import Post
from app.comment.models import Comment
from app.like.models import Like
from app.user.serializers import ProfilePicSerializer, ProfileSerializer, RegisterSerializer, LoginSerializer
from app.follow.models import Follow

User = get_user_model()


def generate_otp():
    return str(random.randint(100000, 999999))


class AuthViewSet(ViewSet):
    
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['username', 'email', 'is_verified']
    filterset_fields = ['username', 'email', 'id']

    # ======================
    # REGISTER
    # ======================
    @action(detail=False, methods=["post"])
    def register(self, request):
        
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            otp = generate_otp()
            user.otp = otp
            user.is_verified = False
            user.save()

            send_mail(
                "Verify your account",
                f"Your OTP is {otp}",
                "noreply@gmail.com",
                [user.email],
                fail_silently=True,
            )

            return Response({"message": "OTP sent"}, status=201)

        return Response(serializer.errors, status=400)

    # ======================
    # VERIFY OTP
    # ======================
    @action(detail=False, methods=["post"])
    def verify_otp(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        user = User.objects.filter(email=email).first()

        if not user:
            return Response({"error": "User not found"}, status=404)

        if user.otp != otp:
            return Response({"error": "Invalid OTP"}, status=400)

        user.is_verified = True
        user.otp = None
        user.save()

        return Response({"message": "Verified successfully"})

    # ======================
    # LOGIN
    # ======================
    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)

            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": serializer.data
            })

        return Response(serializer.errors, status=400)

    # ======================
    # FORGOT PASSWORD
    # ======================
    @action(detail=False, methods=["post"])
    def forgot_password(self, request):
        email = request.data.get("email")

        user = User.objects.filter(email=email).first()

        if not user:
            return Response({"error": "Email not registered"}, status=404)

        otp = generate_otp()
        user.otp = otp
        user.save()

        send_mail(
            "Reset Password OTP",
            f"Your OTP is {otp}",
            "noreply@gmail.com",
            [email],
            fail_silently=True,
        )

        return Response({"message": "OTP sent", "email": email})

    # ======================
    # VERIFY RESET OTP
    # ======================
    @action(detail=False, methods=["post"])
    def verify_reset_otp(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        user = User.objects.filter(email=email).first()

        if not user:
            return Response({"error": "User not found"}, status=404)

        if user.otp != otp:
            return Response({"error": "Invalid OTP"}, status=400)

        return Response({"message": "OTP verified", "email": email})

    # ======================
    # RESET PASSWORD
    # ======================
    @action(detail=False, methods=["post"])
    def reset_password(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = User.objects.filter(email=email).first()

        if not user:
            return Response({"error": "User not found"}, status=404)

        user.password = make_password(password)
        user.otp = None
        user.save()

        return Response({"message": "Password reset successful"})
    
    
    
    # ======================
    # LOGOUT
    # ======================
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logged out"})
        except Exception:
            return Response({"error": "Invalid token"}, status=400)

    # ======================
    # DELETE ACCOUNT
    # ======================
    @action(detail=False, methods=["delete"], permission_classes=[IsAuthenticated])
    def delete_account(self, request):
        request.user.delete()
        return Response({"message": "Account deleted"})
        
    # ======================
    # PROFILE 
    # ======================
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def profile(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    # ======================
    # SPECIFIC USER PROFILE 
    # ======================
    @action(detail=False, methods=["get"], url_path="user-profile/(?P<username>[^/.]+)")
    def user_profile(self, request, username=None):

        user = get_object_or_404(User, username=username)

        # follow or not 
        if request.user.is_authenticated:
            is_following = Follow.objects.filter(
                follower=request.user,
                following=user
            ).exists()
        else:
            is_following = False

        serializer = ProfileSerializer(user)

        post_count = Post.objects.filter(user=user).count()
        comment_count = Comment.objects.filter(user=user).count()
        like_count = Like.objects.filter(user=user).count()
        followers_count = Follow.objects.filter(following=user).count()
        following_count = Follow.objects.filter(follower=user).count()

        # unfollowed user 
        if not (request.user == user or is_following):
            return Response({
                "user": serializer.data,
                "is_following": False,
                "counts": {
                    "posts": post_count,
                    "comments": comment_count,
                    "likes": like_count,
                    "followers": followers_count,
                    "following": following_count
                }
            })

        # followed user 
        posts = Post.objects.filter(user=user)
        comments = Comment.objects.filter(user=user)
        likes = Like.objects.filter(user=user)

        return Response({
            "user": serializer.data,
            "is_following": True,
            "counts": {
                "posts": post_count,
                "comments": comment_count,
                "likes": like_count,
                "followers": followers_count,
                "following": following_count
            },
            "posts": [{"id": p.id, "title": p.title, "content": p.content} for p in posts],
            "comments": [{"id": c.id, "text": c.text, "post_id": c.post.id} for c in comments],
            "likes_count": like_count
        })
        
    # ======================
    # UPLOAD PROFILE PIC 
    # ======================
    
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def upload_profile_pic(self, request):
        serializer = ProfilePicSerializer(data=request.data)

        if serializer.is_valid():
            request.user.profile_pic = serializer.validated_data["profile_pic"]
            request.user.save()

            return Response({
                "message": "Profile picture updated",
                "profile_pic": request.user.profile_pic.url
            })

        return Response(serializer.errors, status=400)
    
    # ======================
    # DELETE PROFILE PIC 
    # ======================
    @action(detail=False, methods=["delete"], permission_classes=[IsAuthenticated])
    def delete_profile_image(self, request):
        request.user.profile_pic = None
        request.user.save()

        return Response({"message": "Profile image removed"})
    
    # ======================
    # USER LIST 
    # ======================
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def user_list(self, request):
        queryset = User.objects.all()   

        filter_backend = DjangoFilterBackend()
        queryset = filter_backend.filter_queryset(
            request, queryset, self
        )

        serializer = ProfileSerializer(queryset, many=True)  
        return Response(serializer.data)