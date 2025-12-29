# models/listing_reject_wizard.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class DumucListingRejectWizard(models.TransientModel):
    _name = "dumuc.listing.reject.wizard"
    _description = "Wizard từ chối tin đăng"

    listing_id = fields.Many2one('dumuc.listing', string='Tin đăng', required=True)
    reason_id = fields.Many2one('dumuc.listing.reject.reason', string='Lý do từ chối', required=True)
    note = fields.Text('Ghi chú')
    create_violation = fields.Boolean('Tạo báo cáo vi phạm', default=False)

    def action_confirm_reject(self):
        self.ensure_one()
        listing = self.listing_id.sudo()
        admin = self.env.user
        # call listing action to reject
        listing.sudo().action_reject(reason_id=self.reason_id, note=self.note)
        # optional: create violation
        if self.create_violation:
            self.env['dumuc.listing.violation'].sudo().create({
                'listing_id': listing.id,
                'reporter_id': admin.partner_id.id,
                'reason': self.reason_id.name + (('\n' + (self.note or '')) if self.note else ''),
                'status': 'open',
            })
        return {'type': 'ir.actions.client', 'tag': 'reload'}