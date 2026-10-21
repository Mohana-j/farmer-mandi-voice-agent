# Data Sources & Market Portal Integration Guide

**Project:** Farmer Mandi Price Voice Agent  
**Event:** Agentic AI Hackathon 2026 — Powered by Ziro.Digital  

---

## 1. Selected Public Market Data Portal

### Primary Target: Open Government Data (OGD) Platform / Agmarknet API
- **Official Portal:** Agmarknet (Agricultural Marketing Information Network), Directorate of Marketing & Inspection (DMI), Ministry of Agriculture and Farmers Welfare, Government of India.
- **Resource API Endpoint:** `https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070`
- **Catalog Name:** *Current Daily Price and Arrival of Agricultural Commodities in Various Markets*.

### Why This Source is Suitable
1. **Statutory Legitimacy:** Official market data reported directly by APMC (Agricultural Produce Market Committee) mandi secretariats.
2. **Standardized Attributes:** Includes state, district, market, commodity, variety, grade, arrival date, minimum price, maximum price, and modal price.
3. **Open Access:** Provided under the National Data Sharing and Accessibility Policy (NDSAP) of the Government of India for civic tech, research, and farmer welfare applications.

---

## 2. Permitted Retrieval Methods & Access Limitations

### API Access vs. Scraping
- **Permitted Access:** JSON REST API via `api.data.gov.in` using standard HTTP GET requests.
- **Authentication:** Requires a registered API key from `data.gov.in`.
- **Rate Limits:** The platform enforces rate limits (typically 1,000 to 5,000 calls per day depending on key tier).
- **Timeouts & Delays:** Due to server load during peak morning mandi trading hours (09:00 to 12:00 IST), response latencies can exceed 5–8 seconds.

### Access Controls & Security Integrity
- This project strictly adheres to ethical integration standards:
  - **No CAPTCHA bypass.**
  - **No automated OTP cracking or account hijacking.**
  - **No scraping of password-protected or paid subscription portals.**
  - **Respect for `robots.txt`** and reasonable timeouts (configured to 8 seconds by default).

---

## 3. Switching Between Live and Synthetic Demo Mode

The system provides a configuration switch via the `.env` file or environment variables:

```bash
# Set to 'synthetic' for guaranteed offline demonstration and unit testing
DATA_PROVIDER_MODE=synthetic

# Set to 'live' to connect to the official Open Government Data API
DATA_PROVIDER_MODE=live
LIVE_PORTAL_API_KEY=your_registered_gov_api_key_here
LIVE_PORTAL_API_URL=https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070
LIVE_PORTAL_TIMEOUT_SECONDS=8
```

### Transparent Mode Attribution
The application never masks synthetic data as live government data.
- **Synthetic mode:** Marked with `[Demo Mode]` tag in spoken text, amber badge in the UI, and data tagged as `synthetic`.
- **Live mode:** Marked with green `Live Mandi Portal` badge in UI, actual arrival dates, and official record IDs (`GOV-TN-001`).
- **Automatic Fallback:** If `live` mode is selected but the key is missing or the external API times out, the backend gracefully falls back to synthetic fixtures with an explicit audit log noting the exact fallback reason.

---

## 4. Synthetic Demo Data Provider Architecture

For repeatable testing, hackathon jury demonstrations, and offline operation, the `DemoDataProvider` provides realistic agricultural fixtures modeled after the Dharmapuri / Salem horticultural belt in Tamil Nadu:

| Market Name | Market Location | Distance | Crop | Grade | Reported Price & Unit | Normalized Price | Observation Date |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Palacode APMC** | Palacode, Dharmapuri | 18.2 km | Tomato | Grade A | ₹2,200 / quintal | ₹22.00 / kg | Today's Date |
| **Dharmapuri Regulated Market** | Dharmapuri Town | 8.5 km | Tomato | Grade A | ₹21.00 / kg | ₹21.00 / kg | Today's Date |
| **Pennagaram Uzhavar Sandhai** | Pennagaram, Dharmapuri | 31.0 km | Tomato | Grade A | ₹2,400 / quintal | ₹24.00 / kg | Today's Date |
| **Krishnagiri Market** | Krishnagiri District | 54.0 km | Tomato | Grade A | ₹2,650 / quintal | ₹26.50 / kg | Excluded (> 50 km) |

All fixtures are tagged with `data_mode="synthetic"` and unique record IDs (`SYN-DHP-001`).
