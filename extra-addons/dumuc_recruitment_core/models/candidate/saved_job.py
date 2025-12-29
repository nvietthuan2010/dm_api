from odoo import models, fields


class CandidateSavedJob(models.Model):
    _name = "dumuc.candidate.saved.job"
    _description = "Tin tuyển dụng đã lưu"

    candidate_id = fields.Many2one(
        "dumuc.candidate.profile",
        string="Ứng viên"
    )
    job_id = fields.Many2one(
        "hr.job",
        string="Tin tuyển dụng"
    )
    saved_date = fields.Datetime(
        string="Ngày lưu",
        default=fields.Datetime.now
    )
