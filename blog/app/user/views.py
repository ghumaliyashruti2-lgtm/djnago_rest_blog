from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from app.user.serializers import DeleteAccountSerializer, DeleteProfilePicSerializer, ForgotPasswordSerializer, LogoutSerializer, ProfilePicSerializer, ProfileSerializer, RefreshTokenSerializer, RegisterSerializer, LoginSerializer, ResendOTPSerializer, ResetPasswordSerializer, UserProfileSerializer, VerifyOTPSerializer
from app.user.models import OTP
from rest_framework.parsers import MultiPartParser, FormParser
import random
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.permission import IsOwnerOrReadOnly
User = get_user_model()

def generate_otp():
    return str(random.randint(100000, 999999))


class AuthViewSet(ViewSet):
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['username', 'email', 'is_verified']
    serializer_class = RegisterSerializer

    # ======================
    # REGISTER
    # ======================
    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={"200":RegisterSerializer},
        operation_id="User Register"
    )
        
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
    @swagger_auto_schema(
        request_body=VerifyOTPSerializer,
        responses={"200":VerifyOTPSerializer},
        operation_id="User Verify Otp"
    )
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
    @swagger_auto_schema(
        request_body=ResendOTPSerializer,
        responses={"200":ResendOTPSerializer,},
        operation_id="User Resend Otp",
    )
        
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
    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={"200":LoginSerializer},
        operation_id="User Login"
    )
    
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
    @swagger_auto_schema(
        request_body=ForgotPasswordSerializer,
        responses={"200":ForgotPasswordSerializer},
        operation_id="User Forgot Password"
    )
    
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
    @swagger_auto_schema(
        request_body=ResendOTPSerializer,
        responses={"200":ResendOTPSerializer},
        operation_id="User Verify Reset Otp"
    )
    
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
    @swagger_auto_schema(
        request_body=ResetPasswordSerializer,
        responses={"200":ResetPasswordSerializer},
        operation_id="User Reset Password"
    )
    
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
    @swagger_auto_schema(
        request_body=RefreshTokenSerializer,
        responses={"200":RefreshTokenSerializer},
        operation_id="User Refresh Token"
    )
    
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
    @swagger_auto_schema(
        request_body=LogoutSerializer,
        responses={"200":LogoutSerializer},
        operation_id="User Logout"
    )
    
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated,IsOwnerOrReadOnly])
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
    
    @swagger_auto_schema(
        request_body=DeleteAccountSerializer,
        responses={"200":DeleteAccountSerializer},
        operation_id="Delete Account",
        
    )
    @action(detail=False, methods=["delete"], permission_classes=[IsAuthenticated,IsOwnerOrReadOnly])
    def delete_account(self, request):

        serializer = DeleteAccountSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        return Response(data)
        
    # ======================
    # PROFILE 
    # ======================
    @swagger_auto_schema(
        responses={"200":ProfileSerializer},
        operation_id="User Profile"
    )
    
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated,IsOwnerOrReadOnly])
    def profile(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

        
    # ======================
    # UPLOAD PROFILE PIC 
    # ======================
    @swagger_auto_schema(
        request_body=ProfilePicSerializer,
        responses={"200": ProfilePicSerializer},
        operation_id="Upload User Profile"
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated,IsOwnerOrReadOnly],parser_classes=[MultiPartParser, FormParser])
    def upload_profile_pic(self, request):

        serializer = ProfilePicSerializer(
            instance=request.user,  
            data=request.data
        )

        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        return Response(data)
    
    # ======================
    # DELETE PROFILE PIC 
    # ======================
    @swagger_auto_schema(
        responses={"200": DeleteProfilePicSerializer},
        operation_id="User Profile Pic Delete "
    )
    
    @action(detail=False, methods=["delete"], permission_classes=[IsAuthenticated,IsOwnerOrReadOnly])
    def delete_profile_image(self, request):
        
        serializer = DeleteProfilePicSerializer(context={"request": request})
        data = serializer.save()
        return Response(data)
            
    
    # ======================
    # SPECIFIC USER PROFILE 
    # ======================
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'username',
                openapi.IN_PATH,
                description="Username of the user",
                type=openapi.TYPE_STRING
            )
        ],
        responses={200: UserProfileSerializer},
        operation_id="Specific User Profile"
    )
    
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
    @swagger_auto_schema(
        responses={200: ProfileSerializer(many=True)},
        operation_id="User List"
    )
    @action(detail=False, methods=["get"])
    def user_list(self, request):
        queryset = User.objects.all()
        serializer = ProfileSerializer(queryset, many=True)
        return Response(serializer.data)