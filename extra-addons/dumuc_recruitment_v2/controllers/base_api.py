import jwt
from functools import wraps
from odoo.http import request
from odoo import http
from odoo.exceptions import ValidationError
from services.jwt_service import decode_token


JWT_SECRET = "DUMUC_SECRET_KEY"

def api_ok(data=None):
    return {"success": True, "data": data, "error": None}


def api_error(code, message):
    return {
        "success": False,
        "data": None,
        "error": {"code": code, "message": message}
    }

def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.httprequest.headers.get("Authorization")
        if not token:
            return {
                "success": False,
                "error": {
                    "code": "NO_TOKEN",
                    "message": "Missing token"
                }
            }

        try:
            payload = jwt.decode(
                token.replace("Bearer ", ""),
                JWT_SECRET,
                algorithms=["HS256"],
            )
            request.uid = payload["uid"]
        except Exception:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": "Invalid or expired token"
                }
            }

        return func(*args, **kwargs)

    return wrapper

def _get_token_from_header():
    request = http.request
    token = request.httprequest.headers.get("Authorization")

    if not token:
        return None, http.Response("Missing Authorization token", status=401)

    return token, None


# --------------------------
# ADMIN GUARD
# --------------------------

def require_admin():
    token, error = _get_token_from_header()
    if error:
        return error

    payload = decode_token(token)
    if isinstance(payload, http.Response):
        return payload

    if payload.get("role") != "admin":
        return http.Response("Admin permission required", status=403)

    user = http.request.env["res.users"].sudo().browse(payload["user_id"])

    if not user.exists():
        return http.Response("Admin user not found", status=403)

    if not user.has_group("base.group_system"):
        return http.Response("User is not an Odoo admin", status=403)

    return user, payload



#
# ---------------------------
# EMPLOYER GUARD
# ---------------------------
#
def require_employer():
    token, error = _get_token_from_header()
    if error:
        return error

    payload = decode_token(token)
    if isinstance(payload, http.Response):
        return payload

    if payload.get("role") != "employer":
        return http.Response("Employer permission required", status=403)

    user = http.request.env["res.users"].sudo().browse(payload["user_id"])
    company = http.request.env["dumuc.company"].sudo().browse(payload["company_id"])

    if not user.exists():
        return http.Response("User not found", status=403)

    if not company.exists():
        return http.Response("Company not found", status=403)

    if company.status == "blocked":
        return http.Response("Company account is blocked", status=403)

    return user, company, payload



#
# ---------------------------
# SEEKER GUARD
# ---------------------------
#
def require_seeker():
    token, error = _get_token_from_header()
    if error:
        return error

    payload = decode_jwt(token)
    if isinstance(payload, http.Response):
        return payload

    if payload.get("role") != "seeker":
        return http.Response("Seeker permission required", status=403)

    seeker = http.request.env["dumuc.seeker"].sudo().browse(payload["seeker_id"])

    if not seeker.exists():
        return http.Response("Seeker profile not found", status=403)

    if seeker.status == "blocked":
        return http.Response("Your account is blocked", status=403)

    return seeker, payload


def paginate(recordset, page=1, page_size=20):
    page = max(int(page), 1)
    page_size = min(max(int(page_size), 1), 100)

    total = recordset.search_count([])
    offset = (page - 1) * page_size

    items = recordset[offset: offset + page_size]

    return {
        "items": items,
        "meta": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }

def safe_call(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            return api_error("VALIDATION_ERROR", str(e))
        except Exception:
            return api_error("INTERNAL_ERROR", "Internal server error")
    return wrapper

def ensure_company_owns_job(job, company):
    if not job.exists():
        return http.Response("Job not found", status=404)

    if job.company_id.id != company.id:
        return http.Response(
            "Access denied — job does not belong to your company",
            status=403
        )

    return True
