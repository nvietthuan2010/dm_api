from odoo import models, fields


class GarageVerification(models.Model):
    _name = "dumuc.garage.verification"
    _description = "Yêu cầu xác thực Garage"

    garage_id = fields.Many2one(
        "dumuc.garage.profile",
        string="Garage"
    )
    reviewer_id = fields.Many2one(
        "res.users",
        string="Người xét duyệt"
    )

    document_front = fields.Binary(
        string="Tài liệu mặt trước"
    )
    document_back = fields.Binary(
        string="Tài liệu mặt sau"
    )

    status = fields.Selection([
        ('pending', 'Chờ duyệt'),
        ('verified', 'Đã xác thực'),
        ('rejected', 'Từ chối')
    ], string="Trạng thái", default="pending")

    note = fields.Text(string="Ghi chú")

    def action_verify(self):
        """Moderator duyệt"""
        self.status = "verified"
        self.garage_id.verified = True

    def action_reject(self, note=""):
        """Moderator từ chối"""
        self.status = "rejected"
        self.note = note
        self.garage_id.verified = False
