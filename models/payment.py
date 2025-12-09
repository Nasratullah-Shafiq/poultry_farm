from odoo.exceptions import ValidationError
from odoo import models, fields, api


class PoultryPayment(models.Model):
    _name = 'poultry.payment'
    _description = 'Customer Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # -------------------------
    # Basic Fields
    # -------------------------
    customer_id = fields.Many2one('poultry.customer', string='Customer', required=True, ondelete='cascade')
    sale_id = fields.Many2one('poultry.sale', string='Sale')
    date = fields.Date(string="Payment Date", default=fields.Date.today(), required=True)
    amount = fields.Monetary(string="Amount Paid", required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
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

    # Computed amount due
    amount_due = fields.Monetary(
        string="Amount Due",
        currency_field='currency_id',
        compute="_compute_amount_due",
        store=True
    )

    # -------------------------
    # Onchange Logic
    # -------------------------
    @api.onchange('sale_id')
    def _onchange_sale_id(self):
        """Automatically set the customer based on the selected sale."""
        if self.sale_id:
            self.customer_id = self.sale_id.customer_id

    # -------------------------
    # Compute Functions
    # -------------------------
    @api.depends('customer_id.sale_ids.total', 'customer_id.payment_ids.amount')
    def _compute_amount_due(self):
        """Calculate the remaining unpaid balance for the customer."""
        for payment in self:
            if payment.customer_id:
                total_sale = sum(payment.customer_id.sale_ids.mapped('total'))
                total_paid = sum(payment.customer_id.payment_ids.mapped('amount'))
                payment.amount_due = total_sale - total_paid
            else:
                payment.amount_due = 0.0

    # -------------------------
    # Backend Validation
    # -------------------------
    @api.constrains('amount', 'amount_due')
    def _check_payment_amount(self):
        """Validate payment rules before saving the record."""
        for rec in self:

            # Rule 1: Prevent payment when there is no outstanding amount
            if rec.amount == 0 and rec.amount_due == 0:
                raise ValidationError(
                    "Payment cannot be recorded because the customer has no outstanding balance."
                )

            # Rule 2: Amount must be greater than zero
            if rec.amount <= 0:
                raise ValidationError("Please enter an amount greater than zero.")

            # Rule 3: Customer must have at least one sale
            if rec.customer_id.total_sale == 0:
                raise ValidationError(
                    "This customer has no recorded sales. Payment is not allowed."
                )

            # Rule 4: Prevent negative outstanding balance
            if rec.amount_due < 0:
                raise ValidationError(
                    "Payment exceeds the customer's total sale amount. Please enter a valid amount."
                )

            # Rule 5: Prevent paying more than the amount due
            if rec.amount > rec.amount_due:
                raise ValidationError(
                    f"The payment amount cannot exceed the remaining balance. Amount Due: {rec.amount_due}"
                )

