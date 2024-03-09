import requests
from django.http import HttpRequest
from django.shortcuts import redirect

from adiutor import settings


class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_exception(self, request, exception):
        if settings.DEBUG:
            return None

        self._create_github_issue(request, exception)
        return self._redirect_user()

    def _create_github_issue(self: 'ErrorHandlingMiddleware', request: HttpRequest, error: Exception):
        if not settings.GITHUB_PAT:
            return

        response = requests.post(
            url='https://api.github.com/repos/bernardesMario/adiutorRemake/issues',
            headers={
                'X-GitHub-Api-Version': '2022-11-28',
                'Accept': 'application/vnd.github+json',
                'Authorization': f'Bearer {settings.GITHUB_PAT}',
            },
            json={
                'title': f'Exception raised: {type(error)} {error}',
                'body': f'{type(error)} {error} during request {request.method} {request.path} with {request.body}',
                'labels': ['bug']
            }
        )

        print(response)

    def _redirect_user(self: 'ErrorHandlingMiddleware'):
        return redirect('main:handle-error')
