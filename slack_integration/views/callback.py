import json
import logging
from hmac import compare_digest

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseBadRequest
from django.http.response import HttpResponseForbidden, HttpResponseNotFound, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from slack_integration.callbacks import get_handler
from slack_integration.exceptions import InvalidSlackCallbackError
from slack_integration.utils import utf8bytes

logger = logging.getLogger('slack_integration.callbacks.message')


@require_POST
@csrf_exempt
def message_callback(request):
    if not hasattr(settings, 'SLACK_API_VERIFY_TOKEN'):
        raise ImproperlyConfigured('Must define SLACK_API_VERIFY_TOKEN before you can use callbacks')

    payload = request.POST.get('payload')
    if not payload:
        return HttpResponseBadRequest('no payload specified')
    data = json.loads(request.POST.get('payload'))

    if not compare_digest(data.get('token').encode('utf-8'), utf8bytes(settings.SLACK_API_VERIFY_TOKEN)):
        logger.warning('Received callback request with bad token: %s', data.get('token'))
        return HttpResponseForbidden('invalid verification token')

    callback = data.get('callback_id')
    if not callback:
        logger.warning('Received callback request without callback_id')
        return HttpResponseBadRequest('no callback specified')

    handler = get_handler(callback)
    if not handler:
        logger.warning('Received callback request with unknown callback_id: %s', callback)
        return HttpResponseNotFound('unknown callback')

    logger.info('Received callback request: %s', data)
    try:
        result = handler(data)
    except InvalidSlackCallbackError as e:
        logger.warning('Invalid callback parameters: %s' % e.message)
        return HttpResponseBadRequest('invalid callback parameters: %s' % e.message)

    return JsonResponse(result)
