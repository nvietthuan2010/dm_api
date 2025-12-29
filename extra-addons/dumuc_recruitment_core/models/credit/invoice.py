from odoo import models, fields


class CreditInvoice(models.Model):
    _name = "dumuc.credit.invoice"
    _description = "Hóa đơn mua tín dụng"

    package_id = fields.Many2one(
        "dumuc.credit.package",
        string="Gói tín dụng"
    )
    garage_id = fields.Many2one(
        "dumuc.garage.profile",
        string="Garage mua"
    )
    amount = fields.Float(string="Giá trị hóa đơn")
    payment_method = fields.Char(string="Phương thức thanh toán")

    status = fields.Selection([
        ('pending', 'Chờ thanh toán'),
        ('paid', 'Đã thanh toán'),
        ('failed', 'Thất bại')
    ], string="Trạng thái", default='pending')

    create_date = fields.Datetime(
        string="Ngày tạo hóa đơn",
        default=fields.Datetime.now
    )

    def action_mark_paid(self):
        """Xác nhận thanh toán và nạp tín dụng"""
        self.status = 'paid'
        wallet = self.env["dumuc.credit.wallet"].search(
            [('garage_id', '=', self.garage_id.id)], limit=1)

        if not wallet:
            wallet = self.env["dumuc.credit.wallet"].create({
                "garage_id": self.garage_id.id
            })

        wallet.add_credits(self.package_id.credits, invoice=self)
