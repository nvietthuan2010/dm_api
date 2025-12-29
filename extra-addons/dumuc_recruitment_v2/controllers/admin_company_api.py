from odoo import http
from odoo.http import request
from base_api import api_ok, api_error, jwt_required, require_admin


class AdminCompanyAPI(http.Controller):

    @http.route(
        "/api/recruit/admin/companies",
        type="json",
        auth="none",
        methods=["GET"],
    )
    @jwt_required
    def list_companies(self, is_verified=None, is_active=None):
        err = require_admin()
        if err:
            return err

        domain = []
        if is_verified is not None:
            domain.append(("is_verified", "=", bool(int(is_verified))))
        if is_active is not None:
            domain.append(("is_active", "=", bool(int(is_active))))

        companies = request.env["dumuc.company"].sudo().search(
            domain, order="id desc"
        )

        return api_ok([
            {
                "id": c.id,
                "name": c.name,
                "email": c.email,
                "phone": c.phone,
                "is_verified": c.is_verified,
                "is_active": c.is_active,
            }
            for c in companies
        ])


    @http.route(
        "/api/recruit/admin/companies/<int:company_id>",
        type="json",
        auth="none",
        methods=["GET"],
    )
    @jwt_required
    def get_company(self, company_id):
        err = require_admin()
        if err:
            return err

        company = request.env["dumuc.company"].sudo().browse(company_id)
        if not company.exists():
            return api_error("NOT_FOUND", "Company not found")

        wallet = company.get_wallet()

        return api_ok({
            "id": company.id,
            "name": company.name,
            "email": company.email,
            "phone": company.phone,
            "address": company.address,
            "is_verified": company.is_verified,
            "is_active": company.is_active,
            "wallet": {
                "balance": wallet.balance
            }
        })

    @http.route(
        "/api/recruit/admin/companies/<int:company_id>/verify",
        type="json",
        auth="none",
        methods=["POST"],
    )
    @jwt_required
    def verify_company(self, company_id):
        err = require_admin()
        if err:
            return err

        company = request.env["dumuc.company"].sudo().browse(company_id)
        if not company.exists():
            return api_error("NOT_FOUND", "Company not found")

        company.write({"is_verified": True})

        return api_ok({
            "id": company.id,
            "is_verified": True
        })
    

    @http.route(
        "/api/recruit/admin/companies/<int:company_id>/block",
        type="json",
        auth="none",
        methods=["POST"],
    )
    @jwt_required
    def block_company(self, company_id):
        err = require_admin()
        if err:
            return err

        company = request.env["dumuc.company"].sudo().browse(company_id)
        if not company.exists():
            return api_error("NOT_FOUND", "Company not found")

        company.write({"is_active": False})

        return api_ok({
            "id": company.id,
            "is_active": False
        })


    @http.route(
        "/api/recruit/admin/companies/<int:company_id>/unblock",
        type="json",
        auth="none",
        methods=["POST"],
    )
    @jwt_required
    def unblock_company(self, company_id):
        err = require_admin()
        if err:
            return err

        company = request.env["dumuc.company"].sudo().browse(company_id)
        if not company.exists():
            return api_error("NOT_FOUND", "Company not found")

        company.write({"is_active": True})

        return api_ok({
            "id": company.id,
            "is_active": True
        })


