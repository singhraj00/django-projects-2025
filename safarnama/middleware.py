from django.contrib import messages

class ClearMessagesMiddleware:
    """
    Ensures messages are only shown once, clears them after each request.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Consume messages so they are not carried over
        list(messages.get_messages(request))
        return response
