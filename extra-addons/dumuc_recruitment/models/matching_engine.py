from odoo import models
from math import radians, sin, cos, sqrt, atan2
from ..utils.google_maps import GoogleMapsClient
from ..utils.osrm_client import OSRMClient

class GigMatchingEngine(models.AbstractModel):
    _name = "dumuc.match.engine"
    _description = "Gig Matching Engine"

    def match_workers(self, gig):
        config = self.env['dumuc.match.config'].sudo().search([], limit=1)
        if not config:
            config = self.env['dumuc.match.config'].sudo().create({})

        workers = self.env['dumuc.gig.profile'].sudo().search([('kyc_status','=','verified')])

        results = []
        for worker in workers:
            s_skill = self.skill_score(gig, worker)
            s_dist = self.distance_score(gig, worker)
            s_rate = self.rate_score(gig, worker)
            s_avail = self.availability_score(worker)

            total = (
                s_skill * config.weight_skill +
                s_dist * config.weight_distance +
                s_rate * config.weight_rate +
                s_avail * config.weight_availability
            )

            if gig.is_urgent:
                total += config.urgent_bonus

            results.append({
                "worker": worker,
                "score": round(total, 2),
                "detail": {
                    "skill": round(s_skill,2),
                    "distance": round(s_dist,2),
                    "rate": round(s_rate,2),
                    "availability": s_avail,
                }
            })

        results.sort(key=lambda r: r['score'], reverse=True)
        return results
    
    def distance_score(self, gig, worker):
        config = self.env['dumuc.recruit.config'].search([], limit=1)

        # No geo mode → fallback
        if config.geo_mode == 'disabled':
            return 60

        if not gig.latitude or not worker.latitude:
            return 60

        g = (gig.latitude, gig.longitude)
        w = (worker.latitude, worker.longitude)

        # Google driving mode
        if config.geo_mode == 'drive_google' and config.google_api_key:
            client = GoogleMapsClient(config.google_api_key)
            meters = client.driving_distance(w, g)
            return self._score_from_distance(meters)

        # OSRM driving mode
        if config.geo_mode == 'drive_osrm' and config.osrm_url:
            osrm = OSRMClient(config.osrm_url)
            meters = osrm.driving_distance(w, g)
            return self._score_from_distance(meters)

        # Haversine fallback
        meters = self._haversine(w[0], w[1], g[0], g[1])
        return self._score_from_distance(meters)

    def _score_from_distance(self, meters):
        if meters is None:
            return 60
        if meters <= 2000:
            return 100
        elif meters <= 5000:
            return 90
        elif meters <= 10000:
            return 75
        elif meters <= 20000:
            return 60
        return 30

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371000
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        return 2 * R * atan2(sqrt(a), sqrt(1-a))