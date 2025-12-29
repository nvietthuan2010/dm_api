# dumuc_recruitment/controllers/credit_guard.py

from functools import wraps
from odoo import http
from odoo.http import Response
from odoo.exceptions import UserError

from jwt import JWTAuth


def require_credit(service_code):
    """
    Decorator kiểm tra credit trước khi xử lý API.
    Example:
        @require_credit("POST_JOB")
        def post_job(...)
    """
    def decorator(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):

            # args[0] = self (controller instance)
            controller = args[0]

            # Lấy company từ JWT
            jwt = JWTAuth()

            company = jwt.get_current_company(http.request)
            if not company:
                return Response(
                    "Authentication Failed - No Company",
                    status=401,
                )

            engine = http.request.env["dumuc.credit.engine"]

            try:
                engine.consume(
                    company_id=company.id,
                    service_code=service_code,
                    model=None,
                    record_id=None
                )
            except UserError as e:
                # trả lỗi 402 Payment Required
                return Response(
                    f"Credit required: {str(e)}",
                    status=402,
                )

            # Nếu đủ credit → OK
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def require_subscription():
    def wrap(fn):
        def inner(self, *args, **kwargs):
            company = JWTAuth().get_current_company(http.request)
            sub = http.request.env['dumuc.company.subscription'].search([('company_id','=',company.id), ('is_active','=',True)], limit=1)
            if not sub:
                return Response("Subscription required", status=402)
            return fn(self, *args, **kwargs)
        return inner
    return wrap