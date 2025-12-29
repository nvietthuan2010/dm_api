from odoo import models, fields


class GarageStats(models.Model):
    _name = "dumuc.garage.stats"
    _description = "Thống kê hoạt động Garage"

    garage_id = fields.Many2one(
        "dumuc.garage.profile",
        string="Garage"
    )

    total_jobs = fields.Integer(string="Tổng số tin đã đăng")
    total_hires = fields.Integer(string="Tổng ứng viên tuyển được")
    credits_used = fields.Integer(string="Tổng tín dụng tiêu thụ")
