from __future__ import print_function, division
# from . import createinvoice
"""
from __future__ import print_function
sudo su -  odoo9 -s /bin/bash 
./odoo.py shell -d <dbname>
account_invoice_obj = env['account.invoice']

"""
"""
from openerp import api, fields, models
import datetime
import time
from datetime import date,timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)
"""
ERRORFILE = '/var/tmp/errfile.csv'

errfile = open(ERRORFILE, 'a')


class ReportInvoice():
    """ out_invoice is customer invoice, not vendor bill"""

    def listInvoices(self, mydate, invtype):
        """ List all customer invoices greater than mydate
           invtype is 'out_invoice' for Customer invoice or 'in_invoice' for vendor bills
        """
        account_invoice_obj = env['account.invoice'].search([('date_invoice', '>', mydate), \
                                                             ('type', '=', invtype), ('user_id.name', '=', 'Moses')])
        prt = 'Date,Customer,product,qty,unitprice\n'
        prtl = ""
        for invoice in account_invoice_obj:
            lenlines = len(invoice.invoice_line_ids)
            if invoice.date_invoice and lenlines > 0:
                prt = prt + str(invoice.date_invoice) + ',' + str(invoice.partner_id.name) + ',' + \
                      str(invoice.invoice_line_ids[0].name) + ',' + str(invoice.invoice_line_ids[0].quantity) \
                      + ',' + str(invoice.invoice_line_ids[0].price_unit) + '\n'
                lenlines = len(invoice.invoice_line_ids)

                prtl = ""
                for k in range(1, lenlines):
                    prtl = ',,' + str(invoice.invoice_line_ids[k].name) + ',' + str(
                        invoice.invoice_line_ids[k].quantity) \
                           + ',' + str(invoice.invoice_line_ids[k].price_unit) + '\n'

                    prt = prt + prtl
        return prt

    """ out_invoice is customer invoice, not vendor bill
	in_invoice is vendor bill
	"""

    def totalInvoices(self, mydate, invtype):
        """ List all customer invoice totals by customer greater than mydate
           invtype is 'out_invoice' for Customer invoice or 'in_invoice' for vendor bills
        """
        ercount = 0
        account_invoice_obj = env['account.invoice'].search([('date_invoice', '>', mydate), \
                                                             ('type', '=', invtype), ('user_id.name', '=', 'Moses')])
        prt = 'Date,Customer,Amount,Reference\n'
        prtl = ""
        partner_totals = {}
        # for invoice in account_invoice_obj:
        #    partner_totals[invoice.partner_id.name] = 0

        for invoice in account_invoice_obj:
            try:
                partner_totals[invoice.partner_id.name] = partner_totals[invoice.partner_id.name] + \
                                                          invoice.amount_total

                if invoice.date_invoice and invoice.amount_total > 0:
                    prt = prt + str(invoice.date_invoice) + ',' + str(invoice.partner_id.name) + ',' + \
                          str(invoice.amount_total) + ',' + str(invoice.reference) + '\n'

            except KeyError as e:
                partner_totals[invoice.partner_id.name] = invoice.amount_total

                ercount = ercount + 1
                print('Errors,', e.args[0], ',', ercount, file, file=errfile)
                continue
        prt = prt + str(partner_totals)

        return prt


class createinvoice():
    _name = 'createinvoice'
    _description = 'Fido Invoice Creation'
    """
    Create invoice for existing Partner,
    Create invoice for non-existing partner
    Modify invoice to add salesperson
    Modify res.partner  to add salesperson

    """
    comment = "Sales Invoice"
    teamid = 1

    currency_id = 123
    account_id = 1
    payment_term_id = 1

    def crinvoice(self, partner, lines, invtype):
        """ Create invoice in odoo
        """

        # Test with that user which have rights to make Invoicing and payment and who is accountant.
        # Create a customer invoice
        account_invoice_obj = env['account.invoice']

        # Use Sales Journal
        journalrec = env['account.journal'].search([('type', '=', 'sale')])[0]
        partner_id = env['res.partner'].search([('name', '=', partner)])
        account_user_type = env.ref('account.data_account_type_receivable')
        invoice_type = invtype

        account_invoice_customer0 = account_invoice_obj.sudo().create(dict(
            name="Customer Invoice",
            reference_type="none",
            payment_term_id=self.payment_term_id,
            journal_id=journalrec.id,
            partner_id=partner_id.id,
            account_id=self.account_id,
            team_id=self.teamid,
            invoice_line_ids=lines,
            comment=self.comment,
            type=invtype
        ))

        # I manually assign tax on invoice
        invoice_tax_line = {
            'name': 'Test Tax for Customer Invoice',
            'manual': 1,
            'amount': 0,
            'account_id': 1,
            'invoice_id': account_invoice_customer0.id,
        }
        tax = env['account.invoice.tax'].create(invoice_tax_line)
        assert tax, "Tax has not been assigned correctly"
        return account_invoice_customer0


file1 = '/tmp/outf2.csv'
OUTF = open(file1, 'w')
file2 = '/tmp/invoicetotals.csv'
OUTFT = open(file2, 'w')
# print('Creating Invoice....')
# ReportInvoice().createInvoice()

print('****    SEE ', file1, file2)
dateinv = '2017-03-27'
print('Customer Invoices since ', dateinv, file=OUTF)
inv_type = 'out_invoice'
# inv_type = 'out_invoice'

OUT_INV = ReportInvoice().listInvoices(dateinv, inv_type)
# Show invoice totals for date > dateinv
# OUT_INV = ReportInvoice().totalInvoices(dateinv,inv_type)

print(OUT_INV, file=OUTF)
"""
print ('Supplier Invoices or Vendor Bills since ',dateinv,file=OUTF)
IN_INV = ReportInvoice().listInvoices(dateinv,'in_invoice')
print(IN_INV,file=OUTF)
"""
"""
# Totals
IN_INV = ReportInvoice().totalInvoices(dateinv, 'out_invoice')
print(IN_INV, file=OUTFT)
"""
#
rate = 100.0
qty = 500
inv_type = 'out_invoice'
invoice_line_data = [
            (0, 0,
             {
                 'product_id': env['product.template'].search([('id' ,'=' ,1)]).id,
                 'quantity': qty,
                 'account_id': env['account.account'].search(
                     [('user_type_id', '=', env.ref('account.data_account_type_revenue').id)], limit=1).id,
                 'name': 'Pure Water 0',
                 'price_unit': rate,
             }
             )
        ]
new_inv = createinvoice().crinvoice('Moses',invoice_line_data,inv_type)
print ('New invoice amount: ',new_inv.amount_total)
print ('New invoice id: ',new_inv.id)
print ('New invoice Partner: ',new_inv.partner_id.name)

#total_before_confirm = partner.total_invoiced
# print ('total confirm for partner' ,partner, total_before_confirm)

# commit the create or write
self._cr.commit()


OUTF.close()


