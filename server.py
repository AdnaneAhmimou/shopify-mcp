#!/usr/bin/env python3
"""
MCP Server — Entry Point

Registers tools from all service modules:
  - shopify/           Shopify Admin API (products, orders, customers, blogs, SEO, etc.)
  - google_search_console/  Google Search Console (rankings, keywords, impressions)
  - google_analytics/  Google Analytics 4 (traffic, conversions, audience)
  - google_merchant/   Google Merchant Center (product feed, disapprovals, Shopping)
"""
import os
from mcp.server.fastmcp import FastMCP

PORT          = int(os.environ.get("PORT", "8000"))
MCP_TRANSPORT = os.environ.get("MCP_TRANSPORT", "streamable-http")

mcp = FastMCP("shopify_mcp", host="0.0.0.0", port=PORT, json_response=True)

# ── Register all service modules ────────────────────────────────────────────
from shopify.tools               import register as register_shopify
from google_search_console.tools import register as register_gsc
from google_analytics.tools      import register as register_ga
from google_merchant.tools       import register as register_gmc

register_shopify(mcp)
register_gsc(mcp)
register_ga(mcp)
register_gmc(mcp)

# ── Run ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport=MCP_TRANSPORT)
