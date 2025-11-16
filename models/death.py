from odoo import models, fields, api
from odoo.exceptions import UserError


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

    @api.depends('branch_id')
    def _compute_total_poultry(self):
        """Sum total_quantity of all poultry.farm records in the selected branch"""
        for rec in self:
            if rec.branch_id:
                quants = self.env['poultry.farm'].search([('branch_id', '=', rec.branch_id.id)])
                rec.total_poultry = sum(quants.mapped('total_quantity'))
            else:
                rec.total_poultry = 0

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
                             self.env['item.type'].browse(self.item_type_id.id).name if self.item_type_id else item_type_id))
        if farm_record.total_quantity < qty:
            raise UserError("Insufficient stock to record this death. Available: %s, Requested: %s" %
                            (farm_record.total_quantity, qty))
