Property Records

# Property Records

Search for property records in a geographical area, or by a specific address.

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

This endpoint allows you to search for property records and data for a specific address; those located in a specific city, state or zip code; or those found in a circular geographical area. [Learn more](https://developers.rentcast.io/reference/search-queries) about the supported search queries.

It provides several query parameters to allow for the filtering of property records based on specific criteria, including the `saleDateRange` parameter, which can be used to search for properties that were sold within the specified date range.

Each property record will include data for a specific property, including its structural attributes, features, tax assessments, tax amounts, sale history and owner details. View the full [property data schema](https://developers.rentcast.io/reference/property-data-schema) to learn more about the response fields.

<Callout icon="📘" theme="info">
  This is a paginated endpoint that returns up to 500 records in a single response. Use the `limit` and `offset` parameters to paginate through additional results for the same search query. [Learn more](https://developers.rentcast.io/reference/pagination) about pagination.
</Callout>

<Callout icon="📘" theme="info">
  Data availability of specific property record fields may vary by county and state. Our API will always return all available fields and data for each property.
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
    "/properties": {
      "get": {
        "summary": "Property Records",
        "description": "Search for property records in a geographical area, or by a specific address.",
        "operationId": "property-records",
        "parameters": [
          {
            "name": "address",
            "in": "query",
            "description": "The **full address** of the property, in the format `Street, City, State, Zip`. Used to retrieve data for a specific property, or together with the `radius` parameter to search for properties in a circular area",
            "schema": {
              "type": "string",
              "default": "5500 Grand Lake Dr, San Antonio, TX, 78244"
            }
          },
          {
            "name": "city",
            "in": "query",
            "description": "The name of the city, used to search for properties in a specific city. This parameter is case-sensitive",
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "state",
            "in": "query",
            "description": "The 2-character state abbreviation, used to search for properties in a specific state. This parameter is case-sensitive",
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "zipCode",
            "in": "query",
            "description": "The 5-digit zip code, used to search for properties in a specific zip code",
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "latitude",
            "in": "query",
            "description": "The latitude of the search area. Use the `latitude`/`longitude` and `radius` parameters to search for properties in a circular area",
            "schema": {
              "type": "number",
              "format": "float"
            }
          },
          {
            "name": "longitude",
            "in": "query",
            "description": "The longitude of the search area. Use the `latitude`/`longitude` and `radius` parameters to search for properties in a circular area",
            "schema": {
              "type": "number",
              "format": "float"
            }
          },
          {
            "name": "radius",
            "in": "query",
            "description": "The radius of the search area in miles, with a maximum of 100. Use in combination with the `latitude`/`longitude` or `address` parameters to search for properties in a circular area",
            "schema": {
              "type": "number",
              "format": "float"
            }
          },
          {
            "name": "propertyType",
            "in": "query",
            "description": "The type of the property, used to search for properties matching this criteria. See [explanation of property types](https://developers.rentcast.io/reference/property-types). Supports [multiple values](https://developers.rentcast.io/reference/search-queries#using-multiple-value-parameters)",
            "schema": {
              "type": "string",
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
            "description": "The number of bedrooms, used to search for properties matching this criteria. Use `0` to indicate a studio layout. Supports [numeric ranges](https://developers.rentcast.io/reference/search-queries#using-numeric-range-parameters) and [multiple values](https://developers.rentcast.io/reference/search-queries#using-multiple-value-parameters)",
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "bathrooms",
            "in": "query",
            "description": "The number of bathrooms, used to search for properties matching this criteria. Supports fractions to indicate partial bathrooms, [numeric ranges](https://developers.rentcast.io/reference/search-queries#using-numeric-range-parameters) and [multiple values](https://developers.rentcast.io/reference/search-queries#using-multiple-value-parameters)",
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "squareFootage",
            "in": "query",
            "description": "The total living area size in square feet, used to search for properties matching this criteria. Supports [numeric ranges](https://developers.rentcast.io/reference/search-queries#using-numeric-range-parameters) and [multiple values](https://developers.rentcast.io/reference/search-queries#using-multiple-value-parameters)",
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "lotSize",
            "in": "query",
            "description": "The total lot size in square feet, used to search for properties matching this criteria. Supports [numeric ranges](https://developers.rentcast.io/reference/search-queries#using-numeric-range-parameters) and [multiple values](https://developers.rentcast.io/reference/search-queries#using-multiple-value-parameters)",
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "yearBuilt",
            "in": "query",
            "description": "The year of construction, used to search for properties matching this criteria. Supports [numeric ranges](https://developers.rentcast.io/reference/search-queries#using-numeric-range-parameters) and [multiple values](https://developers.rentcast.io/reference/search-queries#using-multiple-value-parameters)",
            "schema": {
              "type": "string"
            }
          },
          {
            "in": "query",
            "name": "saleDateRange",
            "schema": {
              "type": "string"
            },
            "description": "The number of days since a property was last sold, with a minimum of 1. Used to search for properties that were sold within the specified date range. Supports [numeric ranges](https://developers.rentcast.io/reference/search-queries#using-numeric-range-parameters)"
          },
          {
            "in": "query",
            "name": "limit",
            "schema": {
              "type": "integer",
              "format": "int32"
            },
            "description": "The maximum number of property records to return, between 1 and 500. Defaults to `50` if not provided. [Learn more](https://developers.rentcast.io/reference/pagination) about pagination"
          },
          {
            "in": "query",
            "name": "offset",
            "schema": {
              "type": "integer",
              "format": "int32"
            },
            "description": "The index of the first property record to return, used to paginate through large lists of results. Defaults to `0` if not provided. [Learn more](https://developers.rentcast.io/reference/pagination) about pagination"
          },
          {
            "in": "query",
            "name": "includeTotalCount",
            "schema": {
              "type": "boolean"
            },
            "description": "When enabled, will return the total number of results matching the current query in the `X-Total-Count` response header. Defaults to `false` if not provided"
          }
        ],
        "responses": {
          "200": {
            "description": "Success",
            "content": {
              "application/json": {
                "examples": {
                  "Success": {
                    "summary": "Success",
                    "value": [
                      {
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
                        "latitude": 29.475962,
                        "longitude": -98.351442,
                        "propertyType": "Single Family",
                        "bedrooms": 3,
                        "bathrooms": 2,
                        "squareFootage": 1878,
                        "lotSize": 8850,
                        "yearBuilt": 1973,
                        "assessorID": "05076-103-0500",
                        "legalDescription": "CB 5076A BLK 3 LOT 50",
                        "subdivision": "WOODLAKE",
                        "zoning": "RH",
                        "lastSaleDate": "2024-11-18T00:00:00.000Z",
                        "lastSalePrice": 270000,
                        "hoa": {
                          "fee": 175
                        },
                        "features": {
                          "architectureType": "Contemporary",
                          "cooling": true,
                          "coolingType": "Central",
                          "exteriorType": "Wood",
                          "fireplace": true,
                          "fireplaceType": "Masonry",
                          "floorCount": 1,
                          "foundationType": "Slab / Mat / Raft",
                          "garage": true,
                          "garageSpaces": 2,
                          "garageType": "Garage",
                          "heating": true,
                          "heatingType": "Forced Air",
                          "pool": true,
                          "poolType": "Concrete",
                          "roofType": "Asphalt",
                          "roomCount": 5,
                          "unitCount": 1,
                          "viewType": "City"
                        },
                        "taxAssessments": {
                          "2020": {
                            "year": 2020,
                            "value": 142610,
                            "land": 23450,
                            "improvements": 119160
                          },
                          "2021": {
                            "year": 2021,
                            "value": 163440,
                            "land": 45050,
                            "improvements": 118390
                          },
                          "2022": {
                            "year": 2022,
                            "value": 197600,
                            "land": 49560,
                            "improvements": 148040
                          },
                          "2023": {
                            "year": 2023,
                            "value": 225790,
                            "land": 59380,
                            "improvements": 166410
                          },
                          "2024": {
                            "year": 2024,
                            "value": 216513,
                            "land": 59380,
                            "improvements": 157133
                          }
                        },
                        "propertyTaxes": {
                          "2020": {
                            "year": 2020,
                            "total": 3023
                          },
                          "2021": {
                            "year": 2021,
                            "total": 3455
                          },
                          "2022": {
                            "year": 2022,
                            "total": 4077
                          },
                          "2023": {
                            "year": 2023,
                            "total": 4201
                          },
                          "2024": {
                            "year": 2024,
                            "total": 4065
                          }
                        },
                        "history": {
                          "2017-10-19": {
                            "event": "Sale",
                            "date": "2017-10-19T00:00:00.000Z",
                            "price": 185000
                          },
                          "2024-11-18": {
                            "event": "Sale",
                            "date": "2024-11-18T00:00:00.000Z",
                            "price": 270000
                          }
                        },
                        "owner": {
                          "names": ["Rolando Villarreal"],
                          "type": "Individual",
                          "mailingAddress": {
                            "id": "5500-Grand-Lake-Dr,-San-Antonio,-TX-78244",
                            "formattedAddress": "5500 Grand Lake Dr, San Antonio, TX 78244",
                            "addressLine1": "5500 Grand Lake Dr",
                            "addressLine2": null,
                            "city": "San Antonio",
                            "state": "TX",
                            "stateFips": "48",
                            "zipCode": "78244"
                          }
                        },
                        "ownerOccupied": true
                      }
                    ]
                  }
                },
                "schema": {
                  "type": "array",
                  "items": {
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
                        "example": 29.475962,
                        "default": ""
                      },
                      "longitude": {
                        "type": "number",
                        "example": -98.351442,
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
                        "example": 8850,
                        "default": ""
                      },
                      "yearBuilt": {
                        "type": "number",
                        "example": 1973,
                        "default": ""
                      },
                      "assessorID": {
                        "type": "string",
                        "example": "05076-103-0500"
                      },
                      "legalDescription": {
                        "type": "string",
                        "example": "CB 5076A BLK 3 LOT 50"
                      },
                      "subdivision": {
                        "type": "string",
                        "example": "WOODLAKE"
                      },
                      "zoning": {
                        "type": "string",
                        "example": "RH"
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
                      },
                      "hoa": {
                        "type": "object",
                        "properties": {
                          "fee": {
                            "type": "number",
                            "example": 175,
                            "default": ""
                          }
                        }
                      },
                      "features": {
                        "type": "object",
                        "properties": {
                          "architectureType": {
                            "type": "string",
                            "example": "Contemporary"
                          },
                          "cooling": {
                            "type": "boolean",
                            "example": true,
                            "default": ""
                          },
                          "coolingType": {
                            "type": "string",
                            "example": "Central"
                          },
                          "exteriorType": {
                            "type": "string",
                            "example": "Wood"
                          },
                          "fireplace": {
                            "type": "boolean",
                            "example": true,
                            "default": ""
                          },
                          "fireplaceType": {
                            "type": "string",
                            "example": "Masonry"
                          },
                          "floorCount": {
                            "type": "number",
                            "example": 1,
                            "default": ""
                          },
                          "foundationType": {
                            "type": "string",
                            "example": "Slab / Mat / Raft"
                          },
                          "garage": {
                            "type": "boolean",
                            "example": true,
                            "default": ""
                          },
                          "garageSpaces": {
                            "type": "number",
                            "example": 2,
                            "default": ""
                          },
                          "garageType": {
                            "type": "string",
                            "example": "Garage"
                          },
                          "heating": {
                            "type": "boolean",
                            "example": true,
                            "default": ""
                          },
                          "heatingType": {
                            "type": "string",
                            "example": "Forced Air"
                          },
                          "pool": {
                            "type": "boolean",
                            "example": true,
                            "default": ""
                          },
                          "poolType": {
                            "type": "string",
                            "example": "Concrete"
                          },
                          "roofType": {
                            "type": "string",
                            "example": "Asphalt"
                          },
                          "roomCount": {
                            "type": "number",
                            "example": 5,
                            "default": ""
                          },
                          "unitCount": {
                            "type": "number",
                            "example": 1,
                            "default": ""
                          },
                          "viewType": {
                            "type": "string",
                            "example": "City"
                          }
                        }
                      },
                      "taxAssessments": {
                        "type": "object",
                        "properties": {
                          "2020": {
                            "type": "object",
                            "properties": {
                              "year": {
                                "type": "number",
                                "example": 2020,
                                "default": ""
                              },
                              "value": {
                                "type": "number",
                                "example": 142610,
                                "default": ""
                              },
                              "land": {
                                "type": "number",
                                "example": 23450,
                                "default": ""
                              },
                              "improvements": {
                                "type": "number",
                                "example": 119160,
                                "default": ""
                              }
                            }
                          },
                          "2021": {
                            "type": "object",
                            "properties": {
                              "year": {
                                "type": "number",
                                "example": 2021,
                                "default": ""
                              },
                              "value": {
                                "type": "number",
                                "example": 163440,
                                "default": ""
                              },
                              "land": {
                                "type": "number",
                                "example": 45050,
                                "default": ""
                              },
                              "improvements": {
                                "type": "number",
                                "example": 118390,
                                "default": ""
                              }
                            }
                          },
                          "2022": {
                            "type": "object",
                            "properties": {
                              "year": {
                                "type": "number",
                                "example": 2022,
                                "default": ""
                              },
                              "value": {
                                "type": "number",
                                "example": 197600,
                                "default": ""
                              },
                              "land": {
                                "type": "number",
                                "example": 49560,
                                "default": ""
                              },
                              "improvements": {
                                "type": "number",
                                "example": 148040,
                                "default": ""
                              }
                            }
                          },
                          "2023": {
                            "type": "object",
                            "properties": {
                              "year": {
                                "type": "number",
                                "example": 2023,
                                "default": ""
                              },
                              "value": {
                                "type": "number",
                                "example": 225790,
                                "default": ""
                              },
                              "land": {
                                "type": "number",
                                "example": 59380,
                                "default": ""
                              },
                              "improvements": {
                                "type": "number",
                                "example": 166410,
                                "default": ""
                              }
                            }
                          },
                          "2024": {
                            "type": "object",
                            "properties": {
                              "year": {
                                "type": "number",
                                "example": 2024,
                                "default": ""
                              },
                              "value": {
                                "type": "number",
                                "example": 216513,
                                "default": ""
                              },
                              "land": {
                                "type": "number",
                                "example": 59380,
                                "default": ""
                              },
                              "improvements": {
                                "type": "number",
                                "example": 157133,
                                "default": ""
                              }
                            }
                          }
                        }
                      },
                      "propertyTaxes": {
                        "type": "object",
                        "properties": {
                          "2020": {
                            "type": "object",
                            "properties": {
                              "year": {
                                "type": "number",
                                "example": 2020,
                                "default": ""
                              },
                              "total": {
                                "type": "number",
                                "example": 3023,
                                "default": ""
                              }
                            }
                          },
                          "2021": {
                            "type": "object",
                            "properties": {
                              "year": {
                                "type": "number",
                                "example": 2021,
                                "default": ""
                              },
                              "total": {
                                "type": "number",
                                "example": 3455,
                                "default": ""
                              }
                            }
                          },
                          "2022": {
                            "type": "object",
                            "properties": {
                              "year": {
                                "type": "number",
                                "example": 2022,
                                "default": ""
                              },
                              "total": {
                                "type": "number",
                                "example": 4077,
                                "default": ""
                              }
                            }
                          },
                          "2023": {
                            "type": "object",
                            "properties": {
                              "year": {
                                "type": "number",
                                "example": 2023,
                                "default": ""
                              },
                              "total": {
                                "type": "number",
                                "example": 4201,
                                "default": ""
                              }
                            }
                          },
                          "2024": {
                            "type": "object",
                            "properties": {
                              "year": {
                                "type": "number",
                                "example": 2024,
                                "default": ""
                              },
                              "total": {
                                "type": "number",
                                "example": 4065,
                                "default": ""
                              }
                            }
                          }
                        }
                      },
                      "history": {
                        "type": "object",
                        "properties": {
                          "2017-10-19": {
                            "type": "object",
                            "properties": {
                              "event": {
                                "type": "string",
                                "example": "Sale"
                              },
                              "date": {
                                "type": "string",
                                "example": "2017-10-19T00:00:00.000Z",
                                "format": "date-time"
                              },
                              "price": {
                                "type": "number",
                                "example": 185000,
                                "default": ""
                              }
                            }
                          },
                          "2024-11-18": {
                            "type": "object",
                            "properties": {
                              "event": {
                                "type": "string",
                                "example": "Sale"
                              },
                              "date": {
                                "type": "string",
                                "example": "2024-11-18T00:00:00.000Z",
                                "format": "date-time"
                              },
                              "price": {
                                "type": "number",
                                "example": 270000,
                                "default": ""
                              }
                            }
                          }
                        }
                      },
                      "owner": {
                        "type": "object",
                        "properties": {
                          "names": {
                            "type": "array",
                            "items": {
                              "type": "string",
                              "example": "Rolando Villarreal"
                            }
                          },
                          "type": {
                            "type": "string",
                            "example": "Individual"
                          },
                          "mailingAddress": {
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
                              }
                            }
                          }
                        }
                      },
                      "ownerOccupied": {
                        "type": "boolean",
                        "example": true,
                        "default": ""
                      }
                    }
                  }
                }
              }
            }
          },
          "401": {
            "description": "Auth Error",
            "content": {
              "application/json": {
                "examples": {
                  "Auth Error": {
                    "value": {
                      "status": 401,
                      "error": "auth/api-key-invalid",
                      "message": "No API key provided in request. An API key must be provided in the 'X-Api-Key' header"
                    },
                    "summary": "Auth Error"
                  }
                },
                "schema": {
                  "properties": {
                    "status": {
                      "type": "number",
                      "default": ""
                    },
                    "error": {
                      "type": "string"
                    },
                    "message": {
                      "type": "string"
                    }
                  },
                  "type": "object"
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
