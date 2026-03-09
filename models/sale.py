from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
#
# class PoultrySale(models.Model):
#     _name = 'poultry.sale'  # Technical model name used internally by Odoo
#     _description = 'Poultry Sale'  # Human-readable description of the model
#     _inherit = ['mail.thread', 'mail.activity.mixin']  # Enable chatter & activity features
#
#     # ---------------------------
#     # Basic Sale Information
#     # ---------------------------
#     date = fields.Date(string="Date", required=True, default=fields.Date.today)  # Date of the sale (mandatory field)
#     branch_id = fields.Many2one(
#         'poultry.branch',
#         string="Branch",
#         required=True,
#         default=lambda self: self.env['poultry.branch'].search([], limit=1)
#     )  # Link to the branch where sale occurs
#
#     product_id = fields.Many2one('poultry.product', string='Product', required=True)
#     product_type = fields.Selection(
#         related='product_id.product_type',
#         string="Product Type",
#         store=True,
#         readonly=True,
#         tracking=True
#     )  # Type of poultry item being sold
#     quantity = fields.Integer(string="Quantity for Sale", default=1)  # Number of items sold, default is 1
#     sale_price = fields.Monetary(currency_field='currency_id', required=True)  # Price per unit in selected currency
#     purchase_price = fields.Monetary(string='Purchase Price', currency_field='currency_id', readonly=True)
#     uom_id = fields.Many2one(
#         'uom.uom', string='Unit of Measure', required=True,
#         default=lambda self: self.env.ref('uom.product_uom_unit')  # Default unit of measure is 1 piece
#     )
#     currency_id = fields.Many2one(
#         'res.currency', default=lambda self: self.env.company.currency_id
#     )  # Currency for the sale, defaults to company currency
#     customer_id = fields.Many2one(
#         'poultry.partner',
#         domain="[('partner_type','=','customer')]",
#         context={'default_partner_type': 'customer'}
#     )
#
#     farm_id = fields.Many2one('poultry.farm.house', string='Farm', required=True)
#
#     # ---------------------------
#     # Computed Fields
#     # ---------------------------
#     total = fields.Monetary(
#         currency_field='currency_id', compute='_compute_total', String="Total", store=True
#     )  # Total sale revenue = quantity * sale_price, stored in DB
#
#     available_quantity = fields.Integer(string="Available Quantity", compute='_compute_available_quantity', store=True)
#
#     status = fields.Selection(
#         [
#             ('new', 'New Sale'),
#             ('sale_done', 'Sale Done')
#         ],
#         string="Status",
#         default='new',
#         tracking=True
#     )
#
#     # ---------------------------
#     # Actions
#     # ---------------------------
#     def action_sale_done(self):
#         for rec in self:
#             if rec.total <= 0:
#                 raise ValidationError("Sale total must be greater than zero.")
#             rec._update_stock()
#             rec.status = 'sale_done'
#
#     # ---------------------------
#     # Constraints
#     # ---------------------------
#     @api.constrains('customer_id')
#     def _check_customer(self):
#         for rec in self:
#             if not rec.customer_id:
#                 raise UserError("Customer is required. Please select a customer.")
#
#     @api.constrains('sale_price')
#     def _check_sale_price(self):
#         for rec in self:
#             if rec.sale_price <= 0:
#                 raise ValidationError("Unit price must be greater than zero.")
#
#     @api.onchange('product_id')
#     def _onchange_product_id(self):
#         if self.product_id:
#             # Fetch latest purchase price
#             latest_purchase = self.env['poultry.purchase'].search(
#                 [('product_id', '=', self.product_id.id)],
#                 order='date desc', limit=1
#             )
#             self.purchase_price = latest_purchase.purchase_price if latest_purchase else 0
#
#     @api.depends('branch_id', 'farm_id', 'product_id')
#     def _compute_available_quantity(self):
#         for rec in self:
#             if rec.branch_id and rec.farm_id and rec.product_id:
#                 stock = self.env['poultry.stock'].search([
#                     ('branch_id', '=', rec.branch_id.id),
#                     ('farm_id', '=', rec.farm_id.id),
#                     ('product_id', '=', rec.product_id.id)
#                 ], limit=1)
#                 rec.available_quantity = stock.total_quantity if stock else 0
#             else:
#                 rec.available_quantity = 0
#
#     @api.depends('quantity', 'sale_price')
#     def _compute_total(self):
#         for rec in self:
#             rec.total = rec.quantity * rec.sale_price
#
#     # ---------------------------
#     # Create / Write Overrides
#     # ---------------------------
#     def write(self, vals):
#         old_quantities = {rec.id: rec.quantity for rec in self}
#         old_branches = {rec.id: rec.branch_id for rec in self}
#         old_products = {rec.id: rec.product_id for rec in self}
#
#         res = super().write(vals)
#
#         for rec in self:
#             old_qty = old_quantities.get(rec.id, 0)
#             old_branch = old_branches.get(rec.id)
#             old_product = old_products.get(rec.id)
#             rec._update_stock(old_qty, old_branch, old_product)
#
#         return res
#
#     @api.model
#     def create(self, vals):
#         rec = super().create(vals)
#         rec._update_stock()
#         return rec
#
#     # ---------------------------
#     # Stock Management
#     # ---------------------------
#     def _update_stock(self, old_qty=0, old_branch=None, old_product=None):
#         """Update stock after sale."""
#         for rec in self:
#
#             # Restore old stock if editing
#             if old_branch and old_product and old_qty > 0:
#                 old_stock = self.env['poultry.stock'].search([
#                     ('branch_id', '=', old_branch.id),
#                     ('product_id', '=', old_product.id)
#                 ], limit=1)
#                 if old_stock:
#                     old_stock.total_quantity += old_qty
#
#             # Current stock
#             stock = self.env['poultry.stock'].search([
#                 ('branch_id', '=', rec.branch_id.id),
#                 ('farm_id', '=', rec.farm_id.id),
#                 ('product_id', '=', rec.product_id.id)
#             ], limit=1)
#
#             if not stock:
#                 raise UserError("No stock found for this branch/farm/product!")
#
#             remaining_qty = stock.total_quantity - rec.quantity
#
#             stock.total_quantity = remaining_qty

# poultry_farm_management/models/farm.py


class PoultrySale(models.Model):
    _name = 'poultry.sale'
    _description = 'Poultry Sale'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ---------------------------
    # Basic Sale Information
    # ---------------------------
    date = fields.Date(string="Date", required=True, default=fields.Date.today)
    branch_id = fields.Many2one(
        'poultry.branch',
        string="Branch",
        required=True,
        default=lambda self: self.env['poultry.branch'].search([], limit=1)
    )
    farm_id = fields.Many2one('poultry.farm.house', string='Farm', required=True)
    product_id = fields.Many2one('poultry.product', string='Product', required=True)
    product_type = fields.Selection(
        related='product_id.product_type',
        string="Product Type",
        store=True,
        readonly=True,
        tracking=True
    )
    quantity = fields.Integer(string="Quantity for Sale", default=1)
    sale_price = fields.Monetary(currency_field='currency_id', required=True)
    purchase_price = fields.Monetary(string='Purchase Price', currency_field='currency_id', readonly=True)
    uom_id = fields.Many2one(
        'uom.uom', string='Unit of Measure', required=True,
        default=lambda self: self.env.ref('uom.product_uom_unit')
    )
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    customer_id = fields.Many2one(
        'poultry.partner',
        domain="[('partner_type','=','customer')]",
        context={'default_partner_type': 'customer'}
    )

    # ---------------------------
    # Computed Fields
    # ---------------------------
    total = fields.Monetary(
        currency_field='currency_id', compute='_compute_total', string="Total", store=True
    )
    available_quantity = fields.Integer(string="Available Quantity", compute='_compute_available_quantity', store=True)
    status = fields.Selection(
        [('new', 'New Sale'), ('sale_done', 'Sale Done')],
        string="Status",
        default='new',
        tracking=True
    )

    # ---------------------------
    # Actions
    # ---------------------------
    def action_sale_done(self):
        """Confirm the sale and subtract stock once."""
        for rec in self:
            if rec.total <= 0:
                raise ValidationError("Sale total must be greater than zero.")
            if rec.status != 'sale_done':
                rec._update_stock(subtract=True)
                rec.status = 'sale_done'

    # ---------------------------
    # Constraints & Validations
    # ---------------------------
    @api.constrains('customer_id')
    def _check_customer(self):
        for rec in self:
            if not rec.customer_id:
                raise UserError("Customer is required. Please select a customer.")

    @api.constrains('sale_price')
    def _check_sale_price(self):
        for rec in self:
            if rec.sale_price <= 0:
                raise ValidationError("Unit price must be greater than zero.")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            latest_purchase = self.env['poultry.purchase'].search(
                [('product_id', '=', self.product_id.id)],
                order='date desc', limit=1
            )
            self.purchase_price = latest_purchase.purchase_price if latest_purchase else 0

    @api.depends('branch_id', 'farm_id', 'product_id')
    def _compute_available_quantity(self):
        for rec in self:
            if rec.branch_id and rec.farm_id and rec.product_id:
                stock = self.env['poultry.stock'].search([
                    ('branch_id', '=', rec.branch_id.id),
                    ('farm_id', '=', rec.farm_id.id),
                    ('product_id', '=', rec.product_id.id)
                ], limit=1)
                rec.available_quantity = stock.total_quantity if stock else 0
            else:
                rec.available_quantity = 0

    @api.depends('quantity', 'sale_price')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.quantity * rec.sale_price

    # ---------------------------
    # Create / Write Overrides
    # ---------------------------
    def create(self, vals):
        rec = super().create(vals)
        # Stock will only be subtracted when sale is marked done
        return rec

    def write(self, vals):
        old_quantities = {rec.id: rec.quantity for rec in self}
        old_branches = {rec.id: rec.branch_id for rec in self}
        old_products = {rec.id: rec.product_id for rec in self}

        res = super().write(vals)

        for rec in self:
            # Only restore stock for edits if sale is not done
            if rec.status == 'new':
                old_qty = old_quantities.get(rec.id, 0)
                old_branch = old_branches.get(rec.id)
                old_product = old_products.get(rec.id)
                rec._update_stock(old_qty, old_branch, old_product, subtract=False)

        return res

    # ---------------------------
    # Stock Management
    # ---------------------------
    def _update_stock(self, old_qty=0, old_branch=None, old_product=None, subtract=True):
        """Update stock safely: restore old stock and subtract new stock only once."""
        for rec in self:
            # Restore old stock if editing
            if old_branch and old_product and old_qty > 0:
                old_stock = self.env['poultry.stock'].search([
                    ('branch_id', '=', old_branch.id),
                    ('farm_id', '=', rec.farm_id.id),
                    ('product_id', '=', old_product.id)
                ], limit=1)
                if old_stock:
                    old_stock.total_quantity += old_qty

            # Current stock
            stock = self.env['poultry.stock'].search([
                ('branch_id', '=', rec.branch_id.id),
                ('farm_id', '=', rec.farm_id.id),
                ('product_id', '=', rec.product_id.id)
            ], limit=1)

            if not stock:
                raise UserError("No stock found for this branch/farm/product!")

            if subtract:
                stock.total_quantity -= rec.quantity