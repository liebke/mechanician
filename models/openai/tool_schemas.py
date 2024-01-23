tool_schemas = [
        {
            "type": "function",
            "function": {
                "name": "createProductOffer",
                "description": "Creates a new ProductOffer object",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ProductOfferType": {
                            "type": "string",
                            "description": "The ProductOffer Type, must be one of the following: Bundle, Package, Component, Promotion, ComponentGroup"
                        },
                         "BusinessId": {
                            "type": "string",
                            "description": """An automatically generated, business-readable ID that labels the entity with a suitable ID that can be used to reference the entity so that longer, internal system identifiers are not needed. Along with Name, you can use this identifier to search for entities, in addition to the other search options."""
                        },
                        "MaxChildElements": {
                            "type": "integer",
                            "description": "Maximum customer portfolio instances"
                        },
                        "MinMinChildElements": {
                            "type": "integer",
                            "description": "Minimum customer portfolio instances"
                        },
                        "AvailableEndDate": {
                            "type": "string",
                            "format": "date",
                            "description": """The date on which the entity is no longer available to customers, which must fall within the effective date range."""
                        },
                        "AvailableStartDate": {
                            "type": "string",
                            "format": "date",
                            "description": """The date on which the entity becomes available to customers, which must fall within the effective date range. This value is required by default."""
                        },
                        "BusinessID": {
                            "type": "string",
                            "description": "The business identifier"
                        },
                        "CategoryID": {
                            "type": "string",
                            "description": "The category identifier"
                        },
                        "Description": {
                            "type": "string",
                            "description": "A description of the entity."
                        },
                        "EffectiveEndDate": {
                            "type": "string",
                            "format": "date",
                            "description": """The date on which the entity should become inactive in your organization. This value is optional to allow for no expiry date."""
                        },
                        "EffectiveStartDate": {
                            "type": "string",
                            "format": "date",
                            "description": """The date on which the entity should become effective and active in your organization. This value is required by default."""
                        },
                        "ElementGuid": {
                            "type": "string",
                            "description": "The element GUID"
                        },
                        "ElementTypeGuid": {
                            "type": "string",
                            "description": "The element type GUID"
                        },
                        "Name": {
                            "type": "string",
                            "description": """Name: A descriptive name for the entity that must be unique in the category of the product catalog where the entity resides. For example, two components may not share the same name unless they sit in different categories of the catalog. This value is required."""
                        }
                    },
                    "required": ["Name", "ProductCategory", "ProductId"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "createProductToProductRelationship",
                "description": "Creates a new Relationship object between two Products",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ParentProductOffer": {
                            "type": "string",
                            "description": "The ID of the parent product offer"
                        },
                        "ChildProductOffer": {
                            "type": "string",
                            "description": "The ID of the child product offer"
                        },
                        
                    },
                    "required": ["SourceProduct", "TargetProduct"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "createProductToChargeRelationship",
                "description": "Creates a new Relationship object between a Product and a Charge object",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ProductId": {
                            "type": "string",
                            "description": "The ID of the Product"
                        },
                        "ChargeId": {
                            "type": "string",
                            "description": "The ID of the Charge"
                        },
                        
                    },
                    "required": ["ProductId", "ChargeId"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "createCharge",
                "description": "Creates a new Product object",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ChargeType": {
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
                        "AvailableEndDate": {
                            "type": "string",
                            "format": "date",
                            "description": "The available end date"
                        },
                        "AvailableStartDate": {
                            "type": "string",
                            "format": "date",
                            "description": "The available start date"
                        },
                        "BusinessID": {
                            "type": "string",
                            "description": "The business identifier"
                        },
                        "CategoryID": {
                            "type": "string",
                            "description": "The category identifier"
                        },
                        "Description": {
                            "type": "string",
                            "description": "The description of the Charge"
                        },
                        "ActivationEndDate": {
                            "type": "string",
                            "format": "date",
                            "description": "The activation end date"
                        },
                        "ActivationStartDate": {
                            "type": "string",
                            "format": "date",
                            "description": "The activation start date"
                        },
                        "Name": {
                            "type": "string",
                            "description": "The name of the launch entity"
                        },
                        "ChargeId": {
                            "type": "string",
                            "description": "The ID of the Charge"
                        },
                        "Rate": {
                            "type": "string",
                            "description": "The Rate of the Charge"
                        }
                    },
                    "required": ["Name", "ChargeId"]
                }
            }
        }
    ]