# poultry_farm_management/models/farm.py
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class PoultrySale(models.Model):
    _name = 'poultry.sale'  # Technical model name used internally by Odoo
    _description = 'Poultry Sale'  # Human-readable description of the model
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Enable chatter & activity features

    # ---------------------------
    # Basic Sale Information
    # ---------------------------
    date = fields.Date(required=True)  # Date of the sale (mandatory field)
    branch_id = fields.Many2one('poultry.branch', required=True)  # Link to the branch where sale occurs
    item_type_id = fields.Many2one('item.type', string='Type', required=True)  # Type of poultry item being sold
    quantity = fields.Integer(string="Quantity for Sale", default=1)  # Number of items sold, default is 1
    sale_price = fields.Monetary(currency_field='currency_id', required=True)  # Price per unit in selected currency
    purchase_price = fields.Monetary(string='Purchase Price', currency_field='currency_id', readonly=True)
    uom_id = fields.Many2one(
        'uom.uom', string='Unit of Measure', required=True,
        default=lambda self: self.env.ref('uom.product_uom_unit')  # Default unit of measure is 1 piece
    )
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id
    )  # Currency for the sale, defaults to company currency
    customer_id = fields.Many2one('poultry.customer', string='Customer', ondelete='cascade')
    farm_id = fields.Many2one('poultry.farm.house', string='Farm', required=True)

    # ---------------------------
    # Computed Fields
    # ---------------------------
    total = fields.Monetary(
        currency_field='currency_id', compute='_compute_total', String="Total", store=True
    )  # Total sale revenue = quantity * sale_price, stored in DB

    available_quantity = fields.Integer(string="Available Quantity", compute='_compute_available_quantity', store=True)

    payment_ids = fields.One2many('poultry.payment','sale_id',string="Payments")

    status = fields.Selection(
        [
            ('new', 'New Sale'),
            ('sale_done', 'Sale Done')
        ],
        string="Status",
        default='new',
        tracking=True
    )

    def action_sale_done(self):
        for rec in self:
            if rec.total <= 0:
                raise ValidationError("Sale total must be greater than zero.")
            rec.status = 'sale_done'

    # ---------------------------
    # Constraints & Validations
    # ---------------------------
    @api.constrains('customer_id')
    def _check_customer(self):
        for rec in self:
            if not rec.customer_id:
                raise UserError("Customer is required. Please select a customer before saving.")

    @api.onchange('item_type_id')
    def _onchange_item_type_id(self):
        if not self.item_type_id:
            return

        # Fetch latest purchase price
        latest_purchase = self.env['poultry.purchase'].search(
            [('item_type_id', '=', self.item_type_id.id)],
            order='date desc',
            limit=1
        )

        if latest_purchase:
            self.purchase_price = latest_purchase.purchase_price
        else:
            self.purchase_price = 0

    @api.constrains('sale_price')
    def _check_sale_price(self):
        """Ensure unit price is greater than zero."""
        for rec in self:
            if rec.sale_price <= 0:
                raise ValidationError("Unit Price must be greater than zero.")

    @api.depends('branch_id', 'farm_id', 'item_type_id')
    def _compute_available_quantity(self):
        """Compute available stock for the selected branch, farm, and item type."""
        for rec in self:
            if rec.branch_id and rec.farm_id and rec.item_type_id:
                stock = self.env['poultry.farm'].search([
                    ('branch_id', '=', rec.branch_id.id),
                    ('farm_id', '=', rec.farm_id.id),
                    ('item_type_id', '=', rec.item_type_id.id)
                ], limit=1)
                rec.available_quantity = stock.total_quantity if stock else 0
            else:
                rec.available_quantity = 0

    @api.depends('quantity', 'sale_price')
    def _compute_total(self):
        """Compute total revenue for the sale."""
        for rec in self:
            rec.total = rec.quantity * rec.sale_price

    # ---------------------------
    # Overridden ORM Methods
    # ---------------------------
    def write(self, vals):
        """Override write to update stock whenever a sale record is edited."""
        res = super(PoultrySale, self).write(vals)
        self._update_stock()
        return res

    @api.model
    def create(self, vals):
        """Override create to update stock whenever a new sale is created."""
        rec = super(PoultrySale, self).create(vals)
        rec._update_stock()
        return rec

    # ---------------------------
    # Stock Management
    # ---------------------------
    def _update_stock(self, old_qty=0, old_branch=None, old_type=None):
        """
        Update stock levels based on sale.

        Steps:
        1. Restore previous quantity if editing existing record
        2. Fetch current stock for branch and item type
        3. Validate that sale quantity does not exceed stock
        4. Deduct sold quantity from stock
        """
        for rec in self:

            # Restore old quantity when editing
            if old_branch:
                old_stock = self.env['poultry.farm'].search([
                    ('branch_id', '=', old_branch.id),
                    ('item_type_id', '=', old_type.id)
                ], limit=1)
                if old_stock:
                    old_stock.total_quantity += old_qty

            # Fetch current stock
            stock = self.env['poultry.farm'].search([
                ('branch_id', '=', rec.branch_id.id),
                ('item_type_id', '=', rec.item_type_id.id)
            ], limit=1)

            if not stock:
                raise UserError("No stock found for this branch and item type!")

            # Validate that sale quantity does not exceed available stock
            if rec.quantity > stock.total_quantity:
                raise UserError(
                    f"Sale quantity ({rec.quantity}) cannot be greater "
                    f"than available stock ({stock.total_quantity})!"
                )

            # Deduct sold quantity from stock
            stock.total_quantity -= rec.quantity
