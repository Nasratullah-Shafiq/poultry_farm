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






    # @api.depends('sale_id.total', 'sale_id.payment_ids.amount')
    # def _compute_payment_status(self):
    #     for rec in self:
    #         if rec.sale_id:
    #             total_paid = sum(rec.sale_id.payment_ids.mapped('amount'))
    #             if total_paid <= 0:
    #                 rec.payment_status = 'not_paid'
    #             elif total_paid < rec.sale_id.total:
    #                 rec.payment_status = 'partial'
    #             else:
    #                 rec.payment_status = 'paid'
    #         else:
    #             rec.payment_status = 'not_paid'

    # @api.depends('customer_id')
    # def _compute_amount_due(self):
    #     for rec in self:
    #         if rec.customer_id:
    #             # Get all unpaid sales of this customer
    #             sales = self.env['poultry.sale'].search([
    #                 ('customer_id', '=', rec.customer_id.id)
    #             ])
    #
    #             # Sum total due
    #             total_due = sum(sale.amount_due for sale in sales)
    #
    #             rec.amount_due = total_due
    #         else:
    #             rec.amount_due = 0
    #
    # @api.model
    # def create(self, vals):
    #     payment = super(PoultryPayment, self).create(vals)
    #     sale = payment.sale_id
    #     if sale:
    #         # Add payment to sale
    #         sale.amount_received += payment.amount
    #         # Update payment status automatically
    #         if sale.amount_received >= sale.revenue:
    #             sale.payment_status = 'paid'
    #         elif sale.amount_received > 0:
    #             sale.payment_status = 'partial'
    #         else:
    #             sale.payment_status = 'not_paid'
    #     return payment

    # @api.depends('customer_id')
    # def _compute_amount_due(self):
    #     for rec in self:
    #         if rec.customer_id:
    #             sales = self.env['poultry.sale'].search([('customer_id', '=', rec.customer_id.id)])
    #             total_due = sum(sale.total - sale.amount_paid for sale in sales)
    #             rec.amount_due = total_due
    #         else:
    #             rec.amount_due = 0

    # @api.model
    # def create(self, vals):
    #     payment = super(PoultryPayment, self).create(vals)
    #     if payment.sale_id:
    #         sale = payment.sale_id
    #         sale._compute_amount_paid()
    #         sale._compute_amount_due()
    #         sale._compute_payment_status()
    #     return payment

    # def write(self, vals):
    #     res = super(PoultryPayment, self).write(vals)
    #     for rec in self:
    #         if rec.sale_id:
    #             rec.sale_id._compute_amount_paid()
    #             rec.sale_id._compute_amount_due()
    #             rec.sale_id._compute_payment_status()
    #     return res

    # def unlink(self):
    #     sales_to_update = self.mapped('sale_id')
    #     res = super(PoultryPayment, self).unlink()
    #     for sale in sales_to_update:
    #         sale._compute_amount_paid()
    #         sale._compute_amount_due()
    #         sale._compute_payment_status()
    #     return res

    # @api.constrains('amount')
    # def _check_amount(self):
    #     for rec in self:
    #         if rec.amount <= 0:
    #             raise ValidationError("Payment amount must be greater than zero.")
    #         # Prevent overpayment
    #         if rec.sale_id:
    #             remaining_due = rec.sale_id.revenue - rec.sale_id.amount_paid
    #             if rec.amount > remaining_due:
    #                 raise ValidationError(
    #                     f"Payment amount cannot exceed remaining due for this sale ({remaining_due})."
    #                 )
    #         else:
    #             # If sale_id not selected, check against total customer due
    #             total_due = rec.amount_due
    #             if rec.amount > total_due:
    #                 raise ValidationError(
    #                     f"Payment amount cannot exceed total customer due ({total_due})."
    #                 )
