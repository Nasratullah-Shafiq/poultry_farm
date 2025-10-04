from odoo import models, fields, api

class PoultryStockMove(models.Model):
    _name = 'poultry.stock.move'
    _description = 'Poultry Stock Movements'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Date(string="Date", default=fields.Date.today, required=True)
    item_id = fields.Many2one('poultry.item', string="Item", required=True)
    move_type = fields.Selection(
        [
            ('in', 'Stock In'),
            ('out', 'Stock Out')
        ],
        string="Movement Type",
        required=True
    )
    quantity = fields.Float(string="Quantity", required=True)
    branch_id = fields.Many2one('poultry.branch', string="Branch")
    reference = fields.Char(string="Reference")

    notes = fields.Text(string="Notes")

    @api.model
    def create(self, vals):
        """Validation to prevent negative stock"""
        if vals.get('move_type') == 'out':
            item = self.env['poultry.item'].browse(vals['item_id'])
            current_stock = item.remaining_qty
            if vals['quantity'] > current_stock:
                raise ValueError(f"Not enough stock for {item.name}. Current stock: {current_stock}")
        return super(PoultryStockMove, self).create(vals)
