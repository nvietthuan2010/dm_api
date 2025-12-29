from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DumucWalletTransaction(models.Model):
    _name = "dumuc.wallet.tx"
    _description = "Wallet Transaction / Action Log"
    _order = "create_date desc"

    # ==================================================
    # RELATION
    # ==================================================

    company_id = fields.Many2one(
        "dumuc.company",
        string="Company",
        required=True,
        ondelete="cascade",
        index=True
    )

    wallet_id = fields.Many2one(
        "dumuc.wallet",
        string="Wallet",
        required=True,
        ondelete="cascade",
        index=True
    )

    # ==================================================
    # ACTION
    # ==================================================

    action = fields.Selection(
        [
            ("TOPUP", "Topup Credit"),
            ("POST_JOB", "Post Job"),
            ("VIEW_SEEKER", "Unlock Seeker"),
            ("POST_GIG", "Post Gig"),
            ("SYSTEM_ADJUST", "System Adjustment"),
        ],
        string="Action",
        required=True,
        index=True
    )

    # ==================================================
    # TARGET
    # ==================================================

    target_model = fields.Char(
        string="Target Model",
        help="Model name of target, e.g. dumuc.job.seeker"
    )

    target_id = fields.Integer(
        string="Target ID",
        help="ID of target record"
    )

    # ==================================================
    # AMOUNT
    # ==================================================

    amount = fields.Integer(
        string="Credit Change",
        required=True,
        help="Số credit cộng (+) hoặc trừ (-)"
    )

    balance_after = fields.Integer(
        string="Balance After",
        help="Snapshot số dư sau giao dịch"
    )

    # ==================================================
    # META
    # ==================================================

    note = fields.Char(
        string="Ghi chú"
    )

    is_system = fields.Boolean(
        string="Giao dịch hệ thống",
        default=False
    )

    # ==================================================
    # TIME
    # ==================================================

    create_date = fields.Datetime(
        string="Thời điểm",
        readonly=True
    )

    # ==================================================
    # CORE FACTORY METHOD
    # ==================================================

    @api.model
    def create_tx(self, wallet, action, amount, target_model=None, target_id=None, note=None, is_system=False):
        """
        Tạo transaction CHUẨN – DUY NHẤT
        Wallet phải gọi method này, controller không được gọi trực tiếp
        """

        if not wallet:
            raise ValidationError("Wallet không hợp lệ")

        if amount == 0:
            raise ValidationError("Transaction amount không được bằng 0")

        tx = self.create({
            "company_id": wallet.company_id.id,
            "wallet_id": wallet.id,
            "action": action,
            "target_model": target_model,
            "target_id": target_id,
            "amount": amount,
            "balance_after": wallet.balance,
            "note": note,
            "is_system": is_system,
        })

        return tx

    # ==================================================
    # SAFETY
    # ==================================================

    def unlink(self):
        raise ValidationError("Không được phép xóa lịch sử giao dịch")

    def write(self, vals):
        raise ValidationError("Không được phép sửa lịch sử giao dịch")
