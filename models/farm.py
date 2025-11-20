# poultry_farm_management/models/farm.py
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class Feed(models.Model):
    _name = 'poultry.feed'
    _description = 'Feed Inventory'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # <-- Add chatter support

    name = fields.Char(required=True)
    branch_id = fields.Many2one('poultry.branch')
    quantity = fields.Float()
    unit = fields.Char(default='kg')
    purchase_price = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    date = fields.Date(string="Date Purchased", default=fields.Date.today)  # <-- add this

class Medicine(models.Model):
    _name = 'poultry.medicine'
    _description = 'Medicine Inventory'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # <-- Add chatter support

    name = fields.Char(required=True)
    branch_id = fields.Many2one('poultry.branch')
    quantity = fields.Float()
    purchase_price = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    date = fields.Date(string="Purchase Date", default=fields.Date.today)  # <-- add this

class Vaccination(models.Model):
    _name = 'poultry.vaccination'
    _description = 'Vaccination Schedule'

    name = fields.Char(required=True)
    item_type_id = fields.Many2one('item.type', string='Type')
    branch_id = fields.Many2one('poultry.branch')
    vaccine_name = fields.Char(required=True)
    vaccine_date = fields.Date(required=True)
    notes = fields.Text()
    responsible_id = fields.Many2one('poultry.employee', string='Responsible')
