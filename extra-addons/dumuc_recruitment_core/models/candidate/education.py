from odoo import models, fields


class CandidateEducation(models.Model):
    _name = "dumuc.candidate.education"
    _description = "Học vấn của ứng viên"

    candidate_id = fields.Many2one(
        "dumuc.candidate.profile",
        string="Ứng viên"
    )
    school = fields.Char(string="Trường học")
    degree = fields.Char(string="Bằng cấp")
    start_date = fields.Date(string="Ngày bắt đầu")
    end_date = fields.Date(string="Ngày kết thúc")
