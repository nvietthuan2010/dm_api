from odoo import models, fields


class CreditService(models.Model):
    _name = "dumuc.credit.service"
    _description = "Dịch vụ tiêu tín dụng"

    name = fields.Char(string="Tên dịch vụ", required=True)
    code = fields.Char(string="Mã dịch vụ", required=True)

    cost = fields.Integer(string="Chi phí")

    description = fields.Text(string="Mô tả")

    active = fields.Boolean(default=True)
