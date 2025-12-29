from odoo import models, fields


class Applicant(models.Model):
    _inherit = "hr.applicant"
    _description = "Ứng viên ứng tuyển tin tuyển dụng"

    job_id = fields.Many2one("hr.job", string="Tin tuyển dụng")
    candidate_id = fields.Many2one(
        "dumuc.candidate.profile",
        string="Hồ sơ ứng viên"
    )
    score_total = fields.Float(
        string="Tổng điểm đánh giá",
        help="Điểm tổng hợp từ các quy tắc tính điểm"
    )
