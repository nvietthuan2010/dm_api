from odoo import models, fields


class GarageSubscription(models.Model):
    _name = "dumuc.garage.subscription"
    _description = "Gói sử dụng Garage"

    garage_id = fields.Many2one("dumuc.garage.profile", string="Garage")
    package_id = fields.Many2one("dumuc.credit.package", string="Gói")
    start_date = fields.Date(string="Ngày bắt đầu")
    end_date = fields.Date(string="Ngày kết thúc")
