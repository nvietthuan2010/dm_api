from odoo import models, fields


class ModerationRecord(models.Model):
    _name = "dumuc.moderation.record"
    _description = "Lịch sử kiểm duyệt tin / garage"

    reviewer_id = fields.Many2one("res.users", string="Người duyệt", required=True)
    target_model = fields.Char(string="Model đối tượng")
    target_id = fields.Integer(string="ID đối tượng")
    action = fields.Selection(
        [('approve', 'Duyệt'),
         ('reject', 'Từ chối'),
         ('auto_expired', 'Tự động hết hạn'),
         ('auto_published', 'Tự động đăng')],
        string="Hành động",
        required=True)
    reason = fields.Text(string="Lý do")
    create_date = fields.Datetime(string="Thời gian", readonly=True)
