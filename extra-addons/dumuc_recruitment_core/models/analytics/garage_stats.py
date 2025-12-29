from odoo import models, fields


class GarageStats(models.Model):
    _name = "dumuc.analytics.garage.stats"
    _description = "Thống kê Garage"

    garage_id = fields.Many2one(
        "dumuc.garage.profile",
        string="Garage"
    )

    total_jobs = fields.Integer(string="Tổng tin tuyển dụng")
    total_hires = fields.Integer(string="Tổng ứng viên tuyển được")
    total_credits_used = fields.Integer(string="Tổng tín dụng đã tiêu")
    total_applicants = fields.Integer(string="Tổng ứng viên ứng tuyển")
