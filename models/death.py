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

    item_type_id = fields.Many2one(
        'item.type',
        string="Poultry Type",
        required=True,
        help="The poultry type for the death record",
        store=True
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
                rec.death_month = str(rec.date.month)  # Correct field name
                rec.death_year = str(rec.date.year)  # Correct field name
            else:
                rec.death_month = False
                rec.death_year = False



    @api.constrains('quantity')
    def _check_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                raise UserError("Death quantity must be greater than zero.")

    @api.depends('branch_id', 'item_type_id')
    def _compute_death_count(self):
        """Sum of deaths for same branch & type"""
        for rec in self:
            if rec.branch_id and rec.item_type_id:
                deaths = self.env['poultry.death'].search([
                    ('branch_id', '=', rec.branch_id.id),
                    ('item_type_id', '=', rec.item_type_id.id)
                ])
                rec.death_count = sum(deaths.mapped('quantity'))
            else:
                rec.death_count = 0


    def _compute_death_statistics(self):
        """
        Compute:
        - Last 24 hours deaths
        - Current month deaths
        - Current year deaths
        """
        # We compute once and reuse for all records
        now = datetime.now()
        today = date.today()

        last_24h = now - timedelta(hours=24)
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)

        Death = self.env['poultry.death']

        # Last 24 hours
        last_24h_total = sum(
            Death.search([
                ('date', '>=', last_24h.date())
            ]).mapped('quantity')
        )

        # Current month
        month_total = sum(
            Death.search([
                ('date', '>=', month_start),
                ('date', '<=', today)
            ]).mapped('quantity')
        )

        # Current year
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



    @api.depends('branch_id', 'item_type_id')
    def _compute_death_count(self):
        for rec in self:
            deaths = self.env['poultry.death'].search([
                ('branch_id', '=', rec.branch_id.id),
                ('item_type_id', '=', rec.item_type_id.id)
            ])
            rec.death_count = sum(d.quantity for d in deaths)

    @api.depends('branch_id', 'item_type_id', 'farm_id')
    def _compute_total_poultry(self):
        for rec in self:
            if not rec.branch_id or not rec.item_type_id or not rec.farm_id:
                rec.total_poultry = 0
                continue

            farms = self.env['poultry.farm'].search([
                ('branch_id', '=', rec.branch_id.id),
                ('item_type_id', '=', rec.item_type_id.id),
                ('farm_id', '=', rec.farm_id.id),
            ])

            rec.total_poultry = sum(f.total_quantity for f in farms)

    # @api.depends('branch_id', 'item_type_id')
    # def _compute_total_poultry(self):
    #     for rec in self:
    #         farms = self.env['poultry.farm'].search([
    #             ('branch_id', '=', rec.branch_id.id),
    #             ('item_type_id', '=', rec.item_type_id.id)
    #         ])
    #         rec.total_poultry = sum(f.total_quantity for f in farms)

    # -------------------------
    # Helpers to modify stock
    # -------------------------
    def _get_farm_stock(self, branch_id, item_type_id):
        """Return the poultry.farm record for branch+type or None"""
        return self.env['poultry.farm'].search([
            ('branch_id', '=', branch_id),
            ('item_type_id', '=', item_type_id)
        ], limit=1)

    def _ensure_sufficient_stock(self, farm_record, qty):
        """Raise if farm_record missing or does not have at least qty available"""
        if not farm_record:
            raise UserError("No stock found for branch %s and type %s. Add purchases first." %
                            (self.env['poultry.branch'].browse(self.branch_id.id).name if self.branch_id else branch_id,
                             self.env['item.type'].browse(
                                 self.item_type_id.id).name if self.item_type_id else item_type_id))
        if farm_record.total_quantity < qty:
            raise UserError("Insufficient stock to record this death. Available: %s, Requested: %s" %
                            (farm_record.total_quantity, qty))



    def _update_stock(self, old_qty=0, old_branch=None, old_type=None):
        """
        Update stock in poultry.farm when deaths are recorded.
        Handles create, update, and delete with validation.
        """
        for rec in self:

            # ------------------------------------------------
            # 1️⃣ REVERT OLD STOCK (when editing)
            # ------------------------------------------------
            if old_branch:
                old_stock = self.env['poultry.farm'].search([
                    ('branch_id', '=', old_branch.id),
                ], limit=1)

                if old_stock:
                    old_stock.total_quantity += old_qty

            # ------------------------------------------------
            # 2️⃣ GET CURRENT STOCK FOR NEW WRITE/CREATE
            # ------------------------------------------------
            stock = self.env['poultry.farm'].search([
                ('branch_id', '=', rec.branch_id.id),
            ], limit=1)

            if not stock:
                raise UserError("No poultry stock found for this branch!")

            # ------------------------------------------------
            # 3️⃣ VALIDATION — DEAD CHICKENS > AVAILABLE STOCK
            # ------------------------------------------------
            if rec.quantity > stock.total_quantity:
                raise UserError(
                    f"Invalid Entry!\n"
                    f"Death quantity ({rec.quantity}) cannot be greater "
                    f"than available stock ({stock.total_quantity})."
                )

            # ------------------------------------------------
            # 4️⃣ APPLY NEW STOCK (subtract)
            # ------------------------------------------------
            stock.total_quantity -= rec.quantity

    # ======================================================
    # OVERRIDE CREATE
    # ======================================================
    @api.model
    def create(self, vals):
        rec = super().create(vals)
        rec._update_stock()
        return rec

    # ======================================================
    # OVERRIDE WRITE
    # ======================================================
    def write(self, vals):
        for rec in self:
            old_qty = rec.quantity
            old_branch = rec.branch_id
            old_type = None  # remove if not needed

            res = super(PoultryDeath, rec).write(vals)
            rec._update_stock(old_qty, old_branch, old_type)

        return True

    # ======================================================
    # OVERRIDE DELETE
    # ======================================================
    def unlink(self):
        for rec in self:
            stock = self.env['poultry.farm'].search([
                ('branch_id', '=', rec.branch_id.id),
            ], limit=1)

            if stock:
                stock.total_quantity += rec.quantity  # restore

        return super().unlink()