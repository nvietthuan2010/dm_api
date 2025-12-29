from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DumucCreditPackage(models.Model):
    _name = "dumuc.credit.package"
    _description = "Credit Topup Package"
    _order = "price_vnd asc"

    # ==================================================
    # IDENTITY
    # ==================================================

    code = fields.Char(
        string="Mã gói",
        required=True,
        index=True,
        help="Mã định danh nội bộ, không thay đổi sau khi sử dụng"
    )

    name = fields.Char(
        string="Tên gói",
        required=True
    )

    # ==================================================
    # PRICING
    # ==================================================

    price_vnd = fields.Integer(
        string="Giá tiền (VND)",
        required=True
    )

    credit_amount = fields.Integer(
        string="Credit gốc",
        required=True
    )

    bonus_credit = fields.Integer(
        string="Credit thưởng",
        default=0
    )

    # ==================================================
    # DISPLAY
    # ==================================================

    description = fields.Text(string="Mô tả gói")

    is_active = fields.Boolean(
        string="Đang bán",
        default=True
    )

    # ==================================================
    # COMPUTED (UI)
    # ==================================================

    total_credit = fields.Integer(
        string="Tổng Credit",
        compute="_compute_total_credit"
    )

    price_per_credit = fields.Integer(
        string="Giá / Credit (VND)",
        compute="_compute_price_per_credit"
    )

    # ==================================================
    # COMPUTE
    # ==================================================

    @api.depends("credit_amount", "bonus_credit")
    def _compute_total_credit(self):
        for rec in self:
            rec.total_credit = rec.credit_amount + rec.bonus_credit

    @api.depends("price_vnd", "credit_amount", "bonus_credit")
    def _compute_price_per_credit(self):
        for rec in self:
            total = rec.credit_amount + rec.bonus_credit
            rec.price_per_credit = int(rec.price_vnd / total) if total else 0

    # ==================================================
    # CONSTRAINTS
    # ==================================================

    _sql_constraints = [
        ("uniq_credit_package_code", "unique(code)", "Mã gói phải là duy nhất"),
    ]

    @api.constrains("price_vnd", "credit_amount")
    def _check_positive_values(self):
        for rec in self:
            if rec.price_vnd <= 0:
                raise ValidationError("Giá tiền phải lớn hơn 0")
            if rec.credit_amount <= 0:
                raise ValidationError("Credit phải lớn hơn 0")
