"""
Shopify MCP Tools — Products, Orders, Customers, Collections,
Inventory, Fulfillments, Blogs, Pages, Discounts, Variants,
Images, Redirects, Gift Cards, Shipping, Transactions, Reports, Metafields.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from core.client import _request, _error, _fmt


def register(mcp):

    # ═══════════════════════════════════════════════════════════════════════
    # PRODUCTS
    # ═══════════════════════════════════════════════════════════════════════

    class ListProductsInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        limit:         Optional[int] = Field(default=50, ge=1, le=250)
        status:        Optional[str] = Field(default=None, description="active, archived, draft")
        product_type:  Optional[str] = Field(default=None)
        vendor:        Optional[str] = Field(default=None)
        collection_id: Optional[int] = Field(default=None)
        since_id:      Optional[int] = Field(default=None)
        fields:        Optional[str] = Field(default=None)

    @mcp.tool(name="shopify_list_products", annotations={"readOnlyHint": True})
    async def shopify_list_products(params: ListProductsInput) -> str:
        """List products from the Shopify store with optional filters."""
        try:
            p: Dict[str, Any] = {"limit": params.limit}
            for f in ["status", "product_type", "vendor", "collection_id", "since_id", "fields"]:
                val = getattr(params, f)
                if val is not None:
                    p[f] = val
            data = await _request("GET", "products.json", params=p)
            products = data.get("products", [])
            return _fmt({"count": len(products), "products": products})
        except Exception as e:
            return _error(e)

    class GetProductInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        product_id: int = Field(..., description="The Shopify product ID")

    @mcp.tool(name="shopify_get_product", annotations={"readOnlyHint": True})
    async def shopify_get_product(params: GetProductInput) -> str:
        """Retrieve a single product by ID."""
        try:
            data = await _request("GET", f"products/{params.product_id}.json")
            return _fmt(data.get("product", data))
        except Exception as e:
            return _error(e)

    class CreateProductInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        title:        str                            = Field(..., min_length=1)
        body_html:    Optional[str]                  = Field(default=None)
        vendor:       Optional[str]                  = Field(default=None)
        product_type: Optional[str]                  = Field(default=None)
        tags:         Optional[str]                  = Field(default=None)
        status:       Optional[str]                  = Field(default="draft")
        variants:     Optional[List[Dict[str, Any]]] = Field(default=None)
        options:      Optional[List[Dict[str, Any]]] = Field(default=None)
        images:       Optional[List[Dict[str, Any]]] = Field(default=None)

    @mcp.tool(name="shopify_create_product", annotations={"readOnlyHint": False})
    async def shopify_create_product(params: CreateProductInput) -> str:
        """Create a new product in the Shopify store."""
        try:
            product: Dict[str, Any] = {"title": params.title}
            for f in ["body_html", "vendor", "product_type", "tags", "status", "variants", "options", "images"]:
                val = getattr(params, f)
                if val is not None:
                    product[f] = val
            data = await _request("POST", "products.json", body={"product": product})
            return _fmt(data.get("product", data))
        except Exception as e:
            return _error(e)

    class UpdateProductInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        product_id:   int                            = Field(..., description="Product ID to update")
        title:        Optional[str]                  = Field(default=None)
        body_html:    Optional[str]                  = Field(default=None)
        vendor:       Optional[str]                  = Field(default=None)
        product_type: Optional[str]                  = Field(default=None)
        tags:         Optional[str]                  = Field(default=None)
        status:       Optional[str]                  = Field(default=None)
        variants:     Optional[List[Dict[str, Any]]] = Field(default=None)

    @mcp.tool(name="shopify_update_product", annotations={"readOnlyHint": False})
    async def shopify_update_product(params: UpdateProductInput) -> str:
        """Update an existing product. Only provided fields are changed."""
        try:
            product: Dict[str, Any] = {}
            for f in ["title", "body_html", "vendor", "product_type", "tags", "status", "variants"]:
                val = getattr(params, f)
                if val is not None:
                    product[f] = val
            data = await _request("PUT", f"products/{params.product_id}.json", body={"product": product})
            return _fmt(data.get("product", data))
        except Exception as e:
            return _error(e)

    class DeleteProductInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        product_id: int = Field(..., description="Product ID to delete")

    @mcp.tool(name="shopify_delete_product", annotations={"readOnlyHint": False, "destructiveHint": True})
    async def shopify_delete_product(params: DeleteProductInput) -> str:
        """Permanently delete a product."""
        try:
            await _request("DELETE", f"products/{params.product_id}.json")
            return f"Product {params.product_id} deleted."
        except Exception as e:
            return _error(e)

    class ProductCountInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        status:       Optional[str] = Field(default=None)
        vendor:       Optional[str] = Field(default=None)
        product_type: Optional[str] = Field(default=None)

    @mcp.tool(name="shopify_count_products", annotations={"readOnlyHint": True})
    async def shopify_count_products(params: ProductCountInput) -> str:
        """Get the total count of products."""
        try:
            p: Dict[str, Any] = {}
            for f in ["status", "vendor", "product_type"]:
                val = getattr(params, f)
                if val is not None:
                    p[f] = val
            data = await _request("GET", "products/count.json", params=p)
            return _fmt(data)
        except Exception as e:
            return _error(e)

    # ═══════════════════════════════════════════════════════════════════════
    # PRODUCT VARIANTS
    # ═══════════════════════════════════════════════════════════════════════

    class ListVariantsInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        product_id: int           = Field(..., description="Product ID")
        limit:      Optional[int] = Field(default=50, ge=1, le=250)

    @mcp.tool(name="shopify_list_variants", annotations={"readOnlyHint": True})
    async def shopify_list_variants(params: ListVariantsInput) -> str:
        """List all variants for a product (sizes, colors, prices, SKUs)."""
        try:
            data     = await _request("GET", f"products/{params.product_id}/variants.json", params={"limit": params.limit})
            variants = data.get("variants", [])
            return _fmt({"count": len(variants), "variants": variants})
        except Exception as e:
            return _error(e)

    class UpdateVariantInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        variant_id:          int             = Field(..., description="Variant ID to update")
        price:               Optional[str]   = Field(default=None)
        compare_at_price:    Optional[str]   = Field(default=None)
        sku:                 Optional[str]   = Field(default=None)
        barcode:             Optional[str]   = Field(default=None)
        weight:              Optional[float] = Field(default=None)
        weight_unit:         Optional[str]   = Field(default=None, description="g, kg, lb, oz")
        inventory_policy:    Optional[str]   = Field(default=None, description="deny or continue")
        requires_shipping:   Optional[bool]  = Field(default=None)
        taxable:             Optional[bool]  = Field(default=None)
        option1:             Optional[str]   = Field(default=None)
        option2:             Optional[str]   = Field(default=None)
        option3:             Optional[str]   = Field(default=None)

    @mcp.tool(name="shopify_update_variant", annotations={"readOnlyHint": False})
    async def shopify_update_variant(params: UpdateVariantInput) -> str:
        """Update a product variant — price, compare-at price, SKU, weight, options."""
        try:
            variant: Dict[str, Any] = {}
            for f in ["price", "compare_at_price", "sku", "barcode", "weight", "weight_unit",
                      "inventory_policy", "requires_shipping", "taxable", "option1", "option2", "option3"]:
                val = getattr(params, f)
                if val is not None:
                    variant[f] = val
            data = await _request("PUT", f"variants/{params.variant_id}.json", body={"variant": variant})
            return _fmt(data.get("variant", data))
        except Exception as e:
            return _error(e)

    # ═══════════════════════════════════════════════════════════════════════
    # PRODUCT IMAGES
    # ═══════════════════════════════════════════════════════════════════════

    class ListProductImagesInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        product_id: int = Field(..., description="Product ID")

    @mcp.tool(name="shopify_list_product_images", annotations={"readOnlyHint": True})
    async def shopify_list_product_images(params: ListProductImagesInput) -> str:
        """List all images for a product."""
        try:
            data   = await _request("GET", f"products/{params.product_id}/images.json")
            images = data.get("images", [])
            return _fmt({"count": len(images), "images": images})
        except Exception as e:
            return _error(e)

    class AddProductImageInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        product_id:  int                  = Field(..., description="Product ID")
        src:         str                  = Field(..., description="Public URL of the image")
        alt:         Optional[str]        = Field(default=None)
        position:    Optional[int]        = Field(default=None)
        variant_ids: Optional[List[int]]  = Field(default=None)

    @mcp.tool(name="shopify_add_product_image", annotations={"readOnlyHint": False})
    async def shopify_add_product_image(params: AddProductImageInput) -> str:
        """Add an image to a product from a public URL."""
        try:
            image: Dict[str, Any] = {"src": params.src}
            for f in ["alt", "position", "variant_ids"]:
                val = getattr(params, f)
                if val is not None:
                    image[f] = val
            data = await _request("POST", f"products/{params.product_id}/images.json", body={"image": image})
            return _fmt(data.get("image", data))
        except Exception as e:
            return _error(e)

    class DeleteProductImageInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        product_id: int = Field(..., description="Product ID")
        image_id:   int = Field(..., description="Image ID to delete")

    @mcp.tool(name="shopify_delete_product_image", annotations={"readOnlyHint": False, "destructiveHint": True})
    async def shopify_delete_product_image(params: DeleteProductImageInput) -> str:
        """Delete an image from a product."""
        try:
            await _request("DELETE", f"products/{params.product_id}/images/{params.image_id}.json")
            return f"Image {params.image_id} deleted from product {params.product_id}."
        except Exception as e:
            return _error(e)

    # ═══════════════════════════════════════════════════════════════════════
    # METAFIELDS (SEO: meta title, meta description)
    # ═══════════════════════════════════════════════════════════════════════

    class GetMetafieldsInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        resource:    str           = Field(..., description="products, collections, customers, orders, pages, blogs, shop")
        resource_id: Optional[int] = Field(default=None, description="Resource ID (omit for shop)")
        namespace:   Optional[str] = Field(default=None, description="e.g. 'global'")
        limit:       Optional[int] = Field(default=50, ge=1, le=250)

    @mcp.tool(name="shopify_get_metafields", annotations={"readOnlyHint": True})
    async def shopify_get_metafields(params: GetMetafieldsInput) -> str:
        """Get metafields for any resource. Product SEO fields are in namespace='global'."""
        try:
            path = f"{params.resource}/{params.resource_id}/metafields.json" if params.resource_id else "metafields.json"
            p: Dict[str, Any] = {"limit": params.limit}
            if params.namespace:
                p["namespace"] = params.namespace
            data       = await _request("GET", path, params=p)
            metafields = data.get("metafields", [])
            return _fmt({"count": len(metafields), "metafields": metafields})
        except Exception as e:
            return _error(e)

    class UpdateProductSEOInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        product_id:       int           = Field(..., description="Product ID")
        meta_title:       Optional[str] = Field(default=None, description="SEO meta title (max 70 chars)")
        meta_description: Optional[str] = Field(default=None, description="SEO meta description (max 160 chars)")

    @mcp.tool(name="shopify_update_product_seo", annotations={"readOnlyHint": False})
    async def shopify_update_product_seo(params: UpdateProductSEOInput) -> str:
        """Update the SEO meta title and/or meta description for a product."""
        try:
            results = []
            if params.meta_title is not None:
                body = {"metafield": {"namespace": "global", "key": "title_tag", "value": params.meta_title, "type": "single_line_text_field"}}
                data = await _request("POST", f"products/{params.product_id}/metafields.json", body=body)
                results.append({"field": "meta_title", "result": data.get("metafield", data)})
            if params.meta_description is not None:
                body = {"metafield": {"namespace": "global", "key": "description_tag", "value": params.meta_description, "type": "single_line_text_field"}}
                data = await _request("POST", f"products/{params.product_id}/metafields.json", body=body)
                results.append({"field": "meta_description", "result": data.get("metafield", data)})
            if not results:
                return "No fields provided. Pass meta_title and/or meta_description."
            return _fmt({"product_id": params.product_id, "updated": results})
        except Exception as e:
            return _error(e)

    class SetMetafieldInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        resource:    str           = Field(..., description="products, collections, customers, orders, pages, blogs, shop")
        resource_id: Optional[int] = Field(default=None)
        namespace:   str           = Field(..., description="e.g. 'global'")
        key:         str           = Field(..., description="e.g. 'title_tag' or 'description_tag'")
        value:       str           = Field(...)
        type:        Optional[str] = Field(default="single_line_text_field")

    @mcp.tool(name="shopify_set_metafield", annotations={"readOnlyHint": False})
    async def shopify_set_metafield(params: SetMetafieldInput) -> str:
        """Set any metafield on any resource."""
        try:
            path = f"{params.resource}/{params.resource_id}/metafields.json" if params.resource_id else "metafields.json"
            body = {"metafield": {"namespace": params.namespace, "key": params.key, "value": params.value, "type": params.type}}
            data = await _request("POST", path, body=body)
            return _fmt(data.get("metafield", data))
        except Exception as e:
            return _error(e)

    # ═══════════════════════════════════════════════════════════════════════
    # ORDERS
    # ═══════════════════════════════════════════════════════════════════════

    class ListOrdersInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        limit:              Optional[int] = Field(default=50, ge=1, le=250)
        status:             Optional[str] = Field(default="any")
        financial_status:   Optional[str] = Field(default=None)
        fulfillment_status: Optional[str] = Field(default=None)
        since_id:           Optional[int] = Field(default=None)
        created_at_min:     Optional[str] = Field(default=None)
        created_at_max:     Optional[str] = Field(default=None)
        fields:             Optional[str] = Field(default=None)

    @mcp.tool(name="shopify_list_orders", annotations={"readOnlyHint": True})
    async def shopify_list_orders(params: ListOrdersInput) -> str:
        """List orders with optional filters."""
        try:
            p: Dict[str, Any] = {"limit": params.limit, "status": params.status}
            for f in ["financial_status", "fulfillment_status", "since_id", "created_at_min", "created_at_max", "fields"]:
                val = getattr(params, f)
                if val is not None:
                    p[f] = val
            data   = await _request("GET", "orders.json", params=p)
            orders = data.get("orders", [])
            return _fmt({"count": len(orders), "orders": orders})
        except Exception as e:
            return _error(e)

    class GetOrderInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        order_id: int = Field(..., description="Shopify order ID")

    @mcp.tool(name="shopify_get_order", annotations={"readOnlyHint": True})
    async def shopify_get_order(params: GetOrderInput) -> str:
        """Retrieve a single order by ID."""
        try:
            data = await _request("GET", f"orders/{params.order_id}.json")
            return _fmt(data.get("order", data))
        except Exception as e:
            return _error(e)

    class OrderCountInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        status:             Optional[str] = Field(default="any")
        financial_status:   Optional[str] = Field(default=None)
        fulfillment_status: Optional[str] = Field(default=None)

    @mcp.tool(name="shopify_count_orders", annotations={"readOnlyHint": True})
    async def shopify_count_orders(params: OrderCountInput) -> str:
        """Get total order count."""
        try:
            p: Dict[str, Any] = {"status": params.status}
            for f in ["financial_status", "fulfillment_status"]:
                val = getattr(params, f)
                if val is not None:
                    p[f] = val
            data = await _request("GET", "orders/count.json", params=p)
            return _fmt(data)
        except Exception as e:
            return _error(e)

    class CloseOrderInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        order_id: int = Field(...)

    @mcp.tool(name="shopify_close_order", annotations={"readOnlyHint": False})
    async def shopify_close_order(params: CloseOrderInput) -> str:
        """Close an order (mark as completed)."""
        try:
            data = await _request("POST", f"orders/{params.order_id}/close.json")
            return _fmt(data.get("order", data))
        except Exception as e:
            return _error(e)

    class CancelOrderInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        order_id: int            = Field(...)
        reason:   Optional[str]  = Field(default=None, description="customer, fraud, inventory, declined, other")
        email:    Optional[bool] = Field(default=True)
        restock:  Optional[bool] = Field(default=False)

    @mcp.tool(name="shopify_cancel_order", annotations={"readOnlyHint": False, "destructiveHint": True})
    async def shopify_cancel_order(params: CancelOrderInput) -> str:
        """Cancel an order."""
        try:
            body: Dict[str, Any] = {}
            for f in ["reason", "email", "restock"]:
                val = getattr(params, f)
                if val is not None:
                    body[f] = val
            data = await _request("POST", f"orders/{params.order_id}/cancel.json", body=body)
            return _fmt(data.get("order", data))
        except Exception as e:
            return _error(e)

    # ═══════════════════════════════════════════════════════════════════════
    # DRAFT ORDERS
    # ═══════════════════════════════════════════════════════════════════════

    class ListDraftOrdersInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        limit:  Optional[int] = Field(default=50, ge=1, le=250)
        status: Optional[str] = Field(default="open", description="open, invoice_sent, completed, any")

    @mcp.tool(name="shopify_list_draft_orders", annotations={"readOnlyHint": True})
    async def shopify_list_draft_orders(params: ListDraftOrdersInput) -> str:
        """List draft orders (quotes/invoices)."""
        try:
            data   = await _request("GET", "draft_orders.json", params={"limit": params.limit, "status": params.status})
            orders = data.get("draft_orders", [])
            return _fmt({"count": len(orders), "draft_orders": orders})
        except Exception as e:
            return _error(e)

    class CreateDraftOrderInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        line_items:  List[Dict[str, Any]] = Field(..., description="Line items with variant_id and quantity")
        customer_id: Optional[int]        = Field(default=None)
        email:       Optional[str]        = Field(default=None)
        note:        Optional[str]        = Field(default=None)
        tags:        Optional[str]        = Field(default=None)

    @mcp.tool(name="shopify_create_draft_order", annotations={"readOnlyHint": False})
    async def shopify_create_draft_order(params: CreateDraftOrderInput) -> str:
        """Create a draft order (quote). Can be sent as invoice to customer."""
        try:
            order: Dict[str, Any] = {"line_items": params.line_items}
            for f in ["customer_id", "email", "note", "tags"]:
                val = getattr(params, f)
                if val is not None:
                    order[f] = val
            data = await _request("POST", "draft_orders.json", body={"draft_order": order})
            return _fmt(data.get("draft_order", data))
        except Exception as e:
            return _error(e)

    class SendDraftInvoiceInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        draft_order_id: int           = Field(...)
        to:             Optional[str] = Field(default=None)
        subject:        Optional[str] = Field(default=None)
        custom_message: Optional[str] = Field(default=None)

    @mcp.tool(name="shopify_send_draft_order_invoice", annotations={"readOnlyHint": False})
    async def shopify_send_draft_order_invoice(params: SendDraftInvoiceInput) -> str:
        """Send an invoice email for a draft order to the customer."""
        try:
            invoice: Dict[str, Any] = {}
            for f in ["to", "subject", "custom_message"]:
                val = getattr(params, f)
                if val is not None:
                    invoice[f] = val
            data = await _request("POST", f"draft_orders/{params.draft_order_id}/send_invoice.json", body={"draft_order_invoice": invoice})
            return _fmt(data)
        except Exception as e:
            return _error(e)

    # ═══════════════════════════════════════════════════════════════════════
    # REFUNDS
    # ═══════════════════════════════════════════════════════════════════════

    class ListRefundsInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        order_id: int           = Field(...)
        limit:    Optional[int] = Field(default=50, ge=1, le=250)

    @mcp.tool(name="shopify_list_refunds", annotations={"readOnlyHint": True})
    async def shopify_list_refunds(params: ListRefundsInput) -> str:
        """List all refunds for an order."""
        try:
            data    = await _request("GET", f"orders/{params.order_id}/refunds.json", params={"limit": params.limit})
            refunds = data.get("refunds", [])
            return _fmt({"count": len(refunds), "refunds": refunds})
        except Exception as e:
            return _error(e)

    class CreateRefundInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        order_id:          int                            = Field(...)
        notify:            Optional[bool]                 = Field(default=True)
        note:              Optional[str]                  = Field(default=None)
        shipping:          Optional[Dict[str, Any]]       = Field(default=None)
        refund_line_items: Optional[List[Dict[str, Any]]] = Field(default=None)
        transactions:      Optional[List[Dict[str, Any]]] = Field(default=None)

    @mcp.tool(name="shopify_create_refund", annotations={"readOnlyHint": False, "destructiveHint": True})
    async def shopify_create_refund(params: CreateRefundInput) -> str:
        """Issue a full or partial refund on an order."""
        try:
            refund: Dict[str, Any] = {}
            for f in ["notify", "note", "shipping", "refund_line_items", "transactions"]:
                val = getattr(params, f)
                if val is not None:
                    refund[f] = val
            data = await _request("POST", f"orders/{params.order_id}/refunds.json", body={"refund": refund})
            return _fmt(data.get("refund", data))
        except Exception as e:
            return _error(e)

    # ═══════════════════════════════════════════════════════════════════════
    # CUSTOMERS
    # ═══════════════════════════════════════════════════════════════════════

    class ListCustomersInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        limit:          Optional[int] = Field(default=50, ge=1, le=250)
        since_id:       Optional[int] = Field(default=None)
        created_at_min: Optional[str] = Field(default=None)
        created_at_max: Optional[str] = Field(default=None)
        fields:         Optional[str] = Field(default=None)

    @mcp.tool(name="shopify_list_customers", annotations={"readOnlyHint": True})
    async def shopify_list_customers(params: ListCustomersInput) -> str:
        """List customers from the store."""
        try:
            p: Dict[str, Any] = {"limit": params.limit}
            for f in ["since_id", "created_at_min", "created_at_max", "fields"]:
                val = getattr(params, f)
                if val is not None:
                    p[f] = val
            data      = await _request("GET", "customers.json", params=p)
            customers = data.get("customers", [])
            return _fmt({"count": len(customers), "customers": customers})
        except Exception as e:
            return _error(e)

    class SearchCustomersInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        query: str           = Field(..., min_length=1)
        limit: Optional[int] = Field(default=50, ge=1, le=250)

    @mcp.tool(name="shopify_search_customers", annotations={"readOnlyHint": True})
    async def shopify_search_customers(params: SearchCustomersInput) -> str:
        """Search customers by name, email, or other fields."""
        try:
            data      = await _request("GET", "customers/search.json", params={"query": params.query, "limit": params.limit})
            customers = data.get("customers", [])
            return _fmt({"count": len(customers), "customers": customers})
        except Exception as e:
            return _error(e)

    class GetCustomerInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        customer_id: int = Field(...)

    @mcp.tool(name="shopify_get_customer", annotations={"readOnlyHint": True})
    async def shopify_get_customer(params: GetCustomerInput) -> str:
        """Retrieve a single customer by ID."""
        try:
            data = await _request("GET", f"customers/{params.customer_id}.json")
            return _fmt(data.get("customer", data))
        except Exception as e:
            return _error(e)

    class CreateCustomerInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        first_name:        Optional[str]                  = Field(default=None)
        last_name:         Optional[str]                  = Field(default=None)
        email:             Optional[str]                  = Field(default=None)
        phone:             Optional[str]                  = Field(default=None)
        tags:              Optional[str]                  = Field(default=None)
        note:              Optional[str]                  = Field(default=None)
        addresses:         Optional[List[Dict[str, Any]]] = Field(default=None)
        send_email_invite: Optional[bool]                 = Field(default=False)

    @mcp.tool(name="shopify_create_customer", annotations={"readOnlyHint": False})
    async def shopify_create_customer(params: CreateCustomerInput) -> str:
        """Create a new customer."""
        try:
            customer: Dict[str, Any] = {}
            for f in ["first_name", "last_name", "email", "phone", "tags", "note", "addresses", "send_email_invite"]:
                val = getattr(params, f)
                if val is not None:
                    customer[f] = val
            data = await _request("POST", "customers.json", body={"customer": customer})
            return _fmt(data.get("customer", data))
        except Exception as e:
            return _error(e)

    class UpdateCustomerInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        customer_id: int           = Field(...)
        first_name:  Optional[str] = Field(default=None)
        last_name:   Optional[str] = Field(default=None)
        email:       Optional[str] = Field(default=None)
        phone:       Optional[str] = Field(default=None)
        tags:        Optional[str] = Field(default=None)
        note:        Optional[str] = Field(default=None)

    @mcp.tool(name="shopify_update_customer", annotations={"readOnlyHint": False})
    async def shopify_update_customer(params: UpdateCustomerInput) -> str:
        """Update an existing customer."""
        try:
            customer: Dict[str, Any] = {}
            for f in ["first_name", "last_name", "email", "phone", "tags", "note"]:
                val = getattr(params, f)
                if val is not None:
                    customer[f] = val
            data = await _request("PUT", f"customers/{params.customer_id}.json", body={"customer": customer})
            return _fmt(data.get("customer", data))
        except Exception as e:
            return _error(e)

    class CustomerOrdersInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        customer_id: int           = Field(...)
        limit:       Optional[int] = Field(default=50, ge=1, le=250)
        status:      Optional[str] = Field(default="any")

    @mcp.tool(name="shopify_get_customer_orders", annotations={"readOnlyHint": True})
    async def shopify_get_customer_orders(params: CustomerOrdersInput) -> str:
        """Get all orders for a specific customer."""
        try:
            data   = await _request("GET", f"customers/{params.customer_id}/orders.json", params={"limit": params.limit, "status": params.status})
            orders = data.get("orders", [])
            return _fmt({"count": len(orders), "orders": orders})
        except Exception as e:
            return _error(e)

    # ═══════════════════════════════════════════════════════════════════════
    # COLLECTIONS
    # ═══════════════════════════════════════════════════════════════════════

    class ListCollectionsInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        limit:           Optional[int] = Field(default=50, ge=1, le=250)
        since_id:        Optional[int] = Field(default=None)
        collection_type: Optional[str] = Field(default="custom", description="'custom' or 'smart'")

    @mcp.tool(name="shopify_list_collections", annotations={"readOnlyHint": True})
    async def shopify_list_collections(params: ListCollectionsInput) -> str:
        """List custom or smart collections."""
        try:
            endpoint    = "custom_collections.json" if params.collection_type == "custom" else "smart_collections.json"
            p: Dict[str, Any] = {"limit": params.limit}
            if params.since_id:
                p["since_id"] = params.since_id
            data        = await _request("GET", endpoint, params=p)
            key         = "custom_collections" if params.collection_type == "custom" else "smart_collections"
            collections = data.get(key, [])
            return _fmt({"count": len(collections), "collections": collections})
        except Exception as e:
            return _error(e)

    class GetCollectionProductsInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        collection_id: int           = Field(...)
        limit:         Optional[int] = Field(default=50, ge=1, le=250)

    @mcp.tool(name="shopify_get_collection_products", annotations={"readOnlyHint": True})
    async def shopify_get_collection_products(params: GetCollectionProductsInput) -> str:
        """Get all products in a specific collection."""
        try:
            data     = await _request("GET", "products.json", params={"limit": params.limit, "collection_id": params.collection_id})
            products = data.get("products", [])
            return _fmt({"count": len(products), "products": products})
        except Exception as e:
            return _error(e)

    # ═══════════════════════════════════════════════════════════════════════
    # INVENTORY
    # ═══════════════════════════════════════════════════════════════════════

    class EmptyInput(BaseModel):
        model_config = ConfigDict(extra="forbid")

    @mcp.tool(name="shopify_list_locations", annotations={"readOnlyHint": True})
    async def shopify_list_locations(params: EmptyInput) -> str:
        """List all inventory locations for the store."""
        try:
            data      = await _request("GET", "locations.json")
            locations = data.get("locations", [])
            return _fmt({"count": len(locations), "locations": locations})
        except Exception as e:
            return _error(e)

    class GetInventoryLevelsInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        location_id:        Optional[int] = Field(default=None)
        inventory_item_ids: Optional[str] = Field(default=None, description="Comma-separated inventory item IDs")

    @mcp.tool(name="shopify_get_inventory_levels", annotations={"readOnlyHint": True})
    async def shopify_get_inventory_levels(params: GetInventoryLevelsInput) -> str:
        """Get inventory levels for specific locations or items."""
        try:
            p: Dict[str, Any] = {}
            if params.location_id:
                p["location_ids"] = params.location_id
            if params.inventory_item_ids:
                p["inventory_item_ids"] = params.inventory_item_ids
            data   = await _request("GET", "inventory_levels.json", params=p)
            levels = data.get("inventory_levels", [])
            return _fmt({"count": len(levels), "inventory_levels": levels})
        except Exception as e:
            return _error(e)

    class SetInventoryLevelInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        inventory_item_id: int = Field(...)
        location_id:       int = Field(...)
        available:         int = Field(..., description="Available quantity to set")

    @mcp.tool(name="shopify_set_inventory_level", annotations={"readOnlyHint": False})
    async def shopify_set_inventory_level(params: SetInventoryLevelInput) -> str:
        """Set the available inventory for an item at a location."""
        try:
            body = {"inventory_item_id": params.inventory_item_id, "location_id": params.location_id, "available": params.available}
            data = await _request("POST", "inventory_levels/set.json", body=body)
            return _fmt(data.get("inventory_level", data))
        except Exception as e:
            return _error(e)

    # ═══════════════════════════════════════════════════════════════════════
    # FULFILLMENTS
    # ═══════════════════════════════════════════════════════════════════════

    class ListFulfillmentsInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        order_id: int           = Field(...)
        limit:    Optional[int] = Field(default=50, ge=1, le=250)

    @mcp.tool(name="shopify_list_fulfillments", annotations={"readOnlyHint": True})
    async def shopify_list_fulfillments(params: ListFulfillmentsInput) -> str:
        """List fulfillments for a specific order."""
        try:
            data         = await _request("GET", f"orders/{params.order_id}/fulfillments.json", params={"limit": params.limit})
            fulfillments = data.get("fulfillments", [])
            return _fmt({"count": len(fulfillments), "fulfillments": fulfillments})
        except Exception as e:
            return _error(e)

    class CreateFulfillmentInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        order_id:         int                            = Field(...)
        location_id:      int                            = Field(...)
        tracking_number:  Optional[str]                  = Field(default=None)
        tracking_company: Optional[str]                  = Field(default=None)
        tracking_url:     Optional[str]                  = Field(default=None)
        line_items:       Optional[List[Dict[str, Any]]] = Field(default=None)
        notify_customer:  Optional[bool]                 = Field(default=True)

    @mcp.tool(name="shopify_create_fulfillment", annotations={"readOnlyHint": False})
    async def shopify_create_fulfillment(params: CreateFulfillmentInput) -> str:
        """Create a fulfillment for an order (ship items)."""
        try:
            fulfillment: Dict[str, Any] = {"location_id": params.location_id}
            for f in ["tracking_number", "tracking_company", "tracking_url", "line_items", "notify_customer"]:
                val = getattr(params, f)
                if val is not None:
                    fulfillment[f] = val
            data = await _request("POST", f"orders/{params.order_id}/fulfillments.json", body={"fulfillment": fulfillment})
            return _fmt(data.get("fulfillment", data))
        except Exception as e:
            return _error(e)

    # ═══════════════════════════════════════════════════════════════════════
    # DISCOUNTS & PRICE RULES
    # ═══════════════════════════════════════════════════════════════════════

    class ListPriceRulesInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        limit:    Optional[int] = Field(default=50, ge=1, le=250)
        since_id: Optional[int] = Field(default=None)

    @mcp.tool(name="shopify_list_price_rules", annotations={"readOnlyHint": True})
    async def shopify_list_price_rules(params: ListPriceRulesInput) -> str:
        """List all price rules (discount campaigns)."""
        try:
            p: Dict[str, Any] = {"limit": params.limit}
            if params.since_id:
                p["since_id"] = params.since_id
            data  = await _request("GET", "price_rules.json", params=p)
            rules = data.get("price_rules", [])
            return _fmt({"count": len(rules), "price_rules": rules})
        except Exception as e:
            return _error(e)

    class CreatePriceRuleInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        title:              str            = Field(...)
        value_type:         str            = Field(..., description="'percentage' or 'fixed_amount'")
        value:              str            = Field(..., description="e.g. '-10.0'")
        target_type:        str            = Field(default="line_item")
        target_selection:   str            = Field(default="all")
        allocation_method:  str            = Field(default="across")
        customer_selection: str            = Field(default="all")
        starts_at:          str            = Field(..., description="ISO 8601 date")
        ends_at:            Optional[str]  = Field(default=None)
        usage_limit:        Optional[int]  = Field(default=None)
        once_per_customer:  Optional[bool] = Field(default=False)

    @mcp.tool(name="shopify_create_price_rule", annotations={"readOnlyHint": False})
    async def shopify_create_price_rule(params: CreatePriceRuleInput) -> str:
        """Create a new price rule (discount campaign)."""
        try:
            rule: Dict[str, Any] = {}
            for f in ["title", "value_type", "value", "target_type", "target_selection",
                      "allocation_method", "customer_selection", "starts_at", "ends_at",
                      "usage_limit", "once_per_customer"]:
                val = getattr(params, f)
                if val is not None:
                    rule[f] = val
            data = await _request("POST", "price_rules.json", body={"price_rule": rule})
            return _fmt(data.get("price_rule", data))
        except Exception as e:
            return _error(e)

    class ListDiscountCodesInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        price_rule_id: int           = Field(...)
        limit:         Optional[int] = Field(default=50, ge=1, le=250)

    @mcp.tool(name="shopify_list_discount_codes", annotations={"readOnlyHint": True})
    async def shopify_list_discount_codes(params: ListDiscountCodesInput) -> str:
        """List all discount codes for a price rule."""
        try:
            data  = await _request("GET", f"price_rules/{params.price_rule_id}/discount_codes.json", params={"limit": params.limit})
            codes = data.get("discount_codes", [])
            return _fmt({"count": len(codes), "discount_codes": codes})
        except Exception as e:
            return _error(e)

    class CreateDiscountCodeInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        price_rule_id: int = Field(...)
        code:          str = Field(..., description="e.g. 'SUMMER20'")

    @mcp.tool(name="shopify_create_discount_code", annotations={"readOnlyHint": False})
    async def shopify_create_discount_code(params: CreateDiscountCodeInput) -> str:
        """Create a discount code for a price rule."""
        try:
            data = await _request("POST", f"price_rules/{params.price_rule_id}/discount_codes.json", body={"discount_code": {"code": params.code}})
            return _fmt(data.get("discount_code", data))
        except Exception as e:
            return _error(e)

    # ═══════════════════════════════════════════════════════════════════════
    # PAGES
    # ═══════════════════════════════════════════════════════════════════════

    class ListPagesInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        limit:            Optional[int] = Field(default=50, ge=1, le=250)
        published_status: Optional[str] = Field(default="any", description="published, unpublished, any")

    @mcp.tool(name="shopify_list_pages", annotations={"readOnlyHint": True})
    async def shopify_list_pages(params: ListPagesInput) -> str:
        """List all static pages in the store (About, FAQ, etc.)."""
        try:
            data  = await _request("GET", "pages.json", params={"limit": params.limit, "published_status": params.published_status})
            pages = data.get("pages", [])
            return _fmt({"count": len(pages), "pages": pages})
        except Exception as e:
            return _error(e)

    class CreatePageInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        title:            str            = Field(...)
        body_html:        Optional[str]  = Field(default=None)
        handle:           Optional[str]  = Field(default=None, description="URL slug, e.g. 'about-us'")
        meta_title:       Optional[str]  = Field(default=None)
        meta_description: Optional[str]  = Field(default=None)
        published:        Optional[bool] = Field(default=False)

    @mcp.tool(name="shopify_create_page", annotations={"readOnlyHint": False})
    async def shopify_create_page(params: CreatePageInput) -> str:
        """Create a new static page in the store."""
        try:
            page: Dict[str, Any] = {"title": params.title}
            for f in ["body_html", "handle", "meta_title", "meta_description", "published"]:
                val = getattr(params, f)
                if val is not None:
                    page[f] = val
            data = await _request("POST", "pages.json", body={"page": page})
            return _fmt(data.get("page", data))
        except Exception as e:
            return _error(e)

    class UpdatePageInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        page_id:          int            = Field(...)
        title:            Optional[str]  = Field(default=None)
        body_html:        Optional[str]  = Field(default=None)
        handle:           Optional[str]  = Field(default=None)
        meta_title:       Optional[str]  = Field(default=None)
        meta_description: Optional[str]  = Field(default=None)
        published:        Optional[bool] = Field(default=None)

    @mcp.tool(name="shopify_update_page", annotations={"readOnlyHint": False})
    async def shopify_update_page(params: UpdatePageInput) -> str:
        """Update a static page content or SEO fields."""
        try:
            page: Dict[str, Any] = {}
            for f in ["title", "body_html", "handle", "meta_title", "meta_description", "published"]:
                val = getattr(params, f)
                if val is not None:
                    page[f] = val
            data = await _request("PUT", f"pages/{params.page_id}.json", body={"page": page})
            return _fmt(data.get("page", data))
        except Exception as e:
            return _error(e)

    # ═══════════════════════════════════════════════════════════════════════
    # BLOGS & ARTICLES
    # ═══════════════════════════════════════════════════════════════════════

    class ListBlogsInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        limit:    Optional[int] = Field(default=50, ge=1, le=250)
        since_id: Optional[int] = Field(default=None)

    @mcp.tool(name="shopify_list_blogs", annotations={"readOnlyHint": True})
    async def shopify_list_blogs(params: ListBlogsInput) -> str:
        """List all blogs in the Shopify store."""
        try:
            p: Dict[str, Any] = {"limit": params.limit}
            if params.since_id:
                p["since_id"] = params.since_id
            data  = await _request("GET", "blogs.json", params=p)
            blogs = data.get("blogs", [])
            return _fmt({"count": len(blogs), "blogs": blogs})
        except Exception as e:
            return _error(e)

    class ListArticlesInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        blog_id:          int            = Field(...)
        limit:            Optional[int]  = Field(default=50, ge=1, le=250)
        since_id:         Optional[int]  = Field(default=None)
        published_status: Optional[str]  = Field(default="any", description="published, unpublished, any")

    @mcp.tool(name="shopify_list_articles", annotations={"readOnlyHint": True})
    async def shopify_list_articles(params: ListArticlesInput) -> str:
        """List articles in a specific blog."""
        try:
            p: Dict[str, Any] = {"limit": params.limit, "published_status": params.published_status}
            if params.since_id:
                p["since_id"] = params.since_id
            data     = await _request("GET", f"blogs/{params.blog_id}/articles.json", params=p)
            articles = data.get("articles", [])
            return _fmt({"count": len(articles), "articles": articles})
        except Exception as e:
            return _error(e)

    class GetArticleInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        blog_id:    int = Field(...)
        article_id: int = Field(...)

    @mcp.tool(name="shopify_get_article", annotations={"readOnlyHint": True})
    async def shopify_get_article(params: GetArticleInput) -> str:
        """Retrieve a single blog article by ID."""
        try:
            data = await _request("GET", f"blogs/{params.blog_id}/articles/{params.article_id}.json")
            return _fmt(data.get("article", data))
        except Exception as e:
            return _error(e)

    class CreateArticleInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        blog_id:          int            = Field(...)
        title:            str            = Field(..., min_length=1)
        body_html:        Optional[str]  = Field(default=None)
        author:           Optional[str]  = Field(default=None)
        tags:             Optional[str]  = Field(default=None)
        summary_html:     Optional[str]  = Field(default=None)
        meta_title:       Optional[str]  = Field(default=None)
        meta_description: Optional[str]  = Field(default=None)
        published:        Optional[bool] = Field(default=False, description="False = draft")

    @mcp.tool(name="shopify_create_article", annotations={"readOnlyHint": False})
    async def shopify_create_article(params: CreateArticleInput) -> str:
        """Create a new blog article. Set published=False to save as draft."""
        try:
            article: Dict[str, Any] = {"title": params.title}
            for f in ["body_html", "author", "tags", "summary_html", "meta_title", "meta_description", "published"]:
                val = getattr(params, f)
                if val is not None:
                    article[f] = val
            data = await _request("POST", f"blogs/{params.blog_id}/articles.json", body={"article": article})
            return _fmt(data.get("article", data))
        except Exception as e:
            return _error(e)

    class UpdateArticleInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        blog_id:          int            = Field(...)
        article_id:       int            = Field(...)
        title:            Optional[str]  = Field(default=None)
        body_html:        Optional[str]  = Field(default=None)
        author:           Optional[str]  = Field(default=None)
        tags:             Optional[str]  = Field(default=None)
        summary_html:     Optional[str]  = Field(default=None)
        meta_title:       Optional[str]  = Field(default=None)
        meta_description: Optional[str]  = Field(default=None)
        published:        Optional[bool] = Field(default=None)

    @mcp.tool(name="shopify_update_article", annotations={"readOnlyHint": False})
    async def shopify_update_article(params: UpdateArticleInput) -> str:
        """Update an existing blog article."""
        try:
            article: Dict[str, Any] = {}
            for f in ["title", "body_html", "author", "tags", "summary_html", "meta_title", "meta_description", "published"]:
                val = getattr(params, f)
                if val is not None:
                    article[f] = val
            data = await _request("PUT", f"blogs/{params.blog_id}/articles/{params.article_id}.json", body={"article": article})
            return _fmt(data.get("article", data))
        except Exception as e:
            return _error(e)

    class DeleteArticleInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        blog_id:    int = Field(...)
        article_id: int = Field(...)

    @mcp.tool(name="shopify_delete_article", annotations={"readOnlyHint": False, "destructiveHint": True})
    async def shopify_delete_article(params: DeleteArticleInput) -> str:
        """Permanently delete a blog article."""
        try:
            await _request("DELETE", f"blogs/{params.blog_id}/articles/{params.article_id}.json")
            return f"Article {params.article_id} deleted from blog {params.blog_id}."
        except Exception as e:
            return _error(e)

    # ═══════════════════════════════════════════════════════════════════════
    # REDIRECTS
    # ═══════════════════════════════════════════════════════════════════════

    class ListRedirectsInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        limit:  Optional[int] = Field(default=50, ge=1, le=250)
        path:   Optional[str] = Field(default=None)
        target: Optional[str] = Field(default=None)

    @mcp.tool(name="shopify_list_redirects", annotations={"readOnlyHint": True})
    async def shopify_list_redirects(params: ListRedirectsInput) -> str:
        """List URL redirects (301s) in the store."""
        try:
            p: Dict[str, Any] = {"limit": params.limit}
            for f in ["path", "target"]:
                val = getattr(params, f)
                if val is not None:
                    p[f] = val
            data      = await _request("GET", "redirects.json", params=p)
            redirects = data.get("redirects", [])
            return _fmt({"count": len(redirects), "redirects": redirects})
        except Exception as e:
            return _error(e)

    class CreateRedirectInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        path:   str = Field(..., description="Source path, e.g. '/old-product'")
        target: str = Field(..., description="Target path or URL")

    @mcp.tool(name="shopify_create_redirect", annotations={"readOnlyHint": False})
    async def shopify_create_redirect(params: CreateRedirectInput) -> str:
        """Create a 301 URL redirect."""
        try:
            data = await _request("POST", "redirects.json", body={"redirect": {"path": params.path, "target": params.target}})
            return _fmt(data.get("redirect", data))
        except Exception as e:
            return _error(e)

    class DeleteRedirectInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        redirect_id: int = Field(...)

    @mcp.tool(name="shopify_delete_redirect", annotations={"readOnlyHint": False, "destructiveHint": True})
    async def shopify_delete_redirect(params: DeleteRedirectInput) -> str:
        """Delete a URL redirect."""
        try:
            await _request("DELETE", f"redirects/{params.redirect_id}.json")
            return f"Redirect {params.redirect_id} deleted."
        except Exception as e:
            return _error(e)

    # ═══════════════════════════════════════════════════════════════════════
    # GIFT CARDS
    # ═══════════════════════════════════════════════════════════════════════

    class ListGiftCardsInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        limit:  Optional[int] = Field(default=50, ge=1, le=250)
        status: Optional[str] = Field(default="enabled", description="enabled or disabled")

    @mcp.tool(name="shopify_list_gift_cards", annotations={"readOnlyHint": True})
    async def shopify_list_gift_cards(params: ListGiftCardsInput) -> str:
        """List gift cards in the store."""
        try:
            data  = await _request("GET", "gift_cards.json", params={"limit": params.limit, "status": params.status})
            cards = data.get("gift_cards", [])
            return _fmt({"count": len(cards), "gift_cards": cards})
        except Exception as e:
            return _error(e)

    class CreateGiftCardInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        initial_value: str           = Field(..., description="e.g. '50.00'")
        code:          Optional[str] = Field(default=None, description="Auto-generated if omitted")
        note:          Optional[str] = Field(default=None)
        expires_on:    Optional[str] = Field(default=None, description="YYYY-MM-DD")
        customer_id:   Optional[int] = Field(default=None)

    @mcp.tool(name="shopify_create_gift_card", annotations={"readOnlyHint": False})
    async def shopify_create_gift_card(params: CreateGiftCardInput) -> str:
        """Create a new gift card."""
        try:
            card: Dict[str, Any] = {"initial_value": params.initial_value}
            for f in ["code", "note", "expires_on", "customer_id"]:
                val = getattr(params, f)
                if val is not None:
                    card[f] = val
            data = await _request("POST", "gift_cards.json", body={"gift_card": card})
            return _fmt(data.get("gift_card", data))
        except Exception as e:
            return _error(e)

    # ═══════════════════════════════════════════════════════════════════════
    # SHIPPING ZONES & TRANSACTIONS
    # ═══════════════════════════════════════════════════════════════════════

    @mcp.tool(name="shopify_list_shipping_zones", annotations={"readOnlyHint": True})
    async def shopify_list_shipping_zones(params: EmptyInput) -> str:
        """List all shipping zones and their rates."""
        try:
            data  = await _request("GET", "shipping_zones.json")
            zones = data.get("shipping_zones", [])
            return _fmt({"count": len(zones), "shipping_zones": zones})
        except Exception as e:
            return _error(e)

    class ListTransactionsInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        order_id: int           = Field(...)
        limit:    Optional[int] = Field(default=50, ge=1, le=250)

    @mcp.tool(name="shopify_list_transactions", annotations={"readOnlyHint": True})
    async def shopify_list_transactions(params: ListTransactionsInput) -> str:
        """List payment transactions for an order."""
        try:
            data         = await _request("GET", f"orders/{params.order_id}/transactions.json", params={"limit": params.limit})
            transactions = data.get("transactions", [])
            return _fmt({"count": len(transactions), "transactions": transactions})
        except Exception as e:
            return _error(e)

    # ═══════════════════════════════════════════════════════════════════════
    # SHOP INFO & WEBHOOKS
    # ═══════════════════════════════════════════════════════════════════════

    @mcp.tool(name="shopify_get_shop", annotations={"readOnlyHint": True})
    async def shopify_get_shop(params: EmptyInput) -> str:
        """Get store info: name, domain, plan, currency, timezone."""
        try:
            data = await _request("GET", "shop.json")
            return _fmt(data.get("shop", data))
        except Exception as e:
            return _error(e)

    class ListWebhooksInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        limit: Optional[int] = Field(default=50, ge=1, le=250)
        topic: Optional[str] = Field(default=None, description="e.g. orders/create")

    @mcp.tool(name="shopify_list_webhooks", annotations={"readOnlyHint": True})
    async def shopify_list_webhooks(params: ListWebhooksInput) -> str:
        """List configured webhooks."""
        try:
            p: Dict[str, Any] = {"limit": params.limit}
            if params.topic:
                p["topic"] = params.topic
            data     = await _request("GET", "webhooks.json", params=p)
            webhooks = data.get("webhooks", [])
            return _fmt({"count": len(webhooks), "webhooks": webhooks})
        except Exception as e:
            return _error(e)

    class CreateWebhookInput(BaseModel):
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        topic:   str           = Field(..., description="e.g. orders/create, products/update")
        address: str           = Field(..., description="URL to receive the webhook POST")
        format:  Optional[str] = Field(default="json")

    @mcp.tool(name="shopify_create_webhook", annotations={"readOnlyHint": False})
    async def shopify_create_webhook(params: CreateWebhookInput) -> str:
        """Create a new webhook subscription."""
        try:
            data = await _request("POST", "webhooks.json", body={"webhook": {"topic": params.topic, "address": params.address, "format": params.format}})
            return _fmt(data.get("webhook", data))
        except Exception as e:
            return _error(e)

    # ═══════════════════════════════════════════════════════════════════════
    # REPORTS & ANALYTICS
    # ═══════════════════════════════════════════════════════════════════════

    class SalesReportInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        created_at_min:   str            = Field(..., description="Start date ISO 8601")
        created_at_max:   str            = Field(..., description="End date ISO 8601")
        limit:            Optional[int]  = Field(default=250, ge=1, le=250)
        financial_status: Optional[str]  = Field(default="paid")

    @mcp.tool(name="shopify_sales_report", annotations={"readOnlyHint": True})
    async def shopify_sales_report(params: SalesReportInput) -> str:
        """Get a sales report for a date range with revenue summary."""
        try:
            p = {
                "created_at_min":   params.created_at_min,
                "created_at_max":   params.created_at_max,
                "limit":            params.limit,
                "financial_status": params.financial_status,
                "status":           "any",
                "fields":           "id,order_number,created_at,total_price,subtotal_price,total_tax,financial_status,line_items,customer",
            }
            data   = await _request("GET", "orders.json", params=p)
            orders = data.get("orders", [])
            total_revenue = sum(float(o.get("total_price", 0)) for o in orders)
            total_items   = sum(sum(li.get("quantity", 0) for li in o.get("line_items", [])) for o in orders)
            return _fmt({
                "summary": {"order_count": len(orders), "total_revenue": round(total_revenue, 2), "total_items_sold": total_items, "date_range": {"from": params.created_at_min, "to": params.created_at_max}},
                "orders": orders,
            })
        except Exception as e:
            return _error(e)

    class TopProductsReportInput(BaseModel):
        model_config = ConfigDict(extra="forbid")
        created_at_min: str           = Field(..., description="Start date ISO 8601")
        created_at_max: str           = Field(..., description="End date ISO 8601")
        limit:          Optional[int] = Field(default=250, ge=1, le=250)

    @mcp.tool(name="shopify_top_products_report", annotations={"readOnlyHint": True})
    async def shopify_top_products_report(params: TopProductsReportInput) -> str:
        """Get top selling products by units sold and revenue for a date range."""
        try:
            p = {"created_at_min": params.created_at_min, "created_at_max": params.created_at_max, "limit": params.limit, "financial_status": "paid", "status": "any", "fields": "line_items"}
            data   = await _request("GET", "orders.json", params=p)
            orders = data.get("orders", [])
            product_stats: Dict[str, Any] = {}
            for order in orders:
                for item in order.get("line_items", []):
                    pid   = str(item.get("product_id", "unknown"))
                    title = item.get("title", "Unknown")
                    qty   = item.get("quantity", 0)
                    price = float(item.get("price", 0)) * qty
                    if pid not in product_stats:
                        product_stats[pid] = {"product_id": pid, "title": title, "units_sold": 0, "revenue": 0.0}
                    product_stats[pid]["units_sold"] += qty
                    product_stats[pid]["revenue"]    += price
            sorted_products = sorted(product_stats.values(), key=lambda x: x["units_sold"], reverse=True)
            for p_stat in sorted_products:
                p_stat["revenue"] = round(p_stat["revenue"], 2)
            return _fmt({"top_products": sorted_products})
        except Exception as e:
            return _error(e)
