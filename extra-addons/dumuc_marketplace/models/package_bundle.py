from odoo import models, fields

class DumucPackageBundle(models.Model):
    _name = "dumuc.package.bundle"
    _description = "Gói Bundle được cấp cho Seller"
    _order = "id desc"

    partner_id = fields.Many2one("res.partner", required=True)

    package_id = fields.Many2one(
        "dumuc.service.package",
        required=True,
        domain=[("service_type", "=", "bundle")]
    )

    # quota còn lại
    remaining_push = fields.Integer(default=0)
    remaining_renew = fields.Integer(default=0)

    # snapshot giá bundle
    purchase_price = fields.Float()

    # lúc mua bundle
    transaction_id = fields.Many2one("dumuc.transaction")

    is_active = fields.Boolean(default=True)


    def _get_available_bundle(self, partner, action_type):

        domain = [
            ("partner_id", "=", partner.id),
            ("is_active", "=", True)
        ]

        if action_type == "bundle_push":
            domain.append(("remaining_push", ">", 0))

        if action_type == "bundle_renew":
            domain.append(("remaining_renew", ">", 0))

        return self.env["dumuc.package.bundle"].search(domain, limit=1)
