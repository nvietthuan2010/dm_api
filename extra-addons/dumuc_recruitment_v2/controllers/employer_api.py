from odoo import http, fields
from odoo.http import request

from base_api import require_employer


def ensure_job_belongs_to_company(job, company_id):
    if (not job) or (not job.exists()):
        return http.Response("Job not found", status=404)

    if job.company_id.id != company_id:
        return http.Response("Access denied", status=403)

    return True


def ensure_app_belongs_to_company(app, company_id):
    if (not app) or (not app.exists()):
        return http.Response("Application not found", status=404)

    if app.job_id.company_id.id != company_id:
        return http.Response("Access denied", status=403)

    return True

def check_daily_unlock_limit(company_id):
    today = fields.Date.today()

    count_today = request.env["dumuc.unlock.log"].sudo().search_count([
        ("company_id", "=", company_id),
        ("is_rollback", "=", False),
        ("unlock_date", ">=", today)
    ])

    policy = request.env["dumuc.unlock.policy"].sudo().search([], limit=1)

    limit_val = policy.daily_unlock_limit or 20

    return count_today < limit_val

def evaluate_refund_auto_rules(log):

    seeker = log.seeker_id
    company = log.company_id

    # AUTO APPROVE RULES
    if seeker.status == "blocked":
        return "auto_approve", "Seeker account blocked"

    if not seeker.phone or len(seeker.phone) < 9:
        return "auto_approve", "Invalid phone number"

    if seeker.is_public is False:
        return "auto_approve", "Seeker profile hidden after unlock"

    # AUTO REJECT RULES
    minutes = (fields.Datetime.now() - log.unlock_date).total_seconds() / 60

    if minutes < 2:
        return "auto_reject", "Unlock refund too soon"

    refunds = request.env["dumuc.unlock.log"].sudo().search_count([
        ("company_id", "=", company.id),
        ("refund_status", "in", ["requested","approved","auto_approved"]),
        ("unlock_date", ">=", fields.Date.today())
    ])

    if refunds >= 10:
        return "auto_reject", "High refund frequency today"

    return "manual_review", None


class EmployerAPI(http.Controller):

    # ------------------------------------------------------------
    # JOB LIST
    # ------------------------------------------------------------

    @http.route(
        "/api/recruit/employer/jobs",
        auth="public",
        type="json",
        methods=["GET"]
    )
    def api_list_jobs(self, status=None):

        employer, payload = require_employer()
        if isinstance(employer, http.Response):
            return employer

        domain = [("company_id", "=", employer.company_id.id)]

        if status:
            domain.append(("status", "=", status))

        jobs = request.env["dumuc.job"].sudo().search(domain)

        return {
            "success": True,
            "count": len(jobs),
            "items": [
                {
                    "id": j.id,
                    "title": j.title,
                    "status": j.status,
                    "created_at": j.create_date,
                    "applications": len(j.application_ids),
                }
                for j in jobs
            ]
        }


    # ------------------------------------------------------------
    # CREATE JOB (DRAFT)
    # ------------------------------------------------------------

    @http.route(
        "/api/recruit/employer/job",
        auth="public",
        type="json",
        methods=["POST"]
    )
    def api_create_job(self, **vals):

        employer, payload = require_employer()
        if isinstance(employer, http.Response):
            return employer

        job_vals = {
            "title": vals.get("title"),
            "description": vals.get("description"),
            "category_id": vals.get("category_id"),
            "company_id": employer.company_id.id,
            "employer_id": employer.id,
            "status": "draft",
        }

        job = request.env["dumuc.job"].sudo().create(job_vals)

        return {
            "success": True,
            "job_id": job.id,
            "status": job.status
        }


    # ------------------------------------------------------------
    # UPDATE JOB (ONLY draft/pending)
    # ------------------------------------------------------------

    @http.route(
        "/api/recruit/employer/job/<int:job_id>",
        auth="public",
        type="json",
        methods=["PUT"]
    )
    def api_update_job(self, job_id, **vals):

        employer, payload = require_employer()

        job = request.env["dumuc.job"].sudo().browse(job_id)

        allowed = ensure_job_belongs_to_company(job, employer.company_id.id)
        if allowed is not True:
            return allowed

        if job.status not in ("draft", "pending", "archived"):
            return http.Response(
                "Job cannot be edited in current state",
                status=400
            )

        allowed_fields = [
            "title",
            "description",
            "category_id",
            "location",
            "salary_min",
            "salary_max",
            "employment_type",
        ]

        update_vals = {
            k: v for k, v in vals.items()
            if k in allowed_fields
        }

        job.write(update_vals)

        return {
            "success": True,
            "job_id": job.id
        }


    # ------------------------------------------------------------
    # SUBMIT JOB FOR APPROVAL (draft → pending)
    # ------------------------------------------------------------

    @http.route(
        "/api/recruit/employer/job/<int:job_id>/submit",
        auth="public",
        type="json",
        methods=["POST"]
    )
    def api_submit_job(self, job_id):

        employer, payload = require_employer()

        job = request.env["dumuc.job"].sudo().browse(job_id)

        allowed = ensure_job_belongs_to_company(job, employer.company_id.id)
        if allowed is not True:
            return allowed

        if job.status != "draft":
            return http.Response("Only draft jobs can be submitted", status=400)

        # Minimal validation (MVP)
        if not job.title or not job.description:
            return http.Response(
                "Job must have title & description before submit",
                status=400
            )

        job.write({
            "status": "pending",
            "submit_date": fields.Datetime.now()
        })

        return {
            "success": True,
            "status": job.status
        }


    # ------------------------------------------------------------
    # ARCHIVE JOB (active → archived)
    # ------------------------------------------------------------

    @http.route(
        "/api/recruit/employer/job/<int:job_id>/archive",
        auth="public",
        type="json",
        methods=["POST"]
    )
    def api_archive_job(self, job_id):

        employer, payload = require_employer()

        job = request.env["dumuc.job"].sudo().browse(job_id)

        allowed = ensure_job_belongs_to_company(job, employer.company_id.id)
        if allowed is not True:
            return allowed

        if job.status != "active":
            return http.Response("Only active jobs can be archived", status=400)

        job.write({"status": "archived"})

        return {
            "success": True,
            "status": job.status
        }


    # ------------------------------------------------------------
    # REOPEN JOB (archived → active)
    # ------------------------------------------------------------

    @http.route(
        "/api/recruit/employer/job/<int:job_id>/reopen",
        auth="public",
        type="json",
        methods=["POST"]
    )
    def api_reopen_job(self, job_id):

        employer, payload = require_employer()

        job = request.env["dumuc.job"].sudo().browse(job_id)

        allowed = ensure_job_belongs_to_company(job, employer.company_id.id)
        if allowed is not True:
            return allowed

        if job.status != "archived":
            return http.Response("Only archived jobs can be reopened", status=400)

        job.write({"status": "active"})

        return {
            "success": True,
            "status": job.status
        }


    # ------------------------------------------------------------
    # LIST APPLICATIONS FOR A JOB
    # ------------------------------------------------------------

    @http.route(
        "/api/recruit/employer/job/<int:job_id>/applications",
        auth="public",
        type="json",
        methods=["GET"]
    )
    def api_list_job_applications(self, job_id):

        employer, payload = require_employer()

        job = request.env["dumuc.job"].sudo().browse(job_id)

        allowed = ensure_job_belongs_to_company(job, employer.company_id.id)
        if allowed is not True:
            return allowed

        apps = job.application_ids

        return {
            "success": True,
            "count": len(apps),
            "items": [
                {
                    "id": a.id,
                    "status": a.status,
                    "applied_at": a.create_date,
                    "seeker": {
                        "id": a.seeker_id.id,
                        "full_name": a.seeker_id.full_name,
                        "headline": a.seeker_id.headline,
                    }
                }
                for a in apps
            ]
        }


    # ------------------------------------------------------------
    # VIEW APPLICATION DETAIL
    # ------------------------------------------------------------

    @http.route(
        "/api/recruit/employer/application/<int:app_id>",
        auth="public",
        type="json",
        methods=["GET"]
    )
    def api_get_application(self, app_id):

        employer, payload = require_employer()

        app = request.env["dumuc.application"].sudo().browse(app_id)

        allowed = ensure_app_belongs_to_company(app, employer.company_id.id)
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
                "seeker": {
                    "id": app.seeker_id.id,
                    "full_name": app.seeker_id.full_name,
                    "location": app.seeker_id.location,
                }
            }
        }


    # ------------------------------------------------------------
    # APPLICATION PIPELINE ACTIONS
    # ------------------------------------------------------------

    def _transition_application(self, app, to_state):

        allowed_map = {
            "viewed":     ("new",),
            "interview":  ("viewed",),
            "rejected":   ("viewed", "interview"),
            "accepted":   ("interview",)
        }

        if app.status not in allowed_map.get(to_state, ()):
            return http.Response(
                f"Invalid state transition {app.status} → {to_state}",
                status=400
            )

        app.write({"status": to_state})

        return {"success": True, "status": to_state}


    @http.route(
        "/api/recruit/employer/application/<int:app_id>/viewed",
        auth="public",
        type="json",
        methods=["POST"]
    )
    def api_mark_viewed(self, app_id):

        employer, payload = require_employer()

        app = request.env["dumuc.application"].sudo().browse(app_id)

        allowed = ensure_app_belongs_to_company(app, employer.company_id.id)
        if allowed is not True:
            return allowed

        return self._transition_application(app, "viewed")


    @http.route(
        "/api/recruit/employer/application/<int:app_id>/interview",
        auth="public",
        type="json",
        methods=["POST"]
    )
    def api_mark_interview(self, app_id):

        employer, payload = require_employer()

        app = request.env["dumuc.application"].sudo().browse(app_id)

        allowed = ensure_app_belongs_to_company(app, employer.company_id.id)
        if allowed is not True:
            return allowed

        return self._transition_application(app, "interview")


    @http.route(
        "/api/recruit/employer/application/<int:app_id>/reject",
        auth="public",
        type="json",
        methods=["POST"]
    )
    def api_reject_application(self, app_id, reason=None):

        employer, payload = require_employer()

        app = request.env["dumuc.application"].sudo().browse(app_id)

        allowed = ensure_app_belongs_to_company(app, employer.company_id.id)
        if allowed is not True:
            return allowed

        app.write({"reject_reason": reason})

        return self._transition_application(app, "rejected")


    @http.route(
        "/api/recruit/employer/application/<int:app_id>/accept",
        auth="public",
        type="json",
        methods=["POST"]
    )
    def api_accept_application(self, app_id):

        employer, payload = require_employer()

        app = request.env["dumuc.application"].sudo().browse(app_id)

        allowed = ensure_app_belongs_to_company(app, employer.company_id.id)
        if allowed is not True:
            return allowed

        return self._transition_application(app, "accepted")


    @http.route(
        "/api/recruit/employer/seeker/<int:seeker_id>/public",
        auth="public",
        type="json",
        methods=["GET"]
    )
    def api_public_seeker_profile(self, seeker_id):

        employer, payload = require_employer()
        if isinstance(employer, http.Response):
            return employer

        seeker = request.env["dumuc.seeker"].sudo().browse(seeker_id)

        if not seeker.exists():
            return http.Response("Seeker not found", status=404)

        return {
            "success": True,
            "profile": {
                "id": seeker.id,
                "full_name": seeker.full_name,
                "headline": seeker.headline,
                "exp_years": seeker.exp_years,
                "location": seeker.location,
                "category": seeker.category_id.name,
                "skills": [s.name for s in seeker.skill_ids],
                "is_contact_unlocked": False
            }
        }

    @http.route(
        "/api/recruit/employer/application/<int:app_id>/unlock",
        auth="public", type="json", methods=["POST"]
    )
    def api_unlock_seeker_contact(self, app_id):

        employer, payload = require_employer()
        app = request.env["dumuc.application"].sudo().browse(app_id)

        allowed = ensure_app_belongs_to_company(app, employer.company_id.id)
        if allowed is not True:
            return allowed

        # Rule 1 — Must be applied
        if app.status not in ["new","viewed","interview"]:
            return http.Response(
                "Cannot unlock — candidate not in review stage",
                status=400
            )

        # Rule 2 — Job must be active (unless policy allows)
        policy = request.env["dumuc.unlock.policy"].sudo().search([], limit=1)

        if not policy.allow_expired_job_unlock and app.job_id.status != "active":
            return http.Response(
                "Job expired — unlock not allowed",
                status=400
            )

        # Rule 3 — Only once
        if app.is_unlocked:
            return {
                "success": True,
                "message": "Already unlocked",
                "contact": {
                    "phone": app.seeker_id.phone,
                    "email": app.seeker_id.email
                }
            }

        # Rule 4 — Daily limit
        if not check_daily_unlock_limit(employer.company_id.id):
            return http.Response(
                "Daily unlock limit reached",
                status=429
            )

        # Unlock & audit
        app.write({
            "is_unlocked": True,
            "unlock_date": fields.Datetime.now()
        })

        request.env["dumuc.unlock.log"].sudo().create({
            "company_id": employer.company_id.id,
            "seeker_id": app.seeker_id.id,
            "application_id": app.id,
        })

        return {
            "success": True,
            "unlocked": True,
            "contact": {
                "phone": app.seeker_id.phone,
                "email": app.seeker_id.email
            }
        }


    @http.route(
        "/api/recruit/employer/unlock/<int:log_id>/refund/request",
        auth="public", type="json", methods=["POST"]
    )
    def api_request_unlock_refund(self, log_id, **payload):

        employer, token = require_employer()

        log = request.env["dumuc.unlock.log"].sudo().browse(log_id)

        if not log.exists():
            return http.Response("Unlock log not found", status=404)

        if log.company_id.id != employer.company_id.id:
            return http.Response("Not allowed", status=403)

        if log.refund_status not in ["none", "rejected"]:
            return http.Response("Refund already processed", status=400)

        reason = payload.get("reason") or ""
        status, reason = evaluate_refund_auto_rules(log)

        if status == "auto_approve":
            log.write({
                "refund_status": "auto_approved",
                "refund_processed_at": fields.Datetime.now(),
                "is_auto_processed": True,
                "refund_reason": reason,
            })
            return {"success": True, "status": "auto_approved"}

        if status == "auto_reject":
            log.write({
                "refund_status": "auto_rejected",
                "refund_processed_at": fields.Datetime.now(),
                "is_auto_processed": True,
                "refund_reason": reason,
            })
            return {"success": False, "status": "auto_rejected"}
        
        log.write({
            "refund_status": "requested",
            "refund_reason": reason,
        })

        return {
            "success": True,
            "status": "requested"
        }
