from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CreditWallet(models.Model):
    _name = "dumuc.credit.wallet"
    _description = "Ví tín dụng Garage"
    _rec_name = "garage_id"

    garage_id = fields.Many2one("dumuc.garage.profile", string="Garage", required=True)
    balance = fields.Integer(string="Số dư hiện tại", default=0)

    transaction_ids = fields.One2many(
        "dumuc.credit.transaction", "wallet_id", string="Giao dịch"
    )

    @api.model
    def get_wallet(self, garage):
        wallet = self.search([('garage_id', '=', garage.id)], limit=1)
        if not wallet:
            wallet = self.create({'garage_id': garage.id, 'balance': 0})
        return wallet

    def deduct(self, amount, ref=None, ref_type=None):
        """Trừ tín dụng. Kiểm tra đủ số dư. Ghi log."""
        self.ensure_one()
        if amount <= 0:
            return

        if self.balance < amount:
            raise UserError(_("Không đủ tín dụng để thực hiện thao tác này"))

        before = self.balance
        after = before - amount

        self.balance = after

        self.env["dumuc.credit.transaction"].create({
            "wallet_id": self.id,
            "amount": amount,
            "type": "debit",
            "balance_before": before,
            "balance_after": after,
            "reference": ref,
            "reference_type": ref_type,
        })

    def add(self, amount, package=None):
        """Cộng tín dụng khi mua gói"""
        self.ensure_one()
        before = self.balance
        after = before + amount

        self.balance = after

        self.env["dumuc.credit.transaction"].create({
            "wallet_id": self.id,
            "amount": amount,
            "type": "credit",
            "balance_before": before,
            "balance_after": after,
            "reference": package,
            "reference_type": "subscription",
        })
