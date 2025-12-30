# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DumucUserRoleBinding(models.Model):
    _name = "dumuc.user.role.binding"
    _description = "DuMuc User Role Binding"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "write_date desc"

    user_id = fields.Many2one(
        "res.users",
        string="Người dùng",
        required=True,
        tracking=True,
        ondelete="cascade",
    )

    module = fields.Selection(
        [
            ("market", "Marketplace"),
            # các module khác sẽ enable ở phase sau
            # ("recruit", "Recruit"),
            # ("edu", "Education"),
        ],
        string="Module",
        required=True,
        default="market",
        tracking=True,
        readonly=True,
    )

    role = fields.Selection(
        [
            ("seller", "Người bán cá nhân"),
            ("salon", "Salon / Garage"),
            ("evaluator", "Đánh giá viên"),
            ("moderator", "Kiểm duyệt viên"),
            ("admin", "Quản trị Marketplace"),
        ],
        string="Vai trò Marketplace",
        required=True,
        tracking=True,
    )

    status = fields.Selection(
        [
            ("active", "Hoạt động"),
            ("suspended", "Tạm khóa"),
            ("banned", "Cấm vĩnh viễn"),
        ],
        string="Trạng thái",
        default="active",
        tracking=True,
        required=True,
    )

    assigned_by = fields.Many2one(
        "res.users",
        string="Người gán quyền",
        default=lambda self: self.env.user,
        readonly=True,
    )

    note = fields.Text("Ghi chú nội bộ")

    _sql_constraints = [
        (
            "unique_user_module",
            "unique(user_id,module)",
            "Mỗi người dùng chỉ được phép có một vai trò trong mỗi module.",
        )
    ]

    @api.constrains("module", "role")
    def _check_role_scope(self):
        for rec in self:
            if rec.module == "market" and rec.role not in [
                "seller", "salon", "evaluator", "moderator", "admin"
            ]:
                raise ValidationError(_("Vai trò không hợp lệ đối với module Marketplace."))
