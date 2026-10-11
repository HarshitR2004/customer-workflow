"""
Mock data and synthetic knowledge base for DemoShop e-commerce customer support.
"""

from typing import Dict, Any, Optional
import re

# Comprehensive synthetic knowledge base for DemoShop.
# Intentionally detailed, comprehensive, and verbose so that injecting it into the prompt
# demonstrates massive prompt token bloat and context inefficiency for FinOps benchmarking.
DEMOSHOP_KNOWLEDGE_BASE = """
================================================================================
                    DEMOSHOP OFFICIAL CUSTOMER SUPPORT POLICY MANUAL
                                VERSION 4.2 - UPDATED 2026
================================================================================

1. GENERAL COMPANY OVERVIEW
DemoShop is a premier digital retailer specializing in consumer electronics, computer peripherals,
smart home appliances, audio systems, and lifestyle accessories. Our primary customer service goal
is to deliver high-quality, transparent assistance while adhering strictly to company guidelines.

2. SHIPPING AND FULFILLMENT POLICIES
2.1 Standard Shipping:
- Standard shipping takes 3 to 5 business days for continental US destinations.
- Orders placed after 2:00 PM EST are processed on the following business day.
- Standard shipping is fulfilled via DemoExpress Courier or National Postal Logistics.
- Tracking numbers are issued within 24 hours of fulfillment.
- Packages may occasionally experience carrier transit delays due to inclement weather, mechanical
  breakdowns, peak holiday seasons, or regional logistics bottlenecks.

2.2 Expedited & Overnight Shipping:
- Expedited shipping guarantees delivery within 2 business days.
- Priority Overnight shipping guarantees next business day delivery by 10:30 AM local time.
- Expedited fees are non-refundable unless the carrier fails to meet the guaranteed delivery window
  due solely to courier fault (acts of nature, severe storms, and incorrect customer addresses excluded).

2.3 International Shipping:
- Available to over 65 countries worldwide.
- International shipping timelines range from 7 to 21 business days depending on customs clearance.
- Customers are responsible for all applicable import tariffs, value-added taxes (VAT), and border handling fees.
- Tracking updates outside the country of origin may experience intermittent delays of 48-72 hours.

2.4 Delayed, Damaged, and Lost Packages:
- A package is officially categorized as "Delayed" if it has not arrived within 2 business days following
  the estimated delivery date stated at checkout.
- If a package is Delayed by 5 or more business days past the expected delivery date, the customer becomes
  eligible for either:
    (a) An immediate complimentary priority replacement reshipment, OR
    (b) A full refund credited back to the original payment method upon customer request.
- Lost Packages: An investigation is automatically initiated with the carrier if tracking shows no scan
  activity for 7 consecutive business days. If deemed lost, a full refund or replacement is processed within 48 hours.
- Damaged in Transit: Customers must report physical packaging damage within 7 calendar days of delivery.
  Photographic evidence of damaged packaging and damaged goods is required for processing an expedited replacement.

3. RETURNS AND REFUND POLICIES
3.1 Return Window:
- DemoShop provides a standard 30-day return window starting from the confirmed date of delivery.
- Items must be returned in their original packaging, including all original accessories, documentation,
  cables, manuals, and protective wrapping.

3.2 Condition of Returned Items & Restocking Fees:
- Items in brand new, unopened condition receive a 100% refund of the purchase price.
- Opened items in like-new condition with complete accessories are subject to inspection and a 0% restocking fee.
- Items showing visible signs of wear, missing original accessories, or missing packaging may incur a 15% restocking fee.
- Consumable goods, software license keys, custom-configured PCs, and intimate wearable audio ear-tips (for hygienic reasons)
  are strictly non-returnable once opened unless proven defective upon arrival.

3.3 Refund Processing & Timelines:
- Once a returned package is received at the central DemoShop Fulfillment Center, quality inspection takes 2 business days.
- Approved refunds are credited to the original payment method within 3 to 5 business days.
- Depending on the customer's financial institution or card issuer, posting to billing statements may require an
  additional 2 to 7 business days.
- DemoShop does not issue cash refunds for purchases made with debit or credit cards.
- Store credit refunds are issued immediately upon return inspection approval and include a 5% bonus credit incentive.

4. CANCELLATION POLICIES
4.1 Order Cancellation Window:
- Customers may self-cancel or request support cancellation of an order within 30 minutes of order placement
  without any penalty, provided the warehouse has not locked the order for picking and packing.
- Once an order enters "Processing / Packing" status in the warehouse queue, it cannot be canceled in-flight.
- If an order has already shipped, the customer must accept delivery and initiate a standard return RMA (Return Merchandise Authorization).

4.2 Pre-Order and Backorder Cancellations:
- Pre-orders and backordered merchandise may be canceled at any time prior to fulfillment notification with zero penalty.

5. WARRANTY AND REPAIR POLICIES
5.1 Standard Limited Warranty (1-Year):
- All hardware products sold directly by DemoShop include a 1-Year Limited Manufacturer & Retailer Warranty.
- The warranty covers internal component defects, manufacturing flaws, mechanical failures, power supply issues,
  and screen malfunctions occurring during normal intended usage.
- The warranty strictly excludes: accidental drops, liquid spills, unauthorized third-party modifications, cosmetic wear,
  overclocking damage, power surges without certified surge protectors, or loss and theft.

5.2 Extended DemoCare Protection Plan:
- Customers enrolled in DemoCare (2-Year or 3-Year plans) receive accidental damage handling coverage with a $29 deductible.
- Includes priority expedited repair turnaround and 24/7 dedicated technical support hotline.

5.3 Warranty Claim Process:
- Customers initiate a claim by contacting DemoShop Support with their original Order ID and serial number.
- Remote hardware diagnostic steps must be performed before an RMA is authorized.
- DemoShop covers prepaid shipping labels for valid warranty returns within the warranty term.
- Turnaround time for warranty repair or replacement unit shipment is 5 to 7 business days from receipt.

6. PAYMENT AND BILLING POLICIES
6.1 Supported Payment Methods:
- Major credit and debit cards (Visa, MasterCard, American Express, Discover).
- Digital wallets (Apple Pay, Google Pay, PayPal).
- Flexible financing partners (Klarna, Affirm) for eligible purchases over $100.

6.2 Duplicate Charges & Authorization Holds:
- When an order is placed, an authorization hold is placed on the customer's card. In rare circumstances involving
  temporary network timeouts, multiple pending authorizations may appear on the customer's bank statement.
- Pending authorizations automatically drop off within 24 to 72 hours depending on the customer's banking institution.
- If a customer card has experienced an actual confirmed duplicate settlement (two settled charges for one order),
  DemoShop billing support will immediately initiate a direct reversal of the duplicate transaction upon verification.
  Reversed funds appear within 3-5 business days.

6.3 Payment Fraud Prevention and Security:
- DemoShop utilizes advanced automated fraud scoring. Orders flagged for suspicious mismatches between billing and
  shipping addresses may require manual identity verification before release.

7. CUSTOMER SUPPORT ESCALATION TIERS AND SLA
- Tier 1 Support: General inquiries, order status updates, standard cancellations, and return label generation.
  Target First Response Time: Under 2 hours during normal business operations.
- Tier 2 Escalations: Delayed shipment claims beyond 5 days, complex technical warranty troubleshooting,
  damaged transit claims, and billing dispute settlements.
  Target Resolution Time: Under 24 hours.
- Customer Satisfaction Commitment: DemoShop is dedicated to respectful, empathetic, and resolution-oriented communication.
  Every representative must maintain a polite, constructive tone regardless of customer frustration or urgency.
================================================================================
"""

# Synthetic database of mock customer orders
MOCK_ORDERS: Dict[str, Dict[str, Any]] = {
    "12345": {
        "order_id": "12345",
        "customer_name": "Alex Mercer",
        "product": "Wireless Noise-Canceling Headphones",
        "purchase_date": "8 days ago",
        "shipping_status": "Delayed",
        "expected_delivery": "3 days ago",
        "carrier": "DemoExpress",
        "tracking_number": "DX-998812345",
        "last_scan_location": "Regional Hub - Transit Delay",
        "price_usd": 149.99,
        "payment_method": "Visa ending in 4012",
        "refund_eligibility": "Eligible for refund or replacement (exceeds 2-day delivery delay SLA)",
    },
    "54321": {
        "order_id": "54321",
        "customer_name": "Samantha Reed",
        "product": "UltraSound 5.1 Home Theater Soundbar",
        "purchase_date": "4 days ago",
        "shipping_status": "Delivered",
        "expected_delivery": "Yesterday",
        "carrier": "DemoExpress",
        "tracking_number": "DX-554454321",
        "last_scan_location": "Front Porch - Signed by Resident",
        "price_usd": 299.99,
        "payment_method": "MasterCard ending in 8831",
        "refund_eligibility": "Eligible for immediate replacement upon photographic proof of transit damage",
    },
    "98765": {
        "order_id": "98765",
        "customer_name": "David Chen",
        "product": "SmartWatch Pro Titanium (Qty: 2)",
        "purchase_date": "15 minutes ago",
        "shipping_status": "Order Placed - Pending Fulfillment",
        "expected_delivery": "In 4 days",
        "carrier": "National Postal Logistics",
        "tracking_number": "Pending",
        "last_scan_location": "Warehouse Queue",
        "price_usd": 398.00,
        "payment_method": "Apple Pay",
        "refund_eligibility": "Eligible for immediate order modification or partial cancellation within 30-minute window",
    },
    "11223": {
        "order_id": "11223",
        "customer_name": "Elena Rostova",
        "product": "Ergonomic Lumbar Office Chair",
        "purchase_date": "2 days ago",
        "shipping_status": "Shipped - In Transit",
        "expected_delivery": "Tomorrow",
        "carrier": "DemoExpress Heavy Freight",
        "tracking_number": "DX-112233445",
        "last_scan_location": "En Route to Local Sorting Facility",
        "price_usd": 249.50,
        "payment_method": "Visa ending in 9102",
        "refund_eligibility": "Duplicate billing charge verified in system; eligible for immediate reversal of second transaction",
    },
    "33445": {
        "order_id": "33445",
        "customer_name": "Marcus Vance",
        "product": "4K Ultra-Wide 144Hz Gaming Monitor",
        "purchase_date": "11 months ago",
        "shipping_status": "Delivered",
        "expected_delivery": "11 months ago",
        "carrier": "DemoExpress",
        "tracking_number": "DX-334459900",
        "last_scan_location": "Customer Address",
        "price_usd": 499.99,
        "payment_method": "PayPal",
        "refund_eligibility": "Under 1-Year Limited Manufacturer Warranty (1 month remaining); eligible for warranty repair or replacement RMA",
    },
}

# 5 diverse sample customer tickets for testing
SAMPLE_TICKETS = [
    {
        "id": "TICKET-1",
        "title": "Delayed Headphones & Refund Inquiry",
        "customer_name": "Alex Mercer",
        "order_id": "12345",
        "text": "I ordered headphones 8 days ago, but they still haven't arrived. My order ID is #12345. Can you check the shipping status and tell me if I can get a refund?",
    },
    {
        "id": "TICKET-2",
        "title": "Crushed Box & Defective Soundbar",
        "customer_name": "Samantha Reed",
        "order_id": "54321",
        "text": "Received my UltraSound Soundbar (Order #54321) yesterday, but the package was completely crushed and the speaker won't turn on. I am furious! I need an immediate replacement or refund.",
    },
    {
        "id": "TICKET-3",
        "title": "Accidental Duplicate Item Cancellation",
        "customer_name": "David Chen",
        "order_id": "98765",
        "text": "Hi, I accidentally ordered two SmartWatches under Order #98765 ten minutes ago. Can I cancel one of them before it ships? Thanks!",
    },
    {
        "id": "TICKET-4",
        "title": "Double Billing Charge on Credit Card",
        "customer_name": "Elena Rostova",
        "order_id": "11223",
        "text": "My credit card was charged twice for order #11223 (Ergonomic Chair). Please reverse the duplicate charge immediately.",
    },
    {
        "id": "TICKET-5",
        "title": "Monitor Screen Flickering Warranty Request",
        "customer_name": "Marcus Vance",
        "order_id": "33445",
        "text": "I purchased a 4K Gaming Monitor 11 months ago (Order #33445) and the screen just started flickering badly. Is this covered under warranty? How do I get it fixed?",
    },
]


def extract_order_id_from_text(text: str) -> Optional[str]:
    """
    Utility helper to extract order ID (e.g. #12345 or 12345) from ticket text.
    """
    match = re.search(r"#?(\b\d{5}\b)", text)
    if match:
        return match.group(1)
    return None


def get_mock_order(order_id: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Retrieve mock order record for a given order ID.
    """
    if not order_id:
        return None
    clean_id = order_id.replace("#", "").strip()
    return MOCK_ORDERS.get(clean_id)


def format_order_details(order: Optional[Dict[str, Any]]) -> str:
    """
    Format mock order dictionary into readable text for prompt injection.
    """
    if not order:
        return "No specific order record found in database for this ticket."

    return f"""Order Record Details:
- Order ID: #{order.get('order_id')}
- Customer Name: {order.get('customer_name')}
- Product: {order.get('product')}
- Purchase Date: {order.get('purchase_date')}
- Shipping Status: {order.get('shipping_status')}
- Expected Delivery: {order.get('expected_delivery')}
- Carrier: {order.get('carrier')}
- Tracking Number: {order.get('tracking_number')}
- Last Scan Location: {order.get('last_scan_location')}
- Total Paid: ${order.get('price_usd', 0.0):.2f}
- Payment Method: {order.get('payment_method')}
- System Refund / Action Eligibility: {order.get('refund_eligibility')}"""
