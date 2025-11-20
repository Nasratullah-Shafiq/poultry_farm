from odoo import models, fields, api



class PoultryPayment(models.Model):
    _name = 'poultry.payment'
    _description = 'Customer Payment'

    customer_id = fields.Many2one('poultry.customer', string="Customer", required=True)
    sale_id = fields.Many2one('poultry.sale', string="Sale")
    date = fields.Date(string="Payment Date", default=fields.Date.today(), required=True)
    amount = fields.Monetary(string="Amount Paid", required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    payment_note = fields.Text(string="Notes")

    @api.model
    def create(self, vals):
        payment = super(PoultryPayment, self).create(vals)
        sale = payment.sale_id
        if sale:
            # Add payment to sale
            sale.amount_received += payment.amount
            # Update payment status automatically
            if sale.amount_received >= sale.revenue:
                sale.payment_status = 'paid'
            elif sale.amount_received > 0:
                sale.payment_status = 'partial'
            else:
                sale.payment_status = 'not_paid'
        return payment
