from odoo import http


def api_ok(data=None):
    return {"success": True, "data": data, "error": None}


def api_error(code, message):
    return {
        "success": False,
        "data": None,
        "error": {"code": code, "message": message},
    }


def get_json():
    try:
        return http.request.get_json_data()
    except Exception:
        return {}
