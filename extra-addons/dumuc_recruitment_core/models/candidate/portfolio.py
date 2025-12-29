from odoo import models, fields


class CandidatePortfolio(models.Model):
    _name = "dumuc.candidate.portfolio"
    _description = "Dự án / Portfolio ứng viên"

    candidate_id = fields.Many2one(
        "dumuc.candidate.profile",
        string="Ứng viên"
    )
    title = fields.Char(string="Tên dự án")
    link = fields.Char(string="Đường dẫn")
    description = fields.Text(string="Mô tả dự án")
