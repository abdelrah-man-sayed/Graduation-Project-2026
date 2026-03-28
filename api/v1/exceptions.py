from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            "error": {
                "code": response.status_code,
                "message": "Required parameter: q",
                "errors": []
            }
        }

        if isinstance(response.data, dict):
            for field, messages in response.data.items():
                msg = messages[0] if isinstance(messages, list) else messages
                custom_data["error"]["errors"].append({
                    "message": f"Required parameter: {field}",
                    "domain": "global",
                    "reason": "required"
                })
        
        response.data = custom_data

    return response