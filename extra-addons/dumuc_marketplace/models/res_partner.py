from odoo import models, fields, api
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = "res.partner"

    # Loại tài khoản
    dumuc_user_type = fields.Selection([
        ("private", "Cá nhân"),
        ("salon", "Salon"),
        ("evaluator", "Đánh giá viên"),
        ("admin", "Admin"),
    ], string="Loại tài khoản DuMuc")

   

    # Tin free đã dùng
    dumuc_free_post_used = fields.Integer(
        string="Số tin miễn phí đã dùng",
        default=0,
    )

    # Salon profile
    dumuc_salon_name = fields.Char("Tên Salon")
    dumuc_salon_address = fields.Char("Địa chỉ Salon")
    dumuc_salon_business_license = fields.Char("Giấy phép kinh doanh")
    dumuc_salon_tax_code = fields.Char("Mã số thuế")
    dumuc_salon_contact_person = fields.Char("Người liên hệ")
    dumuc_salon_contact_email = fields.Char("Email liên hệ")
    dumuc_salon_verified = fields.Boolean("Salon đã xác thực?", default=False)

    # Evaluator profile
    dumuc_is_evaluator = fields.Boolean("Là Đánh giá viên?", default=False)
    dumuc_evaluator_level = fields.Selection([
        ("basic", "Basic"),
        ("pro", "Pro"),
        ("expert", "Expert"),
    ], string="Cấp Đánh giá viên")
    dumuc_evaluator_certifications = fields.Text("Chứng chỉ chuyên môn")
    dumuc_evaluator_average_rating = fields.Float("Điểm đánh giá trung bình", digits=(2, 2))
    dumuc_evaluator_total_checks = fields.Integer("Tổng số xe đã kiểm định", default=0)

    star_rating = fields.Selection([
        ('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')
    ], string="Xếp hạng", compute="_compute_star_rating")


    dumuc_inspection_result_ids = fields.One2many(
        "dumuc.inspection.result", "evaluator_id",
        string="Hồ sơ kiểm định"
    )

    dumuc_evaluator_review_ids = fields.One2many(
        "dumuc.evaluator.review", "evaluator_id",
        string="Đánh giá từ khách hàng"
    )

    dumuc_status = fields.Selection([
        ('active', 'Hoạt động'),
        ('suspended', 'Tạm khóa'),
        ('blocked', 'Khóa'),
    ], default='active', index=True)

    saved_listing_ids = fields.Many2many(
        'dumuc.listing',
        string="Tin đã lưu"
    )

    dumuc_wallet_balance = fields.Float(
        string="Số dư ví",
        compute="_compute_wallet_balance",
        store=False,
        readonly=True,
    )

    def _compute_wallet_balance(self):
        Tx = self.env["dumuc.transaction"].sudo()
        for partner in self:
            txs = Tx.search([("partner_id", "=", partner.id)])
            partner.dumuc_wallet_balance = sum(txs.mapped("amount"))

    def action_verify_salon(self):
        for rec in self:
            if not self.env.user.has_group('dumuc_marketplace.group_dumuc_admin'):
                raise UserError("Chỉ admin được xác thực salon")
            rec.dumuc_salon_verified = True


    @api.depends('dumuc_evaluator_average_rating')
    def _compute_star_rating(self):
        for user in self:
            # Làm tròn số để hiện sao (VD: 4.8 -> 5 sao)
            user.star_rating = str(int(round(user.dumuc_evaluator_average_rating or 0)))

    def _dumuc_recompute_evaluator_stats(self):
        """Cập nhật lại avg_rating & total_checks từ bảng đánh giá."""
        # Dùng sudo() để đảm bảo tính toán được hết dữ liệu ngay cả khi user hiện tại không có quyền đọc
        Review = self.env["dumuc.evaluator.review"].sudo()
        
        for user in self:
            if not user.is_evaluator: # Kiểm tra flag (dựa trên field bạn đã define trước đó)
                continue

            # 1. Tính tổng số lượt đánh giá (Tối ưu bằng search_count)
            domain = [("evaluator_id", "=", user.id)]
            total_checks = Review.search_count(domain)
            user.dumuc_evaluator_total_checks = total_checks

            # 2. Tính điểm trung bình (Chỉ lấy các review có chấm điểm > 0)
            # Lấy danh sách rating (String) về
            reviews = Review.search(domain)
            
            # Chuyển đổi String sang Int và lọc bỏ giá trị False/None
            # Lưu ý: rating là Selection nên giá trị là '1', '2'... cần ép kiểu int()
            scores = [int(r.rating) for r in reviews if r.rating and int(r.rating) > 0]
            
            if scores:
                # Tính trung bình cộng
                avg = sum(scores) / len(scores)
                user.dumuc_evaluator_average_rating = avg
            else:
                user.dumuc_evaluator_average_rating = 0.0
    
    
    def action_seller_topup(self, amount):
        self.ensure_one()

        self.dumuc_wallet_balance += amount

        self.env['dumuc.transaction'].create({
            'partner_id': self.id,
            'amount': amount,
            'type': 'recharge',
        })
    
    def action_seller_request_inspection(self, listing, evaluator=None):
        self.ensure_one()

        if listing.state != 'active':
            raise UserError(_("Chỉ có thể kiểm định tin đang hiển thị"))

        price = self.env.ref('dumuc_marketplace.package_inspection_basic').price

        if self.dumuc_wallet_balance < price:
            raise UserError(_("WALLET_NOT_ENOUGH"))

        # Trừ ví
        self.dumuc_wallet_balance -= price

        booking = self.env['dumuc.inspection.booking'].create({
            'listing_id': listing.id,
            'requester_id': self.id,
            'evaluator_id': evaluator.id if evaluator else False,
            'state': 'pending',
            'price': price,
        })

        self.env['dumuc.transaction'].create({
            'partner_id': self.id,
            'amount': -price,
            'type': 'inspection',
            'ref_id': booking.id,
        })

        return booking