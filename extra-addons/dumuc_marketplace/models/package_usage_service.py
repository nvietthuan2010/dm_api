from odoo import models

class PackageUsageService(models.AbstractModel):
    _name = "dumuc.package.usage.service"
    _description = "Ghi nhận lịch sử sử dụng gói DuMuc"

    def log_usage(self, partner, listing, package, action_type, price, transaction=None, note=None):

        return self.env["dumuc.package.usage"].sudo().create({
            "partner_id": partner.id,
            "listing_id": listing.id,
            "package_id": package.id,
            "action_type": action_type,
            "applied_price": price,
            "transaction_id": transaction.id if transaction else False,
            "note": note,
            "source": "api",   # mặc định FE gọi API
        })
