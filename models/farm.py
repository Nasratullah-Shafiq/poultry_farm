# poultry_farm_management/models/farm.py
from odoo import models, fields, api

class PoultryType(models.Model):
    _name = 'item.type'
    _description = 'Item Type'

    name = fields.Char(required=True)
    description = fields.Text()



class PoultryPurchase(models.Model):
    _name = 'poultry.purchase'
    _description = 'Poultry Purchase'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Date(required=True)
    branch_id = fields.Many2one('poultry.branch', required=True)
    item_type_id = fields.Many2one('item.type', string='Type', required=True)
    quantity = fields.Integer(default=1)
    unit_price = fields.Monetary(currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    supplier = fields.Char()
    total = fields.Monetary(currency_field='currency_id', compute='_compute_total', store=True)

    @api.depends('quantity', 'unit_price')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.quantity * rec.unit_price

    def write(self, vals):
        res = super(PoultryPurchase, self).write(vals)
        self._update_stock()
        return res

    @api.model
    def create(self, vals):
        rec = super(PoultryPurchase, self).create(vals)
        rec._update_stock()
        return rec

    def _update_stock(self):
        for rec in self:
            stock = self.env['poultry.farm'].search([
                ('branch_id', '=', rec.branch_id.id),
                ('item_type_id', '=', rec.item_type_id.id)
            ], limit=1)
            if stock:
                stock.total_quantity += rec.quantity
            else:
                self.env['poultry.farm'].create({
                    'branch_id': rec.branch_id.id,
                    'item_type_id': rec.item_type_id.id,
                    'total_quantity': rec.quantity
                })


# class PoultryPurchase(models.Model):
#     _name = 'poultry.purchase'
#     _description = 'Poultry Purchase'
#     _inherit = ['mail.thread', 'mail.activity.mixin']  # <-- Add chatter support
#
#     date = fields.Date(required=True)
#     branch_id = fields.Many2one('poultry.branch', required=True)
#     item_type_id = fields.Many2one('item.type', string='Type', required=True)
#     quantity = fields.Integer(default=1)
#     unit_price = fields.Monetary(currency_field='currency_id', required=True)
#     currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
#     supplier = fields.Char()
#     source_details = fields.Text()
#     total = fields.Monetary(currency_field='currency_id', compute='_compute_total', store=True)
#
#     @api.depends('quantity','unit_price')
#     def _compute_total(self):
#         for rec in self:
#             rec.total = rec.quantity * (rec.unit_price or 0.0)

# class PoultrySale(models.Model):
#     _name = 'poultry.sale'
#     _description = 'Poultry Sale'
#     _inherit = ['mail.thread', 'mail.activity.mixin']  # <-- Add chatter support
#
#     date = fields.Date(required=True)
#     branch_id = fields.Many2one('poultry.branch', required=True)
#     item_type_id = fields.Many2one('item.type', string='Type', required=True)
#     quantity = fields.Integer(default=1)
#     unit_price = fields.Monetary(currency_field='currency_id', required=True)
#     currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
#     buyer = fields.Char()
#     revenue = fields.Monetary(currency_field='currency_id', compute='_compute_revenue', store=True)
#     # poultry_id = fields.Many2one('poultry.farm', string="Poultry Farm", required=True)
#
#     @api.depends('quantity','unit_price')
#     def _compute_revenue(self):
#         for rec in self:
#             rec.revenue = rec.quantity * (rec.unit_price or 0.0)
class PoultrySale(models.Model):
    _name = 'poultry.sale'
    _description = 'Poultry Sale'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Date(required=True)
    branch_id = fields.Many2one('poultry.branch', required=True)
    item_type_id = fields.Many2one('item.type', string='Type', required=True)
    quantity = fields.Integer(default=1)
    unit_price = fields.Monetary(currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    buyer = fields.Char()
    revenue = fields.Monetary(currency_field='currency_id', compute='_compute_revenue', store=True)

    @api.depends('quantity', 'unit_price')
    def _compute_revenue(self):
        for rec in self:
            rec.revenue = rec.quantity * rec.unit_price

    def write(self, vals):
        res = super(PoultrySale, self).write(vals)
        self._update_stock()
        return res

    @api.model
    def create(self, vals):
        rec = super(PoultrySale, self).create(vals)
        rec._update_stock()
        return rec

    def _update_stock(self):
        for rec in self:
            stock = self.env['poultry.farm'].search([
                ('branch_id', '=', rec.branch_id.id),
                ('item_type_id', '=', rec.item_type_id.id)
            ], limit=1)
            if stock:
                stock.total_quantity -= rec.quantity
                if stock.total_quantity < 0:
                    stock.total_quantity = 0  # prevent negative stock
            else:
                raise UserError("No stock found for this branch and item type!")

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
