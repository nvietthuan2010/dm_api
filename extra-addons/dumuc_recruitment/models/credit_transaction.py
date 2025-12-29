from odoo import models, fields

class CreditTransaction(models.Model):
    _name = 'dumuc.credit.transaction'
    _description = "Giao dịch credit"

    company_id = fields.Many2one('dumuc.company', string="Công ty")

    type = fields.Selection([
        ('topup', "Nạp credit"),
        ('spend', "Tiêu credit"),
    ], string="Loại")

    amount = fields.Float(string="Số lượng")
    balance_after = fields.Float(string="Số dư sau")
    description = fields.Char(string="Mô tả")
    created_at = fields.Datetime(string="Ngày tạo", default=fields.Datetime.now)
    expiry_date = fields.Date("Ngày hết hạn")
    is_expired = fields.Boolean("Đã hết hạn", default=False)

    credit_type = fields.Selection([
        ('paid', 'Credit mua'),
        ('bonus', 'Credit thưởng'),
        ('promo', 'Credit khuyến mãi'),
    ], default='paid')


class CreditPolicy(models.Model):
    _name = "dumuc.credit.policy"
    _description = "Chính sách hết hạn Credit"

    credit_type = fields.Selection([
        ('paid','Paid'),
        ('bonus','Bonus'),
        ('promo','Promo'),
    ])

    expiry_days = fields.Integer(default=90)  # ví dụ 90 ngày