from odoo import http
from odoo.http import request
from base_api import api_ok, api_error, jwt_required, require_admin


class AdminCreditPackageAPI(http.Controller):

    # ==================================================
    # LIST
    # ==================================================
    @http.route(
        "/api/recruit/admin/credit-packages",
        type="json",
        auth="none",
        methods=["GET"],
    )
    @jwt_required
    def list_packages(self):
        err = require_admin()
        if err:
            return err

        packages = request.env["dumuc.credit.package"].sudo().search([])

        return api_ok([
            {
                "id": p.id,
                "code": p.code,
                "name": p.name,
                "price_vnd": p.price_vnd,
                "credit_amount": p.credit_amount,
                "bonus_credit": p.bonus_credit,
                "total_credit": p.total_credit,
                "price_per_credit": p.price_per_credit,
                "is_active": p.is_active,
            }
            for p in packages
        ])

    # ==================================================
    # DETAIL
    # ==================================================
    @http.route(
        "/api/recruit/admin/credit-packages/<int:package_id>",
        type="json",
        auth="none",
        methods=["GET"],
    )
    @jwt_required
    def get_package(self, package_id):
        err = require_admin()
        if err:
            return err

        package = request.env["dumuc.credit.package"].sudo().browse(package_id)
        if not package.exists():
            return api_error("NOT_FOUND", "Package not found")

        return api_ok({
            "id": package.id,
            "code": package.code,
            "name": package.name,
            "price_vnd": package.price_vnd,
            "credit_amount": package.credit_amount,
            "bonus_credit": package.bonus_credit,
            "description": package.description,
            "is_active": package.is_active,
        })

    # ==================================================
    # CREATE
    # ==================================================
    @http.route(
        "/api/recruit/admin/credit-packages",
        type="json",
        auth="none",
        methods=["POST"],
    )
    @jwt_required
    def create_package(self, **payload):
        err = require_admin()
        if err:
            return err

        required_fields = ["code", "name", "price_vnd", "credit_amount"]
        for f in required_fields:
            if f not in payload:
                return api_error("MISSING_FIELD", f"Missing field: {f}")

        try:
            package = request.env["dumuc.credit.package"].sudo().create({
                "code": payload["code"],
                "name": payload["name"],
                "price_vnd": int(payload["price_vnd"]),
                "credit_amount": int(payload["credit_amount"]),
                "bonus_credit": int(payload.get("bonus_credit", 0)),
                "description": payload.get("description"),
                "is_active": True,
            })
        except Exception as e:
            return api_error("CREATE_FAILED", str(e))

        return api_ok({
            "id": package.id,
            "code": package.code,
        })

    # ==================================================
    # UPDATE
    # ==================================================
    @http.route(
        "/api/recruit/admin/credit-packages/<int:package_id>",
        type="json",
        auth="none",
        methods=["PUT"],
    )
    @jwt_required
    def update_package(self, package_id, **payload):
        err = require_admin()
        if err:
            return err

        package = request.env["dumuc.credit.package"].sudo().browse(package_id)
        if not package.exists():
            return api_error("NOT_FOUND", "Package not found")

        allowed_fields = [
            "name",
            "price_vnd",
            "credit_amount",
            "bonus_credit",
            "description",
            "is_active",
        ]

        values = {
            k: payload[k]
            for k in allowed_fields
            if k in payload
        }

        try:
            package.write(values)
        except Exception as e:
            return api_error("UPDATE_FAILED", str(e))

        return api_ok({"id": package.id})

    # ==================================================
    # DEACTIVATE (SOFT DELETE)
    # ==================================================
    @http.route(
        "/api/recruit/admin/credit-packages/<int:package_id>",
        type="json",
        auth="none",
        methods=["DELETE"],
    )
    @jwt_required
    def deactivate_package(self, package_id):
        err = require_admin()
        if err:
            return err

        package = request.env["dumuc.credit.package"].sudo().browse(package_id)
        if not package.exists():
            return api_error("NOT_FOUND", "Package not found")

        package.write({"is_active": False})

        return api_ok({"id": package.id, "is_active": False})
