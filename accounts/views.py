
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import RegisterSerializer, LoginSerializer

ACCESS_COOKIE = getattr(settings, "JWT_ACCESS_COOKIE", "access_token")
REFRESH_COOKIE = getattr(settings, "JWT_REFRESH_COOKIE", "refresh_token")
COOKIE_SECURE = getattr(settings, "JWT_COOKIE_SECURE", False)
COOKIE_SAMESITE = getattr(settings, "JWT_COOKIE_SAMESITE", "Lax")
COOKIE_HTTPONLY = getattr(settings, "JWT_COOKIE_HTTPONLY", True)


def set_token_cookies(response: Response, access: str, refresh: str):
    # httpOnly cookies
    response.set_cookie(
        ACCESS_COOKIE, access,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/",
    )
    response.set_cookie(
        REFRESH_COOKIE, refresh,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/auth/",   # refresh/логин/логаут висят под /auth
    )
    return response


def clear_token_cookies(response: Response):
    response.delete_cookie(ACCESS_COOKIE, path="/")
    response.delete_cookie(REFRESH_COOKIE, path="/auth/")
    return response


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(generics.CreateAPIView):
    """
    POST /auth/register/  — регистрация
    """
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(generics.GenericAPIView):
    """
    POST /auth/login/ — логин (username или email + password)
    - Возвращает access/refresh JWT
    - Кладёт их в httpOnly cookies
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        data = {
            "access": access,
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        }
        resp = Response(data, status=status.HTTP_200_OK)
        return set_token_cookies(resp, access, str(refresh))


@method_decorator(csrf_exempt, name="dispatch")
class CookieTokenRefreshView(TokenRefreshView):
    """
    POST /auth/refresh/
    - Берёт refresh токен из cookie, если не передан в теле
    - Ротирует refresh (см. SIMPLE_JWT), старый — в blacklist
    - Возвращает новый access (+обновлённый refresh) и обновляет cookies
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Если в body нет refresh — берём из cookie
        if not request.data.get("refresh"):
            cookie_refresh = request.COOKIES.get(REFRESH_COOKIE)
            if cookie_refresh:
                request.data["refresh"] = cookie_refresh

        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access = response.data.get("access")
            refresh = response.data.get("refresh")  # при ROTATE_REFRESH_TOKENS=True
            if access and refresh:
                set_token_cookies(response, access, refresh)
            elif access:
                # Если включена ротация, обычно refresh тоже придёт.
                response.set_cookie(
                    ACCESS_COOKIE, access,
                    httponly=COOKIE_HTTPONLY, secure=COOKIE_SECURE,
                    samesite=COOKIE_SAMESITE, path="/",
                )
        return response


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(generics.GenericAPIView):
    """
    POST /auth/logout/
    - Берёт refresh токен из cookie
    - Кладёт его в blacklist
    - Чистит cookies
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        cookie_refresh = request.COOKIES.get(REFRESH_COOKIE)
        if cookie_refresh:
            try:
                token = RefreshToken(cookie_refresh)
                token.blacklist()  # ⛔ чёрный список
            except Exception:
                pass  # если токен уже невалиден — просто чистим куки

        resp = Response({"detail": "Logged out"}, status=status.HTTP_200_OK)
        return clear_token_cookies(resp)
