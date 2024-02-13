tool_instructions = [
    {
      "type": "function",
      "function": {
        "name": "create_document_collection",
        "description": "Creates a new document collection.",
        "parameters": {
          "type": "object",
          "properties": {
            "collection_name": {
              "type": "string",
              "description": "The name of the collection to create."
            }
          },
          "required": ["collection_name"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "create_link_collection",
        "description": "Creates a new link collection.",
        "parameters": {
          "type": "object",
          "properties": {
            "link_collection_name": {
              "type": "string",
              "description": "The name of the link collection to create."
            }
          },
          "required": ["link_collection_name"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "delete_collection",
        "description": "Deletes an existing collection.",
        "parameters": {
          "type": "object",
          "properties": {
            "collection_name": {
              "type": "string",
              "description": "The name of the collection to delete."
            }
          },
          "required": ["collection_name"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "delete_document",
        "description": "Deletes an existing document.",
        "parameters": {
          "type": "object",
          "properties": {
            "document_id": {
              "type": "string",
              "description": "The ID of the document to delete."
            }
          },
          "required": ["document_id"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "delete_link",
        "description": "Deletes an existing link.",
        "parameters": {
          "type": "object",
          "properties": {
            "link_id": {
              "type": "string",
              "description": "The ID of the link to delete."
            }
          },
          "required": ["link_id"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "create_document",
        "description": "Creates a new document in a collection.",
        "parameters": {
          "type": "object",
          "properties": {
            "collection_name": {
              "type": "string",
              "description": "The name of the collection."
            },
            "document_id": {
              "type": "string",
              "description": "The id of the document to create."
            },
            "document": {
              "type": "object",
              "description": "The document to create, this is a JSON object with many fields as described by the user."
            }
          },
          "required": ["collection_name", "document_id", "document"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "add_field_to_document",
        "description": "Adds a new field, with a specified value, to a document in a collection.",
        "parameters": {
          "type": "object",
          "properties": {
            "collection_name": {
              "type": "string",
              "description": "The name of the collection."
            },
            "document_id": {
              "type": "string",
              "description": "The id of the document to create."
            },
            "field_name": {
              "type": "object",
              "description": "The name of the field to create."
            },
            "field_value": {
              "type": "object",
              "description": "The value of the field to be created."
            }
          },
          "required": ["collection_name", "document_id", "field_name", "field_value"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "link_documents",
        "description": "Creates a link between two documents.",
        "parameters": {
          "type": "object",
          "properties": {
            "source_collection_name": {
              "type": "string",
              "description": "The name of the source collection."
            },
            "source_document_id": {
              "type": "string",
              "description": "The id of the source document."
            },
            "target_collection_name": {
              "type": "string",
              "description": "The name of the target collection."
            },
            "target_document_id": {
              "type": "string",
              "description": "The id of the target document."
            },
            "link_collection": {
              "type": "object",
              "description": "The link collection."
            },
            "link_attributes": {
              "type": "object",
              "description": "The attributes of the link."
            }
          },
          "required": ["source_collection_name", "source_document_id", "target_collection_name", "target_document_id", "link_collection"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "get_document",
        "description": "Gets a document from a collection.",
        "parameters": {
          "type": "object",
          "properties": {
            "collection_name": {
              "type": "string",
              "description": "The name of the collection."
            },
            "document_id": {
              "type": "string",
              "description": "The id of the document to get."
            }
          },
          "required": ["collection_name", "document_id"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "list_documents_linked_to",
        "description": "Lists all documents in the target collection that are linked from the source document.",
        "parameters": {
          "type": "object",
          "properties": {
            "target_collection_name": {
              "type": "string",
              "description": "The name of the target collection."
            },
            "target_document_id": {
              "type": "string",
              "description": "The id of the target document."
            },
            "from_collection_name": {
              "type": "string",
              "description": "The name of the source collection."
            },
            "link_collection_name": {
              "type": "string",
              "description": "The name of the link collection."
            }
          },
          "required": ["target_collection_name", "target_document_id", "from_collection_name", "link_collection_name"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "list_documents_linked_from",
        "description": "Lists all documents in the target collection that are linked to the source document.",
        "parameters": {
          "type": "object",
          "properties": {
            "source_collection_name": {
              "type": "string",
              "description": "The name of the source collection."
            },
            "source_document_id": {
              "type": "string",
              "description": "The id of the source document."
            },
            "target_collection_name": {
              "type": "string",
              "description": "The name of the target collection."
            },
            "link_collection_name": {
              "type": "string",
              "description": "The name of the link collection."
            }
          },
          "required": ["source_collection_name", "source_document_id", "target_collection_name", "link_collection_name"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "list_documents",
        "description": "Lists all documents in a collection.",
        "parameters": {
          "type": "object",
          "properties": {
            "collection_name": {
              "type": "string",
              "description": "The name of the collection."
            }
          },
          "required": ["collection_name"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "list_links",
        "description": "Lists all links in a link collection.",
        "parameters": {
          "type": "object",
          "properties": {
            "link_collection_name": {
              "type": "string",
              "description": "The name of the link collection."
            }
          },
          "required": ["link_collection_name"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "list_inbound_links",
        "description": "Lists all inbound links to a document.",
        "parameters": {
          "type": "object",
          "properties": {
            "target_collection_name": {
              "type": "string",
              "description": "The name of the target collection."
            },
            "target_document_id": {
              "type": "string",
              "description": "The id of the target document."
            },
            "link_collection_name": {
              "type": "string",
              "description": "The name of the link collection."
            }
          },
          "required": ["target_collection_name", "target_document_id", "link_collection_name"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "list_outbound_links",
        "description": "Lists all outbound links from a document.",
        "parameters": {
          "type": "object",
          "properties": {
            "source_collection_name": {
              "type": "string",
              "description": "The name of the source collection."
            },
            "source_document_id": {
              "type": "string",
              "description": "The id of the source document."
            },
            "link_collection_name": {
              "type": "string",
              "description": "The name of the link collection."
            }
          },
          "required": ["source_collection_name", "source_document_id", "link_collection_name"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "list_document_collections",
        "description": "Lists all document collections."
      }
    },
    {
      "type": "function",
      "function": {
        "name": "list_link_collections",
        "description": "Lists all link collections."
      }
    },
    {
      "type": "function",
      "function": {
        "name": "list_collections",
        "description": "Lists all collections, both document collections and link collections."
      }
    }
  ]
