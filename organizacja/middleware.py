from django.db import connection
from rest_framework_simplejwt.tokens import AccessToken


class RLSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        header = request.headers.get('Authorization')
        org_id = 0

        if header and header.startswith('Bearer '):
            try:
                token_str = header.split(' ')[1]
                token = AccessToken(token_str)

                org_id = token.get('id_organizacja', 0)
            except Exception:
                org_id = 0

        with connection.cursor() as cursor:
            cursor.execute(f"SET app.current_org_id = {org_id};")

        response = self.get_response(request)
        return response