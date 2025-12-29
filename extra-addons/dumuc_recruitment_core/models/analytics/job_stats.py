from odoo import models, fields


class JobStats(models.Model):
    _name = "dumuc.job.stats"
    _description = "Thống kê tin tuyển dụng"

    job_id = fields.Many2one(
        "hr.job",
        string="Tin tuyển dụng"
    )

    total_views = fields.Integer(
        string="Lượt xem"
    )

    total_applicants = fields.Integer(
        string="Tổng số ứng viên"
    )

    total_matches = fields.Integer(
        string="Số matching"
    )

    total_spent_credits = fields.Integer(
        string="Tín dụng tiêu thụ"
    )
