from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DumucCompany(models.Model):
    _name = "dumuc.company"
    _description = "Recruitment Company"
    _rec_name = "name"

    # ==================================================
    # IDENTITY
    # ==================================================

    name = fields.Char(
        string="Tên công ty",
        required=True
    )

    user_id = fields.Many2one(
        "res.users",
        string="Tài khoản chủ",
        required=True,
        ondelete="cascade",
        index=True
    )

    # ==================================================
    # CONTACT
    # ==================================================

    phone = fields.Char(string="Số điện thoại")
    email = fields.Char(string="Email")
    address = fields.Char(string="Địa chỉ")

    # ==================================================
    # STATUS
    # ==================================================

    is_verified = fields.Boolean(
        string="Đã xác thực",
        default=False
    )

    is_active = fields.Boolean(default=True)

    # ==================================================
    # RELATIONS
    # ==================================================

    job_ids = fields.One2many(
        "dumuc.job",
        "company_id",
        string="Tin tuyển dụng"
    )

    wallet_balance = fields.Integer(
        string="Số dư ví",
        compute="_compute_wallet_balance",
        readonly=True
    )

    # ==================================================
    # COMPUTE METHODS
    def _compute_wallet_balance(self):
        for company in self:
            wallet = company.get_wallet()
            company.wallet_balance = wallet.balance
    # ==================================================
    # WALLET HELPERS (CORE)
    # ==================================================

    def get_wallet(self):
        """Lấy ví hiện tại hoặc tạo mới nếu chưa có"""
        self.ensure_one()
        wallet = self.env["dumuc.wallet"].search(
            [("company_id", "=", self.id)],
            limit=1
        )
        if not wallet:
            wallet = self.env["dumuc.wallet"].create({
                "company_id": self.id,
            })
        return wallet

    def check_credit(self, amount):
        """Kiểm tra đủ credit"""
        self.ensure_one()
        wallet = self.get_wallet()
        return wallet.balance >= amount

    def spend_credit(self, amount, action, ref=None, note=None):
        """
        Trừ credit theo hành động nghiệp vụ
        - amount: số credit
        - action: mã dịch vụ (POST_JOB, VIEW_SEEKER, ...)
        - ref: record liên quan (job, seeker...)
        """
        self.ensure_one()
        wallet = self.get_wallet()

        if wallet.balance < amount:
            raise ValidationError("Không đủ credit để thực hiện hành động này")

        wallet.spend(
            amount=amount,
            action=action,
            ref=ref,
            note=note
        )
        return True

    def topup_credit(self, amount, note=None):
        """Nạp credit"""
        self.ensure_one()
        wallet = self.get_wallet()
        wallet.topup(amount, note=note)
        return True


class UnlockPolicy(models.TransientModel):
    _name = "dumuc.unlock.policy"
    _description = "Unlock Control Policy"

    daily_unlock_limit = fields.Integer(
        string="Số hồ sơ tối đa mỗi ngày",
        default=20
    )

    allow_expired_job_unlock = fields.Boolean(
        string="Cho phép unlock khi job hết hạn",
        default=False
    )
