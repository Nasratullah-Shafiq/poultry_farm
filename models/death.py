from odoo.exceptions import UserError

from odoo import SUPERUSER_ID
from odoo import models, fields, api


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

    date = fields.Date(
        string="Date of Death",
        required=True,
        default=fields.Date.today
    )

    quantity = fields.Integer(
        string="Number of Dead Birds",
        required=True
    )

    reason = fields.Selection(
        [
            ('disease', 'Disease'),
            ('injury', 'Injury'),
            ('natural', 'Natural Cause'),
            ('unknown', 'Unknown')
        ],
        string="Reason",
        required=True
    )

    description = fields.Text(string="Additional Notes")
    notes = fields.Text(string="Additional Notes")

    death_count = fields.Integer(
        string="Total Deaths in Batch",
        compute="_compute_death_count",
        store=True
    )

    item_type_id = fields.Many2one(
        'item.type',
        string="Poultry Type",
        required=True,
        help="The poultry type for the death record"
    )

    # ✅ Computed remaining quantity based on poultry type AND branch
    remaining_quantity = fields.Integer(
        string="Remaining Quantity",
        # compute='_compute_remaining_quantity',
        store=False,
        readonly=True
    )

    # total poultry in the selected branch (all types)
    total_poultry = fields.Integer(
        string="Total Poultry in Branch",
        compute="_compute_total_poultry",
        store=False,
        readonly=True
    )

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

    # @api.depends('branch_id')
    # def _compute_total_poultry(self):
    #     """Sum total_quantity of all poultry.farm records in the selected branch"""
    #     for rec in self:
    #         if rec.branch_id:
    #             quants = self.env['poultry.farm'].search([('branch_id', '=', rec.branch_id.id)])
    #             rec.total_poultry = sum(quants.mapped('total_quantity'))
    #         else:
    #             rec.total_poultry = 0

    @api.depends('branch_id')
    def _compute_death_count(self):
        for rec in self:
            deaths = self.env['poultry.death'].search([
                ('branch_id', '=', rec.branch_id.id),
                ('item_type_id', '=', rec.item_type_id.id)
            ])
            rec.death_count = sum(d.quantity for d in deaths)

    @api.depends('branch_id', 'item_type_id')
    def _compute_total_poultry(self):
        for rec in self:
            farms = self.env['poultry.farm'].search([
                ('branch_id', '=', rec.branch_id.id),
                ('item_type_id', '=', rec.item_type_id.id)
            ])
            rec.total_poultry = sum(f.total_quantity for f in farms)

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

        # ---------------- STOCK UPDATE LOGIC ------------------

    # def _update_stock(self, old_qty=0, old_branch=None, old_type=None):
    #     """
    #     Subtract death quantity from poultry.farm (like sales logic).
    #     Handles create, update, and delete.
    #     """
    #
    #     for rec in self:
    #         branch = rec.branch_id
    #         ptype = rec.item_type_id
    #
    #         # 1️⃣ REVERT OLD STOCK (if editing or deleting)
    #         if old_branch and old_type:
    #             old_stock = self.env['poultry.farm'].search([
    #                 ('branch_id', '=', old_branch.id),
    #                 ('item_type_id', '=', old_type.id)
    #             ], limit=1)
    #             if old_stock:
    #                 old_stock.total_quantity += old_qty  # return old stock
    #
    #         # 2️⃣ APPLY NEW STOCK (subtract)
    #         stock = self.env['poultry.farm'].search([
    #             ('branch_id', '=', branch.id),
    #
    #         ], limit=1)
    #
    #         if not stock:
    #             raise UserError("No stock found for this branch and type!")
    #
    #         new_qty = stock.total_quantity - rec.quantity
    #         stock.total_quantity = new_qty if new_qty >= 0 else 0
    #
    #     # ---------------- OVERRIDE CREATE ------------------
    #
    # @api.model
    #
    # def create(self, vals):
    #     rec = super().create(vals)
    #     rec._update_stock()
    #     return rec
    #
    # # ---------------- OVERRIDE WRITE ------------------
    #
    # def write(self, vals):
    #     for rec in self:
    #         old_qty = rec.quantity
    #         old_branch = rec.branch_id
    #         old_type = rec.item_type_id
    #
    #         res = super(PoultryDeath, rec).write(vals)
    #
    #         rec._update_stock(old_qty, old_branch, old_type)
    #
    #     return True
    #
    # # ---------------- OVERRIDE DELETE ------------------
    #
    # def unlink(self):
    #     for rec in self:
    #         stock = self.env['poultry.farm'].search([
    #             ('branch_id', '=', rec.branch_id.id),
    #             ('item_type_id', '=', rec.item_type_id.id)
    #         ], limit=1)
    #
    #         if stock:
    #             stock.total_quantity += rec.quantity  # return quantity
    #
    #     return super().unlink()

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