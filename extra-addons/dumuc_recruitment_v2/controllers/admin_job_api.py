from odoo import http
from odoo.http import request
from base_api import api_ok, api_error, jwt_required, require_admin, paginate

def admin_log(action, target_type, target_id, details=None):
    http.request.env["dumuc.admin.log"].sudo().create({
        "admin_user_id": http.request.env.user.id,
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "details": details,
    })



class AdminJobAPI(http.Controller):

    # ==================================================
    # LIST JOBS
    # ==================================================
    @http.route(
        "/api/recruit/admin/jobs/pending",
        auth="public",
        type="json",
        methods=["GET"]
    )
    def api_admin_list_pending_jobs(self):

        admin, payload = require_admin()

        jobs = http.request.env["dumuc.job"].sudo().search([
            ("status", "=", "pending")
        ])

        return {
            "success": True,
            "count": len(jobs),
            "items": [
                {
                    "id": j.id,
                    "title": j.title,
                    "company": j.company_id.name,
                    "category": j.category_id.name,
                    "created_at": j.create_date,
                }
                for j in jobs
            ]
        }
    
    @http.route(
        "/api/recruit/admin/jobs",
        type="json",
        auth="public",
        methods=["GET"],
    )
    def list_jobs(self, state=None, company_id=None, **payload):
        admin, payload = require_admin()

        domain = []
        if state:
            domain.append(("state", "=", state))
        if company_id:
            domain.append(("company_id", "=", int(company_id)))

        jobs_rs = request.env["dumuc.job"].sudo().search(domain, order="created_at desc")

        result = paginate(
            jobs_rs,
            page=payload.get("page", 1),
            page_size=payload.get("page_size", 20),
        )

        return api_ok({
            "items": [
                {
                    "id": j.id,
                    "title": j.title,
                    "company": j.company_id.name,
                    "state": j.state,
                    "employment_type": j.employment_type,
                    "location": j.location,
                    "salary_min": j.salary_min,
                    "salary_max": j.salary_max,
                    "created_at": j.created_at,
                }
                for j in result["items"]
            ],
            "meta": result["meta"]
        })

    # ==================================================
    # JOB DETAIL
    # ==================================================
    @http.route(
        "/api/recruit/admin/jobs/<int:job_id>",
        type="json",
        auth="public",
        methods=["GET"],
    )
    def get_job(self, job_id):
        admin, payload = require_admin()

        job = request.env["dumuc.job"].sudo().browse(job_id)
        if not job.exists():
            return api_error("NOT_FOUND", "Job not found")

        return api_ok({
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "company": {
                "id": job.company_id.id,
                "name": job.company_id.name,
            },
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "salary_unit": job.salary_unit,
            "employment_type": job.employment_type,
            "location": job.location,
            "quantity": job.quantity,
            "state": job.state,
            "created_at": job.created_at,
            "published_at": job.published_at,
            "expires_at": job.expires_at,
        })

    # ==================================================
    # UPDATE JOB CONTENT (ADMIN EDIT)
    # ==================================================
    @http.route(
        "/api/recruit/admin/jobs/<int:job_id>",
        type="json",
        auth="public",
        methods=["PUT"],
    )
    def update_job(self, job_id, **payload):
        admin, payload = require_admin()

        job = request.env["dumuc.job"].sudo().browse(job_id)
        if not job.exists():
            return api_error("NOT_FOUND", "Job not found")

        editable_fields = [
            "title",
            "description",
            "salary_min",
            "salary_max",
            "salary_unit",
            "employment_type",
            "location",
            "quantity",
            "expires_at",
        ]

        values = {k: payload[k] for k in editable_fields if k in payload}

        try:
            job.write(values)
        except Exception as e:
            return api_error("UPDATE_FAILED", str(e))

        return api_ok({"id": job.id})

    # ==================================================
    # APPROVE JOB
    # ==================================================
    @http.route(
        "/api/recruit/admin/job/<int:job_id>/approve",
        auth="public",
        type="json",
        methods=["POST"]
    )
    def api_admin_approve_job(self, job_id):

        admin, payload = require_admin()

        job = http.request.env["dumuc.job"].sudo().browse(job_id)

        if not job.exists():
            return http.Response("Job not found", status=404)

        job.write({
            "status": "active"
        })

        admin_log("approve_job", "job", job.id, f"Approved job {job.title}")

        return {
            "success": True,
            "status": job.status
        }


    # ==================================================
    # REJECT JOB
    # ==================================================
    @http.route(
        "/api/recruit/admin/job/<int:job_id>/reject",
        auth="public",
        type="json",
        methods=["POST"]
    )
    def api_admin_reject_job(self, job_id, reason=None):

        admin, payload = require_admin()

        if not reason:
            return http.Response("Reject reason is required", status=400)

        job = http.request.env["dumuc.job"].sudo().browse(job_id)

        if not job.exists():
            return http.Response("Job not found", status=404)

        job.write({
            "status": "rejected",
            "reject_reason": reason,
        })

        admin_log("reject_job", "job", job.id, f"Reason: {reason}")

        return {
            "success": True,
            "status": job.status
        }


    @http.route(
        "/api/recruit/admin/job/<int:job_id>/block",
        auth="public",
        type="json",
        methods=["POST"]
    )
    def api_admin_block_job(self, job_id, reason=None):

        admin, payload = require_admin()

        job = http.request.env["dumuc.job"].sudo().browse(job_id)

        if not job.exists():
            return http.Response("Job not found", status=404)

        job.write({
            "status": "blocked",
            "block_reason": reason,
        })

        admin_log("block_job", "job", job.id, f"Reason: {reason}")

        return {
            "success": True,
            "status": job.status
        }


    # ==================================================
    # EXPIRE JOB
    # ==================================================
    @http.route(
        "/api/recruit/admin/jobs/<int:job_id>/expire",
        type="json",
        auth="none",
        methods=["POST"],
    )
    @jwt_required
    def expire_job(self, job_id):
        err = require_admin()
        if err:
            return err

        job = request.env["dumuc.job"].sudo().browse(job_id)
        if not job.exists():
            return api_error("NOT_FOUND", "Job not found")

        job.action_expire()

        return api_ok({
            "id": job.id,
            "state": job.state,
        })
