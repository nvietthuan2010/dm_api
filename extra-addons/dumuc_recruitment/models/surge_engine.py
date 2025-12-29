from odoo import models, fields
from datetime import datetime


class SurgePricingEngine(models.AbstractModel):
    _name = "dumuc.surge.engine"
    _description = "Engine tính dynamic pricing"

    def compute_multiplier(self, gig, worker=None, distance_meters=None):
        config = self.env['dumuc.surge.config'].search([], limit=1)
        if not config or not config.enable_surge:
            return 1.0

        multiplier = 1.0

        # 1) Peak time
        hour = datetime.now().hour
        if config.peak_start <= hour <= config.peak_end:
            multiplier *= config.peak_multiplier

        # 2) Distance factor
        if distance_meters:
            km = distance_meters / 1000.0
            if km > config.distance_threshold_km:
                multiplier *= config.distance_multiplier

        # 3) Urgent
        if gig.is_urgent:
            multiplier *= config.urgent_multiplier

        # 4) Worker rating (if exists)
        if worker and worker.rating and worker.rating >= config.rating_threshold:
            multiplier *= config.rating_multiplier

        # 5) Supply vs demand
        online_workers = self.env['dumuc.gig.profile'].search_count([('availability', '=', 'online')])
        active_gigs = self.env['dumuc.gig.request'].search_count([('status', '=', 'active')])

        if active_gigs > online_workers:  # demand > supply
            multiplier *= config.supply_demand_multiplier

        return round(multiplier, 2)
