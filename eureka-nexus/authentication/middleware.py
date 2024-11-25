# to block inactive users from accessing the site

from django.http import JsonResponse

class BlockInactiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_active:
            return JsonResponse({'error': 'Account is deactivated. Please reactivate via email.'}, status=403)
        return self.get_response(request)
