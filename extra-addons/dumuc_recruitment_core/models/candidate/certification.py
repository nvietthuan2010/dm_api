from odoo import models, fields


class CandidateCertification(models.Model):
    _name = "dumuc.candidate.certification"
    _description = "Chứng chỉ của ứng viên"

    candidate_id = fields.Many2one(
        "dumuc.candidate.profile",
        string="Ứng viên"
    )
    name = fields.Char(string="Tên chứng chỉ")
    organization = fields.Char(string="Tổ chức cấp")
    issue_date = fields.Date(string="Ngày cấp")
