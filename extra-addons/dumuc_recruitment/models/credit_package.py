from odoo import models, fields

class CreditPackage(models.Model):
    _name = 'dumuc.credit.package'
    _description = "Gói credit"

    name = fields.Char(string="Tên gói")
    price_vnd = fields.Float(string="Giá (VND)")
    credits = fields.Float(string="Credit")
    is_active = fields.Boolean(string="Kích hoạt", default=True)
    description = fields.Text(string="Mô tả")

class CompanyWallet(models.Model):
    _name = "dumuc.company.wallet"
    _description = "Ví Credit Garage"

    company_id = fields.Many2one("dumuc.company", required=True)
    balance = fields.Integer(default=0)

    transaction_ids = fields.One2many("dumuc.credit.tx", "wallet_id")


class CreditTransaction(models.Model):
    _name = "dumuc.credit.tx"
    _description = "Lịch sử giao dịch Credit"

    wallet_id = fields.Many2one("dumuc.company.wallet")
    type = fields.Selection([
        ('topup','Nạp'),
        ('spend','Tiêu'),
        ('refund','Hoàn')
    ], default='spend')

    amount = fields.Integer()
    balance_after = fields.Integer()

    description = fields.Char()
    related_model = fields.Char()
    related_id = fields.Integer()
    created_at = fields.Datetime(default=fields.Datetime.now)
    credit_type = fields.Selection([
        ('paid', 'Mua'),
        ('bonus', 'Bonus'),
        ('promo', 'Khuyến mãi')
    ], default='paid')

    expiry_date = fields.Date("Ngày hết hạn")
    is_expired = fields.Boolean("Đã hết hạn", default=False)


class CreditService(models.Model):
    _name = "dumuc.credit.service"
    _description = "Dịch vụ & Chi phí credit"

    code = fields.Char()  # POST_JOB / VIEW_SEEKER / BOOST / GIG_POST / GIG_BOOK
    name = fields.Char()
    cost = fields.Integer()


class CreditPricingRule(models.Model):
    _name = "dumuc.credit.pricing.rule"
    _description = "Quy tắc tính Credit động"

    service_code = fields.Char(required=True)  # POST_JOB, VIEW_SEEKER, BOOST...
    
    category_id = fields.Many2one("dumuc.job.category")
    urgent = fields.Boolean()
    subscription_required = fields.Boolean()

    time_start = fields.Float("Giờ bắt đầu")  # e.g 8.0 for 8h
    time_end = fields.Float("Giờ kết thúc")
    
    region = fields.Char()  # e.g TP.HCM, Hà Nội

    multiplier = fields.Float(default=1.0)
    base_adjust = fields.Integer(default=0)

    is_active = fields.Boolean(default=True)
