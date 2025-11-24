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
                sales = self.env['poultry.sale'].search([('customer_id', '=', rec.customer_id.id)])
                total_due = sum(sale.revenue - sale.amount_paid for sale in sales)
                rec.amount_due = total_due
            else:
                rec.amount_due = 0

    @api.model
    def create(self, vals):
        payment = super(PoultryPayment, self).create(vals)
        if payment.sale_id:
            sale = payment.sale_id
            sale._compute_amount_paid()
            sale._compute_amount_due()
            sale._compute_payment_status()
        return payment

    def write(self, vals):
        res = super(PoultryPayment, self).write(vals)
        for rec in self:
            if rec.sale_id:
                rec.sale_id._compute_amount_paid()
                rec.sale_id._compute_amount_due()
                rec.sale_id._compute_payment_status()
        return res

    def unlink(self):
        sales_to_update = self.mapped('sale_id')
        res = super(PoultryPayment, self).unlink()
        for sale in sales_to_update:
            sale._compute_amount_paid()
            sale._compute_amount_due()
            sale._compute_payment_status()
        return res

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError("Payment amount must be greater than zero.")
            # Prevent overpayment
            if rec.sale_id:
                remaining_due = rec.sale_id.revenue - rec.sale_id.amount_paid
                if rec.amount > remaining_due:
                    raise ValidationError(
                        f"Payment amount cannot exceed remaining due for this sale ({remaining_due})."
                    )
            else:
                # If sale_id not selected, check against total customer due
                total_due = rec.amount_due
                if rec.amount > total_due:
                    raise ValidationError(
                        f"Payment amount cannot exceed total customer due ({total_due})."
                    )
