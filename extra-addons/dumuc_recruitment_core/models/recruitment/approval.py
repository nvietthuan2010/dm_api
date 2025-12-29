from odoo import models, fields


class JobApproval(models.Model):
    _name = "dumuc.job.approval"
    _description = "Lịch sử duyệt tin tuyển dụng"

    job_id = fields.Many2one("hr.job", string="Tin tuyển dụng")
    reviewer_id = fields.Many2one("res.users", string="Người duyệt")

    state = fields.Selection([
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối')
    ], string="Trạng thái duyệt")

    note = fields.Text(string="Ghi chú")
