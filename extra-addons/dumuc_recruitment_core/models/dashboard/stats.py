# -*- coding: utf-8 -*-
from odoo import models, fields

class JobhubStats(models.Model):
    _name = "jobhub.stats"

    name = fields.Char()
    value = fields.Float()
