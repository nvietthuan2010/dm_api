from odoo import models, fields, api
from odoo.exceptions import UserError


class CreditEngine(models.AbstractModel):
    _name = "dumuc.credit.engine"
    _description = "Xử lý tiêu credit"

    def _get_wallet(self, company_id):
        wallet = self.env['dumuc.company.wallet'].search([('company_id','=',company_id)], limit=1)
        if not wallet:
            wallet = self.env['dumuc.company.wallet'].create({'company_id': company_id})
        return wallet

    def consume(self, company_id, service_code, model=None, record_id=None):
        service = self.env['dumuc.credit.service'].search([('code','=',service_code)], limit=1)
        if not service:
            raise UserError("Service not configured")

        wallet = self._get_wallet(company_id)

        if wallet.balance < service.cost:
            raise UserError("Không đủ credit. Vui lòng nạp thêm.")

        new_balance = wallet.balance - service.cost
        wallet.balance = new_balance

        self.env['dumuc.credit.tx'].create({
            'wallet_id': wallet.id,
            'type': 'spend',
            'amount': -service.cost,
            'balance_after': new_balance,
            'description': f'Tiêu dịch vụ: {service.name}',
            'related_model': model,
            'related_id': record_id
        })

        return True

    def topup(self, company_id, credits, credit_type='paid', package_id=None):
        """
        Nạp credit → tính expiry date theo policy.
        credit_type: paid / bonus / promo
        """

        if credits <= 0:
            raise UserError("Số credits phải lớn hơn 0.")

        wallet = self._get_wallet(company_id)

        # Tìm policy
        policy = self.env['dumuc.credit.policy'].search([
            ('credit_type', '=', credit_type)
        ], limit=1)

        # default expiry: 180 days for paid
        expiry_days = policy.expiry_days if policy else 180

        expiry_date = fields.Date.to_string(
            fields.Date.add(fields.Date.today(), days=expiry_days)
        )

        # Update balance
        new_balance = wallet.balance + credits
        wallet.balance = new_balance

        # Ghi transaction
        tx_vals = {
            'wallet_id': wallet.id,
            'type': 'topup',
            'amount': credits,
            'balance_after': new_balance,
            'credit_type': credit_type,
            'expiry_date': expiry_date,
            'description': f'Nạp {credits} credits ({credit_type})'
        }
        if package_id:
            tx_vals['related_model'] = 'dumuc.credit.package'
            tx_vals['related_id'] = package_id

        self.env['dumuc.credit.tx'].create(tx_vals)

        return {
            'status': 'success',
            'company_id': company_id,
            'credits_added': credits,
            'credit_type': credit_type,
            'expiry_date': expiry_date,
            'balance': new_balance
        }


    def compute_cost(self, company_id, service_code, context=None):
        """
        context = {
            'category_id': x,
            'urgent': True,
            'region': 'HCM',
            'timestamp': dt,
            ...
        }
        """
        service = self.env['dumuc.credit.service'].search([('code','=',service_code)], limit=1)
        if not service:
            raise UserError("Service not configured")

        cost = service.cost  # base cost

        rules = self.env['dumuc.credit.pricing.rule'].search([
            ('service_code','=',service_code),
            ('is_active','=',True),
        ])

        for rule in rules:

            # category match
            if rule.category_id and context.get('category_id') != rule.category_id.id:
                continue

            # urgent match
            if rule.urgent and not context.get('urgent'):
                continue

            # time range
            if rule.time_start and rule.time_end:
                hour = context.get('hour')
                if not (rule.time_start <= hour <= rule.time_end):
                    continue

            # region
            if rule.region and context.get('region') != rule.region:
                continue

            # apply rule
            cost = int(cost * rule.multiplier + rule.base_adjust)

        return cost

