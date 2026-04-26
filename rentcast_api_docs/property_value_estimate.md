Value Estimate

# Value Estimate

Returns a property value estimate and comparable properties.

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

This endpoint returns the current property value estimate and comparable sale listings for a specific address or a latitude/longitude coordinate.

The value estimate returned by this endpoint represents the current market value, or after-repair value (ARV), of a given property.

It also returns several subject property attributes in the `subjectProperty` field. View the full [property valuation schema](https://developers.rentcast.io/reference/property-valuation-schema) to learn more about the response fields.

The returned comparable listings will be sorted by the `correlation` field in descending order, with the most similar listings appearing first. They can be used to display sales comps for a given property, or to calculate your own home value estimates.

<Callout icon="📘" theme="info">
  See [this guide](https://developers.rentcast.io/reference/property-valuation#increasing-avm-accuracy) to learn more about fine-tuning the AVM and comparable selection algorithms, and increasing the accuracy of the value estimates.
</Callout>

<Callout icon="📘" theme="info">
  For multi-family properties (`Multi-Family` or `Apartment` [property types](https://developers.rentcast.io/reference/property-types)), this endpoint will return a value estimate for the **entire multi-family or apartment building**. [Learn more](https://developers.rentcast.io/reference/property-valuation#avms-for-multi-family-properties) about AVMs for multi-family properties.
</Callout>

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

# OpenAPI definition

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "RentCast API",
    "version": "1.0"
  },
  "servers": [
    {
      "url": "https://api.rentcast.io/v1"
    }
  ],
  "components": {
    "securitySchemes": {
      "sec0": {
        "type": "apiKey",
        "in": "header",
        "name": "X-Api-Key"
      }
    }
  },
  "security": [
    {
      "sec0": []
    }
  ],
  "paths": {
    "/avm/value": {
      "get": {
        "summary": "Value Estimate",
        "description": "Returns a property value estimate and comparable properties.",
        "operationId": "value-estimate",
        "parameters": [
          {
            "name": "address",
            "in": "query",
            "description": "The **full address** of the property, in the format `Street, City, State, Zip`. You need to provide either the `address` or the `latitude`/`longitude` parameters",
            "schema": {
              "type": "string",
              "default": "5500 Grand Lake Dr, San Antonio, TX, 78244"
            }
          },
          {
            "name": "latitude",
            "in": "query",
            "description": "The latitude of the property. The `latitude`/`longitude` can be provided instead of the `address` parameter",
            "schema": {
              "type": "number",
              "format": "float"
            }
          },
          {
            "name": "longitude",
            "in": "query",
            "description": "The longitude of the property. The `latitude`/`longitude` can be provided instead of the `address` parameter",
            "schema": {
              "type": "number",
              "format": "float"
            }
          },
          {
            "name": "propertyType",
            "in": "query",
            "description": "The type of the property. See [explanation of property types](https://developers.rentcast.io/reference/property-types)",
            "schema": {
              "type": "string",
              "default": "",
              "enum": [
                "Single Family",
                "Condo",
                "Townhouse",
                "Manufactured",
                "Multi-Family",
                "Apartment",
                "Land"
              ]
            }
          },
          {
            "name": "bedrooms",
            "in": "query",
            "description": "The number of bedrooms in the property. Use `0` to indicate a studio layout",
            "schema": {
              "type": "number",
              "format": "float",
              "default": ""
            }
          },
          {
            "name": "bathrooms",
            "in": "query",
            "description": "The number of bathrooms in the property. Supports fractions to indicate partial bathrooms",
            "schema": {
              "type": "number",
              "format": "float",
              "default": ""
            }
          },
          {
            "name": "squareFootage",
            "in": "query",
            "description": "The total living area size of the property, in square feet",
            "schema": {
              "type": "number",
              "format": "float",
              "default": ""
            }
          },
          {
            "name": "maxRadius",
            "in": "query",
            "description": "The maximum distance between comparable listings and the subject property, in miles",
            "schema": {
              "type": "number",
              "format": "float"
            }
          },
          {
            "name": "daysOld",
            "in": "query",
            "description": "The maximum number of days since comparable listings were last seen on the market, with a minimum of 1",
            "schema": {
              "type": "integer",
              "format": "int32"
            }
          },
          {
            "name": "compCount",
            "in": "query",
            "description": "The number of comparable listings to use when calculating the value estimate, between 5 and 25. Defaults to `15` if not provided",
            "schema": {
              "type": "integer",
              "format": "int32",
              "default": 5
            }
          },
          {
            "in": "query",
            "name": "lookupSubjectAttributes",
            "schema": {
              "type": "boolean",
              "default": ""
            },
            "description": "When enabled, will attempt to look up subject property attributes to find more relevant comps. Defaults to `true` if not provided. [Learn more](https://developers.rentcast.io/reference/property-valuation#subject-property-attribute-lookup) about this feature"
          }
        ],
        "responses": {
          "200": {
            "description": "Success",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "price": {
                      "type": "number",
                      "example": 250000,
                      "default": ""
                    },
                    "priceRangeLow": {
                      "type": "number",
                      "example": 195000,
                      "default": ""
                    },
                    "priceRangeHigh": {
                      "type": "number",
                      "example": 304000,
                      "default": ""
                    },
                    "subjectProperty": {
                      "type": "object",
                      "properties": {
                        "id": {
                          "type": "string",
                          "example": "5500-Grand-Lake-Dr,-San-Antonio,-TX-78244"
                        },
                        "formattedAddress": {
                          "type": "string",
                          "example": "5500 Grand Lake Dr, San Antonio, TX 78244"
                        },
                        "addressLine1": {
                          "type": "string",
                          "example": "5500 Grand Lake Dr"
                        },
                        "addressLine2": {
                          "type": "string"
                        },
                        "city": {
                          "type": "string",
                          "example": "San Antonio"
                        },
                        "state": {
                          "type": "string",
                          "example": "TX"
                        },
                        "stateFips": {
                          "type": "string",
                          "example": "48"
                        },
                        "zipCode": {
                          "type": "string",
                          "example": "78244"
                        },
                        "county": {
                          "type": "string",
                          "example": "Bexar"
                        },
                        "countyFips": {
                          "type": "string",
                          "example": "029"
                        },
                        "latitude": {
                          "type": "number",
                          "example": 29.476011,
                          "default": ""
                        },
                        "longitude": {
                          "type": "number",
                          "example": -98.351454,
                          "default": ""
                        },
                        "propertyType": {
                          "type": "string",
                          "example": "Single Family"
                        },
                        "bedrooms": {
                          "type": "number",
                          "example": 3,
                          "default": ""
                        },
                        "bathrooms": {
                          "type": "number",
                          "example": 2,
                          "default": ""
                        },
                        "squareFootage": {
                          "type": "number",
                          "example": 1878,
                          "default": ""
                        },
                        "lotSize": {
                          "type": "number",
                          "example": 8843,
                          "default": ""
                        },
                        "yearBuilt": {
                          "type": "number",
                          "example": 1973,
                          "default": ""
                        },
                        "lastSaleDate": {
                          "type": "string",
                          "example": "2024-11-18T00:00:00.000Z",
                          "format": "date-time"
                        },
                        "lastSalePrice": {
                          "type": "number",
                          "example": 270000,
                          "default": ""
                        }
                      }
                    },
                    "comparables": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "id": {
                            "type": "string",
                            "example": "5207-Pine-Lake-Dr,-San-Antonio,-TX-78244"
                          },
                          "formattedAddress": {
                            "type": "string",
                            "example": "5207 Pine Lake Dr, San Antonio, TX 78244"
                          },
                          "addressLine1": {
                            "type": "string",
                            "example": "5207 Pine Lake Dr"
                          },
                          "addressLine2": {
                            "type": "string"
                          },
                          "city": {
                            "type": "string",
                            "example": "San Antonio"
                          },
                          "state": {
                            "type": "string",
                            "example": "TX"
                          },
                          "stateFips": {
                            "type": "string",
                            "example": "48"
                          },
                          "zipCode": {
                            "type": "string",
                            "example": "78244"
                          },
                          "county": {
                            "type": "string",
                            "example": "Bexar"
                          },
                          "countyFips": {
                            "type": "string",
                            "example": "029"
                          },
                          "latitude": {
                            "type": "number",
                            "example": 29.47046,
                            "default": ""
                          },
                          "longitude": {
                            "type": "number",
                            "example": -98.351561,
                            "default": ""
                          },
                          "propertyType": {
                            "type": "string",
                            "example": "Single Family"
                          },
                          "bedrooms": {
                            "type": "number",
                            "example": 3,
                            "default": ""
                          },
                          "bathrooms": {
                            "type": "number",
                            "example": 2,
                            "default": ""
                          },
                          "squareFootage": {
                            "type": "number",
                            "example": 1895,
                            "default": ""
                          },
                          "lotSize": {
                            "type": "number",
                            "example": 6882,
                            "default": ""
                          },
                          "yearBuilt": {
                            "type": "number",
                            "example": 1988,
                            "default": ""
                          },
                          "status": {
                            "type": "string",
                            "example": "Active"
                          },
                          "price": {
                            "type": "number",
                            "example": 289444,
                            "default": ""
                          },
                          "listingType": {
                            "type": "string",
                            "example": "Standard"
                          },
                          "listedDate": {
                            "type": "string",
                            "example": "2025-04-11T00:00:00.000Z",
                            "format": "date-time"
                          },
                          "removedDate": {
                            "type": "string",
                            "format": "date-time"
                          },
                          "lastSeenDate": {
                            "type": "string",
                            "example": "2025-09-03T10:57:39.532Z",
                            "format": "date-time"
                          },
                          "daysOnMarket": {
                            "type": "number",
                            "example": 146,
                            "default": ""
                          },
                          "distance": {
                            "type": "number",
                            "example": 0.384,
                            "default": ""
                          },
                          "daysOld": {
                            "type": "number",
                            "example": 1,
                            "default": ""
                          },
                          "correlation": {
                            "type": "number",
                            "example": 0.9916,
                            "default": ""
                          }
                        }
                      }
                    }
                  }
                },
                "examples": {
                  "Success": {
                    "value": {
                      "price": 250000,
                      "priceRangeLow": 195000,
                      "priceRangeHigh": 304000,
                      "subjectProperty": {
                        "id": "5500-Grand-Lake-Dr,-San-Antonio,-TX-78244",
                        "formattedAddress": "5500 Grand Lake Dr, San Antonio, TX 78244",
                        "addressLine1": "5500 Grand Lake Dr",
                        "addressLine2": null,
                        "city": "San Antonio",
                        "state": "TX",
                        "stateFips": "48",
                        "zipCode": "78244",
                        "county": "Bexar",
                        "countyFips": "029",
                        "latitude": 29.476011,
                        "longitude": -98.351454,
                        "propertyType": "Single Family",
                        "bedrooms": 3,
                        "bathrooms": 2,
                        "squareFootage": 1878,
                        "lotSize": 8843,
                        "yearBuilt": 1973,
                        "lastSaleDate": "2024-11-18T00:00:00.000Z",
                        "lastSalePrice": 270000
                      },
                      "comparables": [
                        {
                          "id": "5207-Pine-Lake-Dr,-San-Antonio,-TX-78244",
                          "formattedAddress": "5207 Pine Lake Dr, San Antonio, TX 78244",
                          "addressLine1": "5207 Pine Lake Dr",
                          "addressLine2": null,
                          "city": "San Antonio",
                          "state": "TX",
                          "stateFips": "48",
                          "zipCode": "78244",
                          "county": "Bexar",
                          "countyFips": "029",
                          "latitude": 29.47046,
                          "longitude": -98.351561,
                          "propertyType": "Single Family",
                          "bedrooms": 3,
                          "bathrooms": 2,
                          "squareFootage": 1895,
                          "lotSize": 6882,
                          "yearBuilt": 1988,
                          "status": "Active",
                          "price": 289444,
                          "listingType": "Standard",
                          "listedDate": "2025-04-11T00:00:00.000Z",
                          "removedDate": null,
                          "lastSeenDate": "2025-09-03T10:57:39.532Z",
                          "daysOnMarket": 146,
                          "distance": 0.384,
                          "daysOld": 1,
                          "correlation": 0.9916
                        },
                        {
                          "id": "6707-Lake-Cliff-St,-San-Antonio,-TX-78244",
                          "formattedAddress": "6707 Lake Cliff St, San Antonio, TX 78244",
                          "addressLine1": "6707 Lake Cliff St",
                          "addressLine2": null,
                          "city": "San Antonio",
                          "state": "TX",
                          "stateFips": "48",
                          "zipCode": "78244",
                          "county": "Bexar",
                          "countyFips": "029",
                          "latitude": 29.47617,
                          "longitude": -98.356908,
                          "propertyType": "Single Family",
                          "bedrooms": 3,
                          "bathrooms": 2,
                          "squareFootage": 1811,
                          "lotSize": 8146,
                          "yearBuilt": 1977,
                          "status": "Inactive",
                          "price": 279000,
                          "listingType": "Standard",
                          "listedDate": "2025-06-06T00:00:00.000Z",
                          "removedDate": "2025-07-12T00:00:00.000Z",
                          "lastSeenDate": "2025-07-11T13:21:20.968Z",
                          "daysOnMarket": 36,
                          "distance": 0.3286,
                          "daysOld": 55,
                          "correlation": 0.9887
                        },
                        {
                          "id": "6917-Deep-Lake-Dr,-San-Antonio,-TX-78244",
                          "formattedAddress": "6917 Deep Lake Dr, San Antonio, TX 78244",
                          "addressLine1": "6917 Deep Lake Dr",
                          "addressLine2": null,
                          "city": "San Antonio",
                          "state": "TX",
                          "stateFips": "48",
                          "zipCode": "78244",
                          "county": "Bexar",
                          "countyFips": "029",
                          "latitude": 29.479375,
                          "longitude": -98.351978,
                          "propertyType": "Single Family",
                          "bedrooms": 3,
                          "bathrooms": 2,
                          "squareFootage": 1753,
                          "lotSize": 11151,
                          "yearBuilt": 1974,
                          "status": "Inactive",
                          "price": 199900,
                          "listingType": "Standard",
                          "listedDate": "2025-05-22T00:00:00.000Z",
                          "removedDate": "2025-08-27T00:00:00.000Z",
                          "lastSeenDate": "2025-08-26T12:36:31.859Z",
                          "daysOnMarket": 97,
                          "distance": 0.2348,
                          "daysOld": 9,
                          "correlation": 0.9863
                        },
                        {
                          "id": "5314-Lost-Tree,-San-Antonio,-TX-78244",
                          "formattedAddress": "5314 Lost Tree, San Antonio, TX 78244",
                          "addressLine1": "5314 Lost Tree",
                          "addressLine2": null,
                          "city": "San Antonio",
                          "state": "TX",
                          "stateFips": "48",
                          "zipCode": "78244",
                          "county": "Bexar",
                          "countyFips": "029",
                          "latitude": 29.477064,
                          "longitude": -98.343686,
                          "propertyType": "Single Family",
                          "bedrooms": 3,
                          "bathrooms": 2,
                          "squareFootage": 1948,
                          "lotSize": 9017,
                          "yearBuilt": 2000,
                          "status": "Inactive",
                          "price": 159900,
                          "listingType": "Standard",
                          "listedDate": "2025-06-23T00:00:00.000Z",
                          "removedDate": "2025-06-28T00:00:00.000Z",
                          "lastSeenDate": "2025-06-27T11:02:28.080Z",
                          "daysOnMarket": 5,
                          "distance": 0.4734,
                          "daysOld": 69,
                          "correlation": 0.9859
                        },
                        {
                          "id": "7207-Solar-Eclipse,-Converse,-TX-78109",
                          "formattedAddress": "7207 Solar Eclipse, Converse, TX 78109",
                          "addressLine1": "7207 Solar Eclipse",
                          "addressLine2": null,
                          "city": "Converse",
                          "state": "TX",
                          "stateFips": "48",
                          "zipCode": "78109",
                          "county": "Bexar",
                          "countyFips": "029",
                          "latitude": 29.463689,
                          "longitude": -98.348663,
                          "propertyType": "Single Family",
                          "bedrooms": 3,
                          "bathrooms": 2,
                          "squareFootage": 1883,
                          "lotSize": 5140,
                          "yearBuilt": 2022,
                          "status": "Active",
                          "price": 320000,
                          "listingType": "Standard",
                          "listedDate": "2025-03-10T00:00:00.000Z",
                          "removedDate": null,
                          "lastSeenDate": "2025-09-03T10:33:44.607Z",
                          "daysOnMarket": 178,
                          "distance": 0.8687,
                          "daysOld": 1,
                          "correlation": 0.9835
                        }
                      ]
                    },
                    "summary": "Success"
                  }
                }
              }
            }
          },
          "401": {
            "description": "Auth Error",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "status": {
                      "type": "number",
                      "example": 401,
                      "default": ""
                    },
                    "error": {
                      "type": "string",
                      "example": "auth/api-key-invalid"
                    },
                    "message": {
                      "type": "string",
                      "example": "No API key provided in request. An API key must be provided in the 'X-Api-Key' header"
                    }
                  }
                },
                "examples": {
                  "Auth Error": {
                    "summary": "Auth Error",
                    "value": {
                      "status": 401,
                      "error": "auth/api-key-invalid",
                      "message": "No API key provided in request. An API key must be provided in the 'X-Api-Key' header"
                    }
                  }
                }
              }
            }
          }
        },
        "deprecated": false
      }
    }
  },
  "x-readme": {
    "headers": [],
    "explorer-enabled": true,
    "proxy-enabled": true
  },
  "x-readme-fauxas": true
}
```
