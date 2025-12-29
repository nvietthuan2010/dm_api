from odoo import models, fields


class CandidateAvailability(models.Model):
    _name = "dumuc.candidate.availability"
    _description = "Thời gian sẵn sàng làm việc"

    candidate_id = fields.Many2one(
        "dumuc.candidate.profile",
        string="Ứng viên"
    )
    available = fields.Boolean(
        string="Có sẵn làm việc"
    )
    rate_day = fields.Float(
        string="Đơn giá theo ngày"
    )
    zone = fields.Char(
        string="Khu vực"
    )
