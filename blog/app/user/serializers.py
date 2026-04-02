from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()


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