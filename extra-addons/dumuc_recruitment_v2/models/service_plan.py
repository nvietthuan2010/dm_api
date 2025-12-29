from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DumucServicePlan(models.Model):
    _name = "dumuc.service.plan"
    _description = "Service Pricing Plan"
    _order = "credit_cost asc"

    # ==================================================
    # IDENTITY
    # ==================================================

    code = fields.Char(
        string="Mã dịch vụ",
        required=True,
        index=True,
        help="Mã nội bộ dùng cho logic hệ thống (VD: POST_JOB)"
    )

    name = fields.Char(
        string="Tên dịch vụ",
        required=True
    )

    # ==================================================
    # PRICING RULE
    # ==================================================

    credit_cost = fields.Integer(
        string="Chi phí (Credits)",
        required=True,
        help="Số credits bị trừ mỗi lần sử dụng dịch vụ"
    )

    # ==================================================
    # DISPLAY
    # ==================================================

    description = fields.Text(
        string="Mô tả"
    )

    is_active = fields.Boolean(
        string="Đang áp dụng",
        default=True
    )

    # ==================================================
    # CONSTRAINTS
    # ==================================================

    _sql_constraints = [
        ("uniq_service_plan_code", "unique(code)", "Mã dịch vụ phải là duy nhất"),
    ]

    @api.constrains("credit_cost")
    def _check_credit_cost(self):
        for rec in self:
            if rec.credit_cost < 0:
                raise ValidationError("Chi phí credits không được âm")
