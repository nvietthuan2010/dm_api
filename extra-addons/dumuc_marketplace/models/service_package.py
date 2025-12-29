from odoo import models, fields

class DumucServicePackage(models.Model):
    _name = "dumuc.service.package"
    _description = "Gói dịch vụ DuMuc"
    _order = "sequence, price"

    name = fields.Char(required=True)
    description = fields.Text()

    service_type = fields.Selection([
        ("posting", "Đăng tin"),
        ("push", "Đẩy tin / VIP"),
        ("renew", "Gia hạn tin"),
        ("bundle", "Gói Combo"),
        ("inspection", "Dịch vụ kiểm định"),
    ], required=True)

    price = fields.Float("Đơn giá", required=True)

    duration_days = fields.Integer("Thời gian hiệu lực (ngày)")

    is_default = fields.Boolean("Gói mặc định?")
    is_active = fields.Boolean(default=True)

    sequence = fields.Integer(default=10)

    push_top = fields.Boolean("Đẩy lên đầu")
    vip_badge = fields.Boolean("Gắn nhãn VIP")
    highlight = fields.Boolean("Bôi màu nổi bật")
    homepage_slot = fields.Boolean("Hiển thị ngoài trang chủ")

    is_bundle = fields.Boolean("Là gói combo?")

    bundle_posting_qty = fields.Integer(default=0)
    bundle_push_qty = fields.Integer(default=0)
    bundle_renew_qty = fields.Integer(default=0)

    def get_default_package(self, service_type):
        return self.search([
            ("service_type", "=", service_type),
            ("is_default", "=", True),
            ("is_active", "=", True)
        ], limit=1)
