# poultry_farm_management/models/farm.py
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class PoultryType(models.Model):
    _name = 'item.type'
    _description = 'Item Type'

    name = fields.Char(required=True)
    description = fields.Text()



class PoultryPurchase(models.Model):
    _name = 'poultry.purchase'
    _description = 'Poultry Purchase'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Date(required=True)
    branch_id = fields.Many2one('poultry.branch', required=True)
    item_type_id = fields.Many2one('item.type', string='Type', required=True)
    quantity = fields.Integer(default=1)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True,
                             default=lambda self: self.env.ref('uom.product_uom_unit'))
    unit_price = fields.Monetary(currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    supplier = fields.Char()
    total = fields.Monetary(currency_field='currency_id', compute='_compute_total', store=True)

    @api.depends('quantity', 'unit_price')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.quantity * rec.unit_price

    def write(self, vals):
        res = super(PoultryPurchase, self).write(vals)
        self._update_stock()
        return res

    @api.model
    def create(self, vals):
        rec = super(PoultryPurchase, self).create(vals)
        rec._update_stock()
        return rec

    def _update_stock(self):
        for rec in self:
            stock = self.env['poultry.farm'].search([
                ('branch_id', '=', rec.branch_id.id),
                ('item_type_id', '=', rec.item_type_id.id)
            ], limit=1)
            if stock:
                stock.total_quantity += rec.quantity
            else:
                self.env['poultry.farm'].create({
                    'branch_id': rec.branch_id.id,
                    'item_type_id': rec.item_type_id.id,
                    'total_quantity': rec.quantity,
                    'uom_id': rec.uom_id.id,
                })









class PoultrySale(models.Model):
    _name = 'poultry.sale'
    _description = 'Poultry Sale'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Date(required=True)
    branch_id = fields.Many2one('poultry.branch', required=True)
    item_type_id = fields.Many2one('item.type', string='Type', required=True)
    quantity = fields.Integer(string = "Quantity for Sale", default=1)
    unit_price = fields.Monetary(currency_field='currency_id', required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True,
                             default=lambda self: self.env.ref('uom.product_uom_unit'))
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    buyer = fields.Char()
    revenue = fields.Monetary(currency_field='currency_id', compute='_compute_revenue', store=True)

    available_quantity = fields.Integer(
        string="Available Quantity",
        compute='_compute_available_quantity',
        store=False
    )
    payment_type = fields.Selection([
        ('cash', 'Cash'),
        ('credit', 'Credit'),
    ], string="Payment Type", default='cash', required=True)

    amount_received = fields.Monetary(
        currency_field='currency_id',
        string="Amount Received",
        default=0.0,
        help="Amount paid by the customer at the time of sale."
    )

    amount_due = fields.Monetary(
        currency_field='currency_id',
        string="Amount Due",
        compute="_compute_amount_due",
        store=True
    )

    due_date = fields.Date(
        string="Due Date",
        help="Payment deadline if payment type is credit."
    )

    payment_status = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
    ], string="Payment Status", compute="_compute_payment_status", store=True)

    payment_note = fields.Text(string="Payment Notes")

    @api.constrains('unit_price')
    def _check_unit_price(self):
        for rec in self:
            if rec.unit_price <= 0:
                raise ValidationError("Unit Price must be greater than zero.")

    @api.depends('revenue', 'amount_received')
    def _compute_amount_due(self):
        for rec in self:
            rec.amount_due = rec.revenue - rec.amount_received

    @api.depends('amount_received', 'revenue')
    def _compute_payment_status(self):
        for rec in self:
            if rec.amount_received <= 0:
                rec.payment_status = 'not_paid'
            elif rec.amount_received < rec.revenue:
                rec.payment_status = 'partial'
            else:
                rec.payment_status = 'paid'

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        if self.payment_type == 'cash':
            self.due_date = False
            self.amount_received = self.revenue
        else:
            self.amount_received = 0








    @api.depends('branch_id', 'item_type_id')
    def _compute_available_quantity(self):
        """Compute available quantity based on branch and type"""
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
        for rec in self:
            rec.revenue = rec.quantity * rec.unit_price

    def write(self, vals):
        res = super(PoultrySale, self).write(vals)
        self._update_stock()
        return res

    @api.model
    def create(self, vals):
        rec = super(PoultrySale, self).create(vals)
        rec._update_stock()
        return rec

    # def _update_stock(self):
    #     for rec in self:
    #         stock = self.env['poultry.farm'].search([
    #             ('branch_id', '=', rec.branch_id.id),
    #             ('item_type_id', '=', rec.item_type_id.id)
    #         ], limit=1)
    #         if stock:
    #             stock.total_quantity -= rec.quantity
    #             if stock.total_quantity < 0:
    #                 stock.total_quantity = 0  # prevent negative stock
    #         else:
    #             raise UserError("No stock found for this branch and item type!")
    def _update_stock(self, old_qty=0, old_branch=None, old_type=None):
        for rec in self:

            # 1️⃣ Restore old quantity when editing
            if old_branch:
                old_stock = self.env['poultry.farm'].search([
                    ('branch_id', '=', old_branch.id),
                    ('item_type_id', '=', old_type.id)
                ], limit=1)
                if old_stock:
                    old_stock.total_quantity += old_qty

            # 2️⃣ Fetch current stock
            stock = self.env['poultry.farm'].search([
                ('branch_id', '=', rec.branch_id.id),
                ('item_type_id', '=', rec.item_type_id.id)
            ], limit=1)

            if not stock:
                raise UserError("No stock found for this branch and item type!")

            # 3️⃣ VALIDATION – Sale cannot exceed available stock
            if rec.quantity > stock.total_quantity:
                raise UserError(
                    f"Sale quantity ({rec.quantity}) cannot be greater "
                    f"than available stock ({stock.total_quantity})!"
                )

            # 4️⃣ Apply stock subtraction
            stock.total_quantity -= rec.quantity





class Feed(models.Model):
    _name = 'poultry.feed'
    _description = 'Feed Inventory'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # <-- Add chatter support

    name = fields.Char(required=True)
    branch_id = fields.Many2one('poultry.branch')
    quantity = fields.Float()
    unit = fields.Char(default='kg')
    purchase_price = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    date = fields.Date(string="Date Purchased", default=fields.Date.today)  # <-- add this

class Medicine(models.Model):
    _name = 'poultry.medicine'
    _description = 'Medicine Inventory'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # <-- Add chatter support

    name = fields.Char(required=True)
    branch_id = fields.Many2one('poultry.branch')
    quantity = fields.Float()
    purchase_price = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    date = fields.Date(string="Purchase Date", default=fields.Date.today)  # <-- add this

class Vaccination(models.Model):
    _name = 'poultry.vaccination'
    _description = 'Vaccination Schedule'

    name = fields.Char(required=True)
    item_type_id = fields.Many2one('item.type', string='Type')
    branch_id = fields.Many2one('poultry.branch')
    vaccine_name = fields.Char(required=True)
    vaccine_date = fields.Date(required=True)
    notes = fields.Text()
    responsible_id = fields.Many2one('poultry.employee', string='Responsible')
