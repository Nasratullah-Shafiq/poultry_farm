from odoo import SUPERUSER_ID
from odoo import models, fields, api
from odoo.exceptions import UserError

from datetime import datetime, timedelta, date


class PoultryDeath(models.Model):
    _name = 'poultry.death'
    _description = 'Poultry Death Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'date'

    branch_id = fields.Many2one(
        'poultry.branch',
        string="Branch",
        # readonly=True,
        store=True,
        help="Branch is automatically fetched from the Poultry Batch"
    )

    date = fields.Date(string="Date of Death", required=True, default=fields.Date.today)
    quantity = fields.Integer(string="Number of Dead Birds", required=True)
    description = fields.Text(string="Additional Notes")
    notes = fields.Text(string="Additional Notes")
    death_count = fields.Integer(string="Total Deaths in Batch", compute="_compute_death_count", store=True)
    reason = fields.Selection(
        [
            ('disease', 'Disease'),
            ('injury', 'Injury'),
            ('natural', 'Natural Cause'),
            ('unknown', 'Unknown')
        ],
        string="Reason",
        required=True,
        default='disease'
    )

    product_type = fields.Selection(
        [
            ('chicken', 'Chicken'),
            ('feed', 'Feed'),
            ('medicine', 'Medicine'),
        ],
        string="Product Type",
        default='chicken',
        required=True
    )

    # total poultry in the selected branch (all types)
    total_poultry = fields.Integer(
        string="Total Poultry in Branch",
        compute="_compute_total_poultry",
        store=False,
        readonly=True
    )

    # --------------------------------------------------
    # KPI FIELDS (Statistics Cards)
    # --------------------------------------------------

    death_last_24h = fields.Integer(
        string="Deaths (Last 24 Hours)",
        compute="_compute_death_statistics"
    )

    death_current_month = fields.Integer(
        string="Deaths (This Month)",
        compute="_compute_death_statistics"
    )

    death_current_year = fields.Integer(
        string="Deaths (This Year)",
        compute="_compute_death_statistics"
    )
    farm_id = fields.Many2one(
        'poultry.farm.house',
        string="Farm",
        domain="[('branch_id', '=', branch_id)]"
    )

    # Month as Selection
    death_month = fields.Selection(
        [
            ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
            ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
            ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
        ],
        string="Month",
        compute="_compute_year_month",
        store=True
    )

    # Year as Selection
    death_year = fields.Selection(
        selection=lambda self: [
            (str(y), str(y))
            for y in range(date.today().year - 10, date.today().year + 1)
        ],
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
                rec.death_month = str(rec.date.month)
                rec.death_year = str(rec.date.year)
            else:
                rec.death_month = False
                rec.death_year = False

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    @api.constrains('quantity')
    def _check_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                raise UserError("Death quantity must be greater than zero.")

    # --------------------------------------------------
    # COMPUTE TOTAL DEATH COUNT
    # --------------------------------------------------

    @api.depends('branch_id', 'product_type', 'farm_id')
    def _compute_total_poultry(self):
        for rec in self:
            if not rec.branch_id or not rec.product_type or not rec.farm_id:
                rec.total_poultry = 0
                continue

            stocks = self.env['poultry.stock'].search([
                ('branch_id', '=', rec.branch_id.id),
                ('farm_id', '=', rec.farm_id.id),
                ('product_type', '=', rec.product_type),
            ])

            rec.total_poultry = sum(stocks.mapped('total_quantity'))

    # --------------------------------------------------
    # COMPUTE TOTAL POULTRY IN FARM
    # --------------------------------------------------

    @api.depends('branch_id', 'product_type', 'farm_id')
    def _compute_total_poultry(self):
        for rec in self:
            if not rec.branch_id or not rec.product_type or not rec.farm_id:
                rec.total_poultry = 0
                continue

            stocks = self.env['poultry.stock'].search([
                ('branch_id', '=', rec.branch_id.id),
                ('farm_id', '=', rec.farm_id.id),
                ('product_type', '=', rec.product_type),
            ])

            rec.total_poultry = sum(stocks.mapped('total_quantity'))

    # --------------------------------------------------
    # DEATH STATISTICS
    # --------------------------------------------------

    def _compute_death_statistics(self):
        now = datetime.now()
        today = date.today()

        last_24h = now - timedelta(hours=24)
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)

        Death = self.env['poultry.death']

        last_24h_total = sum(
            Death.search([('date', '>=', last_24h.date())]).mapped('quantity')
        )

        month_total = sum(
            Death.search([
                ('date', '>=', month_start),
                ('date', '<=', today)
            ]).mapped('quantity')
        )

        year_total = sum(
            Death.search([
                ('date', '>=', year_start),
                ('date', '<=', today)
            ]).mapped('quantity')
        )

        for rec in self:
            rec.death_last_24h = last_24h_total
            rec.death_current_month = month_total
            rec.death_current_year = year_total

    # --------------------------------------------------
    # STOCK UPDATE LOGIC
    # --------------------------------------------------

    def _update_stock(self, old_qty=0, old_branch=None, old_farm=None):
        for rec in self:

            # Restore old stock when editing
            if old_branch and old_farm:
                old_stock = self.env['poultry.stock'].search([
                    ('branch_id', '=', old_branch.id),
                    ('farm_id', '=', old_farm.id),
                    ('product_type', '=', rec.product_type),
                ], limit=1)

                if old_stock:
                    old_stock.total_quantity += old_qty

            stock = self.env['poultry.stock'].search([
                ('branch_id', '=', rec.branch_id.id),
                ('farm_id', '=', rec.farm_id.id),
                ('product_type', '=', rec.product_type),
            ], limit=1)

            if not stock:
                raise UserError(
                    "No poultry stock found for the selected branch, farm, and product type!"
                )

            remaining_qty = stock.total_quantity - rec.quantity

            if remaining_qty < 0:
                raise UserError(
                    f"Invalid Entry!\n"
                    f"Death quantity ({rec.quantity}) exceeds available stock ({stock.total_quantity})."
                )

            stock.total_quantity = remaining_qty

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        rec._update_stock()
        return rec

    # --------------------------------------------------
    # WRITE
    # --------------------------------------------------

    def write(self, vals):
        for rec in self:
            old_qty = rec.quantity
            old_branch = rec.branch_id
            old_farm = rec.farm_id

            super(PoultryDeath, rec).write(vals)
            rec._update_stock(old_qty, old_branch, old_farm)

        return True

    # --------------------------------------------------
    # DELETE
    # --------------------------------------------------

    def unlink(self):
        for rec in self:
            stock = self.env['poultry.stock'].search([
                ('branch_id', '=', rec.branch_id.id),
                ('farm_id', '=', rec.farm_id.id),
                ('product_type', '=', rec.product_type),
            ], limit=1)

            if stock:
                stock.total_quantity += rec.quantity

        return super().unlink()