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
    unit_price = fields.Monetary(currency_field='currency_id', required=True)  # Price per unit in selected currency
    uom_id = fields.Many2one(
        'uom.uom', string='Unit of Measure', required=True,
        default=lambda self: self.env.ref('uom.product_uom_unit')  # Default unit of measure is 1 piece
    )
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id
    )  # Currency for the sale, defaults to company currency
    customer_id = fields.Many2one('poultry.customer', string='Customer',
                                  required=True)  # Customer purchasing the poultry

    # ---------------------------
    # Computed Fields
    # ---------------------------
    revenue = fields.Monetary(
        currency_field='currency_id', compute='_compute_revenue', store=True
    )  # Total sale revenue = quantity * unit_price, stored in DB

    available_quantity = fields.Integer(
        string="Available Quantity",
        compute='_compute_available_quantity',  # Dynamically calculated from poultry stock
        store=False
    )

    # # ---------------------------
    # # Payment Fields
    # # ---------------------------
    # payment_type = fields.Selection([
    #     ('cash', 'Cash'),
    #     ('credit', 'Credit'),
    # ], string="Payment Type", default='cash', required=True)  # Type of payment
    #
    # amount_paid = fields.Monetary(
    #     currency_field='currency_id',
    #     string="Amount Paid",
    #     default=0.0,
    #     help="Amount paid by the customer at the time of sale."
    # )
    # # amount_paid = fields.Monetary(
    # #     string="Amount Paid",
    # #     currency_field='currency_id',
    # #     compute="_compute_amount_paid",
    # #     store=True
    # # )
    #
    # amount_due = fields.Monetary(
    #     currency_field='currency_id',
    #     string="Amount Due",
    #     compute="_compute_amount_due", store=True
    # )  # Computed as revenue - amount_received
    #
    # due_date = fields.Date(
    #     string="Due Date",
    #     help="Payment deadline if payment type is credit."
    # )

    payment_ids = fields.One2many(
        'poultry.payment',
        'sale_id',
        string="Payments"
    )

    # payment_status = fields.Selection([
    #     ('not_paid', 'Not Paid'),
    #     ('partial', 'Partially Paid'),
    #     ('paid', 'Fully Paid'),
    # ], string="Payment Status", compute="_compute_payment_status", store=True)  # Tracks payment status
    #
    # payment_note = fields.Text(string="Payment Notes")  # Optional notes about payment

    # @api.depends('payment_ids.amount')
    # def _compute_amount_paid(self):
    #     for rec in self:
    #         total = sum(rec.payment_ids.mapped('amount'))
    #         rec.amount_paid = total
    #
    # @api.model
    # def create(self, vals):
    #     payment = super(PoultryPayment, self).create(vals)
    #
    #     # Trigger compute fields on sale
    #     if payment.sale_id:
    #         payment.sale_id._compute_amount_paid()
    #         payment.sale_id._compute_amount_due()
    #         payment.sale_id._compute_payment_status()
    #
    #     return payment

    # ---------------------------
    # Constraints & Validations
    # ---------------------------

    @api.constrains('unit_price')
    def _check_unit_price(self):
        """Ensure unit price is greater than zero."""
        for rec in self:
            if rec.unit_price <= 0:
                raise ValidationError("Unit Price must be greater than zero.")

    # ---------------------------
    # Computation Methods
    # ---------------------------
    # @api.depends('revenue', 'amount_paid')
    # def _compute_amount_due(self):
    #     for rec in self:
    #         rec.amount_due = rec.revenue - rec.amount_paid
    #
    # @api.depends('amount_paid', 'revenue')
    # def _compute_payment_status(self):
    #     """Determine the payment status based on amount received."""
    #     for rec in self:
    #         if rec.amount_paid <= 0:
    #             rec.payment_status = 'not_paid'
    #         elif rec.amount_paid < rec.revenue:
    #             rec.payment_status = 'partial'
    #         else:
    #             rec.payment_status = 'paid'

    # @api.onchange('payment_type')
    # def _onchange_payment_type(self):
    #     """Auto-update fields based on payment type selection."""
    #     if self.payment_type == 'cash':
    #         self.due_date = False  # No due date for cash payments
    #         self.amount_paid = self.revenue  # Full payment assumed
    #     else:
    #         self.amount_paid = 0  # Reset for credit payments

    @api.depends('branch_id', 'item_type_id')
    def _compute_available_quantity(self):
        """Compute available stock for the selected branch and item type."""
        for rec in self:
            if rec.branch_id and rec.item_type_id:
                stock = self.env['poultry.farm'].search([
                    ('branch_id', '=', rec.branch_id.id),
                    ('item_type_id', '=', rec.item_type_id.id)
                ], limit=1)
                rec.available_quantity = stock.total_quantity if stock else 0
            else:
                rec.available_quantity = 0

    @api.depends('quantity', 'unit_price')
    def _compute_revenue(self):
        """Compute total revenue for the sale."""
        for rec in self:
            rec.revenue = rec.quantity * rec.unit_price

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
