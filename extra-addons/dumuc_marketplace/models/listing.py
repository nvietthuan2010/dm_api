# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

def _is_admin(self):
    return self.env.user.has_group('dumuc_marketplace.group_dumuc_admin')

def _is_moderator(self):
    return self.env.user.has_group('dumuc_marketplace.group_dumuc_moderator')

def _can_moderate(self):
    return self._is_admin() or self._is_moderator()


class DumucListing(models.Model):
    _name = "dumuc.listing"
    _description = "Tin đăng DuMuc"
    _inherit = ['mail.thread']
    _order = "priority_score desc, posted_at desc"

    name = fields.Char("Tiêu đề", required=True)
    partner_id = fields.Many2one('res.partner', string='Người bán', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Tiền tệ')
    brand_id = fields.Many2one('dumuc.vehicle.brand', string='Hãng')
    model_id = fields.Many2one('dumuc.vehicle.model', string='Dòng')
    year = fields.Integer("Năm sản xuất")
    mileage = fields.Integer("Số km")
    description = fields.Text("Mô tả")
    cover_image = fields.Binary("Ảnh đại diện")
    image_ids = fields.One2many('dumuc.listing.image', 'listing_id', string='Ảnh chi tiết')
    posted_at = fields.Datetime("Ngày đăng", readonly=True)
    expire_at = fields.Datetime("Ngày hết hạn", readonly=False)

    # moderation
    moderation_admin_id = fields.Many2one('res.users', string='Người duyệt', readonly=True)
    moderation_time = fields.Datetime("Thời gian duyệt", readonly=True)
    reject_reason_id = fields.Many2one('dumuc.listing.reject.reason', string="Lý do từ chối")
    moderation_note = fields.Text("Ghi chú kiểm duyệt")
    is_blocked = fields.Boolean("Bị chặn", default=False)

    # workflow
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('pending', 'Chờ duyệt'),
        ('active', 'Đang hiển thị'),
        ('rejected', 'Bị từ chối'),
        ('sold', 'Đã bán'),
        ('suspended', 'Bị tạm khoá'),
        ('expired', 'Hết hạn'),
    ], string='Trạng thái', default='draft', tracking=True)

    # history
    history_ids = fields.One2many('dumuc.listing.history', 'listing_id', string='Lịch sử xử lý')

    # priority / boost
    priority_score = fields.Integer("Điểm ưu tiên", index=True, default=0)
    is_featured = fields.Boolean("Tin nổi bật", default=False)
    featured_until = fields.Datetime("Hết hạn nổi bật")

    # free quota
    is_free_quota = fields.Boolean("Miễn phí đăng (quota)", default=False)
    posted_count = fields.Integer("Số lần đăng", default=0)
    
    

    # links
    inspection_result_id = fields.Many2one('dumuc.inspection.result', string='Báo cáo kiểm định')
    
    #package
    posting_package_id = fields.Many2one('dumuc.service.package', string='Gói đăng tin', readonly=True)
    push_package_id = fields.Many2one("dumuc.service.package", string='Gói Đẩy tin', readonly=True)
    renew_package_id = fields.Many2one("dumuc.service.package", string='Gói Gia hạn tin', readonly=True)
    posting_price = fields.Float("Giá đăng tin", readonly=True)
    push_price = fields.Float("Giá đẩy tin", readonly=True)
    renew_price = fields.Float("Giá gia hạn tin", readonly=True)

    last_push_at = fields.Datetime("Thời điểm đẩy gần nhất")
    push_count = fields.Integer("Số lần đã đẩy", default=0)

    last_renew_at = fields.Datetime("Thời điểm gia hạn gần nhất")
    renew_count = fields.Integer("Số lần gia hạn", default=0)

    #log
    usage_log_ids = fields.One2many(
        "dumuc.package.usage",
        "listing_id",
        string="Lịch sử sử dụng gói"
    )



    # computed helpers
    @api.model
    def create(self, vals):
        rec = super(DumucListing, self).create(vals)
        rec.posted_at = fields.Datetime.now()
        return rec
    
    def _get_available_push_bundle(self):
        return self.env["dumuc.package.bundle"].search([
            ("partner_id", "=", self.partner_id.id),
            ("is_active", "=", True),
            ("remaining_push", ">", 0)
        ], limit=1)
    
    def _apply_push_effect(self):
        self.is_featured = True
        self.featured_until = fields.Datetime.now() + fields.Date.to_relative_delta(days=3)
        self.last_push_at = fields.Datetime.now()
        self.push_count += 1
        self._compute_priority_score()

        self._log_history(
            action="push",
            user=self.env.user,
            note="Đẩy tin thành công"
        )

    def _get_available_renew_bundle(self):
        return self.env["dumuc.package.bundle"].search([
            ("partner_id", "=", self.partner_id.id),
            ("is_active", "=", True),
            ("remaining_renew", ">", 0)
        ], limit=1)
    

    def _get_available_renew_bundle(self):
        return self.env["dumuc.package.bundle"].search([
            ("partner_id", "=", self.partner_id.id),
            ("is_active", "=", True),
            ("remaining_renew", ">", 0)
        ], limit=1)



    def _guard(self, allowed_states, action_name):
        for rec in self:
            if rec.state not in allowed_states:
                rec._log_history(
                    action="blocked_action",
                    user=self.env.user,
                    note=f"Từ chối thao tác [{action_name}] do trạng thái không hợp lệ: {rec.state}"
                )
                raise UserError(_(
                    "Không thể thực hiện hành động [%s] khi tin đang ở trạng thái: %s"
                ) % (action_name, rec.state.upper()))

    # =========================================================
    # SELLER ACTIONS
    # =========================================================
    def action_submit_for_review(self):

        self._guard(
            allowed_states=("draft", "rejected"),
            action_name="Gửi kiểm duyệt"
        )

        max_free = int(self.env['ir.config_parameter'].sudo().get_param(
            'dumuc.max_free_posts', 5))

        partner = self.partner_id

        if partner and partner.dumuc_free_post_used >= max_free:
            raise UserError(_("Đã hết lượt đăng miễn phí. Vui lòng mua gói dịch vụ."))

        if partner and partner.dumuc_free_post_used < max_free:
            self.is_free_quota = True
            partner.sudo().dumuc_free_post_used += 1

        self.state = 'pending'

        self._log_history(
            'submit_for_review',
            partner.user_id or self.env.user,
            note="Người bán gửi kiểm duyệt"
        )

    def action_mark_as_sold(self):

        self._guard(
            allowed_states=("active",),
            action_name="Đánh dấu đã bán"
        )

        self.state = 'sold'

        self._log_history(
            'mark_as_sold',
            self.env.user,
            note="Tin đã bán"
        )

    # =========================================================
    # ADMIN ACTIONS
    # =========================================================
    def action_approve(self):

        self._guard(("pending",), "Duyệt tin")

        self.state = 'active'
        self.moderation_admin_id = self.env.user.id
        self.moderation_time = fields.Datetime.now()

        self._compute_priority_score()

        self._log_history("approve", self.env.user, note="Duyệt tin")

    def action_reject(self, reason_id=None, note=None):

        self._guard(("pending", "active"), "Từ chối tin")

        self.state = 'rejected'
        self.reject_reason_id = reason_id.id if reason_id else False
        self.moderation_admin_id = self.env.user.id
        self.moderation_time = fields.Datetime.now()

        if note:
            self.moderation_note = note

        self._log_history("reject", self.env.user, note or "Từ chối tin")

    def action_suspend(self, reason=None):

        self._guard(("active", "pending"), "Khoá tin")

        self.state = 'suspended'
        self.is_blocked = True

        self._log_history(
            "suspend",
            self.env.user,
            note=reason or "Khoá tin do vi phạm"
        )

    def action_restore(self):

        self._guard(("suspended",), "Khôi phục tin")

        self.state = 'active'
        self.is_blocked = False

        self._log_history("restore", self.env.user, note="Khôi phục tin")

    # =========================================================
    # PRIORITY ENGINE
    # =========================================================
    def _compute_priority_score(self):
        for rec in self:

            score = 0

            if rec.is_featured and rec.featured_until and rec.featured_until > fields.Datetime.now():
                score += 10000

            if rec.posted_at:
                days = (fields.Datetime.now() - rec.posted_at).days
                score += max(0, 100 - days)

            rec.priority_score = score

    # =========================================================
    # HISTORY LOGGING
    # =========================================================
    def _log_history(self, action, user, note=''):
        self.env['dumuc.listing.history'].create({
            'listing_id': self.id,
            'action': action,
            'admin_id': user.id if user else False,
            'note': note,
        })


    def action_push(self):

        self._guard(("active",), "Đẩy tin (Push)")

        partner = self.partner_id
        Wallet = self.env["dumuc.wallet.service"]
        Usage = self.env["dumuc.package.usage"]

        # =====================================================
        # 1️⃣ CASE FREE QUOTA (CHỈ CHO LẦN ĐẦU)
        # =====================================================
        if self.is_free_quota and self.push_count == 0:

            self.push_price = 0
            self._apply_push_effect()

            Usage.create({
                "partner_id": partner.id,
                "listing_id": self.id,
                "package_id": False,
                "action_type": "push",
                "applied_price": 0,
                "transaction_id": False,
                "source": "api",
                "note": "Đẩy tin miễn phí (quota)",
            })

            return True

        # =====================================================
        # 2️⃣ ƯU TIÊN DÙNG BUNDLE (KHÔNG TRỪ VÍ)
        # =====================================================
        bundle = self._get_available_push_bundle()

        if bundle:
            bundle.remaining_push -= 1

            self.push_price = 0
            self._apply_push_effect()

            Usage.create({
                "partner_id": partner.id,
                "listing_id": self.id,
                "package_id": bundle.package_id.id,
                "action_type": "bundle_push",
                "applied_price": 0,
                "transaction_id": bundle.transaction_id.id,
                "source": "api",
                "note": "Sử dụng lượt push từ bundle",
            })

            return True

        # =====================================================
        # 3️⃣ KHÔNG CÓ BUNDLE → MUA PUSH (TRỪ VÍ)
        # =====================================================
        package = self.env["dumuc.service.package"].search([
            ("service_type", "=", "push"),
            ("is_active", "=", True)
        ], limit=1)

        if not package:
            raise UserError("Chưa cấu hình gói đẩy tin.")

        tx = Wallet.create_wallet_transaction(
            partner=partner,
            amount=-package.price,
            tx_type="push",
            ref=self,
            note="Mua dịch vụ đẩy tin"
        )

        self.push_price = package.price
        self._apply_push_effect()

        Usage.create({
            "partner_id": partner.id,
            "listing_id": self.id,
            "package_id": package.id,
            "action_type": "push",
            "applied_price": package.price,
            "transaction_id": tx.id,
            "source": "api",
            "note": "Mua đẩy tin / VIP",
        })

        return True


    def action_renew(self):

        self._guard(
            allowed_states=("active", "expired"),
            action_name="Gia hạn tin (Renew)"
        )

        partner = self.partner_id

        Wallet = self.env["dumuc.wallet.service"]
        Usage = self.env["dumuc.package.usage"]

        # =====================================================
        # 1️⃣ ƯU TIÊN DÙNG BUNDLE RENEW (KHÔNG TRỪ VÍ)
        # =====================================================
        bundle = self._get_available_renew_bundle()

        if bundle:

            bundle.remaining_renew -= 1

            self.renew_price = 0
            self._apply_renew_effect()

            Usage.create({
                "partner_id": partner.id,
                "listing_id": self.id,
                "package_id": bundle.package_id.id,
                "action_type": "bundle_renew",
                "applied_price": 0,
                "transaction_id": bundle.transaction_id.id,
                "source": "api",
                "note": "Gia hạn tin bằng Bundle",
            })

            return True

        # =====================================================
        # 2️⃣ KHÔNG CÓ BUNDLE → MUA GÓI RENEW (TRỪ VÍ)
        # =====================================================
        package = self.env["dumuc.service.package"].search([
            ("service_type", "=", "renew"),
            ("is_active", "=", True)
        ], limit=1)

        if not package:
            raise UserError("Chưa cấu hình gói gia hạn tin.")

        if partner.dumuc_wallet_balance < package.price:
            raise UserError("Số dư ví không đủ để gia hạn.")

        tx = Wallet.create_wallet_transaction(
            partner=partner,
            amount=-package.price,
            tx_type="renew",
            ref=self,
            note="Mua dịch vụ gia hạn tin"
        )

        self.renew_price = package.price
        self._apply_renew_effect()

        Usage.create({
            "partner_id": partner.id,
            "listing_id": self.id,
            "package_id": package.id,
            "action_type": "renew",
            "applied_price": package.price,
            "transaction_id": tx.id,
            "source": "api",
            "note": "Gia hạn tin trả phí",
        })

        return True



    def action_use_bundle_push(self):

        Bundle = self.env["dumuc.package.bundle"]
        Usage  = self.env["dumuc.package.usage.service"]

        bundle = Bundle._get_available_bundle(
            self.partner_id,
            action_type="bundle_push"
        )

        if not bundle:
            raise UserError("Bạn không còn lượt Push trong Bundle.")

        # trừ quota
        bundle.remaining_push -= 1

        # ghi log sử dụng
        Usage.log_usage(
            partner=self.partner_id,
            listing=self,
            package=bundle.package_id,
            action_type="bundle_push",
            price=0,
            transaction=False,
            note="Sử dụng lượt push từ bundle"
        )

        # áp dụng hiệu lực push
        self.is_featured = True
        self.featured_until = fields.Datetime.now() + timedelta(days=3)
        self._compute_priority_score()


    def action_buy_bundle(self, package):

        wallet = self.env["dumuc.wallet.service"]

        tx = wallet.create_wallet_transaction(
            partner=self.partner_id,
            amount=-package.price,
            tx_type="bundle",
            ref=self,
            note="Mua gói Bundle"
        )

        self.env["dumuc.package.bundle"].create({
            "partner_id": self.partner_id.id,
            "package_id": package.id,
            "purchase_price": package.price,
            "remaining_push": package.bundle_push_qty,
            "remaining_renew": package.bundle_renew_qty,
            "transaction_id": tx.id,
        })