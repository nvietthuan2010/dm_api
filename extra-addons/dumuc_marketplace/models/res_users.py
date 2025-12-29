from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    # Phân loại User theo Spec
    role_type = fields.Selection([
        ('admin', 'Admin'),
        ('private', 'Cá nhân'),
        ('salon', 'Salon Xe'),
        ('evaluator', 'Đánh giá viên')
    ], default='private', string="Vai trò")

    # Thông tin Salon (Table: SalonProfiles)
    salon_name = fields.Char("Tên Salon")
    salon_address = fields.Char("Địa chỉ Salon")
    is_verified_salon = fields.Boolean("Đã xác thực Salon", default=False) # Salon Badges
    
    # Wallet
    wallet_balance = fields.Float("Số dư ví")

    # Bookmark (Table: SavedListings)
    saved_listing_ids = fields.Many2many('dumuc.listing', string="Tin đã lưu")