from odoo import http
from odoo.http import request
from base_api import api_ok, api_error, jwt_required, require_admin


class AdminSeekerAPI(http.Controller):

    # ==================================================
    # LIST SEEKERS
    # ==================================================
    @http.route(
        "/api/recruit/admin/seekers",
        type="json",
        auth="none",
        methods=["GET"],
    )
    @jwt_required
    def list_seekers(self, is_public=None, active=None):
        err = require_admin()
        if err:
            return err

        domain = []
        if is_public is not None:
            domain.append(("is_public", "=", bool(int(is_public))))
        if active is not None:
            domain.append(("active", "=", bool(int(active))))

        seekers = request.env["dumuc.seeker"].sudo().search(
            domain, order="created_at desc"
        )

        return api_ok([
            {
                "id": s.id,
                "full_name": s.full_name,
                "email": s.email,
                "phone": s.phone,
                "headline": s.headline,
                "location": s.location,
                "exp_years": s.exp_years,
                "is_public": s.is_public,
                "active": s.active,
                "created_at": s.created_at,
            }
            for s in seekers
        ])

    # ==================================================
    # SEEKER DETAIL
    # ==================================================
    @http.route(
        "/api/recruit/admin/seekers/<int:seeker_id>",
        type="json",
        auth="none",
        methods=["GET"],
    )
    @jwt_required
    def get_seeker(self, seeker_id):
        err = require_admin()
        if err:
            return err

        seeker = request.env["dumuc.seeker"].sudo().browse(seeker_id)
        if not seeker.exists():
            return api_error("NOT_FOUND", "Seeker not found")

        return api_ok({
            "id": seeker.id,
            "full_name": seeker.full_name,
            "email": seeker.email,
            "phone": seeker.phone,
            "headline": seeker.headline,
            "exp_years": seeker.exp_years,
            "location": seeker.location,
            "is_public": seeker.is_public,
            "active": seeker.active,
            "created_at": seeker.created_at,
        })

    # ==================================================
    # UPDATE SEEKER INFO
    # ==================================================
    @http.route(
        "/api/recruit/admin/seekers/<int:seeker_id>",
        type="json",
        auth="none",
        methods=["PUT"],
    )
    @jwt_required
    def update_seeker(self, seeker_id, **payload):
        err = require_admin()
        if err:
            return err

        seeker = request.env["dumuc.seeker"].sudo().browse(seeker_id)
        if not seeker.exists():
            return api_error("NOT_FOUND", "Seeker not found")

        editable_fields = [
            "full_name",
            "email",
            "phone",
            "headline",
            "location",
            "exp_years",
        ]

        values = {k: payload[k] for k in editable_fields if k in payload}

        try:
            seeker.write(values)
        except Exception as e:
            return api_error("UPDATE_FAILED", str(e))

        return api_ok({"id": seeker.id})

    # ==================================================
    # BLOCK SEEKER
    # ==================================================
    @http.route(
        "/api/recruit/admin/seekers/<int:seeker_id>/block",
        type="json",
        auth="none",
        methods=["POST"],
    )
    @jwt_required
    def block_seeker(self, seeker_id):
        err = require_admin()
        if err:
            return err

        seeker = request.env["dumuc.seeker"].sudo().browse(seeker_id)
        if not seeker.exists():
            return api_error("NOT_FOUND", "Seeker not found")

        seeker.write({"active": False})

        return api_ok({
            "id": seeker.id,
            "active": False,
        })

    # ==================================================
    # UNBLOCK SEEKER
    # ==================================================
    @http.route(
        "/api/recruit/admin/seekers/<int:seeker_id>/unblock",
        type="json",
        auth="none",
        methods=["POST"],
    )
    @jwt_required
    def unblock_seeker(self, seeker_id):
        err = require_admin()
        if err:
            return err

        seeker = request.env["dumuc.seeker"].sudo().browse(seeker_id)
        if not seeker.exists():
            return api_error("NOT_FOUND", "Seeker not found")

        seeker.write({"active": True})

        return api_ok({
            "id": seeker.id,
            "active": True,
        })

    # ==================================================
    # TOGGLE PUBLIC PROFILE
    # ==================================================
    @http.route(
        "/api/recruit/admin/seekers/<int:seeker_id>/toggle-public",
        type="json",
        auth="none",
        methods=["POST"],
    )
    @jwt_required
    def toggle_public(self, seeker_id):
        err = require_admin()
        if err:
            return err

        seeker = request.env["dumuc.seeker"].sudo().browse(seeker_id)
        if not seeker.exists():
            return api_error("NOT_FOUND", "Seeker not found")

        seeker.write({"is_public": not seeker.is_public})

        return api_ok({
            "id": seeker.id,
            "is_public": seeker.is_public,
        })
