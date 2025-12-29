# controllers/admin_api.py
from odoo import http
from odoo.http import request
from odoo.tools.safe_eval import safe_eval

class DumucAdminAPI(http.Controller):

    @http.route('/dumuc/admin/dashboard/data', type='json', auth='user')
    def dashboard_data(self, **kw):
        # only allow users in admin group
        user = request.env.user
        if not user.has_group('dumuc_marketplace.group_dumuc_admin'):
            return {'error': 'access_denied'}
        Listing = request.env['dumuc.listing'].sudo()
        data = {
            'counts': {
                'pending': Listing.search_count([('state','=','pending')]),
                'rejected': Listing.search_count([('state','=','rejected')]),
                'active': Listing.search_count([('state','=','active')]),
                'suspended': Listing.search_count([('state','=','suspended')]),
                'expired': Listing.search_count([('state','=','expired')]),
            },
            'pending_items': [
                {
                    'id': r.id,
                    'title': r.name,
                    'price': r.price,
                    'seller': r.partner_id.name,
                    'cover_image': (r.cover_image.decode() if r.cover_image else False),
                    'posted_at': str(r.posted_at),
                    'priority_score': r.priority_score,
                }
                for r in Listing.search([('state','=','pending')], limit=50, order='priority_score desc')
            ]
        }
        return data

    @http.route('/dumuc/admin/listing/approve', type='json', auth='user')
    def listing_approve(self, listing_id, **kw):
        user = request.env.user
        if not user.has_group('dumuc_marketplace_admin.group_dumuc_admin'):
            return {'error': 'access_denied'}
        rec = request.env['dumuc.listing'].sudo().browse(int(listing_id))
        if not rec.exists():
            return {'error': 'not_found'}
        try:
            rec.sudo().action_approve()
            return {'status': 'ok'}
        except Exception as e:
            return {'error': str(e)}

    @http.route('/dumuc/admin/listing/reject_open', type='json', auth='user')
    def listing_reject_open(self, listing_id, **kw):
        # returns action to open reject wizard on client side if needed
        return {'action': 'open_reject_wizard', 'listing_id': listing_id}
