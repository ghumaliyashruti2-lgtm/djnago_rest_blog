from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from app.user.serializers import ForgotPasswordSerializer, LogoutSerializer, ProfilePicSerializer, ProfileSerializer, RefreshTokenSerializer, RegisterSerializer, LoginSerializer, ResendOTPSerializer, ResetPasswordSerializer, UserProfileSerializer, VerifyOTPSerializer
from app.user.models import OTP
import random
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.shortcuts import get_object_or_404
User = get_user_model()

def generate_otp():
    return str(random.randint(100000, 999999))


class AuthViewSet(ViewSet):
    
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['username', 'email', 'is_verified']

    # ======================
    # REGISTER
    # ======================
    @action(detail=False, methods=["post"])
    def register(self, request):
        
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            otp = generate_otp()
            OTP.objects.create(
                user=user,
                email=user.email,
                otp=otp
            )
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
        
        serializer = VerifyOTPSerializer(
            data=request.data,
            context={"request":request}
        )
        
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Verified successfully"}, status=200)

    # ===========================
    # Resend OTP
    # ===========================
    
    @action(detail=False, methods=["post"])
    def resend_otp(self, request):
        
        serializer = ResendOTPSerializer(
            data=request.data,
            context={"request":request}
        )
        
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "OTP Resend successfully"}, status=200)


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
        
        serializer = ForgotPasswordSerializer(
            data=request.data,
            context={"request":request}
        )
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({"message":"OTP sent in your email"})


    # ======================
    # VERIFY RESET OTP
    # ======================
    @action(detail=False, methods=["post"])
    def verify_reset_otp(self, request):
        
        serializer = VerifyOTPSerializer(
            data=request.data,
            context={"request":request}
        )
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({"message": "OTP verified"})
    
    # ======================
    # RESET PASSWORD
    # ======================
    @action(detail=False, methods=["post"])
    def reset_password(self, request):
        
        serializer = RefreshTokenSerializer(
            data=request.data,
            context={"request":request}
        )
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({"message": "Password reset successful"})

    
    # ===========================
    # REFRESH TOKEN 
    # ==========================

    @action(detail=False, methods=["post"])
    def refresh_token(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"error": "Refresh token required"}, status=400)

        try:
            token = RefreshToken(refresh_token)
            access_token = token.access_token

            return Response({
                "access": str(access_token)
            })

        except TokenError:
            return Response({"error": "Invalid or expired refresh token"}, status=400)
        
        
        
    # ======================
    # LOGOUT
    # ======================
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        
        serializer = LogoutSerializer(
                data=request.data,
                context={"request":request}
            )
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({"message": "Logout successful"})

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
    # SPECIFIC USER PROFILE 
    # ======================
    @action(detail=False, methods=["get"], url_path="user_profile/(?P<username>[^/.]+)")
    def user_profile(self, request, username=None):

        user = get_object_or_404(User,username=username)
        serializer = UserProfileSerializer(
            instance = user,
            context ={
                "request":request,
                "username":username
            }
        )
        
        return Response(serializer.data)
    
    
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