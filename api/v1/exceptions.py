from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        first_error_msg = ""
        if isinstance(response.data, dict):
            for key, value in response.data.items():
                if isinstance(value, list):
                    first_error_msg = str(value[0])
                else:
                    first_error_msg = str(value)
                break
        elif isinstance(response.data, list):
            first_error_msg = str(response.data[0])

        custom_data = {
            "error": {
                "code": response.status_code,
                "message": first_error_msg or "حدث خطأ غير معروف",
                "errors": []
            }
        }

        if isinstance(response.data, dict):
            for field, messages in response.data.items():
                msg = messages[0] if isinstance(messages, list) else messages
                custom_data["error"]["errors"].append({
                    "message": str(msg),
                    "domain": field,
                    "reason": "invalid_input"
                })
        
        response.data = custom_data

    return response