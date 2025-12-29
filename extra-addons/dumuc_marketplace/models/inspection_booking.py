# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class InspectionBooking(models.Model):
    _name = "dumuc.inspection.booking"
    _description = "Đơn đặt dịch vụ kiểm định DuMuc"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(
        "Mã booking",
        required=True,
        copy=False,
        default="New",
        tracking=True,
    )

    # Người yêu cầu kiểm định
    customer_id = fields.Many2one(
        "res.partner",
        string="Khách hàng",
        required=True,
        tracking=True,
    )

    # Có thể gắn với listing trên sàn
    listing_id = fields.Many2one(
        "dumuc.listing",
        string="Tin đăng",
        help="Nếu khách yêu cầu kiểm định xe đang đăng trên DuMuc.",
    )

    # Hoặc xe ngoài
    external_vehicle_info = fields.Char(
        "Thông tin xe (ngoài sàn)",
        help="Mô tả nhanh xe không thuộc tin đăng trên DuMuc.",
    )

    # Gói dịch vụ
    package_id = fields.Many2one(
        "dumuc.service.package",
        string="Gói dịch vụ",
        domain=[("package_type", "=", "inspection")],
    )

    # Đánh giá viên phụ trách
    evaluator_id = fields.Many2one(
        "res.partner",
        string="Đánh giá viên",
        domain=[("dumuc_is_evaluator", "=", True)],
        tracking=True,
    )

    scheduled_datetime = fields.Datetime(
        "Thời gian hẹn",
        tracking=True,
    )
    location_address = fields.Char("Địa điểm kiểm định")

    state = fields.Selection([
        ("draft", "Nháp"),
        ("pending", "Chờ xử lý"),
        ("assigned", "Đã gán thợ"),
        ("confirmed", "Đã xác nhận"),
        ("in_progress", "Đang kiểm định"),
        ("done", "Hoàn tất"),
        ("cancelled", "Đã hủy"),
    ], string="Trạng thái", default="pending", tracking=True)

    result_id = fields.One2many(
        "dumuc.inspection.result",
        "booking_id",
        string="Kết quả kiểm định",
    )

    template_id = fields.Many2one(
        "dumuc.inspection.template",
        string="Bộ kiểm định"
    )

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            seq = self.env["ir.sequence"].next_by_code("dumuc.inspection.booking") or "New"
            vals["name"] = seq
        return super().create(vals)

    
    
    def action_evaluator_start(self):
        if self.state != 'confirmed':
            raise UserError(_("Booking chưa sẵn sàng"))

        inspection = self.env['dumuc.inspection.result'].create({
            'booking_id': self.id,
            'evaluator_id': self.evaluator_id.id,
            'template_id': self.template_id.id,
            'state': 'in_progress',
        })

        self.state = 'in_progress'
        return inspection

    def action_evaluator_finish(self):
        self.state = 'done'
        self.booking_id.state = 'done'

        # gắn tích xanh cho listing
        self.booking_id.listing_id.inspection_result_id = self.id


