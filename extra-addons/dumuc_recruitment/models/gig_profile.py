# -*- coding: utf-8 -*-
from odoo import models, fields, api


class GigProfile(models.Model):
    _name = 'dumuc.gig.profile'
    _description = 'Hồ sơ thợ nhận Gig'
    _order = "rating desc, total_bookings desc"

    seeker_id = fields.Many2one('dumuc.seeker', string='Ứng viên', required=True)

    is_gig_active = fields.Boolean('Bật tìm việc', default=True)
    availability_status = fields.Selection([
        ('online', 'Online'),
        ('busy', 'Đang bận'),
        ('offline', 'Offline')
    ], default='offline')

    booking_rate = fields.Float('Đơn giá', required=True)
    rate_unit = fields.Selection([
        ('hour', 'Giờ'),
        ('day', 'Ngày'),
        ('job', 'Trọn gói')
    ], required=True)

    service_area_ids = fields.Many2many('dumuc.location', string='Khu vực làm việc')

    kyc_data = fields.Json('Dữ liệu KYC')
    kyc_status = fields.Selection([
        ('pending', 'Chờ duyệt'),
        ('verified', 'Đã duyệt'),
        ('rejected', 'Từ chối')
    ], default='pending')

    booking_ids = fields.One2many('dumuc.booking', 'worker_id', string='Booking')
    presence_at = fields.Datetime('Thời gian cập nhật trạng thái')
    latitude = fields.Float("Vĩ độ")
    longitude = fields.Float("Kinh độ")
    reputation_score = fields.Float("Điểm Uy Tín", default=0.0)
    rating_avg = fields.Float("Điểm đánh giá TB", compute="_compute_rating", store=True)
    completed_jobs = fields.Integer("Số job hoàn thành", default=0)
    cancelled_jobs = fields.Integer("Số job hủy", default=0)
    response_time_avg = fields.Float("Phản hồi trung bình (phút)", default=0.0)

    badge = fields.Selection([
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum')
    ], string="Huy hiệu", default='bronze')

    @api.depends('booking_ids.worker_rating')
    def _compute_rating(self):
        for rec in self:
            ratings = [b.worker_rating for b in rec.booking_ids if b.worker_rating]
            rec.rating_avg = sum(ratings) / len(ratings) if ratings else 0.0



    def set_online(self):
        self.write({
            'availability': 'online',
            'presence_at': fields.Datetime.now()
        })
        self.env['bus.bus']._sendone(
            'gig_presence',
            {'worker_id': self.id, 'status': 'online'}
        )

    def set_offline(self):
        self.write({
            'availability': 'offline',
            'presence_at': fields.Datetime.now()
        })
        self.env['bus.bus']._sendone(
            'gig_presence',
            {'worker_id': self.id, 'status': 'offline'}
        )

