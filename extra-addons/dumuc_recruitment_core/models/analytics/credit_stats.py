from odoo import models, fields


class CreditStats(models.Model):
    _name = "dumuc.credit.stats"
    _description = "Thống kê tín dụng"

    garage_id = fields.Many2one(
        "dumuc.garage.profile",
        string="Garage"
    )

    total_credits_purchased = fields.Integer(
        string="Tổng tín dụng đã mua"
    )

    total_credits_used = fields.Integer(
        string="Tổng tín dụng đã tiêu"
    )

    remaining_credits = fields.Integer(
        string="Số tín dụng còn lại"
    )
