# poultry_farm_management/models/farm.py
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError




class PoultryPurchase(models.Model):
    _name = 'poultry.purchase'
    _description = 'Poultry Purchase'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Date(required=True)
    branch_id = fields.Many2one('poultry.branch', required=True)
    item_type_id = fields.Many2one('item.type', string='Type', required=True)
    quantity = fields.Integer(default=1)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True,
                             default=lambda self: self.env.ref('uom.product_uom_unit'))
    unit_price = fields.Monetary(currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    supplier_id = fields.Many2one('poultry.supplier', string='Supplier', required=True)
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
                    'total_quantity': rec.quantity,
                    'uom_id': rec.uom_id.id,
                })








