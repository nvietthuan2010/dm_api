# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GigApplication(models.Model):
    _name = 'dumuc.gig.application'
    _description = 'Ứng tuyển gig'

    gig_id = fields.Many2one('dumuc.gig.request', string='Gig', required=True, ondelete='cascade')
    seeker_id = fields.Many2one('dumuc.seeker', string='Ứng viên', required=True)
    applied_at = fields.Datetime('Ngày ứng tuyển', default=fields.Datetime.now)

    status = fields.Selection([
        ('applied', 'Đã ứng tuyển'),
        ('accepted', 'Đã nhận'),
        ('rejected', 'Từ chối')
    ], default='applied', string='Trạng thái')

    def action_accept(self):
        Booking = self.env['dumuc.booking']

        for app in self:
            if app.status != 'applied':
                raise UserError(_("Chỉ có thể chọn đơn ở trạng thái 'Đã ứng tuyển'."))

            profile = self.env['dumuc.gig.profile'].search([
                ('seeker_id', '=', app.seeker_id.id),
                ('kyc_status', '=', 'verified'),
            ], limit=1)

            if not profile:
                raise UserError(_("Ứng viên chưa có hồ sơ Gig hợp lệ."))

            Booking.create({
                'gig_id': app.gig_id.id,
                'employer_id': app.gig_id.employer_id.id,
                'company_id': app.gig_id.company_id.id,
                'worker_id': profile.id,
                'category_id': app.gig_id.category_id.id,
                'job_type': app.gig_id.title,
                'start_time': app.gig_id.start_time,
                'end_time': app.gig_id.end_time,
                'location': app.gig_id.location,
                'total_fee': app.gig_id.price_offer,
            })

            app.status = 'accepted'
