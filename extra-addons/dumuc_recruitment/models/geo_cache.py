from odoo import models, fields, api
from datetime import timedelta, datetime


class GeoCache(models.Model):
    _name = "dumuc.geo.cache"
    _description = "Cache tọa độ địa chỉ"

    input = fields.Char(index=True)
    latitude = fields.Float()
    longitude = fields.Float()
    write_date = fields.Datetime()

    @api.model
    def get_cached(self, input_text):
        rec = self.search([('input', '=', input_text)], limit=1)
        if rec:
            config = self.env['dumuc.recruit.config'].search([], limit=1)
            expire = timedelta(days=config.geo_cache_expire_days)
            if rec.write_date and rec.write_date >= fields.Datetime.now() - expire:
                return rec.latitude, rec.longitude
        return None, None

    @api.model
    def set_cached(self, input_text, lat, lng):
        rec = self.search([('input', '=', input_text)], limit=1)
        if rec:
            rec.write({'latitude': lat, 'longitude': lng})
        else:
            self.create({'input': input_text, 'latitude': lat, 'longitude': lng})
    