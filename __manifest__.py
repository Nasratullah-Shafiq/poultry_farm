# poultry_farm_management/__manifest__.py
{
    'name': 'Poultry Farm Management',
    'version': '17.0.1.0.0',
    'category': 'Agriculture',
    'sequence': -200,
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
        'security/security.xml',
        'data/poultry_default_users.xml',

        # Menus should load first
        'views/menu.xml',

        # Wizard files
        'wizard/finance_report_wizard_views.xml',
        'wizard/sale_report_wizard_views.xml',
        'wizard/purchase_report_wizard_views.xml',
        'wizard/salary_payment_wizard_views.xml',
        'wizard/expense_report_wizard_views.xml',

        # view files
        'views/branch_views.xml',
        'views/employee_views.xml',
        'views/salary_payment_views.xml',
        'views/finance_views.xml',
        # 'views/farm_views.xml',
        'views/sales_views.xml',
        'views/poultry_views.xml',
        'views/poultry_item_views.xml',
        'views/cashier_views.xml',
        'views/death_views.xml',
        'views/customer_views.xml',
        'views/payment_views.xml',
        'views/purchase_views.xml',
        'views/poultry_farm_house_views.xml',
        'views/cash_account_views.xml',
        'views/cash_deposit_views.xml',
        'views/cash_transfer_views.xml',
        'views/expenses_views.xml',
        'views/money_account_views.xml',

        # Reports - actions before templates
        'report/finance_report_action.xml',
        'report/finance_report_template.xml',
        'report/purchase_report_template.xml',
        'report/sales_report_template.xml',
        'report/salary_payment_report_template.xml',
        'report/expense_report_template.xml',
    ],

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
