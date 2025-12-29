from odoo import models, fields


class CandidateExperience(models.Model):
    _name = "dumuc.candidate.experience"
    _description = "Kinh nghiệm làm việc của ứng viên"

    candidate_id = fields.Many2one(
        "dumuc.candidate.profile",
        string="Ứng viên"
    )
    title = fields.Char(string="Chức danh")
    company = fields.Char(string="Công ty")
    start_date = fields.Date(string="Ngày bắt đầu")
    end_date = fields.Date(string="Ngày kết thúc")
    description = fields.Text(string="Mô tả công việc")
