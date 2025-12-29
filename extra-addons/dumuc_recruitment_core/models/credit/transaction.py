from odoo import models, fields


class CreditTransaction(models.Model):
    _name = "dumuc.credit.transaction"
    _description = "Giao dịch tín dụng"

    wallet_id = fields.Many2one("dumuc.credit.wallet", string="Ví", required=True)
    amount = fields.Integer(string="Số lượng", required=True)
    
    type = fields.Selection(
        [('debit', 'Trừ'), ('credit', 'Cộng')],
        string="Loại giao dịch",
        required=True
    )

    balance_before = fields.Integer(string="Số dư trước")
    balance_after = fields.Integer(string="Số dư sau")

    reference = fields.Char(string="Tham chiếu")
    reference_type = fields.Char(string="Loại tham chiếu")

    create_date = fields.Datetime(string="Ngày", readonly=True)
