# models/listing_boost_wizard.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class DumucListingBoostWizard(models.TransientModel):
    _name = "dumuc.listing.boost.wizard"
    _description = "Wizard đẩy tin/Up top"

    listing_id = fields.Many2one('dumuc.listing', string='Tin đăng', required=True)
    package_id = fields.Many2one('dumuc.service.package', string='Gói đẩy tin', domain="[('package_type','=','push')]", required=True)
    duration_days = fields.Integer('Số ngày', related='package_id.duration_days', readonly=True)
    amount = fields.Float('Giá', related='package_id.price', readonly=True)

    def action_confirm_boost(self):
        self.ensure_one()
        partner = self.listing_id.partner_id
        if not partner:
            raise UserError(_("Tin chưa gắn người bán"))
        # charge wallet
        if partner.dumuc_wallet_balance < self.amount:
            raise UserError(_("Số dư ví không đủ. Vui lòng nạp ví."))
        partner.sudo().write({'dumuc_wallet_balance': partner.dumuc_wallet_balance - self.amount})
        # create transaction
        self.env['dumuc.transaction'].sudo().create({
            'partner_id': partner.id,
            'amount': self.amount,
            'direction': 'out',
            'transaction_type': 'push_fee',
            'state': 'done',
            'description': _('Đẩy tin: %s') % (self.listing_id.name)
        })
        # set featured
        self.listing_id.sudo().write({
            'is_featured': True,
            'featured_until': fields.Datetime.add(fields.Datetime.now(), days=self.duration_days)
        })
        self.listing_id._compute_priority_score()
        return {'type': 'ir.actions.client', 'tag': 'reload'}
