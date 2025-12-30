from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    global_display_name = fields.Char("Tên hiển thị hệ thống")
    avatar_image = fields.Binary("Ảnh đại diện")

    email_verified = fields.Boolean("Đã xác thực email", default=False)
    phone_verified = fields.Boolean("Đã xác thực số điện thoại", default=False)

    role_binding_ids = fields.One2many(
        "dumuc.user.role.binding",
        "user_id",
        string="Vai trò hệ thống"
    )
