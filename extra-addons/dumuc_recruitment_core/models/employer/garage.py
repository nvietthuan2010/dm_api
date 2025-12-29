from odoo import models, fields


class GarageProfile(models.Model):
    _name = "dumuc.garage.profile"
    _description = "Hồ sơ Garage / Nhà tuyển dụng"

    name = fields.Char(
        string="Tên doanh nghiệp",
        required=True
    )
    address = fields.Char(string="Địa chỉ")
    phone = fields.Char(string="Số điện thoại")
    email = fields.Char(string="Email")
    website = fields.Char(string="Website")

    owner_id = fields.Many2one(
        "res.users",
        string="Chủ tài khoản Garage"
    )

    verified = fields.Boolean(
        string="Đã xác thực",
        default=False
    )

    verification_ids = fields.One2many(
        "dumuc.garage.verification",
        "garage_id",
        string="Lịch sử xác thực"
    )

    member_ids = fields.One2many(
        "dumuc.garage.member",
        "garage_id",
        string="Danh sách nhân sự"
    )

    job_ids = fields.One2many(
        "hr.job",
        "garage_id",
        string="Tin tuyển dụng"
    )

    subscription_id = fields.Many2one(
        "dumuc.garage.subscription",
        string="Gói dịch vụ"
    )

    def action_request_verification(self):
        """Gửi yêu cầu xác thực"""
        return self.env["dumuc.garage.verification"].create({
            "garage_id": self.id,
            "status": "pending"
        })
