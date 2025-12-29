from odoo import http
from odoo.http import request
from base_api import api_ok, api_error, jwt_required, require_seeker, paginate
from datetime import datetime, timedelta


def ensure_seeker_owns_application(application, seeker):
    if not application.exists():
        return http.Response("Application not found", status=404)

    if application.seeker_id.id != seeker.id:
        return http.Response(
            "Access denied — this application does not belong to you",
            status=403
        )

    return True

def seeker_already_applied(job, seeker):
    return http.request.env["dumuc.application"].sudo().search_count([
        ("job_id", "=", job.id),
        ("seeker_id", "=", seeker.id)
    ]) > 0

def seeker_recent_apply(seeker):
    last = http.request.env["dumuc.application"].sudo().search([
        ("seeker_id", "=", seeker.id)
    ], order="create_date desc", limit=1)

    if not last:
        return False

    # 30s cooldown
    return last.create_date >= datetime.utcnow() - timedelta(seconds=30)


class SeekerAPI(http.Controller):

    @http.route(
        "/api/recruit/seeker/profile",
        auth="public",
        type="json",
        methods=["GET"]
    )
    def api_get_profile(self):

        seeker, payload = require_seeker()
        if isinstance(seeker, http.Response):
            return seeker

        return {
            "success": True,
            "profile": {
                "id": seeker.id,
                "full_name": seeker.full_name,
                "headline": seeker.headline,
                "exp_years": seeker.exp_years,
                "location": seeker.location,
                "category_id": seeker.category_id.id,
            }
        }
    
    @http.route(
        "/api/recruit/seeker/profile",
        auth="public",
        type="json",
        methods=["PUT"]
    )
    def api_update_profile(self, **vals):

        seeker, payload = require_seeker()
        if isinstance(seeker, http.Response):
            return seeker

        allowed_fields = [
            "full_name",
            "headline",
            "exp_years",
            "location",
            "category_id",
        ]

        update_vals = {
            k: v for k, v in vals.items()
            if k in allowed_fields
        }

        seeker.sudo().write(update_vals)

        return {
            "success": True,
            "id": seeker.id,
        }

    @http.route(
        "/api/recruit/seeker/apply",
        auth="public",
        type="json",
        methods=["POST"]
    )
    def api_apply_job(self, **vals):

        seeker, payload = require_seeker()
        if isinstance(seeker, http.Response):
            return seeker

        job_id = vals.get("job_id")
        cover_letter = vals.get("cover_letter")

        job = http.request.env["dumuc.job"].sudo().browse(job_id)

        if not job.exists():
            return http.Response("Job not found", status=404)

        if job.status != "active":
            return http.Response("Job is not open for applications", status=400)

        if seeker_already_applied(job, seeker):
            return http.Response("You already applied to this job", status=400)

        if seeker_recent_apply(seeker):
            return http.Response("Please wait before applying again", status=429)

        app = http.request.env["dumuc.application"].sudo().create({
            "job_id": job.id,
            "seeker_id": seeker.id,
            "status": "new",
            "cover_letter": cover_letter,
        })

        return {
            "success": True,
            "application_id": app.id,
            "status": app.status,
        }
    
    @http.route(
        "/api/recruit/seeker/applications",
        auth="public",
        type="json",
        methods=["GET"]
    )
    def api_list_my_applications(self):

        seeker, payload = require_seeker()
        if isinstance(seeker, http.Response):
            return seeker

        apps = http.request.env["dumuc.application"].sudo().search([
            ("seeker_id", "=", seeker.id)
        ])

        return {
            "success": True,
            "count": len(apps),
            "items": [
                {
                    "id": app.id,
                    "status": app.status,
                    "applied_at": app.create_date,
                    "job": {
                        "id": app.job_id.id,
                        "title": app.job_id.title,
                        "company": app.job_id.company_id.name,
                    }
                }
                for app in apps
            ]
        }

    @http.route(
        "/api/recruit/seeker/applications/<int:app_id>",
        auth="public",
        type="json",
        methods=["GET"]
    )
    def api_get_my_application(self, app_id):

        seeker, payload = require_seeker()

        app = http.request.env["dumuc.application"].sudo().browse(app_id)

        allowed = ensure_seeker_owns_application(app, seeker)
        if allowed is not True:
            return allowed

        return {
            "success": True,
            "application": {
                "id": app.id,
                "status": app.status,
                "job": {
                    "id": app.job_id.id,
                    "title": app.job_id.title,
                },
                "company": {
                    "id": app.job_id.company_id.id,
                    "name": app.job_id.company_id.name,
                }
            }
        }


