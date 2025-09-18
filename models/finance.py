# poultry_farm_management/models/finance.py
from odoo import models, fields, api

class PoultryFinanceEntry(models.Model):
    _name = 'poultry.finance'
    _description = 'Finance Entry (Income / Expense)'

    name = fields.Char(string='Reference', required=True)
    date = fields.Date(required=True)
    branch_id = fields.Many2one('poultry.branch', string='Branch')
    entry_type = fields.Selection([('income','Income'), ('expense','Expense')], default='expense')
    amount = fields.Monetary(currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    account_id = fields.Many2one('account.account', string='Account')
    journal_id = fields.Many2one('account.journal', string='Journal')
    description = fields.Text()
