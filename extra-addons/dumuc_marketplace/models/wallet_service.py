from odoo import models, _, api
from odoo.exceptions import UserError

class WalletService(models.AbstractModel):
    _name = "dumuc.wallet.service"
    _description = "Wallet Accounting Service"

    @api.model
    def create_wallet_transaction(self, partner, amount, tx_type, ref=None, note=None):
        if not partner:
            raise UserError(_("Partner không hợp lệ."))

        balance_now = partner.wallet_balance
        balance_after = balance_now + amount

        if balance_after < 0:
            raise UserError(_("Số dư ví không đủ."))

        vals = {
            "partner_id": partner.id,
            "amount": amount,
            "balance_before": balance_now,
            "balance_after": balance_after,
            "type": tx_type,
            "reference_model": ref._name if ref else False,
            "reference_id": ref.id if ref else False,
            "note": note,
        }

        return self.env["dumuc.transaction"].sudo().create(vals)
