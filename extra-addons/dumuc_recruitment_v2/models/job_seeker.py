from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DumucSeeker(models.Model):
    _name = "dumuc.seeker"
    _description = "Job Seeker"
    _rec_name = "full_name"
    _order = "created_at desc"

    # ==================================================
    # IDENTITY
    # ==================================================

    user_id = fields.Many2one(
        "res.users",
        string="Tài khoản",
        required=True,
        ondelete="cascade",
        index=True
    )

    full_name = fields.Char(
        string="Họ và tên",
        required=True
    )

    email = fields.Char(string="Email")
    phone = fields.Char(string="Số điện thoại")

    # ==================================================
    # PROFILE
    # ==================================================

    headline = fields.Char(
        string="Tiêu đề hồ sơ",
        help="Mô tả ngắn gọn về bản thân"
    )

    exp_years = fields.Integer(
        string="Số năm kinh nghiệm",
        default=0
    )

    location = fields.Char(
        string="Khu vực làm việc"
    )

    is_public = fields.Boolean(
        string="Công khai hồ sơ",
        default=True,
        help="Nhà tuyển dụng chỉ xem được hồ sơ khi bật"
    )

    # ==================================================
    # META
    # ==================================================

    active = fields.Boolean(default=True)

    created_at = fields.Datetime(
        string="Ngày tạo",
        default=fields.Datetime.now,
        readonly=True
    )

    # ==================================================
    # CONSTRAINTS
    # ==================================================

    _sql_constraints = [
        (
            "uniq_seeker_user",
            "unique(user_id)",
            "Mỗi tài khoản chỉ có một hồ sơ ứng viên"
        )
    ]

    # ==================================================
    # BUSINESS METHODS (MVP)
    # ==================================================

    def ensure_public(self):
        """Bật công khai hồ sơ"""
        self.write({"is_public": True})

    def ensure_private(self):
        """Ẩn hồ sơ"""
        self.write({"is_public": False})
