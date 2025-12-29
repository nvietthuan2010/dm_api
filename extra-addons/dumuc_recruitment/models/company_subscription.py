from odoo import models, fields, api


class CompanySubscription(models.Model):
    _name = "dumuc.company.subscription"
    _description = "Subscription của Garage"

    company_id = fields.Many2one("dumuc.company", required=True)
    plan_id = fields.Many2one("dumuc.subscription.plan", required=True)

    start_date = fields.Date(default=fields.Date.today)
    next_renew_date = fields.Date()

    auto_renew = fields.Boolean(default=True)
    is_active = fields.Boolean(default=True)

    trial_used = fields.Boolean(default=False)


    @api.model
    def _cron_monthly_renew(self):
        today = fields.Date.today()
        subs = self.search([('is_active','=',True), ('auto_renew','=',True)])

        engine = self.env['dumuc.credit.engine']

        for sub in subs:
            if sub.next_renew_date and sub.next_renew_date <= today:
                engine.topup(sub.company_id.id, sub.plan_id.monthly_credits)

                sub.next_renew_date = fields.Date.to_string(
                    fields.Date.add(today, months=1)
                )

    def start_trial(self, company_id):
        sub = self.env['dumuc.company.subscription'].search([('company_id','=',company_id)], limit=1)

        if sub and not sub.trial_used:
            engine = self.env['dumuc.credit.engine']
            engine.topup(company_id, 20)
            sub.trial_used = True
