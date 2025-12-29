from odoo import models, fields
from datetime import timedelta

class APILog(models.Model):
    _name = "dumuc.api.log"
    _description = "Nhật ký API"

    endpoint = fields.Char(
        string="Endpoint API"
    )

    method = fields.Char(
        string="Phương thức HTTP"
    )

    request_payload = fields.Text(
        string="Dữ liệu request"
    )

    response_payload = fields.Text(
        string="Dữ liệu response"
    )

    status_code = fields.Integer(
        string="Mã trạng thái"
    )

    duration_ms = fields.Integer(
        string="Thời gian xử lý (ms)"
    )

    timestamp = fields.Datetime(
        string="Thời điểm",
        default=fields.Datetime.now
    )

    user_id = fields.Many2one(
        "res.users",
        string="Tài khoản yêu cầu"
    )

    def _cron_cleanup(self):
        """Xóa log quá 90 ngày"""
        expiry = fields.Datetime.now() - timedelta(days=90)
        self.search([('timestamp', '<', expiry)]).unlink()
