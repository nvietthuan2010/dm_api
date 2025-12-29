from odoo import models, fields


class ActivityLog(models.Model):
    _name = "dumuc.activity.log"
    _description = "Nhật ký hoạt động người dùng"

    user_id = fields.Many2one(
        "res.users",
        string="Người thực hiện"
    )

    action = fields.Char(
        string="Hành động"
    )

    model = fields.Char(
        string="Tên model liên quan"
    )

    record_id = fields.Integer(
        string="ID đối tượng liên quan"
    )

    description = fields.Text(
        string="Chi tiết hoạt động"
    )

    timestamp = fields.Datetime(
        string="Thời điểm",
        default=fields.Datetime.now
    )
