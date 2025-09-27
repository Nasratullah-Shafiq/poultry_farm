from odoo import models, fields, api

class PoultryItem(models.Model):
    _name = 'poultry.item'
    _description = 'Poultry Farm Item'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Item Name", required=True, tracking=True)
    category = fields.Selection([
        ('poultry', 'Poultry'),
        ('eggs', 'Eggs'),
        ('feed', 'Feed'),
        ('medicine', 'Medicine'),
        ('equipment', 'Equipment'),
    ], string="Category", required=True, tracking=True)

    unit = fields.Char(string="Unit", required=True, help="e.g., kg, pieces, liters", tracking=True)

    # Make sure these three fields exist
    initial_qty = fields.Float(string="Initial Quantity", default=0.0, tracking=True)
    stock_in_qty = fields.Float(string="Stock In (Added)", default=0.0, tracking=True)
    stock_out_qty = fields.Float(string="Stock Out (Used/Sold)", default=0.0, tracking=True)

    remaining_qty = fields.Float(
        string="Remaining Quantity",
        compute='_compute_remaining_qty',
        store=True,
        tracking=True
    )

    description = fields.Text(string="Description")

    @api.depends('initial_qty', 'stock_in_qty', 'stock_out_qty')
    def _compute_remaining_qty(self):
        for record in self:
            record.remaining_qty = (record.initial_qty + record.stock_in_qty) - record.stock_out_qty
