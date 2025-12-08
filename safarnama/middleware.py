# myapp/middleware.py
from django.contrib.messages import get_messages

class ClearMessagesMiddleware:
    """
    Middleware to ensure Django messages are cleared after they are displayed,
    preventing them from persisting across multiple requests.
    Works for all pages, including login/logout.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        try:
            # Access the storage and iterate to mark all messages as used
            storage = get_messages(request)
            # Only iterate if there are messages
            if storage:
                list(storage)
        except Exception:
            pass  # fail-safe, do not break request if messages storage is unavailable

        return response
