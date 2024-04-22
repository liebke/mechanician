Each object in the data below represents a product offer for a given brand, there may be cases where products for a single brand overlap in the following columns:

base_nrc, base_rc, final_rc, final_nrc, promo_allowance, base_allowance, allowance_type, allowance_unit

Given that, can you generate a new "{{ brand }}" product that fits within the product line but does not overlap so much with existing products in the category that it would provide business value?

PRODUCTS IN BRAND "{{brand}}":

```
{{ products }}
```

INSTRUCTIONS:

Now create a new Product Offer from the product family "{{ product_family }}" for brand "{{ brand }}" that does not overlap with the existing products in the category. Provide a justification for the new offer that you create.

Once the new product offer is created, ask the user if the product offer is satisfactory, and if they confirm then call the `create_product_offer` function passing it the 'product' parameter which is the a new instance of a product offer JSON object, modeled on the data above, that you must generate.


