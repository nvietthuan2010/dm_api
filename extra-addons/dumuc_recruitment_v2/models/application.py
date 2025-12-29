from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DumucApplication(models.Model):
    _name = "dumuc.application"
    _description = "Job Application"
    _order = "applied_at desc"
    _rec_name = "job_id"

    # ==================================================
    # RELATIONS
    # ==================================================

    job_id = fields.Many2one(
        "dumuc.job",
        string="Tin tuyển dụng",
        required=True,
        ondelete="cascade"
    )

    seeker_id = fields.Many2one(
        "dumuc.seeker",
        string="Ứng viên",
        required=True,
        ondelete="cascade"
    )

    company_id = fields.Many2one(
        "dumuc.company",
        string="Công ty",
        related="job_id.company_id",
        store=True,
        index=True
    )

    # ==================================================
    # CONTENT
    # ==================================================

    cover_letter = fields.Text(
        string="Thư ứng tuyển"
    )

    state = fields.Selection(
        [
            ("new", "Mới"),
            ("viewed", "Đã xem"),
            ("interview", "Phỏng vấn"),
            ("accepted", "Chấp nhận"),
            ("rejected", "Từ chối"),
        ],
        default="new",
        index=True
    )

    reject_reason = fields.Text(string="Lý do từ chối")

    # ==================================================
    # META
    # ==================================================

    applied_at = fields.Datetime(
        string="Thời gian ứng tuyển",
        default=fields.Datetime.now,
        required=True
    )
    is_flagged = fields.Boolean(default=False, string="Là spam")

    is_unlocked = fields.Boolean(
        string="Employer unlocked seeker",
        default=False
    )

    unlock_date = fields.Datetime(
        string="Unlock Date"
    )
    # ==================================================
    # CONSTRAINTS
    # ==================================================

    _sql_constraints = [
        (
            "uniq_job_seeker_application",
            "unique(job_id, seeker_id)",
            "Ứng viên đã ứng tuyển tin này rồi"
        )
    ]

    # ==================================================
    # BUSINESS METHODS (MVP)
    # ==================================================

    def action_mark_viewed(self):
        self.write({"state": "viewed"})

    def action_accept(self):
        self.write({"state": "accepted"})

    def action_reject(self):
        self.write({"state": "rejected"})
