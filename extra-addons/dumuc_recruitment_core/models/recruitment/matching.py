from odoo import models, fields


class MatchingScore(models.Model):
    _name = "dumuc.matching.score"
    _description = "Điểm phù hợp giữa ứng viên và tin tuyển dụng"

    job_id = fields.Many2one("hr.job", string="Tin tuyển dụng")
    candidate_id = fields.Many2one("dumuc.candidate.profile", string="Ứng viên")
    score = fields.Float(string="Điểm matching")
