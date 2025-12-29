from odoo import http
from odoo.http import request
from base_api import api_ok, api_error, jwt_required, require_admin


class AdminServicePlanAPI(http.Controller):

    # ==================================================
    # LIST
    # ==================================================
    @http.route(
        "/api/recruit/admin/service-plans",
        type="json",
        auth="none",
        methods=["GET"],
    )
    @jwt_required
    def list_plans(self):
        err = require_admin()
        if err:
            return err

        plans = request.env["dumuc.service.plan"].sudo().search([])

        return api_ok([
            {
                "id": p.id,
                "code": p.code,
                "name": p.name,
                "credit_cost": p.credit_cost,
                "is_active": p.is_active,
                "description": p.description,
            }
            for p in plans
        ])

    # ==================================================
    # DETAIL
    # ==================================================
    @http.route(
        "/api/recruit/admin/service-plans/<int:plan_id>",
        type="json",
        auth="none",
        methods=["GET"],
    )
    @jwt_required
    def get_plan(self, plan_id):
        err = require_admin()
        if err:
            return err

        plan = request.env["dumuc.service.plan"].sudo().browse(plan_id)
        if not plan.exists():
            return api_error("NOT_FOUND", "Service plan not found")

        return api_ok({
            "id": plan.id,
            "code": plan.code,
            "name": plan.name,
            "credit_cost": plan.credit_cost,
            "description": plan.description,
            "is_active": plan.is_active,
        })

    # ==================================================
    # CREATE
    # ==================================================
    @http.route(
        "/api/recruit/admin/service-plans",
        type="json",
        auth="none",
        methods=["POST"],
    )
    @jwt_required
    def create_plan(self, **payload):
        err = require_admin()
        if err:
            return err

        required_fields = ["code", "name", "credit_cost"]
        for f in required_fields:
            if f not in payload:
                return api_error("MISSING_FIELD", f"Missing field: {f}")

        try:
            plan = request.env["dumuc.service.plan"].sudo().create({
                "code": payload["code"],
                "name": payload["name"],
                "credit_cost": int(payload["credit_cost"]),
                "description": payload.get("description"),
                "is_active": True,
            })
        except Exception as e:
            return api_error("CREATE_FAILED", str(e))

        return api_ok({
            "id": plan.id,
            "code": plan.code,
        })

    # ==================================================
    # UPDATE
    # ==================================================
    @http.route(
        "/api/recruit/admin/service-plans/<int:plan_id>",
        type="json",
        auth="none",
        methods=["PUT"],
    )
    @jwt_required
    def update_plan(self, plan_id, **payload):
        err = require_admin()
        if err:
            return err

        plan = request.env["dumuc.service.plan"].sudo().browse(plan_id)
        if not plan.exists():
            return api_error("NOT_FOUND", "Service plan not found")

        allowed_fields = ["name", "credit_cost", "description", "is_active"]
        values = {k: payload[k] for k in allowed_fields if k in payload}

        try:
            plan.write(values)
        except Exception as e:
            return api_error("UPDATE_FAILED", str(e))

        return api_ok({"id": plan.id})

    # ==================================================
    # DEACTIVATE (SOFT DELETE)
    # ==================================================
    @http.route(
        "/api/recruit/admin/service-plans/<int:plan_id>",
        type="json",
        auth="none",
        methods=["DELETE"],
    )
    @jwt_required
    def deactivate_plan(self, plan_id):
        err = require_admin()
        if err:
            return err

        plan = request.env["dumuc.service.plan"].sudo().browse(plan_id)
        if not plan.exists():
            return api_error("NOT_FOUND", "Service plan not found")

        plan.write({"is_active": False})

        return api_ok({
            "id": plan.id,
            "is_active": False
        })
