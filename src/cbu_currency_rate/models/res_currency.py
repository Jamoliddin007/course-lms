# -*- coding: utf-8 -*-
import requests
from datetime import datetime
from odoo import models, api


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    @api.model
    def _cbu_update_currency_rates(self):
        """CBU dan valyuta kurslarini yangilash"""
        try:
            url = 'https://cbu.uz/uz/arkhiv-kursov-valyut/json/'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            today = datetime.now().date()

            for item in data:
                try:
                    code = item.get('Ccy')
                    if not code:
                        continue

                    currency = self.search([('name', '=', code)], limit=1)
                    if not currency or not currency.active:
                        continue

                    rate_value = float(item.get('Rate', 0))
                    nominal = float(item.get('Nominal', 1))

                    if rate_value <= 0:
                        continue

                    odoo_rate = rate_value / nominal

                    rate_obj = self.env['res.currency.rate'].search([
                        ('currency_id', '=', currency.id),
                        ('name', '=', today),
                        ('company_id', '=', False),
                    ], limit=1)

                    if rate_obj:
                        rate_obj.write({'rate': odoo_rate})
                    else:
                        self.env['res.currency.rate'].create({
                            'currency_id': currency.id,
                            'name': today,
                            'rate': odoo_rate,
                            'company_id': False,
                        })

                except Exception:
                    continue

        except Exception:
            pass