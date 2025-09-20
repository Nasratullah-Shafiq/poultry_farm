# poultry_farm_management/models/farm.py
from odoo import models, fields, api

class PoultryType(models.Model):
    _name = 'poultry.type'
    _description = 'Poultry Type'

    name = fields.Char(required=True)
    description = fields.Text()

class PoultryPurchase(models.Model):
    _name = 'poultry.purchase'
    _description = 'Poultry Purchase'

    date = fields.Date(required=True)
    branch_id = fields.Many2one('poultry.branch', required=True)
    poultry_type_id = fields.Many2one('poultry.type', string='Type', required=True)
    quantity = fields.Integer(default=1)
    unit_price = fields.Monetary(currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    supplier = fields.Char()
    source_details = fields.Text()
    total = fields.Monetary(currency_field='currency_id', compute='_compute_total', store=True)

    @api.depends('quantity','unit_price')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.quantity * (rec.unit_price or 0.0)

class PoultrySale(models.Model):
    _name = 'poultry.sale'
    _description = 'Poultry Sale'

    date = fields.Date(required=True)
    branch_id = fields.Many2one('poultry.branch', required=True)
    poultry_type_id = fields.Many2one('poultry.type', string='Type', required=True)
    quantity = fields.Integer(default=1)
    unit_price = fields.Monetary(currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    buyer = fields.Char()
    revenue = fields.Monetary(currency_field='currency_id', compute='_compute_revenue', store=True)

    @api.depends('quantity','unit_price')
    def _compute_revenue(self):
        for rec in self:
            rec.revenue = rec.quantity * (rec.unit_price or 0.0)

class Feed(models.Model):
    _name = 'poultry.feed'
    _description = 'Feed Inventory'

    name = fields.Char(required=True)
    branch_id = fields.Many2one('poultry.branch')
    quantity = fields.Float()
    unit = fields.Char(default='kg')
    purchase_price = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

class Medicine(models.Model):
    _name = 'poultry.medicine'
    _description = 'Medicine Inventory'

    name = fields.Char(required=True)
    branch_id = fields.Many2one('poultry.branch')
    quantity = fields.Float()
    purchase_price = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

class Vaccination(models.Model):
    _name = 'poultry.vaccination'
    _description = 'Vaccination Schedule'

    name = fields.Char(required=True)
    poultry_type_id = fields.Many2one('poultry.type', string='Type')
    branch_id = fields.Many2one('poultry.branch')
    vaccine_name = fields.Char(required=True)
    vaccine_date = fields.Date(required=True)
    notes = fields.Text()
    responsible_id = fields.Many2one('poultry.employee', string='Responsible')
