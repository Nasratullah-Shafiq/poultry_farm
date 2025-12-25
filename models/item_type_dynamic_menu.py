from odoo import models, fields, api
from odoo.exceptions import UserError

class ItemType(models.Model):
    _inherit = "item.type"

    @api.model
    def create(self, vals):
        # Create the item type first
        rec = super(ItemType, self).create(vals)

        # Automatically create menu, tree view, and window action for this item type
        rec._create_stock_balance_menu_view()

        return rec

    def write(self, vals):
        # If name is updated, update the corresponding menu and action names dynamically
        res = super(ItemType, self).write(vals)
        for rec in self:
            if 'name' in vals:
                rec._update_stock_balance_menu_view()
        return res

    def unlink(self):
        IrUiMenu = self.env['ir.ui.menu']
        IrActWindow = self.env['ir.actions.act_window']
        IrUiView = self.env['ir.ui.view']

        for item in self:
            # 1️⃣ Delete child menu
            menu_name = f"{item.name} Stock"
            IrUiMenu.search([('name', '=', menu_name)]).unlink()

            # 2️⃣ Delete window action
            action_name = f"{item.name} Stock Action"
            IrActWindow.search([('name', '=', action_name)]).unlink()

            # 3️⃣ Delete tree view
            view_name = f"poultry_farm_tree_{item.id}"
            IrUiView.search([('name', '=', view_name)]).unlink()

        return super(ItemType, self).unlink()

    def _create_stock_balance_menu_view(self):
        """Create parent Stock Balance menu, tree view, window action, and child menu for this item type."""
        IrUiMenu = self.env['ir.ui.menu']
        IrActWindow = self.env['ir.actions.act_window']
        IrUiView = self.env['ir.ui.view']


        # 1️⃣ Get parent menu by XML ID
        parent_main_menu = self.env.ref('poultry_farm.menu_poultry_farm', raise_if_not_found=False)

        if not parent_main_menu:
            raise UserError("Parent menu 'menu_poultry_farm' not found. Check XML ID.")

        # 2️⃣ Create Stock Balance under poultry_farm menu
        parent_menu = IrUiMenu.search([('name', '=', 'Stock Balance')], limit=1)
        if not parent_menu:
            parent_menu = IrUiMenu.create({
                'name': 'Stock Balance',
                'sequence': 10,
                'parent_id': parent_main_menu.id,  # ⭐ Set parent here
            })

        for item in self:
            # 2️⃣ Create dynamic tree view
            view_name = f"poultry_farm_tree_{item.id}"
            view = IrUiView.search([('name', '=', view_name)], limit=1)
            if not view:
                view = IrUiView.create({
                    'name': view_name,
                    'type': 'tree',
                    'model': 'poultry.farm',
                    'arch_base': f"""
                        <tree string="{item.name} Stock" create="false" edit="false">
                            <field name="branch_id"/>
                            <field name="item_type_id"/>
                            <field name="total_quantity"/>
                            <field name="uom_id"/>
                            <field name="last_updated"/>
                        </tree>
                    """,
                })

            # 3️⃣ Create window action filtered for this item type
            action_name = f"{item.name} Stock Action"
            action = IrActWindow.search([('name', '=', action_name)], limit=1)
            if not action:
                action = IrActWindow.create({
                    'name': action_name,
                    'res_model': 'poultry.farm',
                    'view_mode': 'tree,form',
                    'view_id': view.id,
                    'domain': f"[('item_type_id','=',{item.id})]",
                })

            # 4️⃣ Create child menu for this item type under Stock Balance
            menu_name = f"{item.name} Stock"
            menu = IrUiMenu.search([('name', '=', menu_name)], limit=1)
            if not menu:
                IrUiMenu.create({
                    'name': menu_name,
                    'parent_id': parent_menu.id,
                    'action': f"ir.actions.act_window,{action.id}",
                })

    def _update_stock_balance_menu_view(self):
        """Update menu and action names if the item type name is changed"""
        IrUiMenu = self.env['ir.ui.menu']
        IrActWindow = self.env['ir.actions.act_window']

        for item in self:
            # Update child menu
            menu_name = f"{item.name} Stock"
            menu = IrUiMenu.search([('name', 'like', f"{item.name} Stock")], limit=1)
            if menu:
                menu.name = menu_name

            # Update action
            action_name = f"{item.name} Stock Action"
            action = IrActWindow.search([('name', 'like', f"{item.name} Stock Action")], limit=1)
            if action:
                action.name = action_name
