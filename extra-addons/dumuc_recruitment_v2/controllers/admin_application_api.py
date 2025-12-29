from odoo import http
from odoo.http import request
from base_api import api_ok, api_error, jwt_required, require_admin, paginate
from odoo.exceptions import UserError, ValidationError

class AdminApplicationAPI(http.Controller):

    @http.route(
        "/api/recruit/admin/applications",
        type="json",
        auth="public",
        methods=["GET"],
    )
    @jwt_required
    def list_applications(self, **payload):
        admin, payload = require_admin()

        domain = []

        if payload.get("job_id"):
            domain.append(("job_id", "=", int(payload["job_id"])))

        if payload.get("company_id"):
            domain.append(("job_id.company_id", "=", int(payload["company_id"])))

        if payload.get("seeker_id"):
            domain.append(("seeker_id", "=", int(payload["seeker_id"])))

        if payload.get("status"):
            domain.append(("status", "=", payload["status"]))

        applications = request.env["dumuc.application"].sudo().search(
            domain, order="applied_at desc"
        )

        result = paginate(
            applications,
            page=payload.get("page", 1),
            page_size=payload.get("page_size", 20),
        )

        return api_ok({
            "items": [
                {
                    "id": a.id,
                    "status": a.status,
                    "is_flagged": a.is_flagged,
                    "applied_at": a.applied_at,
                    "job": {
                        "id": a.job_id.id,
                        "title": a.job_id.title,
                    },
                    "company": {
                        "id": a.job_id.company_id.id,
                        "name": a.job_id.company_id.name,
                    },
                    "seeker": {
                        "id": a.seeker_id.id,
                        "name": a.seeker_id.name,
                        "is_blocked": a.seeker_id.is_active is False,
                    },
                }
                for a in result["items"]
            ],
            "meta": result["meta"],
        })

    @http.route(
        "/api/recruit/admin/applications/<int:app_id>",
        type="json",
        auth="public",
        methods=["GET"],
    )
    @jwt_required
    def application_detail(self, app_id):
        admin, payload = require_admin()

        app = request.env["dumuc.application"].sudo().browse(app_id)
        if not app.exists():
            return api_error("NOT_FOUND", "Application not found")

        return api_ok({
            "id": app.id,
            "status": app.status,
            "cover_letter": app.cover_letter,
            "cv_url": app.cv_attachment_id and f"/web/content/{app.cv_attachment_id.id}" or None,
            "applied_at": app.applied_at,
            "job": {
                "id": app.job_id.id,
                "title": app.job_id.title,
            },
            "company": {
                "id": app.job_id.company_id.id,
                "name": app.job_id.company_id.name,
            },
            "seeker": {
                "id": app.seeker_id.id,
                "name": app.seeker_id.name,
                "email": app.seeker_id.email,
                "phone": app.seeker_id.phone,
                "is_blocked": not app.seeker_id.is_active,
            },
        })

    @http.route(
        "/api/recruit/admin/applications/<int:app_id>/flag",
        type="json",
        auth="none",
        methods=["POST"],
    )
    @jwt_required
    def flag_application(self, app_id):
        admin, payload = require_admin()

        app = request.env["dumuc.application"].sudo().browse(app_id)
        if not app.exists():
            return api_error("NOT_FOUND", "Application not found")

        app.write({"is_flagged": True})

        return api_ok({
            "id": app.id,
            "is_flagged": True
        })
