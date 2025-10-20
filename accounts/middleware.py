from django.utils.deprecation import MiddlewareMixin

class JWTTokenFromCookieMiddleware(MiddlewareMixin):
    """
    Middleware для автоматического извлечения access-токена из cookie
    и добавления его в Authorization header запроса.
    """
    def process_request(self, request):
        access_token = request.COOKIES.get('access_token')
        if access_token:
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
