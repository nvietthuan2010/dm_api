# -*- coding: utf-8 -*-
from odoo import models, fields

class DumucListingImage(models.Model):
    _name = "dumuc.listing.image"
    _description = "Ảnh tin đăng"

    listing_id = fields.Many2one('dumuc.listing', string='Tin đăng', ondelete='cascade')
    image = fields.Binary('Ảnh')
    caption = fields.Char('Chú thích')
    sequence = fields.Integer('Thứ tự', default=10)
    is_cover = fields.Boolean('Ảnh đại diện')
