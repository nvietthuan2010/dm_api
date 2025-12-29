from odoo import models, fields


class AnalyticsDashboard(models.Model):
    _name = "dumuc.analytics.dashboard"
    _description = "Dashboard tổng hợp hệ thống"

    total_jobs = fields.Integer(string="Tổng tin tuyển dụng")
    total_candidates = fields.Integer(string="Tổng ứng viên")
    total_garages = fields.Integer(string="Tổng Garage")
    total_credits_used = fields.Integer(string="Tổng tín dụng tiêu thụ")

    month = fields.Char(string="Tháng")

    def _cron_update_dashboard(self):
        """Cập nhật số liệu dashboard"""
        self.write({
            "total_jobs": self.env["hr.job"].search_count([]),
            "total_candidates": self.env["dumuc.candidate.profile"].search_count([]),
            "total_garages": self.env["dumuc.garage.profile"].search_count([]),
        })
