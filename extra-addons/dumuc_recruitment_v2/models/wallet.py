from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class DumucWallet(models.Model):
    _name = "dumuc.wallet"
    _description = "Company Credit Wallet"
    _order = "id desc"

    company_id = fields.Many2one(
        "dumuc.company",
        string="Company",
        required=True,
        ondelete="cascade",
        index=True
    )

    balance = fields.Integer(
        string="Số dư Credit",
        default=0,
        help="Số credit hiện tại có thể sử dụng"
    )

    is_active = fields.Boolean(string="Wallet đang hoạt động", default=True)

    create_date = fields.Datetime(readonly=True)
    write_date = fields.Datetime(readonly=True)

    _sql_constraints = [
        (
            "unique_company_wallet",
            "unique(company_id)",
            "Mỗi company chỉ có một wallet duy nhất."
        )
    ]


    @api.constrains("balance")
    def _check_balance_not_negative(self):
        for wallet in self:
            if wallet.balance < 0:
                raise ValidationError("Số dư credit không thể âm")

    # ==================================================
    # CORE BUSINESS METHODS
    # ==================================================

    def _ensure_active(self):
        """Đảm bảo wallet còn hoạt động"""
        self.ensure_one()
        if not self.is_active:
            raise UserError("Wallet đang bị khóa")

    def has_enough(self, amount):
        """Kiểm tra đủ credit không"""
        self.ensure_one()
        return self.balance >= amount

    def topup(self, amount, note=None, is_system=False):
        """
        Nạp credit vào wallet
        """
        self.ensure_one()
        self._ensure_active()

        if amount <= 0:
            raise UserError("Số credit nạp phải lớn hơn 0")

        self.balance += amount

        self.env["dumuc.wallet.tx"].create_tx(
            wallet=self,
            action="TOPUP",
            amount=amount,
            note=note or "Topup credit",
            is_system=is_system
        )

        return self.balance

    def spend(self, amount, action, target_model=None, target_id=None, note=None):
        """
        Trừ credit cho một hành động nghiệp vụ
        """
        self.ensure_one()
        self._ensure_active()

        if amount <= 0:
            raise UserError("Số credit trừ phải lớn hơn 0")

        if not self.has_enough(amount):
            raise UserError("Không đủ credit để thực hiện hành động")

        self.balance -= amount

        self.env["dumuc.wallet.tx"].create_tx(
            wallet=self,
            action=action,
            amount=-amount,
            target_model=target_model,
            target_id=target_id,
            note=note
        )

        return self.balance
    

class UnlockLog(models.Model):
    _name = "dumuc.unlock.log"
    _description = "Seeker Unlock Log"

    company_id = fields.Many2one("dumuc.company", required=True)
    seeker_id = fields.Many2one("dumuc.seeker", required=True)
    application_id = fields.Many2one("dumuc.application", required=True)

    unlock_date = fields.Datetime(default=fields.Datetime.now)
    
    is_rollback = fields.Boolean(
        string="Is Rollback",default=False)

    refund_status = fields.Selection([
        ("none", "No Refund"),
        ("requested", "Requested"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ], default="none")

    refund_reason = fields.Text()
    refund_processed_at = fields.Datetime()
    is_auto_processed = fields.Boolean(default=False)

    risk_score = fields.Integer(
        string="Refund Risk Score",
        default=0
    )