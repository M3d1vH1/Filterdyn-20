from fpdf import FPDF
from datetime import datetime
from flask import current_app
from flask_babel import get_locale
import os

class QuotePDFGenerator:
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.add_page()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        
        # Add Unicode font support
        try:
            self.pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
            self.pdf.add_font('DejaVu', 'B', 'DejaVuSansCondensed-Bold.ttf', uni=True)
            self.font_family = 'DejaVu'
        except:
            # Fallback to Arial
            self.font_family = 'Arial'
    
    def generate(self, quote):
        """Generate PDF for quote"""
        locale = get_locale()
        is_greek = locale == 'el'
        
        # Header
        self._add_header(quote, is_greek)
        
        # Company info
        self._add_company_info(quote.tenant, is_greek)
        
        # Customer info
        self._add_customer_info(quote.customer, is_greek)
        
        # Quote details
        self._add_quote_details(quote, is_greek)
        
        # Items table
        self._add_items_table(quote, is_greek)
        
        # Totals
        self._add_totals(quote, is_greek)
        
        # Terms and conditions
        self._add_terms(quote, is_greek)
        
        # Footer
        self._add_footer(quote.tenant, is_greek)
        
        return self.pdf.output(dest='S').encode('latin-1')
    
    def _add_header(self, quote, is_greek=False):
        """Add header with logo and company name"""
        self.pdf.set_font(self.font_family, 'B', 20)
        self.pdf.set_text_color(27, 163, 163)  # Filterdyn teal
        
        # Logo placeholder (you can add actual logo here)
        self.pdf.cell(0, 15, 'FILTERDYN', 0, 1, 'C')
        
        self.pdf.set_font(self.font_family, '', 10)
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.cell(0, 5, 'Water Treatment Solutions', 0, 1, 'C')
        self.pdf.ln(10)
    
    def _add_company_info(self, tenant, is_greek=False):
        """Add company information"""
        self.pdf.set_font(self.font_family, 'B', 12)
        title = 'ΣΤΟΙΧΕΙΑ ΕΤΑΙΡΕΙΑΣ' if is_greek else 'COMPANY INFORMATION'
        self.pdf.cell(0, 8, title, 0, 1)
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
        self.pdf.ln(2)
        
        self.pdf.set_font(self.font_family, '', 10)
        
        # Company details
        if tenant.company_address:
            self.pdf.cell(0, 5, f"Address: {tenant.company_address}", 0, 1)
        if tenant.company_phone:
            self.pdf.cell(0, 5, f"Phone: {tenant.company_phone}", 0, 1)
        if tenant.company_email:
            self.pdf.cell(0, 5, f"Email: {tenant.company_email}", 0, 1)
        
        self.pdf.ln(5)
    
    def _add_customer_info(self, customer, is_greek=False):
        """Add customer information"""
        self.pdf.set_font(self.font_family, 'B', 12)
        title = 'ΣΤΟΙΧΕΙΑ ΠΕΛΑΤΗ' if is_greek else 'CUSTOMER INFORMATION'
        self.pdf.cell(0, 8, title, 0, 1)
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
        self.pdf.ln(2)
        
        self.pdf.set_font(self.font_family, '', 10)
        
        # Customer details
        self.pdf.cell(0, 5, f"Company: {customer.name}", 0, 1)
        if customer.contact_person:
            self.pdf.cell(0, 5, f"Contact: {customer.contact_person}", 0, 1)
        if customer.address:
            self.pdf.cell(0, 5, f"Address: {customer.address}", 0, 1)
        if customer.city:
            self.pdf.cell(0, 5, f"City: {customer.city}", 0, 1)
        if customer.phone:
            self.pdf.cell(0, 5, f"Phone: {customer.phone}", 0, 1)
        if customer.email:
            self.pdf.cell(0, 5, f"Email: {customer.email}", 0, 1)
        
        self.pdf.ln(5)
    
    def _add_quote_details(self, quote, is_greek=False):
        """Add quote details"""
        self.pdf.set_font(self.font_family, 'B', 12)
        title = 'ΣΤΟΙΧΕΙΑ ΠΡΟΣΦΟΡΑΣ' if is_greek else 'QUOTE DETAILS'
        self.pdf.cell(0, 8, title, 0, 1)
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
        self.pdf.ln(2)
        
        self.pdf.set_font(self.font_family, '', 10)
        
        # Quote details
        quote_label = 'Αριθμός Προσφοράς:' if is_greek else 'Quote Number:'
        self.pdf.cell(0, 5, f"{quote_label} {quote.quote_number}", 0, 1)
        
        date_label = 'Ημερομηνία:' if is_greek else 'Date:'
        self.pdf.cell(0, 5, f"{date_label} {quote.created_at.strftime('%d/%m/%Y')}", 0, 1)
        
        title_label = 'Τίτλος:' if is_greek else 'Title:'
        self.pdf.cell(0, 5, f"{title_label} {quote.title}", 0, 1)
        
        if quote.description:
            desc_label = 'Περιγραφή:' if is_greek else 'Description:'
            self.pdf.cell(0, 5, f"{desc_label} {quote.description}", 0, 1)
        
        validity_label = 'Ισχύς Προσφοράς:' if is_greek else 'Quote Validity:'
        self.pdf.cell(0, 5, f"{validity_label} {quote.validity_days} days", 0, 1)
        
        delivery_label = 'Χρόνος Παράδοσης:' if is_greek else 'Delivery Time:'
        self.pdf.cell(0, 5, f"{delivery_label} {quote.delivery_days} days", 0, 1)
        
        payment_label = 'Όροι Πληρωμής:' if is_greek else 'Payment Terms:'
        self.pdf.cell(0, 5, f"{payment_label} {quote.payment_terms}", 0, 1)
        
        self.pdf.ln(5)
    
    def _add_items_table(self, quote, is_greek=False):
        """Add items table"""
        self.pdf.set_font(self.font_family, 'B', 12)
        title = 'ΑΝΤΙΚΕΙΜΕΝΑ ΠΡΟΣΦΟΡΑΣ' if is_greek else 'QUOTE ITEMS'
        self.pdf.cell(0, 8, title, 0, 1)
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
        self.pdf.ln(2)
        
        # Table header
        self.pdf.set_font(self.font_family, 'B', 9)
        self.pdf.set_fill_color(240, 240, 240)
        
        if is_greek:
            headers = ['Περιγραφή', 'Ποσ.', 'Τιμή Μον.', 'Σύνολο']
            col_widths = [100, 20, 30, 30]
        else:
            headers = ['Description', 'Qty', 'Unit Price', 'Total']
            col_widths = [100, 20, 30, 30]
        
        for i, header in enumerate(headers):
            self.pdf.cell(col_widths[i], 8, header, 1, 0, 'C', True)
        self.pdf.ln()
        
        # Table rows
        self.pdf.set_font(self.font_family, '', 9)
        self.pdf.set_fill_color(255, 255, 255)
        
        for item in quote.items:
            # Description
            self.pdf.cell(col_widths[0], 8, item.description[:40], 1, 0, 'L')
            # Quantity
            self.pdf.cell(col_widths[1], 8, f"{item.quantity:.1f}", 1, 0, 'C')
            # Unit Price
            self.pdf.cell(col_widths[2], 8, f"€{item.unit_price:.2f}", 1, 0, 'R')
            # Total
            self.pdf.cell(col_widths[3], 8, f"€{item.line_total:.2f}", 1, 0, 'R')
            self.pdf.ln()
        
        self.pdf.ln(3)
    
    def _add_totals(self, quote, is_greek=False):
        """Add totals section"""
        # Position for totals (right side)
        x_pos = 120
        
        self.pdf.set_font(self.font_family, '', 10)
        
        # Subtotal
        subtotal_label = 'Μερικό Σύνολο:' if is_greek else 'Subtotal:'
        self.pdf.set_xy(x_pos, self.pdf.get_y())
        self.pdf.cell(40, 6, subtotal_label, 0, 0, 'R')
        self.pdf.cell(30, 6, f"€{quote.subtotal:.2f}", 1, 1, 'R')
        
        # Tax
        tax_label = f'ΦΠΑ ({quote.tax_rate}%):' if is_greek else f'VAT ({quote.tax_rate}%):'
        self.pdf.set_x(x_pos)
        self.pdf.cell(40, 6, tax_label, 0, 0, 'R')
        self.pdf.cell(30, 6, f"€{quote.tax_amount:.2f}", 1, 1, 'R')
        
        # Total
        self.pdf.set_font(self.font_family, 'B', 10)
        total_label = 'Γενικό Σύνολο:' if is_greek else 'Total:'
        self.pdf.set_x(x_pos)
        self.pdf.cell(40, 8, total_label, 0, 0, 'R')
        self.pdf.set_fill_color(27, 163, 163)
        self.pdf.set_text_color(255, 255, 255)
        self.pdf.cell(30, 8, f"€{quote.total_amount:.2f}", 1, 1, 'R', True)
        self.pdf.set_text_color(0, 0, 0)
        
        self.pdf.ln(10)
    
    def _add_terms(self, quote, is_greek=False):
        """Add terms and conditions"""
        self.pdf.set_font(self.font_family, 'B', 10)
        title = 'ΟΡΟΙ ΚΑΙ ΠΡΟΫΠΟΘΕΣΕΙΣ' if is_greek else 'TERMS AND CONDITIONS'
        self.pdf.cell(0, 6, title, 0, 1)
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
        self.pdf.ln(2)
        
        self.pdf.set_font(self.font_family, '', 9)
        
        if is_greek:
            terms = [
                f"• Η προσφορά ισχύει για {quote.validity_days} ημέρες από την ημερομηνία έκδοσης.",
                f"• Χρόνος παράδοσης: {quote.delivery_days} εργάσιμες ημέρες.",
                f"• Όροι πληρωμής: {quote.payment_terms}.",
                "• Οι τιμές συμπεριλαμβάνουν ΦΠΑ 24%.",
                "• Η παράδοση γίνεται στην έδρα του πελάτη."
            ]
        else:
            terms = [
                f"• This quote is valid for {quote.validity_days} days from the date of issue.",
                f"• Delivery time: {quote.delivery_days} working days.",
                f"• Payment terms: {quote.payment_terms}.",
                "• Prices include 24% VAT.",
                "• Delivery to customer premises."
            ]
        
        for term in terms:
            self.pdf.cell(0, 5, term, 0, 1)
        
        self.pdf.ln(5)
    
    def _add_footer(self, tenant, is_greek=False):
        """Add footer"""
        # Position at bottom
        self.pdf.set_y(-30)
        
        # Line
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
        self.pdf.ln(2)
        
        self.pdf.set_font(self.font_family, '', 8)
        self.pdf.set_text_color(128, 128, 128)
        
        # Company info in footer
        footer_text = f"{tenant.name}"
        if tenant.company_phone:
            footer_text += f" | Tel: {tenant.company_phone}"
        if tenant.company_email:
            footer_text += f" | Email: {tenant.company_email}"
        
        self.pdf.cell(0, 4, footer_text, 0, 1, 'C')
        
        # Thank you message
        thanks = 'Σας ευχαριστούμε για την εμπιστοσύνη σας!' if is_greek else 'Thank you for your trust!'
        self.pdf.cell(0, 4, thanks, 0, 1, 'C')
