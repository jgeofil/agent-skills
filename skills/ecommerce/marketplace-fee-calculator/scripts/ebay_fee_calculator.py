#!/usr/bin/env python3
"""
eBay Fee and Profit Calculator Engine.

Calculates eBay final value fees, per-order fixed fees, store tier benefits,
seller performance surcharges, ad promotion fees, international fees,
net seller payout, net profit, profit margins, and break-even selling price.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Union, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum
import argparse
import json
import sys


class StoreTier(str, Enum):
    NO_STORE = "no_store"
    STARTER = "starter_store"
    BASIC = "basic_store"
    PREMIUM = "premium_store"
    ANCHOR = "anchor_store"
    ENTERPRISE = "enterprise_store"

    @classmethod
    def from_string(cls, val: str) -> "StoreTier":
        normalized = val.strip().lower().replace("-", "_")
        aliases = {
            "none": cls.NO_STORE,
            "no": cls.NO_STORE,
            "no_store": cls.NO_STORE,
            "nostore": cls.NO_STORE,
            "starter": cls.STARTER,
            "starter_store": cls.STARTER,
            "basic": cls.BASIC,
            "basic_store": cls.BASIC,
            "premium": cls.PREMIUM,
            "premium_store": cls.PREMIUM,
            "anchor": cls.ANCHOR,
            "anchor_store": cls.ANCHOR,
            "enterprise": cls.ENTERPRISE,
            "enterprise_store": cls.ENTERPRISE,
        }
        if normalized in aliases:
            return aliases[normalized]
        for member in cls:
            if member.value == normalized:
                return member
        raise ValueError(
            f"Invalid store tier: '{val}'. Valid options: "
            f"{', '.join(sorted(aliases.keys()))}"
        )


class SellerStatus(str, Enum):
    TOP_RATED_PLUS = "top_rated_plus"
    ABOVE_STANDARD = "above_standard"
    BELOW_STANDARD = "below_standard"
    VERY_HIGH_INAD = "high_item"

    @classmethod
    def from_string(cls, val: str) -> "SellerStatus":
        normalized = val.strip().lower().replace("-", "_")
        aliases = {
            "top_rated": cls.TOP_RATED_PLUS,
            "top_rated_plus": cls.TOP_RATED_PLUS,
            "toprated": cls.TOP_RATED_PLUS,
            "above_standard": cls.ABOVE_STANDARD,
            "above": cls.ABOVE_STANDARD,
            "standard": cls.ABOVE_STANDARD,
            "below_standard": cls.BELOW_STANDARD,
            "below": cls.BELOW_STANDARD,
            "high_item": cls.VERY_HIGH_INAD,
            "very_high_inad": cls.VERY_HIGH_INAD,
            "inad": cls.VERY_HIGH_INAD,
        }
        if normalized in aliases:
            return aliases[normalized]
        for member in cls:
            if member.value == normalized:
                return member
        raise ValueError(
            f"Invalid seller status: '{val}'. Valid options: "
            f"{', '.join(sorted(aliases.keys()))}"
        )


@dataclass(frozen=True)
class FeeBreakdown:
    total_sale: Decimal
    final_value_fee: Decimal
    per_order_fee: Decimal
    performance_penalty_fee: Decimal
    promotion_fee: Decimal
    international_fee: Decimal
    insertion_fee: Decimal
    other_fees: Decimal
    total_ebay_fees: Decimal
    net_payout: Decimal
    net_profit: Decimal
    profit_margin_pct: Decimal
    break_even_sale_price: Decimal

    def to_dict(self) -> Dict[str, Any]:
        """Convert breakdown to string-formatted dictionary for JSON serialization."""
        return {
            "total_sale": str(self.total_sale),
            "final_value_fee": str(self.final_value_fee),
            "per_order_fee": str(self.per_order_fee),
            "performance_penalty_fee": str(self.performance_penalty_fee),
            "promotion_fee": str(self.promotion_fee),
            "international_fee": str(self.international_fee),
            "insertion_fee": str(self.insertion_fee),
            "other_fees": str(self.other_fees),
            "total_ebay_fees": str(self.total_ebay_fees),
            "net_payout": str(self.net_payout),
            "net_profit": str(self.net_profit),
            "profit_margin_pct": str(self.profit_margin_pct),
            "break_even_sale_price": str(self.break_even_sale_price),
        }

    def format_summary(self) -> str:
        """Format a human-readable text report."""
        lines = [
            "=" * 44,
            "         EBAY FEE & PROFIT BREAKDOWN        ",
            "=" * 44,
            f"Total Sale Base (Inc. Tax & Ship): ${self.total_sale:>9}",
            "-" * 44,
            f"Final Value Fee (Variable %):      ${self.final_value_fee:>9}",
            f"Per-Order Fixed Fee:               ${self.per_order_fee:>9}",
            f"Performance Penalty Fee (+3%):     ${self.performance_penalty_fee:>9}",
            f"Promoted Listings Fee:             ${self.promotion_fee:>9}",
            f"International Fee:                 ${self.international_fee:>9}",
            f"Insertion Fee:                     ${self.insertion_fee:>9}",
            f"Other / Optional Fees:             ${self.other_fees:>9}",
            "-" * 44,
            f"Total eBay Platform Fees:          ${self.total_ebay_fees:>9}",
            f"Net Payout (After Fees & Remitted):${self.net_payout:>9}",
            f"Net Profit (After COGS & Shipping):${self.net_profit:>9}",
            f"Profit Margin:                      {self.profit_margin_pct:>9}%",
            f"Break-Even Sale Price:             ${self.break_even_sale_price:>9}",
            "=" * 44,
        ]
        return "\n".join(lines)


def quantize(value: Decimal) -> Decimal:
    """Rounds to 2 decimal places using standard half-up rounding."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# Extracted from Module 1286: category lookup table
US_BASE_FEES = {
    "Antiques": {"default": Decimal("9.35"), "starter": Decimal("13.60")},
    "Art": {"default": Decimal("9.35"), "starter": Decimal("13.60")},
    "Art NFTs": {"default": Decimal("5.00"), "starter": Decimal("5.00")},
    "Baby": {"default": Decimal("9.35"), "starter": Decimal("12.90")},
    "Books, Comics & Magazines": {"default": Decimal("14.60"), "starter": Decimal("14.60")},
    "Business, Office & Industrial": {"default": Decimal("9.35"), "starter": Decimal("12.90")},
    "Cameras & Photography": {"default": Decimal("9.35"), "starter": Decimal("12.90")},
    "Cell Phones & Accessories": {"default": Decimal("9.35"), "starter": Decimal("12.90")},
    "Clothes, Shoes & Accessories": {"default": Decimal("9.35"), "starter": Decimal("12.90")},
    "Coins": {"default": Decimal("9.00"), "starter": Decimal("12.90")},
    "Collectibles": {"default": Decimal("9.35"), "starter": Decimal("12.90")},
    "Computers/Tablets & Networking": {"default": Decimal("9.35"), "starter": Decimal("12.90")},
    "Consumer Electronics": {"default": Decimal("9.35"), "starter": Decimal("12.90")},
    "Crafts": {"default": Decimal("9.35"), "starter": Decimal("12.90")},
    "Dolls & Bears": {"default": Decimal("9.35"), "starter": Decimal("12.90")},
    "Event Tickets": {"default": Decimal("12.90"), "starter": Decimal("12.90")},
    "DVD, Movies & TV": {"default": Decimal("14.60"), "starter": Decimal("14.60")},
    "eBay Motors": {"default": Decimal("9.35"), "starter": Decimal("12.90")},
    "Health & Beauty": {"default": Decimal("9.35"), "starter": Decimal("12.90")},
    "Home & Garden": {"default": Decimal("9.35"), "starter": Decimal("12.90")},
    "Jewellery & Watches": {"default": Decimal("13.00"), "starter": Decimal("12.55")},
    "Music": {"default": Decimal("15.30"), "starter": Decimal("14.60")},
    "Musical Instruments & DJ Equipment": {"default": Decimal("9.80"), "starter": Decimal("14.60")},
    "Pet Supplies": {"default": Decimal("9.35"), "starter": Decimal("12.90")},
    "Pottery, Ceramics & Glass": {"default": Decimal("9.35"), "starter": Decimal("12.90")},
    "Sporting Goods": {"default": Decimal("9.35"), "starter": Decimal("12.90")},
    "Sports Mem, Cards & Fan Shop": {"default": Decimal("9.35"), "starter": Decimal("12.90")},
    "Stamps": {"default": Decimal("9.70"), "starter": Decimal("12.90")},
    "Toys & Games": {"default": Decimal("12.35"), "starter": Decimal("14.60")},
    "Travel": {"default": Decimal("9.35"), "starter": Decimal("12.90")},
    "Video Games & Consoles": {"default": Decimal("9.35"), "starter": Decimal("12.90")},
    "Other": {"default": Decimal("12.90"), "starter": Decimal("13.60")},
}


def lookup_category_rates(category: str) -> Dict[str, Decimal]:
    """Look up base rates for category, matching case-insensitively or falling back to 'Other'."""
    if category in US_BASE_FEES:
        return US_BASE_FEES[category]
    cat_lower = category.strip().lower()
    for cat_name, rates in US_BASE_FEES.items():
        if cat_name.lower() == cat_lower:
            return rates
    # Partial match fallback
    for cat_name, rates in US_BASE_FEES.items():
        if cat_lower in cat_name.lower():
            return rates
    return US_BASE_FEES["Other"]


def compute_final_value_fee(
    total_sale: Decimal,
    store_tier: Union[StoreTier, str],
    override_fvf_rate: Optional[Decimal] = None,
    category: str = "Other"
) -> Decimal:
    """
    Calculates the percentage portion of the Final Value Fee.
    Implements standard eBay tier boundaries ($7,500 for No Store/Starter, $2,500 for Basic+).
    """
    if isinstance(store_tier, str):
        store_tier = StoreTier.from_string(store_tier)

    if override_fvf_rate is not None:
        return total_sale * (override_fvf_rate / Decimal("100"))

    # Determine base rate from store tier and category table
    category_data = lookup_category_rates(category)
    
    if store_tier in (StoreTier.NO_STORE, StoreTier.STARTER):
        base_rate = (category_data["starter"] if store_tier == StoreTier.STARTER 
                     else category_data["default"])
        tier_cap = Decimal("7500.00")
        over_rate = Decimal("0.0235")
    else:
        # Basic, Premium, Anchor, Enterprise
        base_rate = category_data["default"]
        tier_cap = Decimal("2500.00")
        over_rate = Decimal("0.0235")

    decimal_base_rate = base_rate / Decimal("100")

    if total_sale <= tier_cap:
        return total_sale * decimal_base_rate
    else:
        tier_1 = tier_cap * decimal_base_rate
        tier_2 = (total_sale - tier_cap) * over_rate
        return tier_1 + tier_2


def calculate_ebay_fees(
    item_price: Decimal,
    shipping_charged_to_buyer: Decimal = Decimal("0.00"),
    sales_tax: Decimal = Decimal("0.00"),
    item_cost: Decimal = Decimal("0.00"),
    shipping_cost_seller_pays: Decimal = Decimal("0.00"),
    store_tier: Union[StoreTier, str] = StoreTier.NO_STORE,
    seller_status: Union[SellerStatus, str] = SellerStatus.ABOVE_STANDARD,
    category: str = "Other",
    override_fvf_rate: Optional[Decimal] = None,
    promotion_rate_pct: Decimal = Decimal("0.00"),
    international_rate_pct: Decimal = Decimal("0.00"),
    insertion_fee: Decimal = Decimal("0.00"),
    other_fees: Decimal = Decimal("0.00"),
) -> FeeBreakdown:
    """
    Executes the exact eBay profit & fee calculation engine.
    """
    if isinstance(store_tier, str):
        store_tier = StoreTier.from_string(store_tier)
    if isinstance(seller_status, str):
        seller_status = SellerStatus.from_string(seller_status)

    # 1. Total Sale base (used for fee calculations)
    total_sale = item_price + shipping_charged_to_buyer + sales_tax

    # 2. Final Value Fee (variable % portion)
    fvf_percent = compute_final_value_fee(
        total_sale=total_sale,
        store_tier=store_tier,
        override_fvf_rate=override_fvf_rate,
        category=category
    )

    # 3. Per-Order Fixed Fee: $0.30 if Total Sale <= $10.00, otherwise $0.40
    per_order_fee = Decimal("0.30") if total_sale <= Decimal("10.00") else Decimal("0.40")

    # 4. Performance Penalties (Standard eBay policy: +3% on Below Standard or High INAD)
    penalty_rate = Decimal("0.00")
    if seller_status in (SellerStatus.BELOW_STANDARD, SellerStatus.VERY_HIGH_INAD):
        penalty_rate = Decimal("0.03")
    performance_penalty_fee = total_sale * penalty_rate

    # 5. Ad Promotions & International Surcharges
    promo_fee = total_sale * (promotion_rate_pct / Decimal("100"))
    intl_fee = total_sale * (international_rate_pct / Decimal("100"))

    # 6. Aggregate platform costs
    total_ebay_fees = (
        fvf_percent
        + per_order_fee
        + performance_penalty_fee
        + promo_fee
        + intl_fee
        + insertion_fee
        + other_fees
    )

    # 7. Net Payout & Profit Calculations
    # Sales tax is collected and remitted by eBay; it does not flow into seller payout
    net_payout = total_sale - total_ebay_fees - sales_tax
    net_profit = net_payout - shipping_cost_seller_pays - item_cost
    
    revenue_base = item_price + shipping_charged_to_buyer
    profit_margin = (
        (net_profit / revenue_base) * Decimal("100")
        if revenue_base > Decimal("0.00")
        else Decimal("0.00")
    )

    # 8. Break-even Estimation
    # Formula: BreakEvenPrice = (FixedFees + ItemCost + SellerShipping - BuyerShipping) / (1 - EffectiveVariableFeeRate)
    effective_pct_rate = (
        (fvf_percent / total_sale if total_sale > 0 else Decimal("0.136"))
        + penalty_rate
        + (promotion_rate_pct / Decimal("100"))
        + (international_rate_pct / Decimal("100"))
    )
    
    fixed_expenses = (
        per_order_fee
        + insertion_fee
        + other_fees
        + item_cost
        + shipping_cost_seller_pays
        - shipping_charged_to_buyer
    )
    
    if effective_pct_rate < Decimal("1.00"):
        break_even_price = fixed_expenses / (Decimal("1.00") - effective_pct_rate)
    else:
        break_even_price = Decimal("0.00")

    return FeeBreakdown(
        total_sale=quantize(total_sale),
        final_value_fee=quantize(fvf_percent),
        per_order_fee=quantize(per_order_fee),
        performance_penalty_fee=quantize(performance_penalty_fee),
        promotion_fee=quantize(promo_fee),
        international_fee=quantize(intl_fee),
        insertion_fee=quantize(insertion_fee),
        other_fees=quantize(other_fees),
        total_ebay_fees=quantize(total_ebay_fees),
        net_payout=quantize(net_payout),
        net_profit=quantize(net_profit),
        profit_margin_pct=quantize(profit_margin),
        break_even_sale_price=quantize(break_even_price),
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Calculate eBay seller fees, net payout, profit, and break-even selling price."
    )
    parser.add_argument(
        "--price", "-p",
        type=Decimal,
        default=Decimal("0.00"),
        help="Item sale price ($)."
    )
    parser.add_argument(
        "--shipping-charged", "--shipping-buyer",
        type=Decimal,
        default=Decimal("0.00"),
        dest="shipping_charged",
        help="Shipping charged to the buyer ($). Default: 0.00"
    )
    parser.add_argument(
        "--sales-tax", "--tax",
        type=Decimal,
        default=Decimal("0.00"),
        dest="sales_tax",
        help="Estimated buyer sales tax collected/remitted by eBay ($). Default: 0.00"
    )
    parser.add_argument(
        "--item-cost", "--cost",
        type=Decimal,
        default=Decimal("0.00"),
        dest="item_cost",
        help="Cost of goods sold / item acquisition cost ($). Default: 0.00"
    )
    parser.add_argument(
        "--shipping-cost", "--shipping-seller",
        type=Decimal,
        default=Decimal("0.00"),
        dest="shipping_cost",
        help="Actual shipping label cost paid by seller ($). Default: 0.00"
    )
    parser.add_argument(
        "--store-tier", "--tier",
        type=str,
        default="no_store",
        dest="store_tier",
        help="eBay store subscription tier: no_store, starter, basic, premium, anchor, enterprise. Default: no_store"
    )
    parser.add_argument(
        "--seller-status", "--status",
        type=str,
        default="above_standard",
        dest="seller_status",
        help="Seller performance status: top_rated_plus, above_standard, below_standard, high_item. Default: above_standard"
    )
    parser.add_argument(
        "--category", "-c",
        type=str,
        default="Other",
        help="Listing category (e.g., Collectibles, Art, Video Games & Consoles, Other). Default: Other"
    )
    parser.add_argument(
        "--override-fvf",
        type=Decimal,
        default=None,
        dest="override_fvf_rate",
        help="Explicit Final Value Fee rate percentage override (e.g., 12.9 for 12.9%%)."
    )
    parser.add_argument(
        "--promo-rate", "--promo",
        type=Decimal,
        default=Decimal("0.00"),
        dest="promotion_rate_pct",
        help="Promoted Listings ad rate percentage (e.g., 2.0 for 2.0%%). Default: 0.00"
    )
    parser.add_argument(
        "--intl-rate", "--intl",
        type=Decimal,
        default=Decimal("0.00"),
        dest="international_rate_pct",
        help="International fee surcharge percentage (e.g., 1.65 for 1.65%%). Default: 0.00"
    )
    parser.add_argument(
        "--insertion-fee",
        type=Decimal,
        default=Decimal("0.00"),
        dest="insertion_fee",
        help="Listing insertion fee ($). Default: 0.00"
    )
    parser.add_argument(
        "--other-fees",
        type=Decimal,
        default=Decimal("0.00"),
        dest="other_fees",
        help="Other miscellaneous fees ($). Default: 0.00"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON."
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="List all supported categories and their base rates, then exit."
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.list_categories:
        categories_output = {
            cat: {"default_pct": str(vals["default"]), "starter_pct": str(vals["starter"])}
            for cat, vals in sorted(US_BASE_FEES.items())
        }
        if args.json:
            print(json.dumps(categories_output, indent=2))
        else:
            print("=" * 60)
            print(f"{'Category':<38} | {'Basic+ Rate':<10} | {'Starter Rate':<10}")
            print("-" * 60)
            for cat, vals in sorted(US_BASE_FEES.items()):
                print(f"{cat:<38} | {vals['default']:>9}% | {vals['starter']:>9}%")
            print("=" * 60)
        return

    try:
        tier = StoreTier.from_string(args.store_tier)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        status = SellerStatus.from_string(args.seller_status)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    breakdown = calculate_ebay_fees(
        item_price=args.price,
        shipping_charged_to_buyer=args.shipping_charged,
        sales_tax=args.sales_tax,
        item_cost=args.item_cost,
        shipping_cost_seller_pays=args.shipping_cost,
        store_tier=tier,
        seller_status=status,
        category=args.category,
        override_fvf_rate=args.override_fvf_rate,
        promotion_rate_pct=args.promotion_rate_pct,
        international_rate_pct=args.international_rate_pct,
        insertion_fee=args.insertion_fee,
        other_fees=args.other_fees,
    )

    if args.json:
        print(json.dumps(breakdown.to_dict(), indent=2))
    else:
        print(breakdown.format_summary())


if __name__ == "__main__":
    main()
