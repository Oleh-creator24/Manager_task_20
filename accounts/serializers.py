
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from rest_framework import serializers

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """
    Регистрация нового пользователя.
    - Проверяем уникальность email и username
    - Валидация формата email
    - Валидация сложности пароля (Django validators)
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2", "first_name", "last_name")

    def validate_email(self, value):
        value = (value or "").strip().lower()
        validate_email(value)
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError({"password2": "Пароли не совпадают."})
        # Django password validators
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)  # хэширование пароля
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    Логин по username или email + password.
    """
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = (attrs.get("username") or "").strip()
        email = (attrs.get("email") or "").strip().lower()
        password = attrs.get("password")

        if not username and not email:
            raise serializers.ValidationError("Укажите username или email.")

        try:
            if email:
                user = User.objects.get(email__iexact=email)
            else:
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден.")

        if not user.check_password(password):
            raise serializers.ValidationError("Неверный пароль.")

        attrs["user"] = user
        return attrs
