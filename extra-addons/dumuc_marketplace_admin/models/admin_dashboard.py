# models/admin_dashboard.py
from odoo import models, api, fields

class DumucAdminDashboard(models.Model):
    _name = "dumuc.admin.dashboard"
    _description = "Readonly helper model for admin dashboard (virtual)"
    _auto = False

    # fields here are informational; not persisted
    pending_count = fields.Integer(string="Tin chờ duyệt")
    rejected_count = fields.Integer(string="Tin bị từ chối")
    active_count = fields.Integer(string="Tin đang hiển thị")
    suspended_count = fields.Integer(string="Tin bị chặn")
    expired_count = fields.Integer(string="Tin hết hạn")

    @api.model
    def get_counts(self):
        Listing = self.env['dumuc.listing'].sudo()
        return {
            'pending': Listing.search_count([('state','=','pending')]),
            'rejected': Listing.search_count([('state','=','rejected')]),
            'active': Listing.search_count([('state','=','active')]),
            'suspended': Listing.search_count([('state','=','suspended')]),
            'expired': Listing.search_count([('state','=','expired')]),
        }
