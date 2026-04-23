from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
import random
from apps.follows.models import Follow
from apps.likes.models import Like
from apps.posts.models import Post
from apps.comments.models import Comment
from apps.users.models import OTP
import logging
import blog.logs
logger = logging.getLogger(__name__)

User = get_user_model()
def generate_otp():
    return str(random.randint(100000, 999999))

# ======================
# REGISTER
# ======================
class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id","username", "email", "password", "profile_pic"]

        
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"]
        )
        logger.info(f"user {user.username} successfully register")
        return user
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            logger.error(f"register email {value} is already exists")
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            logger.error(f"username {value} alreday exists")
            raise serializers.ValidationError("Username already exists")
        return value

# ==========================
# OTP VERIFY
# =========================

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
   
    def validate(self, data):
        email = data.get("email")
        logger.debug(f"OTP verification started for {email}")
        otp = data.get("otp")
        
        user = User.objects.filter(email=email).first()

        if not user:
            logger.error(f"User not found for email: {email}")
            raise serializers.ValidationError({"error": "User not found"})

        otp_obj = OTP.objects.filter(email=email).order_by("-created_at").first()

        
        
        if not otp_obj:
            logger.error(f"No OTP found for {email}")
            raise serializers.ValidationError({"error": "No OTP found"})

        if otp_obj.otp != otp:
            logger.error(f"Invalid OTP entered for {email}")
            raise serializers.ValidationError({"error": "Invalid OTP"})

        if otp_obj.is_expired():
            logger.error(f"Invalid OTP entered for {email}")
            raise serializers.ValidationError({"error": "OTP expired"})
        
        logger.info(f"OTP verified successfully for {email}")
        
        OTP.objects.filter(email=email).exclude(id=otp_obj.id).delete()
        
        self.user = user
        self.otp_obj = otp_obj
        return data

    def save(self, **kwargs):
        self.user.is_verified = True
        self.user.save()
        self.otp_obj.delete()

        return self.user

# =========================
# Resend OTP
# =========================

class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get("email")

        user = User.objects.filter(email=email).first()
        
        last_otp = OTP.objects.filter(email=email).order_by("-created_at").first()

        if not user:
            logger.error(f"user not found for this user {user}")
            raise serializers.ValidationError({"error": "User not found"})

        if last_otp and not last_otp.is_expired():
            logger.error(f"user {user.username} try to generate new otp before time limit")
            raise serializers.ValidationError("Wait before requesting new OTP")
        self.user = user
        return data

    def save(self, **kwargs):
        otp = generate_otp()

        OTP.objects.create(
            user=self.user,
            email=self.user.email,
            otp=otp
        )

        logger.info(f"OTP resent to {self.user.email}")

        send_mail(
            "Your OTP",
            f"Your OTP is {otp}",
            "noreply@gmail.com",
            [self.user.email],
            fail_silently=True,
        )

        return self.user

# ======================
# LOGIN
# ======================
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data["username"]
        user = authenticate(
            username=username,
            password=data["password"]
        )

        if not user:
            logger.error(f"Failed login attempt for username: {username}")
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_verified:
            logger.error(f"Unverified user tried login: {username}")
            raise serializers.ValidationError("Email not verified")

        logger.info(f"user successfully loggin {username}")
        data["user"] = user
        return data

    def to_representation(self, instance):
        user = instance["user"]

        return {
            "id": user.id,
            "name": user.username,
            "email": user.email,
            "profile": user.profile_pic.url if user.profile_pic else None
        }

# ========================
# FORGOT PASSWORD
# =========================

class ForgotPasswordSerializer(serializers.Serializer):
     email = serializers.EmailField()
     
     def validate(self, data):
         email = data.get ("email")
         
         user = User.objects.filter(email=email).first()
         
         if not user:
            raise serializers.ValidationError({"error": "Email not registered"})
        
        
         self.user = user
         return data
     
     
     def save(self, **kwargs):
        user = self.user
        otp = generate_otp()
        
        OTP.objects.create(
                user=user,
                email=user.email,
                otp=otp
            )

        send_mail(
            "Reset Password OTP",
            f"Your OTP is {otp}",
            "noreply@gmail.com",
            [self.user.email],
            fail_silently=True,
        )
        logger.info(f"user {user.username} attempt forgot password")
        return user

# ======================
# VERIFY RESET OTP 
# ======================

class VerifyResetOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    
    def validate(self, data):
        email=data.get("email")
        otp=data.get("otp")
        
        user = User.objects.filter(email=email).first()
        
        if not user:
            logger.error(f"User not found for email: {email}")
            raise serializers.ValidationError({"error": "User not found"})

        otp_obj = OTP.objects.filter(email=email).order_by("-created_at").first()

        if not otp_obj:
            logger.error(f"No OTP found for {email}")
            raise serializers.ValidationError({"error": "No OTP found"})

        # compare manually
        if otp_obj.otp != otp:
            logger.error(f"Invalid OTP entered for {email}")
            raise serializers.ValidationError({"error": "Invalid OTP"})

        # expiry check
        if otp_obj.is_expired():
            logger.error(f"Invalid OTP entered for {email}")
            raise serializers.ValidationError({"error": "OTP expired"})
        
        logger.info(f"OTP verified successfully for {email}")

        self.context["user"]=user
        return data
    
    def save(self, **kwargs):
        user = self.context["user"]
        user.otp = None
        user.save()

        return user

    
# ======================
# RESET PASSWORD 
# ======================

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, data):
        email=data.get("email")
        password=data.get("password")
        
        user = User.objects.filter(email=email).first()

        if not user:
            logger.error(f"{user} not found")
            raise serializers.ValidationError({"error": "User not found"})

        self.user = user
        return data 
    
    def save(self, **kwargs):
        password = self.validated_data.get("password")
        self.user.password = make_password(password)
        logger.info(f"user {self.user.username} successfully reset password ")
        self.user.save()
 
 
# ======================
# REFRESH TOKEN
# ======================
class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    def validate(self, data):
        refresh_token = data.get("refresh")
        
        if not refresh_token:
            logger.error(f"user {self.user.username} attempt refresh token is required")
            raise serializers.ValidationError({"error": "Refresh token required"}, status=400)

        try:
            token = RefreshToken(refresh_token)
            access_token = token.access_token
            logger.info(f"user successfully refresh token")
            return ({
                "access": str(access_token)
            })

        except TokenError:
            logger.error(f"{self.user.username} token is expired or invalid")
            raise serializers.ValidationError({"error": "Invalid or expired refresh token"}, status=400)

        
 
# ======================
# LOGOUT 
# ======================

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    
    def validate(self, data):
        refresh_token = data.get("refresh")
        
        if not refresh_token:
            logger.error(f"user {self.user.username} for logout refresh token is required")
            raise serializers.ValidationError({"error":"Refresh Token Required"})

        self.refresh_token = refresh_token
        return data
    
    def save(self, **kwargs):
        user = self.context["request"].user
        try:
            token=RefreshToken(self.refresh_token)
            logger.info(f"user {user.username} successfully logout")
            token.blacklist()
        except Exception:
            logger.error(f"user {user.username} enter invalide token for forgotpassword")
            raise serializers.ValidationError({"Invalid Token"})

# ======================
# DELETE ACCOUNT
# ======================    
class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField()
    
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context["request"].user
        password = data.get("password")

        if not user.check_password(password):
            logger.error(f"user {user.username} enter wrong password in delete account")
            raise serializers.ValidationError({
                "password": "Incorrect password"
            })

        return data
    
    def save(self, **kwargs):
        user = self.context["request"].user
        del_user = user
        logger.warning(f"User deleted account: {user.email}")
        user.delete()
        logger.info(f"user {del_user.username} successfully delete own account")
        return {"message": "Account deleted successfully"}

# ======================
# PROFILE
# ======================
class ProfileSerializer(serializers.ModelSerializer):

    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "profile_pic"]

    def get_profile_pic(self, obj):
        return obj.profile_pic.url if obj.profile_pic else None


# ======================
# UPLOAD PROFILE PIC
# ======================
class ProfilePicSerializer(serializers.Serializer):
    profile_pic = serializers.ImageField()

    def validate_profile_pic(self, value):
        if not value.name.lower().endswith((".png", ".jpg", ".jpeg")):
            raise serializers.ValidationError("Invalid file type")
        return value

    def update(self, instance, validated_data):
        instance.profile_pic = validated_data.get("profile_pic")
        instance.save()
        return {
            "profile_pic": instance.profile_pic.url
        }
    
    
# ======================
# DELETE PROFILE PIC 
# ======================
class DeleteProfilePicSerializer(serializers.Serializer):
    def save(self, **kwargs):
        user = self.context["request"].user
        user.profile_pic = "profile_pictures/default_profile.png"
        user.save()

        return {
            "message": "Profile image removed"
        }
    
# ======================
# SPECIFIC USER PROFILE 
# ======================
class UserProfileSerializer(serializers.Serializer):
    
    def to_representation(self,user):
        request = self.context.get("request")
        
        if request and request.user.is_authenticated:
            is_following = Follow.objects.filter(
            follower=request.user,
            following=user
        ).exists()
        else:
            is_following = False
            

        user_data = ProfileSerializer(user).data
        post_count = Post.objects.filter(user=user).count()
        comment_count = Comment.objects.filter(user=user).count()
        like_count = Like.objects.filter(user=user).count()
        followers_count = Follow.objects.filter(following=user).count()
        following_count = Follow.objects.filter(follower=user).count()

        data = {
            "user":user_data,
            "is_following":is_following,
            "counts":{
                "posts":post_count,
                "comments":comment_count,
                "likes":like_count,
                "followers":followers_count,
                "followings":following_count
            }
        }
        
        # unfollowed user 
        if not (request.user == user or is_following):
            return data

        # followed user 
        posts = Post.objects.filter(user=user)
        comments = Comment.objects.filter(user=user)

        data["posts"]= [
            {"id": p.id, "title": p.title, "content": p.content} 
            for p in posts
            ]
        
        data["comments"]= [
            {"id": c.id, "text": c.text, "post_id": c.post.id} 
            for c in comments
            ]
        
        data["likes_count"]= like_count
        
        return data 
     