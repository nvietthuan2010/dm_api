from odoo import models, fields


class CandidateKYC(models.Model):
    _name = "dumuc.candidate.kyc"
    _description = "Xác thực danh tính ứng viên"

    candidate_id = fields.Many2one(
        "dumuc.candidate.profile",
        string="Ứng viên"
    )
    document_front = fields.Binary(string="Giấy tờ mặt trước")
    document_back = fields.Binary(string="Giấy tờ mặt sau")
    verified = fields.Boolean(
        string="Đã xác thực",
        default=False
    )

    def action_verify(self):
        """Admin duyệt xác thực"""
        self.verified = True

    def action_reject(self):
        """Admin từ chối"""
        self.verified = False
