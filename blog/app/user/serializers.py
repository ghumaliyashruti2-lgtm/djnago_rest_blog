from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
import random
from app.follow.models import Follow
from app.like.models import Like
from app.post.models import Post
from app.comment.models import Comment
from app.user.models import OTP

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
        return user
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
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
        otp = data.get("otp")
        
        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError({"error": "User not found"})

        otp_obj = OTP.objects.filter(email=email).order_by("-created_at").first()

        
        print("INPUT OTP:", otp)
        print("DB OTPs:", list(OTP.objects.filter(email=email).values_list("otp", flat=True)))
        
        
        if not otp_obj:
            raise serializers.ValidationError({"error": "No OTP found"})

        # compare manually
        if otp_obj.otp != otp:
            raise serializers.ValidationError({"error": "Invalid OTP"})

        # expiry check
        if otp_obj.is_expired():
            raise serializers.ValidationError({"error": "OTP expired"})
        
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
            raise serializers.ValidationError({"error": "User not found"})

        if last_otp and not last_otp.is_expired():
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

        user = authenticate(
            username=data["username"],
            password=data["password"]
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_verified:
            raise serializers.ValidationError("Email not verified")

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
            raise serializers.ValidationError({"error": "User not found"})
        
        otp_obj = OTP.objects.filter(email=email).order_by("-created_at").first()

        if not otp_obj:
            raise serializers.ValidationError({"error": "No OTP found"})

        if otp_obj.otp != otp:
            raise serializers.ValidationError({"error": "Invalid OTP"})

        if otp_obj.is_expired():
            raise serializers.ValidationError({"error": "OTP expired"})

        self.context["user"]=user
        return data
    
    def save(self, **kwargs):
        user = self.context["user"]

        user.is_verified = True
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
            raise serializers.ValidationError({"error": "User not found"})

        self.user = user
        return data 
    
    def save(self, **kwargs):
        password = self.validated_data.get("password")
        self.user.password = make_password(password)
        self.user.save()
 
 
# ======================
# LOGOUT 
# ======================

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    
    def validate(self, data):
        
        refresh_token = data.get("refresh")
        
        if not refresh_token:
            raise serializers.ValidationError({"Refresh Token Required"})

        self.refresh_token = refresh_token
        return data
    
    def save(self, **kwargs):
        try:
            token=RefreshToken(self.refresh_token)
            token.blacklist()
        except Exception:
            raise serializers.ValidationError({"Invalid Token"})

    
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
    
    
# ======================
# SPECIFIC USER PROFILE 
# ======================
class UserProfileSerializer(serializers.Serializer):
    
    def to_representation(self,instance):
        request = self.context.get("request")
        username = self.context.get("username")
        
        user = get_object_or_404(User, username=username)
        
        if request.user.is_authenticated:
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
                "follwings":following_count
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
        