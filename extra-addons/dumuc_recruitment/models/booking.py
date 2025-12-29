# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Booking(models.Model):
    _name = 'dumuc.booking'
    _description = 'Booking thuê thợ'
    _order = "create_date desc"

    gig_id = fields.Many2one('dumuc.gig.request')
    employer_id = fields.Many2one('res.users')
    company_id = fields.Many2one('dumuc.company')
    worker_id = fields.Many2one('dumuc.gig.profile')

    job_type = fields.Char('Loại công việc')
    category_id = fields.Many2one('dumuc.job.category')

    start_time = fields.Datetime('Bắt đầu')
    end_time = fields.Datetime('Kết thúc')
    location = fields.Char('Địa điểm')

    total_fee = fields.Float('Tổng chi phí')

    status = fields.Selection([
        ('pending', 'Chờ xác nhận'),
        ('accepted', 'Đã nhận'),
        ('in_progress', 'Đang thực hiện'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ], default='pending')

    employer_notes = fields.Text('Ghi chú từ Garage')
    worker_notes = fields.Text('Ghi chú từ thợ')

    employer_rating = fields.Integer('Đánh giá từ Garage')
    worker_rating = fields.Integer('Đánh giá từ thợ')
    employer_review = fields.Text('Review từ Garage')
    worker_review = fields.Text('Review từ thợ')
    surge_multiplier = fields.Float("Hệ số tăng giá", default=1.0)
    surge_final_fee = fields.Float("Thành tiền sau surge")

    def compute_price(self):
        match_engine = self.env['dumuc.match.engine']
        surge_engine = self.env['dumuc.surge.engine']

        # distance
        distance = match_engine.distance_score_raw(self.gig_id, self.worker_id)

        base_price = self.gig_id.price_offer
        surge = surge_engine.compute_multiplier(self.gig_id, self.worker_id, distance)
        self.surge_multiplier = surge
        self.surge_final_fee = round(base_price * surge, 0)

    @api.model
    def create(self, vals):
        rec = super(Booking, self).create(vals)
        rec.compute_price()
        return rec

    def action_accept(self):
        for r in self:
            if r.status != 'pending':
                raise UserError(_("Booking không ở trạng thái 'Chờ xác nhận'."))
            r.status = 'accepted'

    def action_start(self):
        for r in self:
            if r.status != 'accepted':
                raise UserError(_("Không thể bắt đầu."))
            r.status = 'in_progress'

    def action_complete(self):
        worker = self.worker_id
        worker.completed_jobs += 1
        self.env['dumuc.reputation.engine'].compute_and_set(worker)

    def action_cancel(self):
        worker = self.worker_id
        worker.cancelled_jobs += 1
        self.env['dumuc.reputation.engine'].compute_and_set(worker)

