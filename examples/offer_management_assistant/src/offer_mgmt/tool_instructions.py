tool_instructions = [
        {
            "type": "function",
            "function": {
                "name": "create_product_offer",
                "description": "Creates a new ProductOffer object",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_offer_type": {
                            "type": "string",
                            "description": "The ProductOffer Type, must be one of the following: Bundle, Package, Component, Promotion, ComponentGroup"
                        },
                         "business_id": {
                            "type": "string",
                            "description": """An automatically generated, business-readable ID that labels the entity with a suitable ID that can be used to reference the entity so that longer, internal system identifiers are not needed. Along with name, you can use this identifier to search for entities, in addition to the other search options."""
                        },
                        "max_child_elements": {
                            "type": "integer",
                            "description": "Maximum customer portfolio instances"
                        },
                        "min_child_elements": {
                            "type": "integer",
                            "description": "Minimum customer portfolio instances"
                        },
                        "available_end_date": {
                            "type": "string",
                            "format": "date",
                            "description": """The date on which the entity is no longer available to customers, which must fall within the effective date range."""
                        },
                        "available_start_date": {
                            "type": "string",
                            "format": "date",
                            "description": """The date on which the entity becomes available to customers, which must fall within the effective date range. This value is required by default."""
                        },
                        "business_id": {
                            "type": "string",
                            "description": "The business identifier"
                        },
                        "category_id": {
                            "type": "string",
                            "description": "The category identifier"
                        },
                        "description": {
                            "type": "string",
                            "description": "A description of the entity."
                        },
                        "effective_end_date": {
                            "type": "string",
                            "format": "date",
                            "description": """The date on which the entity should become inactive in your organization. This value is optional to allow for no expiry date."""
                        },
                        "effective_start_date": {
                            "type": "string",
                            "format": "date",
                            "description": """The date on which the entity should become effective and active in your organization. This value is required by default."""
                        },
                        "element_guid": {
                            "type": "string",
                            "description": "The element GUID"
                        },
                        "element_type_guid": {
                            "type": "string",
                            "description": "The element type GUID"
                        },
                        "name": {
                            "type": "string",
                            "description": """name: A descriptive name for the entity that must be unique in the category of the product catalog where the entity resides. For example, two components may not share the same name unless they sit in different categories of the catalog. This value is required."""
                        }
                    },
                    "required": ["name", "product_offer_type", "business_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_product_to_product_relationship",
                "description": "Creates a new Relationship object between two Products",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "parent_product_offer": {
                            "type": "string",
                            "description": "The Business ID of the parent product offer"
                        },
                        "child_product_offer": {
                            "type": "string",
                            "description": "The Business ID of the child product offer"
                        },
                        
                    },
                    "required": ["parent_product_offer", "child_product_offer"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_product_to_charge_relationship",
                "description": "Creates a new Relationship object between a Product and a Charge object",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "string",
                            "description": "The Business ID of the Product"
                        },
                        "charge_id": {
                            "type": "string",
                            "description": "The Charge ID of the Charge"
                        },
                        
                    },
                    "required": ["product_id", "charge_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_charge",
                "description": "Creates a new Product object",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "charge_type": {
                            "type": "string",
                            "description": """The Charge Type, must be one of the following: 
                                                * EventCharge, 
                                                * RecurringCharge, 
                                                * NonRecurringCharge, 
                                                * StandaloneRecurringCharge, 
                                                * StandAloneNonRecurringCharge, 
                                                * RecurringCostBasedCharge, 
                                                * NonRecurringCostBasedCharge."""
                        },
                        "category_id": {
                            "type": "string",
                            "description": "The category identifier"
                        },
                        "description": {
                            "type": "string",
                            "description": "The description of the Charge"
                        },
                        "activation_end_date": {
                            "type": "string",
                            "format": "date",
                            "description": "The activation end date"
                        },
                        "activation_start_date": {
                            "type": "string",
                            "format": "date",
                            "description": "The activation start date"
                        },
                        "name": {
                            "type": "string",
                            "description": "The name of the launch entity"
                        },
                        "charge_id": {
                            "type": "string",
                            "description": "The ID of the Charge"
                        },
                        "rate": {
                            "type": "string",
                            "description": "The rate of the Charge"
                        }
                    },
                    "required": ["name", "charge_id"]
                }
            }
        },
        {
        "type": "function",
        "function": {
            "name": "get_product_offer",
            "description": "Returns a Product Offer object given a Business ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "business_id": {
                        "type": "string",
                        "description": "The Business ID of the Product Offer"
                    }
                },
                "required": ["business_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_charge",
            "description": "Returns a Charge object given a Charge ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "charge_id": {
                        "type": "string",
                        "description": "The ID of the Charge"
                    }
                },
                "required": ["charge_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_child_products",
            "description": "Returns all the child product offers of a parent product offer",
            "parameters": {
                "type": "object",
                "properties": {
                    "parent_business_id": {
                        "type": "string",
                        "description": "The Business ID of the Parent Product Offer"
                    }
                },
                "required": ["parent_business_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_parent_products",
            "description": "Returns all the parent product offers of a child product offer",
            "parameters": {
                "type": "object",
                "properties": {
                    "child_business_id": {
                        "type": "string",
                        "description": "The Business ID of the Child Product Offer"
                    }
                },
                "required": ["child_business_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_related_charges",
            "description": "Returns all the Charge Relationship of a product offer",
            "parameters": {
                "type": "object",
                "properties": {
                    "business_id": {
                        "type": "string",
                        "description": "The Business ID of the Product Offer"
                    }
                },
                "required": ["business_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_product_offers",
            "description": "Returns all the available product offers",
            "parameters": {
                "type": "object",
                "properties": {
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_charges",
            "description": "Returns all existing Charges",
            "parameters": {
                "type": "object",
                "properties": {
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_product_relationships",
            "description": "Returns all the existing product relationships",
            "parameters": {
                "type": "object",
                "properties": {
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_charge_relationships",
            "description": "Returns all the existing charge relationships",
            "parameters": {
                "type": "object",
                "properties": {
                },
                "required": []
            }
        }
    },
    ]