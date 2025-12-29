from odoo import models, fields
from odoo.exceptions import UserError


class Company(models.Model):
    _name = 'dumuc.company'
    _description = "Garage/Doanh nghiệp"

    name = fields.Char(string="Tên công ty", required=True)
    tax_code = fields.Char(string="Mã số thuế")
    address = fields.Char(string="Địa chỉ")
    phone = fields.Char(string="Số điện thoại")
    website = fields.Char(string="Website")

    logo = fields.Binary(string="Logo")
    license_file = fields.Binary(string="Giấy phép")

    is_verified = fields.Boolean(string="Đã xác thực", default=False)
    
    user_id = fields.Many2one('res.users', string="Tài khoản chủ")

    created_at = fields.Datetime(string="Ngày tạo", default=fields.Datetime.now)

    transaction_ids = fields.One2many('dumuc.credit.transaction', 'company_id', string="Giao dịch")

    credit_balance = fields.Integer(
        string="Credit",
        compute="_compute_credit_balance",
        store=False
    )

    job_ids = fields.One2many('dumuc.job', 'company_id', string="Tin đã đăng")

    verify_status = fields.Selection([
        ('pending', "Chờ duyệt"),
        ('verified', "Đã xác thực"),
        ('rejected', "Từ chối"),
    ], default='pending', string="Xác thực")

    def _compute_credit_balance(self):
        for comp in self:
            comp.credit_balance = sum(comp.transaction_ids.mapped('amount'))

    def spend_credit(self, amount, description):
        self.ensure_one()
        if self.credit_balance < amount:
            raise UserError("Không đủ credit.")
        
        new_balance = self.credit_balance - amount
        
        self.env['dumuc.credit.transaction'].sudo().create({
            'company_id': self.id,
            'type': 'spend',
            'amount': -amount,
            'balance_after': new_balance,
            'description': description,
        })
    def verify(self):
        self.verify_status = 'verified'

    def reject_verification(self):
        self.verify_status = 'rejected'
