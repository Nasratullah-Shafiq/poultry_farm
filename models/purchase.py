# poultry_farm_management/models/farm.py
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError




class PoultryPurchase(models.Model):
    _name = 'poultry.purchase'
    _description = 'Poultry Purchase'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Date(string="Date", required=True, default=fields.Date.today)
    branch_id = fields.Many2one(
        'poultry.branch',
        string="Branch",
        required=True,
        default=lambda self: self.env['poultry.branch'].search([], limit=1)
    )
    farm_id = fields.Many2one('poultry.farm.house',string='Farm',required=True)
    product_type = fields.Selection(
        related='product_id.product_type',
        string="Product Type",
        store=True,
        readonly=True,
        tracking=True
    )
    product_id = fields.Many2one('poultry.product', string="Product", required=True)

    quantity = fields.Integer(default=1)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True,
                             default=lambda self: self.env.ref('uom.product_uom_unit'))
    purchase_price = fields.Monetary(currency_field='currency_id', required=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.ref('poultry_farm.currency_afn')
    )
    supplier_id = fields.Many2one(
        'poultry.partner',
        string="Supplier",
        domain="[('partner_type','=','supplier')]",
        context={'default_partner_type': 'supplier'},
        tracking=True,
        required=True
    )

    total = fields.Monetary(currency_field='currency_id', compute='_compute_total', store=True)
    status = fields.Selection(
        [
            ('new', 'New'),
            ('purchase_done', 'Purchase Done'),
        ],
        string='Status',
        default='new',
        required=True,
        tracking=True
    )

    # -------------------------
    # COMPUTE
    # -------------------------

    @api.depends('quantity', 'purchase_price')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.quantity * rec.purchase_price

    # -------------------------
    # ACTION BUTTON
    # -------------------------

    def action_purchase_done(self):
        for rec in self:
            if rec.status == 'purchase_done':
                continue

            rec._update_stock()

            # ✅ Safe write (no recursion now)
            rec.status = 'purchase_done'

    # -------------------------
    # STOCK UPDATE LOGIC
    # -------------------------

    def _update_stock(self):
        stock_model = self.env['poultry.stock']

        for rec in self:

            stock = stock_model.search([
                ('branch_id', '=', rec.branch_id.id),
                ('farm_id', '=', rec.farm_id.id),
                ('product_id', '=', rec.product_id.id)
            ], limit=1)

            if stock:
                stock.write({
                    'total_quantity': stock.total_quantity + rec.quantity,
                    'cost_amount': stock.cost_amount + (rec.purchase_price * rec.quantity),
                    'cost': rec.purchase_price,
                    'last_updated': fields.Datetime.now(),
                })
            else:
                stock_model.create({
                    'branch_id': rec.branch_id.id,
                    'farm_id': rec.farm_id.id,
                    'product_id': rec.product_id.id,
                    'uom_id': rec.uom_id.id,
                    'cost': rec.purchase_price,
                    'cost_amount': rec.purchase_price * rec.quantity,
                    'total_quantity': rec.quantity,
                    'currency_id': rec.currency_id.id,
                    'last_updated': fields.Datetime.now(),
                })

    # -------------------------
    # VALIDATION
    # -------------------------

    @api.constrains('quantity', 'purchase_price')
    def _check_values(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError('Quantity must be greater than zero.')

            if rec.purchase_price <= 0:
                raise ValidationError('Unit price must be greater than zero.')

    # -------------------------
    # DOMAIN
    # -------------------------

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if self.branch_id:
            return {
                'domain': {
                    'farm_id': [('branch_id', '=', self.branch_id.id)]
                }
            }
        return {'domain': {'farm_id': []}}

