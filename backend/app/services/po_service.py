"""
Purchase Order Service - PO generation and PDF export
"""
from datetime import date, datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from io import BytesIO

from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.inventory import Inventory
from app.models.user import User


class POService:
    """
    Purchase Order generation and management service.
    """
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
    
    def generate_pdf(self, po_id: int) -> bytes:
        """Generate PDF for a purchase order"""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.units import inch
        
        # Get PO data
        po = self.db.query(PurchaseOrder).filter(
            PurchaseOrder.id == po_id,
            PurchaseOrder.user_id == self.user_id
        ).first()
        
        if not po:
            raise ValueError("Purchase order not found")
        
        supplier = self.db.query(Supplier).filter(Supplier.id == po.supplier_id).first()
        user = self.db.query(User).filter(User.id == self.user_id).first()
        
        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=20
        )
        
        elements = []
        
        # Title
        elements.append(Paragraph("PURCHASE ORDER", title_style))
        elements.append(Spacer(1, 20))
        
        # PO Details
        po_info = [
            ["PO Number:", po.po_number],
            ["Order Date:", po.order_date.strftime("%Y-%m-%d") if po.order_date else ""],
            ["Expected Delivery:", po.expected_delivery_date.strftime("%Y-%m-%d") if po.expected_delivery_date else "TBD"],
            ["Status:", po.status.upper()]
        ]
        
        po_table = Table(po_info, colWidths=[2*inch, 3*inch])
        po_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(po_table)
        elements.append(Spacer(1, 20))
        
        # Supplier Info
        elements.append(Paragraph("SUPPLIER", styles['Heading2']))
        supplier_info = f"""
        <b>{supplier.name if supplier else 'Unknown'}</b><br/>
        {supplier.address or ''}<br/>
        Email: {supplier.contact_email or 'N/A'}<br/>
        Phone: {supplier.contact_phone or 'N/A'}
        """
        elements.append(Paragraph(supplier_info, styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # From Info
        elements.append(Paragraph("FROM", styles['Heading2']))
        from_info = f"""
        <b>{user.company_name or user.full_name or 'Unknown'}</b><br/>
        {user.email}
        """
        elements.append(Paragraph(from_info, styles['Normal']))
        elements.append(Spacer(1, 30))
        
        # Items Table
        elements.append(Paragraph("ORDER ITEMS", styles['Heading2']))
        
        # Table header
        items_data = [["SKU", "Product Name", "Quantity", "Unit Cost", "Total"]]
        
        # Add items
        for item in po.items:
            product = self.db.query(Product).filter(Product.id == item.product_id).first()
            items_data.append([
                product.sku if product else "N/A",
                product.name if product else "Unknown",
                str(item.quantity),
                f"${item.unit_cost:.2f}",
                f"${item.total_cost:.2f}"
            ])
        
        # Add totals
        items_data.append(["", "", "", "Subtotal:", f"${po.subtotal:.2f}"])
        items_data.append(["", "", "", "Tax:", f"${po.tax:.2f}"])
        items_data.append(["", "", "", "TOTAL:", f"${po.total:.2f}"])
        
        items_table = Table(items_data, colWidths=[1*inch, 2.5*inch, 1*inch, 1*inch, 1*inch])
        items_table.setStyle(TableStyle([
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Body style
            ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            
            # Total rows
            ('FONTNAME', (3, -3), (-1, -1), 'Helvetica-Bold'),
            
            # Grid
            ('GRID', (0, 0), (-1, -4), 1, colors.black),
            ('LINEABOVE', (3, -3), (-1, -3), 1, colors.black),
            
            # Padding
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 30))
        
        # Notes
        if po.notes:
            elements.append(Paragraph("NOTES", styles['Heading2']))
            elements.append(Paragraph(po.notes, styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def create_po_from_recommendations(self, product_ids: List[int]) -> int:
        """Create a PO from alert recommendations"""
        from app.services.alert_service import AlertService
        
        if not product_ids:
            raise ValueError("No products specified")
        
        # Group products by supplier
        by_supplier = {}
        
        for product_id in product_ids:
            product = self.db.query(Product).filter(
                Product.id == product_id,
                Product.user_id == self.user_id
            ).first()
            
            if not product:
                continue
            
            supplier_id = product.supplier_id or 0  # 0 for no supplier
            if supplier_id not in by_supplier:
                by_supplier[supplier_id] = []
            by_supplier[supplier_id].append(product)
        
        # Create POs for each supplier
        created_pos = []
        
        for supplier_id, products in by_supplier.items():
            if supplier_id == 0:
                continue  # Skip products without supplier
            
            # Get alert service for quantity recommendations
            alert_service = AlertService(self.db, self.user_id)
            
            # Create PO
            from app.routers.purchase_orders import generate_po_number
            
            po = PurchaseOrder(
                user_id=self.user_id,
                supplier_id=supplier_id,
                po_number=generate_po_number(),
                status="draft"
            )
            self.db.add(po)
            self.db.flush()
            
            subtotal = 0
            
            for product in products:
                # Get recommended quantity from alert or calculate
                inventory = self.db.query(Inventory).filter(
                    Inventory.product_id == product.id
                ).first()
                
                # Simple calculation - order 30 days of stock
                avg_daily = alert_service._get_avg_daily_demand(product.id)
                quantity = max(1, int(avg_daily * 30))
                
                total_cost = quantity * product.unit_cost
                subtotal += total_cost
                
                item = PurchaseOrderItem(
                    purchase_order_id=po.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_cost=product.unit_cost,
                    total_cost=total_cost
                )
                self.db.add(item)
            
            po.subtotal = subtotal
            po.total = subtotal
            created_pos.append(po.id)
        
        self.db.commit()
        
        return created_pos
