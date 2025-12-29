from odoo import models, fields

class DumucPackageUsage(models.Model):
    _name = "dumuc.package.usage"
    _description = "Lịch sử sử dụng gói dịch vụ DuMuc"
    _order = "id desc"

    partner_id = fields.Many2one("res.partner", string="Người dùng", required=True)

    listing_id = fields.Many2one("dumuc.listing", string="Tin đăng", required=True)

    package_id = fields.Many2one("dumuc.service.package", string="Gói dịch vụ", required=True)

    action_type = fields.Selection([
        ("posting", "Đăng tin"),
        ("push", "Đẩy tin / VIP"),
        ("renew", "Gia hạn tin"),
        ("bundle_push", "Sử dụng Push từ Bundle"),
        ("bundle_renew", "Sử dụng Renew từ Bundle"),
    ], string="Loại hành động", required=True)

    # snapshot giá tại thời điểm sử dụng
    applied_price = fields.Float("Giá áp dụng", required=True)

    # liên kết ledger transaction
    transaction_id = fields.Many2one("dumuc.transaction", string="Giao dịch ví")

    # nguồn kích hoạt
    source = fields.Selection([
        ("seller_portal", "Seller Portal"),
        ("api", "External API"),
        ("admin", "Admin"),
        ("system", "System Job"),
    ], default="api", string="Nguồn phát sinh")

    note = fields.Char("Ghi chú")
    create_date = fields.Datetime("Thời điểm thực hiện", readonly=True)
