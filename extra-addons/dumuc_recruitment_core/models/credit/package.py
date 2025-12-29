from odoo import models, fields


class CreditPackage(models.Model):
    _name = "dumuc.credit.package"
    _description = "Gói tín dụng"

    name = fields.Char(string="Tên gói", required=True)
    credits = fields.Integer(string="Tín dụng", required=True)
    price = fields.Integer(string="Giá bán")
    duration_days = fields.Integer(string="Thời hạn sử dụng")
    description = fields.Text(string="Mô tả")
