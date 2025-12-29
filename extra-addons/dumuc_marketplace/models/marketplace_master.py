from odoo import models, fields

from odoo import models, fields


class VehicleBrand(models.Model):
    _name = "dumuc.vehicle.brand"
    _description = "DuMuc Vehicle Brand"
    _order = "name"

    name = fields.Char("Tên hãng", required=True)
    code = fields.Char("Mã hãng", required=True)
    model_ids = fields.One2many(
        "dumuc.vehicle.model", "brand_id", string="Dòng xe"
    )


class VehicleModel(models.Model):
    _name = "dumuc.vehicle.model"
    _description = "DuMuc Vehicle Model"
    _order = "brand_id, name"

    name = fields.Char("Tên dòng xe", required=True)
    brand_id = fields.Many2one(
        "dumuc.vehicle.brand", string="Hãng xe", required=True
    )


class Category(models.Model):
    _name = 'dumuc.vehicle.category'
    _description = 'Loại xe'

    code = fields.Char('Mã loại xe', required=True)
    name = fields.Char('Loại xe', required=True) # Cars, Motorcycles


class ListingRejectReason(models.Model):
    _name = "dumuc.listing.reject.reason"
    _description = "Lý do từ chối tin đăng"

    name = fields.Char("Tiêu đề", required=True)
    code = fields.Char("Mã", required=True)
    description = fields.Text("Mô tả chi tiết")
    active = fields.Boolean(default=True)
