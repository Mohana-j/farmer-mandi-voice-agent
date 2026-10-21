"""Natural voice answer generator in English and Tamil using verified retrieved records."""

from typing import Any, Dict, List, Optional


def generate_voice_answer(
    crop: str,
    summary: Dict[str, Any],
    source_mode: str = "synthetic",
    is_yesterday_data: bool = False,
    is_stale_or_uncertain: bool = False,
) -> Dict[str, str]:
    """Generate deterministic, grounded voice responses in English and Tamil.
    
    Guarantees:
    - Never fabricates prices.
    - Always states observation dates and data mode.
    - Warns that transport costs are unknown and market price is not profit guarantee.
    - Distinguishes yesterday's data from today's data explicitly.
    """
    usable_count = summary.get("usable_markets_count", 0)
    lowest = summary.get("lowest_price_per_kg")
    highest = summary.get("highest_price_per_kg")
    dates = summary.get("dates_observed", [])
    dates_str = ", ".join(dates) if dates else "unspecified dates"
    sources = summary.get("source_names", [])
    source_str = ", ".join(sources) if sources else ("Live portal" if source_mode == "live" else "Mandi records")

    mode_prefix_en = ""
    mode_prefix_ta = ""
    if source_mode == "synthetic":
        mode_prefix_en = "[Demo Mode] "
        mode_prefix_ta = "[மாதிரித் தரவு] "

    if usable_count == 0 or lowest is None or highest is None:
        text_en = (
            f"{mode_prefix_en}No verified {crop} price records were found for the selected area. "
            f"Please check your search location or try a broader radius. "
            f"I cannot provide a price estimate without verified market data."
        )
        text_ta = (
            f"{mode_prefix_ta}தேர்ந்தெடுக்கப்பட்ட பகுதியில் சரிபார்க்கப்பட்ட {crop} விலை விவரங்கள் கிடைக்கவில்லை. "
            f"தயவுசெய்து உங்கள் இடத்தை மீண்டும் சரிபார்க்கவும். "
            f"சரிபார்க்கப்பட்ட தரவு இல்லாமல் விலை மதிப்பீடு வழங்க முடியாது."
        )
        return {"en": text_en, "ta": text_ta}

    # Range phrasing
    if lowest == highest:
        price_range_en = f"₹{lowest:.2f} per kilogram"
        price_range_ta = f"கிலோவிற்கு ₹{lowest:.2f}"
    else:
        price_range_en = f"₹{lowest:.2f} to ₹{highest:.2f} per kilogram"
        price_range_ta = f"கிலோவிற்கு ₹{lowest:.2f} முதல் ₹{highest:.2f} வரை"

    # Yesterday vs Today check
    freshness_clause_en = f"These records are dated {dates_str}."
    freshness_clause_ta = f"இப்பதிவுகள் {dates_str} தேதியிட்டவை."
    if is_yesterday_data:
        freshness_clause_en = f"Notice: Only yesterday's data is available, dated {dates_str}. Today's trading prices may differ."
        freshness_clause_ta = f"கவனிக்க: நேற்று பதிவு செய்யப்பட்ட தரவு மட்டுமே கிடைத்துள்ளது (தேதி: {dates_str}). இன்றைய வர்த்தக விலை மாறக்கூடும்."

    uncertainty_en = ""
    uncertainty_ta = ""
    if is_stale_or_uncertain:
        uncertainty_en = " Note: Some market grades or units are unverified, so this comparison is provisional."
        uncertainty_ta = " குறிப்பு: சில சந்தை தரங்கள் சரிபார்க்கப்படாததால், இது தற்காலிக ஒப்பீடு மட்டுமே."

    # Transport safety reminder
    safety_en = " Transport cost is unknown; the highest price market is not guaranteed to be the most profitable."
    safety_ta = " போக்குவரத்து செலவு கணக்கிடப்படவில்லை; அதிக விலை உள்ள சந்தையே அதிக லாபம் தரும் என்று கூற முடியாது."

    text_en = (
        f"{mode_prefix_en}I found verified records for {usable_count} nearby market{'s' if usable_count > 1 else ''}. "
        f"The recorded {crop} prices range from {price_range_en}. "
        f"{freshness_clause_en} "
        f"Source: {source_str}."
        f"{uncertainty_en}"
        f"{safety_en} "
        f"This is a market price comparison, not a guarantee of net profit."
    )

    text_ta = (
        f"{mode_prefix_ta}அருகிலுள்ள {usable_count} சந்தைகளுக்கான சரிபார்க்கப்பட்ட விவரங்கள் கிடைத்துள்ளன. "
        f"{crop} விலை {price_range_ta} பதிவாகியுள்ளது. "
        f"{freshness_clause_ta} "
        f"மூலம்: {source_str}."
        f"{uncertainty_ta}"
        f"{safety_ta} "
        f"இது சந்தை விலை ஒப்பீடு மட்டுமே, லாப உத்தரவாதம் அல்ல."
    )

    return {"en": text_en, "ta": text_ta}
