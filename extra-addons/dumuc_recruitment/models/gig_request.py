# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GigRequest(models.Model):
    _name = 'dumuc.gig.request'
    _description = 'Yêu cầu thợ ngắn hạn (Gig Request)'
    _order = "create_date desc"

    employer_id = fields.Many2one('res.users', string='Nhà tuyển dụng', required=True)
    company_id = fields.Many2one('dumuc.company', string='Garage', required=True)

    category_id = fields.Many2one('dumuc.job.category', string='Ngành nghề', required=True)
    title = fields.Char('Tiêu đề', required=True)
    description = fields.Html('Mô tả chi tiết')

    price_offer = fields.Float('Giá đề xuất', required=True)
    price_unit = fields.Selection([
        ('hour', 'Giờ'),
        ('day', 'Ngày'),
        ('job', 'Trọn gói'),
    ], string='Đơn vị', required=True)

    start_time = fields.Datetime('Thời gian bắt đầu', required=True)
    end_time = fields.Datetime('Thời gian kết thúc', required=True)
    location = fields.Char('Địa điểm làm việc', required=True)

    quantity = fields.Integer('Số thợ cần', default=1)
    required_skill_ids = fields.Many2many('dumuc.skill', string='Kỹ năng yêu cầu')

    is_urgent = fields.Boolean('Tuyển gấp')

    status = fields.Selection([
        ('draft', 'Nháp'),
        ('active', 'Hoạt động'),
        ('expired', 'Hết hạn'),
        ('closed', 'Đã đóng'),
    ], string='Trạng thái', default='draft')

    application_ids = fields.One2many('dumuc.gig.application', 'gig_id', string='Đơn ứng tuyển')
    booking_ids = fields.One2many('dumuc.booking', 'gig_id', string='Booking')

    expires_at = fields.Datetime('Thời hạn hết hiệu lực')
    created_at = fields.Datetime(string='Ngày tạo', default=fields.Datetime.now)

    latitude = fields.Float("Vĩ độ")
    longitude = fields.Float("Kinh độ")

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._geo_update()
        return record

    def write(self, vals):
        res = super().write(vals)
        if "location" in vals:
            self._geo_update()
        return res

    def _geo_update(self):
        config = self.env['dumuc.recruit.config'].search([], limit=1)
        if not config or not config.google_api_key:
            return

        cache = self.env['dumuc.geo.cache']
        cached = cache.get_cached(self.location)
        if cached != (None, None):
            self.latitude, self.longitude = cached
            return

        client = GoogleMapsClient(config.google_api_key)
        lat, lng = client.geocode(self.location)
        if lat and lng:
            self.write({'latitude': lat, 'longitude': lng})
            cache.set_cached(self.location, lat, lng)

    @api.constrains('start_time', 'end_time')
    def _check_time(self):
        for r in self:
            if r.end_time < r.start_time:
                raise UserError(_("Thời gian kết thúc phải sau thời gian bắt đầu."))

    def action_activate(self):
        for r in self:
            if not r.company_id.verify_status == 'verified':
                raise UserError(_("Garage chưa xác thực."))
            r.status = 'active'

    def action_close(self):
        for r in self:
            r.status = 'closed'
