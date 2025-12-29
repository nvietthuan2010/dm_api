from odoo import models, fields


class GarageMember(models.Model):
    _name = "dumuc.garage.member"
    _description = "Nhân sự HR / thành viên Garage"

    garage_id = fields.Many2one(
        "dumuc.garage.profile",
        string="Garage"
    )

    user_id = fields.Many2one(
        "res.users",
        string="Tài khoản"
    )

    role = fields.Selection([
        ('owner', 'Chủ sở hữu'),
        ('hr', 'Nhân sự'),
        ('viewer', 'Theo dõi')
    ], string="Vai trò")
