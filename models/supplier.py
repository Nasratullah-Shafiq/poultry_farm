from odoo import models, fields, api
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError
import datetime



class PoultrySupplier(models.Model):
    _name = 'poultry.supplier'
    _description = 'Poultry Supplier'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # --------------------------------------------------------
    # BASIC INFORMATION
    # --------------------------------------------------------
    name = fields.Char(string='Supplier Name', required=True, tracking=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    address = fields.Text(string='Address')

    # --------------------------------------------------------
    # RELATIONS
    # --------------------------------------------------------
    purchase_ids = fields.One2many(
        'poultry.purchase',
        'supplier_id',
        string='Purchases'
    )

    payment_ids = fields.One2many(
        'poultry.supplier.payment',
        'supplier_id',
        string='Payments'
    )

    # --------------------------------------------------------
    # CURRENCY
    # --------------------------------------------------------
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    # --------------------------------------------------------
    # COMPUTED TOTALS
    # --------------------------------------------------------
    total_purchase = fields.Monetary(
        string='Total Purchase',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True
    )

    total_paid = fields.Monetary(
        string='Total Paid',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True
    )

    debt = fields.Monetary(
        string='Total Payable',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True
    )

    payment_status = fields.Selection(
        [
            ('not_paid', 'Not Paid'),
            ('partially_paid', 'Partially Paid'),
            ('fully_paid', 'Fully Paid')
        ],
        string='Payment Status',
        compute='_compute_payment_status',
        store=True,
        tracking=True
    )

    # --------------------------------------------------------
    # COMPUTE METHODS
    # --------------------------------------------------------
    @api.depends('total_paid', 'debt')
    def _compute_payment_status(self):
        for record in self:
            if record.debt > 0 and record.total_paid > 0:
                record.payment_status = 'partially_paid'
            elif record.debt > 0 and record.total_paid == 0:
                record.payment_status = 'not_paid'
            elif record.debt == 0:
                record.payment_status = 'fully_paid'
            else:
                record.payment_status = 'not_paid'

    @api.depends('purchase_ids.total', 'payment_ids.amount')
    def _compute_totals(self):
        for supplier in self:
            total_purchase = sum(
                purchase.total for purchase in supplier.purchase_ids if purchase.total
            )
            total_paid = sum(
                payment.amount for payment in supplier.payment_ids if payment.amount
            )

            supplier.total_purchase = total_purchase
            supplier.total_paid = total_paid
            supplier.debt = total_purchase - total_paid

    # --------------------------------------------------------
    # WIZARD: REGISTER PAYMENT
    # --------------------------------------------------------
    def action_register_payment(self):
        return {
            'name': 'Register Supplier Payment',
            'type': 'ir.actions.act_window',
            'res_model': 'poultry.supplier.payment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_supplier_id': self.id,
            }
        }










class SupplierPayment(models.Model):
    _name = 'supplier.payment'
    _description = 'Supplier Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # -------------------------
    # Basic Fields
    # -------------------------
    supplier_id = fields.Many2one(
        'poultry.supplier',
        string='Supplier',
        required=True,
        ondelete='cascade'
    )

    purchase_id = fields.Many2one(
        'poultry.purchase',
        string='Purchase'
    )

    date = fields.Date(
        string="Payment Date",
        default=fields.Date.today(),
        required=True
    )

    amount = fields.Monetary(
        string="Amount Paid",
        required=True,
        currency_field='currency_id'
    )

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )

    payment_note = fields.Text(string="Notes")

    # -------------------------
    # Additional Fields
    # -------------------------
    payment_type = fields.Selection(
        [
            ('cash', 'Cash'),
            ('credit', 'Credit')
        ],
        string="Payment Type",
        default='cash'
    )

    # -------------------------
    # Computed Amount Due
    # -------------------------
    amount_due = fields.Monetary(
        string="Amount Due",
        currency_field='currency_id',
        compute="_compute_amount_due",
        store=True
    )

    # ================================
    #   YEAR & MONTH FOR SEARCH PANEL
    # ================================
    payment_month = fields.Selection(
        [
            ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
            ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
            ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
        ],
        string="Month",
        compute="_compute_year_month",
        store=True
    )

    payment_year = fields.Selection(
        selection="_get_year_selection",
        string="Year",
        compute="_compute_year_month",
        store=True
    )

    # --------------------------------------------------
    # COMPUTE YEAR & MONTH
    # --------------------------------------------------
    @api.depends('date')
    def _compute_year_month(self):
        for rec in self:
            if rec.date:
                rec.payment_month = str(rec.date.month)
                rec.payment_year = str(rec.date.year)
            else:
                rec.payment_month = False
                rec.payment_year = False

    def _get_year_selection(self):
        current_year = datetime.date.today().year
        return [(str(y), str(y)) for y in range(current_year - 10, current_year + 1)]

    # -------------------------
    # Onchange Logic
    # -------------------------
    @api.onchange('purchase_id')
    def _onchange_purchase_id(self):
        """Automatically set the supplier based on the selected purchase."""
        if self.purchase_id:
            self.supplier_id = self.purchase_id.supplier_id

    # -------------------------
    # Compute Functions
    # -------------------------
    @api.depends('supplier_id.purchase_ids.total', 'supplier_id.payment_ids.amount')
    def _compute_amount_due(self):
        """Calculate the remaining unpaid balance for the supplier."""
        for payment in self:
            if payment.supplier_id:
                total_purchase = sum(payment.supplier_id.purchase_ids.mapped('total'))
                total_paid = sum(payment.supplier_id.payment_ids.mapped('amount'))
                payment.amount_due = total_purchase - total_paid
            else:
                payment.amount_due = 0.0

    # -------------------------
    # Backend Validation
    # -------------------------
    @api.constrains('amount', 'amount_due')
    def _check_payment_amount(self):
        """Validate supplier payment rules before saving the record."""
        for rec in self:

            # Rule 1: Prevent payment when there is no outstanding amount
            if rec.amount == 0 and rec.amount_due == 0:
                raise ValidationError(
                    "Payment cannot be recorded because the supplier has no outstanding balance."
                )

            # Rule 2: Amount must be greater than zero
            if rec.amount <= 0:
                raise ValidationError("Please enter an amount greater than zero.")

            # Rule 3: Supplier must have at least one purchase
            if rec.supplier_id.total_purchase == 0:
                raise ValidationError(
                    "This supplier has no recorded purchases. Payment is not allowed."
                )

            # Rule 4: Prevent negative outstanding balance
            if rec.amount_due < 0:
                raise ValidationError(
                    "Payment exceeds the supplier's total purchase amount. Please enter a valid amount."
                )





# from odoo import models, fields
#
# class PoultrySupplier(models.Model):
#     _name = 'poultry.supplier'
#     _description = 'Poultry Supplier'
#
#     name = fields.Char(string='Supplier Name', required=True)
#     phone = fields.Char(string='Phone')
#     email = fields.Char(string='Email')
#     address = fields.Text(string='Address')
#
#     # Optional: show linked purchases in supplier form
#     purchase_ids = fields.One2many('poultry.purchase', 'supplier_id', string='Purchases')
