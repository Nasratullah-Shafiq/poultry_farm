# poultry_farm_management/__manifest__.py
{
    'name': 'Poultry Farm Management',
    'version': '17.0.1.0.0',
    'category': 'Agriculture',
    # 'sequence': -200,
    'summary': 'Manage poultry purchases, sales, feed, medicine, HR and finance for multi-branch farms',
    'description': """
        Poultry Farm Management system:
        - Multi-branch (one main + two sub-branches)
        - Human Resources (employees, attendance placeholder, salaries)
        - Finance (income/expenses, branch reports)
        - Farm (poultry purchase/sales, feed & medicine inventory, vaccination schedules)
        """,
    'author': 'Nasratullah Shafiq / Generated',
    'depends': ['base', 'hr', 'account'],
    'data': [
        'security/ir.model.access.csv',

        # Menus should load first
        'views/menu.xml',

        # Wizard and view files
        'views/finance_report_wizard_views.xml',
        'views/branch_views.xml',
        'views/employee_views.xml',
        'views/finance_views.xml',
        'views/farm_views.xml',
        'views/feed_views.xml',
        'views/sales_views.xml',
        'views/medicine_views.xml',
        'views/poultry_views.xml',
        'views/poultry_sale_report_wizard_views.xml',
        'views/poultry_purchase_report_wizard_views.xml',
        'views/poultry_item_views.xml',
        'views/poultry_stock_move_views.xml',
        'views/death_views.xml',

        # Reports - actions before templates
        'report/finance_report_action.xml',
        'report/finance_report_template.xml',
        'report/poultry_purchase_report_template.xml',
        'report/poultry_sales_report_template.xml',
    ],

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
