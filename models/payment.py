from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PoultryPayment(models.Model):
    _name = 'poultry.payment'
    _description = 'Customer Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    customer_id = fields.Many2one('poultry.customer', string='Customer', required=True, ondelete='cascade')

    sale_id = fields.Many2one('poultry.sale', string='Sale')

    date = fields.Date(string="Payment Date", default=fields.Date.today(), required=True)
    amount = fields.Monetary(string="Amount Paid", required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    payment_note = fields.Text(string="Notes")


    # -------------------------
    # Additional Fields
    # -------------------------
    payment_type = fields.Selection([
        ('cash', 'Cash'),
        ('credit', 'Credit')
    ], string="Payment Type", default='cash')

    # Amount due for this sale
    amount_due = fields.Monetary(
        string="Amount Due",
        currency_field='currency_id',
        compute="_compute_amount_due",
        store=True
    )

    # Payment status for this sale
    payment_status = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid')
    ], string="Payment Status", compute="_compute_payment_status", store=True)

    @api.onchange('sale_id')
    def _onchange_sale_id(self):
        if self.sale_id:
            self.customer_id = self.sale_id.customer_id

    # -------------------------
    # Computed Fields
    # -------------------------
    @api.depends('customer_id.sale_ids.total', 'customer_id.payment_ids.amount')
    def _compute_amount_due(self):
        for payment in self:
            if payment.customer_id:
                # Total sale of this customer
                total_sale = sum(payment.customer_id.sale_ids.mapped('total'))
                # Total paid by this customer
                total_paid = sum(payment.customer_id.payment_ids.mapped('amount'))
                # Remaining debt
                payment.amount_due = total_sale - total_paid
            else:
                payment.amount_due = 0.0

