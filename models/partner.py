from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError



class PoultryPartner(models.Model):
    _name = 'poultry.partner'
    _description = 'Partner (Customer/Supplier)'

    name = fields.Char(string="Name", required=True)
    partner_type = fields.Selection([
        ('customer', 'Customer'),
        ('supplier', 'Supplier')
    ], string="Partner Type", required=True)
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    address = fields.Text(string="Address")
    note = fields.Text(string="Notes")

    # CUSTOMER SALES
    sale_ids = fields.One2many('poultry.sale', 'customer_id', string='Sales')

    # SUPPLIER PURCHASES
    purchase_ids = fields.One2many('poultry.purchase', 'supplier_id', string='Purchases')


    payment_ids = fields.One2many('poultry.payment', 'partner_id', string='Payments')


    # ACCOUNTING FIELDS
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True
    )

    total_amount = fields.Monetary(
        string="Total Amount",
        currency_field='currency_id',
        compute="_compute_accounting",
        store=True
    )

    amount_paid = fields.Monetary(
        string="Amount Paid",
        currency_field='currency_id',
        compute="_compute_accounting",
        store=True
    )

    amount_due = fields.Monetary(
        string="Amount Due",
        currency_field='currency_id',
        compute="_compute_accounting",
        store=True
    )

    # COMPUTE METHOD

    @api.depends('sale_ids.total', 'purchase_ids.total', 'payment_ids.amount')
    def _compute_amounts(self):

        for partner in self:
            if partner.partner_type == 'customer':
                total = sum(partner.sale_ids.mapped('total'))
                paid = sum(
                    partner.payment_ids.filtered(
                        lambda p: p.partner_type == 'customer'
                    ).mapped('amount')
                )
            elif partner.partner_type == 'supplier':
                total = sum(partner.purchase_ids.mapped('total'))
                paid = sum(
                    partner.payment_ids.filtered(
                        lambda p: p.partner_type == 'supplier'
                    ).mapped('amount')
                )
            else:
                total = 0
                paid = 0
            partner.total_amount = total
            partner.amount_paid = paid
            partner.amount_due = total - paid





    # PAYMENTS

    # PAYMENTS (computed to avoid KeyError)
    # payment_ids = fields.One2many(
    #     'poultry.payment',
    #     'partner_id',
    #     string='Payments',
    #     compute='_compute_payments',
    #     store=False
    # )
    #
    # @api.depends()
    # def _compute_payments(self):
    #     for rec in self:
    #         rec.payment_ids = self.env['poultry.payment'].search([('partner_id', '=', rec.id)])



# class PoultryPayment(models.Model):
#
#     _name = 'poultry.payment'
#     _description = 'Partner Payment'
#     _inherit = ['mail.thread']
#     _order = 'date desc'
#
#     # PARTNER INFO
#     partner_id = fields.Many2one('poultry.partner', required=True, tracking=True)
#     partner_type = fields.Selection(related='partner_id.partner_type', store=True)
#     date = fields.Date(default=fields.Date.today, required=True)
#     amount = fields.Float(required=True)
#     note = fields.Text()
#
#     # CASH ACCOUNT
#     cash_account_id = fields.Many2one('poultry.cash.account', required=True)
#     state = fields.Selection([('draft', 'Draft'),('posted', 'Posted')], default='draft')
#
#     # ======================
#     # POST PAYMENT
#     # ======================
#
#     def action_post(self):
#         for rec in self:
#             if rec.state == 'posted':
#                 raise ValidationError("Already posted")
#
#             if rec.amount <= 0:
#                 raise ValidationError("Amount must be positive")
#
#             # CUSTOMER PAYMENT
#             if rec.partner_type == 'customer':
#                 rec.cash_account_id.balance += rec.amount
#
#
#             # SUPPLIER PAYMENT
#             elif rec.partner_type == 'supplier':
#                 if rec.cash_account_id.balance < rec.amount:
#                     raise ValidationError(
#                         "Insufficient balance"
#                     )
#                 rec.cash_account_id.balance -= rec.amount
#             rec.state = 'posted'
#
#
