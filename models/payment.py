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

    amount_due = fields.Monetary(
        string="Customer Total Due",
        currency_field='currency_id',
        compute="_compute_amount_due",
        store=False
    )

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

    @api.depends('customer_id')
    def _compute_amount_due(self):
        for rec in self:
            if rec.customer_id:
                # Get all sales of this customer
                sales = self.env['poultry.sale'].search([
                    ('customer_id', '=', rec.customer_id.id)
                ])
                total_sales = sum(sale.amount for sale in sales)

                # Get all payments made by this customer
                payments = self.env['poultry.payment'].search([
                    ('customer_id', '=', rec.customer_id.id)
                ])
                total_paid = sum(payment.amount for payment in payments)

                # Compute total due
                rec.amount_due = total_sales - total_paid
            else:
                rec.amount_due = 0

    @api.model
    def create(self, vals):
        payment = super(PoultryPayment, self).create(vals)
        sale = payment.sale_id
        if sale:
            # Optional: Update sale's amount_received field if you have it
            if hasattr(sale, 'amount_received'):
                sale.amount_received = sum(
                    self.env['poultry.payment'].search([('sale_id', '=', sale.id)]).mapped('amount')
                )

            # Optional: Update payment status if you have a field
            if hasattr(sale, 'payment_status') and hasattr(sale, 'revenue'):
                if sale.amount_received >= sale.revenue:
                    sale.payment_status = 'paid'
                elif sale.amount_received > 0:
                    sale.payment_status = 'partial'
                else:
                    sale.payment_status = 'not_paid'

        return payment
