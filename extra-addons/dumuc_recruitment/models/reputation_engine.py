from odoo import models


class ReputationEngine(models.AbstractModel):
    _name = "dumuc.reputation.engine"
    _description = "Engine tính điểm uy tín"

    def compute_reputation(self, profile):
        score = 0

        # rating
        if profile.rating_avg:
            score += profile.rating_avg * 20  # scale 0-100

        # completed jobs
        score += min(profile.completed_jobs * 2, 40)

        # cancellation penalty
        score -= profile.cancelled_jobs * 5

        # response time bonus
        if profile.response_time_avg and profile.response_time_avg < 10:
            score += 10

        # KYC bonus
        if profile.kyc_status == 'verified':
            score += 10

        return max(min(score, 100), 0)


    def _assign_badge(self, profile):
        if profile.reputation_score >= 90:
            profile.badge = 'platinum'
        elif profile.reputation_score >= 75:
            profile.badge = 'gold'
        elif profile.reputation_score >= 60:
            profile.badge = 'silver'
        else:
            profile.badge = 'bronze'

    def compute_and_set(self, profile):
        score = self.compute_reputation(profile)
        profile.reputation_score = score
        self._assign_badge(profile)

