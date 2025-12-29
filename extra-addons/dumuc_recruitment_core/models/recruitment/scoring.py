from odoo import models, fields


class ScoringRule(models.Model):
    _name = "dumuc.scoring.rule"
    _description = "Quy tắc tính điểm ứng viên"

    job_id = fields.Many2one("hr.job", string="Tin tuyển dụng")

    field_code = fields.Char(string="Mã tiêu chí đánh giá")
    weight = fields.Float(
        string="Trọng số điểm",
        default=10.0
    )
