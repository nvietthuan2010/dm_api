from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Job(models.Model):
    _inherit = "hr.job"

    approval_state = fields.Selection([
        ('draft', 'Nháp'),
        ('pending_review', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
        ('published', 'Đang hiển thị'),
        ('expired', 'Hết hạn')
    ], string="Trạng thái duyệt", default="draft", tracking=True)

    rejection_reason = fields.Text(string="Lý do từ chối")

    def action_submit_review(self):
        for rec in self:
            if rec.approval_state != "draft":
                raise UserError("Chỉ gửi duyệt từ trạng thái nháp")
            rec.approval_state = "pending_review"

    def action_approve(self):
        for rec in self:
            if rec.approval_state != "pending_review":
                raise UserError("Chỉ duyệt từ trạng thái chờ duyệt")

            rec.approval_state = "approved"
            self.env["dumuc.moderation.record"].create({
                "reviewer_id": self.env.user.id,
                "target_model": "hr.job",
                "target_id": rec.id,
                "action": "approve"
            })

    def action_reject(self, reason):
        for rec in self:
            if rec.approval_state != "pending_review":
                raise UserError("Chỉ từ chối từ trạng thái chờ duyệt")

            rec.approval_state = "rejected"
            rec.rejection_reason = reason

            self.env["dumuc.moderation.record"].create({
                "reviewer_id": self.env.user.id,
                "target_model": "hr.job",
                "target_id": rec.id,
                "action": "reject",
                "reason": reason
            })
