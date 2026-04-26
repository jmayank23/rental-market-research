Property Listings

# Property Listings

Retrieve property sale and rental listings nationwide in the US.

The `/listings` endpoints allow you to search for and retrieve active and inactive sale and rental listings in all 50 US states.

“Sale” listings refer to properties listed for sale, while “rental” listings refer to properties listed for rent.

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

## Listing Records

Each property listing record contains several fields with information for that specific property:

- **Location attributes**: including the full property address, address components, county, FIPS codes, and geographical coordinates
- **Property attributes**: including the property type, number of bedrooms, number of bathrooms, living area size, year built, etc.
- **HOA fees**: including the homeowner's association monthly fee or assessment amount
- **Listing status**: indicating whether the listing is currently active or not
- **Listed price or rent**: sale listings will include their listed price, while rental listings will include their listed rent
- **Listing type**: indicating the type of the listing
- **Listing dates**: including the listing date, the date the listing was removed, the date the listing was last seen, and how many days it's been on the market
- **MLS information**: including the MLS name and number of the listing, if listed on the Multiple Listing Service (MLS)
- **Agent, office and builder information**: including the names and contact information of the listing agent, the listing office or broker, and the property builder
- **Listing history**: including the sale or rental listing history of the property

View the full [property listings schema](https://developers.rentcast.io/reference/property-listings-schema) to learn more about the returned fields and their possible values.

Below is an example of a **standard listing** record returned by our API:

```json Property Listing Example (Standard)
{
  "id": "3821-Hargis-St,-Austin,-TX-78723",
  "formattedAddress": "3821 Hargis St, Austin, TX 78723",
  "addressLine1": "3821 Hargis St",
  "addressLine2": null,
  "city": "Austin",
  "state": "TX",
  "stateFips": "48",
  "zipCode": "78723",
  "county": "Travis",
  "countyFips": "453",
  "latitude": 30.290643,
  "longitude": -97.701547,
  "propertyType": "Single Family",
  "bedrooms": 4,
  "bathrooms": 2.5,
  "squareFootage": 2345,
  "lotSize": 3284,
  "yearBuilt": 2008,
  "hoa": {
    "fee": 65
  },
  "status": "Active",
  "price": 899000,
  "listingType": "Standard",
  "listedDate": "2024-06-24T00:00:00.000Z",
  "removedDate": null,
  "createdDate": "2021-06-25T00:00:00.000Z",
  "lastSeenDate": "2024-09-30T13:11:47.157Z",
  "daysOnMarket": 99,
  "mlsName": "UnlockMLS",
  "mlsNumber": "5519228",
  "listingAgent": {
    "name": "Jennifer Welch",
    "phone": "5124313110",
    "email": "jennifer@gottesmanresidential.com",
    "website": "https://www.gottesmanresidential.com"
  },
  "listingOffice": {
    "name": "Gottesman Residential R.E.",
    "phone": "5124512422",
    "email": "nataliem@gottesmanresidential.com",
    "website": "https://www.gottesmanresidential.com"
  },
  "history": {
    "2021-07-28": {
      "event": "Sale Listing",
      "price": 949000,
      "listingType": "Standard",
      "listedDate": "2021-07-28T00:00:00.000Z",
      "removedDate": "2021-08-23T00:00:00.000Z",
      "daysOnMarket": 26
    },
    "2024-06-24": {
      "event": "Sale Listing",
      "price": 899000,
      "listingType": "Standard",
      "listedDate": "2024-06-24T00:00:00.000Z",
      "removedDate": null,
      "daysOnMarket": 99
    }
  }
}
```

Below is an example of a **new construction listing** record returned by our API:

```json Property Listing Example (New Construction)
{
  "id": "3781-Passion-Vine-Dr,-Alva,-FL-33920",
  "formattedAddress": "3781 Passion Vine Dr, Alva, FL 33920",
  "addressLine1": "3781 Passion Vine Dr",
  "addressLine2": null,
  "city": "Alva",
  "state": "FL",
  "stateFips": "12",
  "zipCode": "33920",
  "county": "Lee",
  "countyFips": "071",
  "latitude": 26.686521,
  "longitude": -81.685764,
  "propertyType": "Single Family",
  "bedrooms": 4,
  "bathrooms": 2,
  "squareFootage": 1850,
  "lotSize": 7405,
  "yearBuilt": 2023,
  "hoa": {
    "fee": 220
  },
  "status": "Active",
  "price": 428595,
  "listingType": "New Construction",
  "listedDate": "2024-09-19T00:00:00.000Z",
  "removedDate": null,
  "createdDate": "2024-07-24T00:00:00.000Z",
  "lastSeenDate": "2024-09-28T12:28:50.115Z",
  "daysOnMarket": 10,
  "builder": {
    "name": "Pulte Homes",
    "development": "Hampton Lakes at River Hall",
    "phone": "2392300326",
    "website": "https://www.pulte.com"
  },
  "history": {
    "2024-09-19": {
      "event": "Sale Listing",
      "price": 428595,
      "listingType": "New Construction",
      "listedDate": "2024-09-19T00:00:00.000Z",
      "removedDate": null,
      "daysOnMarket": 10
    }
  }
}
```

<Callout icon="📘" theme="info">
  Both sale and rental listings use the `price` field to indicate the listed price (for sale listings) or listed rent (for rental listings) of the property.
</Callout>

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

## Data Sources and Coverage

Our property listing data is obtained from various public sources, including online records and directories, and public domain information.

We continuously update our property listing database, and each individual listing is updated at least once per day. Newly published listings are typically ingested and made available through our API within 12-24 hours of being published.

Although we do not retrieve our property listing data directly from the MLS, you should see comparable coverage between your local MLS feeds and our API.

We aim to provide at least 96% sale and rental listing coverage for residential properties in all 50 US states, including single-family, condos, townhomes, manufactured, and 2-4 unit multi-family properties. This includes sale listings of vacant land parcels.

We also aim to provide at least 90% sale and rental listing coverage for 5+ unit commercial dwellings, including apartment buildings, condo complexes, and other large residential developments. At this time, we do not have property listing coverage for office, retail, industrial, manufacturing, farm or other non-residential commercial properties.

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

## Search Queries

Our property listing search endpoints ([`/listings/sale`](https://developers.rentcast.io/reference/sale-listings) and [`/listings/rental/long-term`](https://developers.rentcast.io/reference/rental-listings-long-term)) support retrieving data for a specific address; searching for listings in a city, state or zip code; or searching for them in a circular geographical area.

[See this guide](https://developers.rentcast.io/reference/search-queries) for an overview of how to structure your search queries to retrieve the specific listing data you are looking for, how to retrieve property listings in bulk, as well as how to use multiple value and numeric range query parameters.

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

## Pagination

Our property listing search endpoints ([`/listings/sale`](https://developers.rentcast.io/reference/sale-listings) and [`/listings/rental/long-term`](https://developers.rentcast.io/reference/rental-listings-long-term)) will return large lists of listings in sets, up to 500 listings at a time, and support pagination.

[See this guide](https://developers.rentcast.io/reference/pagination) for an overview of how to use the `limit` and `offset` query parameters to retrieve additional sets of results, as well as how to retrieve the total number of results matching a specific query.

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

## Available Endpoints

The following endpoints are available for retrieving sale and rental listings:

- [`/listings/sale`](https://developers.rentcast.io/reference/sale-listings): an endpoint that allows you to retrieve sale listings matching specific criteria in a given city or state, or in a circular geographical area

- [`/listings/sale/{id}`](https://developers.rentcast.io/reference/sale-listing-by-id): an endpoint that allows you to retrieve a specific sale listing, given its internal id. The id can be retrieved using the [`/properties`](https://developers.rentcast.io/reference/property-data), [`/avm`](https://developers.rentcast.io/reference/property-valuation) or other `/listings` endpoints, or cached in your application from prior requests

- [`/listings/rental/long-term`](https://developers.rentcast.io/reference/rental-listings-long-term): an endpoint that allows you to retrieve rental listings matching specific criteria in a given city or state, or in a circular geographical area

- [`/listings/rental/long-term/{id}`](https://developers.rentcast.io/reference/rental-listing-long-term-by-id): an endpoint that allows you to retrieve a specific rental listing, given its internal id. The id can be retrieved using the [`/properties`](https://developers.rentcast.io/reference/property-data), [`/avm`](https://developers.rentcast.io/reference/property-valuation) or other `/listings` endpoints, or cached in your application from prior requests

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

Sale Listings

# Sale Listings

Search for sale listings in a geographical area, or by a specific address.

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

This endpoint allows you to search for active and inactive "for-sale" property listings for a specific address; those located in a specific city, state or zip code; or those found in a circular geographical area. [Learn more](https://developers.rentcast.io/reference/search-queries) about the supported search queries.

It provides several query parameters to allow for the filtering of sale listings based on specific criteria.

The returned listing records will be sorted by the `lastSeenDate` field in descending order, with the most recent listings appearing first.

Each listing record will include data for a specific property, including its listed price, listing date, status, listing contacts, property attributes, and other information. View the full [property listings schema](https://developers.rentcast.io/reference/property-listings-schema) to learn more about the response fields.

<Callout icon="📘" theme="info">
  This is a paginated endpoint that returns up to 500 listings in a single response. Use the `limit` and `offset` parameters to paginate through additional results for the same search query. [Learn more](https://developers.rentcast.io/reference/pagination) about pagination.
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
    "/listings/sale": {
      "get": {
        "summary": "Sale Listings",
        "description": "Search for sale listings in a geographical area, or by a specific address.",
        "operationId": "sale-listings",
        "parameters": [
          {
            "name": "address",
            "in": "query",
            "description": "The **full address** of the property, in the format `Street, City, State, Zip`. Used to retrieve data for a specific property, or together with the `radius` parameter to search for listings in a circular area",
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "city",
            "in": "query",
            "description": "The name of the city, used to search for listings in a specific city. This parameter is case-sensitive",
            "schema": {
              "type": "string",
              "default": "Austin"
            }
          },
          {
            "name": "state",
            "in": "query",
            "description": "The 2-character state abbreviation, used to search for listings in a specific state. This parameter is case-sensitive",
            "schema": {
              "type": "string",
              "default": "TX"
            }
          },
          {
            "name": "zipCode",
            "in": "query",
            "description": "The 5-digit zip code, used to search for listings in a specific zip code",
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "latitude",
            "in": "query",
            "description": "The latitude of the search area. Use the `latitude`/`longitude` and `radius` parameters to search for listings in a circular area",
            "schema": {
              "type": "number",
              "format": "float"
            }
          },
          {
            "name": "longitude",
            "in": "query",
            "description": "The longitude of the search area. Use the `latitude`/`longitude` and `radius` parameters to search for listings in a circular area",
            "schema": {
              "type": "number",
              "format": "float"
            }
          },
          {
            "name": "radius",
            "in": "query",
            "description": "The radius of the search area in miles, with a maximum of 100. Use in combination with the `latitude`/`longitude` or `address` parameters to search for listings in a circular area",
            "schema": {
              "type": "number",
              "format": "float"
            }
          },
          {
            "name": "propertyType",
            "in": "query",
            "description": "The type of the property, used to search for listings matching this criteria. See [explanation of property types](https://developers.rentcast.io/reference/property-types). Supports [multiple values](https://developers.rentcast.io/reference/search-queries#using-multiple-value-parameters)",
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
            "description": "The number of bedrooms, used to search for listings matching this criteria. Use `0` to indicate a studio layout. Supports [numeric ranges](https://developers.rentcast.io/reference/search-queries#using-numeric-range-parameters) and [multiple values](https://developers.rentcast.io/reference/search-queries#using-multiple-value-parameters)",
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "bathrooms",
            "in": "query",
            "description": "The number of bathrooms, used to search for listings matching this criteria. Supports fractions to indicate partial bathrooms, [numeric ranges](https://developers.rentcast.io/reference/search-queries#using-numeric-range-parameters) and [multiple values](https://developers.rentcast.io/reference/search-queries#using-multiple-value-parameters)",
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "squareFootage",
            "in": "query",
            "description": "The total living area size in square feet, used to search for listings matching this criteria. Supports [numeric ranges](https://developers.rentcast.io/reference/search-queries#using-numeric-range-parameters) and [multiple values](https://developers.rentcast.io/reference/search-queries#using-multiple-value-parameters)",
            "schema": {
              "type": "string",
              "default": ""
            }
          },
          {
            "name": "lotSize",
            "in": "query",
            "description": "The total lot size in square feet, used to search for listings matching this criteria. Supports [numeric ranges](https://developers.rentcast.io/reference/search-queries#using-numeric-range-parameters) and [multiple values](https://developers.rentcast.io/reference/search-queries#using-multiple-value-parameters)",
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "yearBuilt",
            "in": "query",
            "description": "The year of construction, used to search for listings matching this criteria. Supports [numeric ranges](https://developers.rentcast.io/reference/search-queries#using-numeric-range-parameters) and [multiple values](https://developers.rentcast.io/reference/search-queries#using-multiple-value-parameters)",
            "schema": {
              "type": "string",
              "default": ""
            }
          },
          {
            "name": "status",
            "in": "query",
            "description": "The current listing status, used to search for listings matching this criteria. See [explanation of listing statuses](https://developers.rentcast.io/reference/property-listings-schema#listing-status-field-values)",
            "schema": {
              "type": "string",
              "enum": ["Active", "Inactive"],
              "default": "Active"
            }
          },
          {
            "in": "query",
            "name": "price",
            "schema": {
              "type": "string"
            },
            "description": "The listed price of the property, used to search for listings matching this criteria. Supports [numeric ranges](https://developers.rentcast.io/reference/search-queries#using-numeric-range-parameters) and [multiple values](https://developers.rentcast.io/reference/search-queries#using-multiple-value-parameters)"
          },
          {
            "in": "query",
            "name": "daysOld",
            "schema": {
              "type": "string"
            },
            "description": "The number of days since a property was listed on the market, with a minimum of 1. Supports [numeric ranges](https://developers.rentcast.io/reference/search-queries#using-numeric-range-parameters)"
          },
          {
            "in": "query",
            "name": "limit",
            "schema": {
              "type": "integer",
              "format": "int32",
              "default": "5"
            },
            "description": "The maximum number of listing records to return, between 1 and 500. Defaults to `50` if not provided. [Learn more](https://developers.rentcast.io/reference/pagination) about pagination"
          },
          {
            "in": "query",
            "name": "offset",
            "schema": {
              "type": "integer",
              "format": "int32"
            },
            "description": "The index of the first listing record to return, used to paginate through large lists of results. Defaults to `0` if not provided. [Learn more](https://developers.rentcast.io/reference/pagination) about pagination"
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
                    "value": [
                      {
                        "id": "3821-Hargis-St,-Austin,-TX-78723",
                        "formattedAddress": "3821 Hargis St, Austin, TX 78723",
                        "addressLine1": "3821 Hargis St",
                        "addressLine2": null,
                        "city": "Austin",
                        "state": "TX",
                        "stateFips": "48",
                        "zipCode": "78723",
                        "county": "Travis",
                        "countyFips": "453",
                        "latitude": 30.290643,
                        "longitude": -97.701547,
                        "propertyType": "Single Family",
                        "bedrooms": 4,
                        "bathrooms": 2.5,
                        "squareFootage": 2345,
                        "lotSize": 3284,
                        "yearBuilt": 2008,
                        "hoa": {
                          "fee": 65
                        },
                        "status": "Active",
                        "price": 899000,
                        "listingType": "Standard",
                        "listedDate": "2024-06-24T00:00:00.000Z",
                        "removedDate": null,
                        "createdDate": "2021-06-25T00:00:00.000Z",
                        "lastSeenDate": "2024-09-30T13:11:47.157Z",
                        "daysOnMarket": 99,
                        "mlsName": "UnlockMLS",
                        "mlsNumber": "5519228",
                        "listingAgent": {
                          "name": "Jennifer Welch",
                          "phone": "5124313110",
                          "email": "jennifer@gottesmanresidential.com",
                          "website": "https://www.gottesmanresidential.com"
                        },
                        "listingOffice": {
                          "name": "Gottesman Residential R.E.",
                          "phone": "5124512422",
                          "email": "nataliem@gottesmanresidential.com",
                          "website": "https://www.gottesmanresidential.com"
                        },
                        "history": {
                          "2024-06-24": {
                            "event": "Sale Listing",
                            "price": 899000,
                            "listingType": "Standard",
                            "listedDate": "2024-06-24T00:00:00.000Z",
                            "removedDate": null,
                            "daysOnMarket": 99
                          }
                        }
                      },
                      {
                        "id": "6808-Windrift-Way,-Austin,-TX-78745",
                        "formattedAddress": "6808 Windrift Way, Austin, TX 78745",
                        "addressLine1": "6808 Windrift Way",
                        "addressLine2": null,
                        "city": "Austin",
                        "state": "TX",
                        "stateFips": "48",
                        "zipCode": "78745",
                        "county": "Travis",
                        "countyFips": "453",
                        "latitude": 30.199388,
                        "longitude": -97.798729,
                        "propertyType": "Single Family",
                        "bedrooms": 3,
                        "bathrooms": 2,
                        "squareFootage": 1199,
                        "lotSize": 6390,
                        "yearBuilt": 1974,
                        "status": "Active",
                        "price": 424900,
                        "listingType": "Standard",
                        "listedDate": "2024-01-03T00:00:00.000Z",
                        "removedDate": null,
                        "createdDate": "2023-08-15T00:00:00.000Z",
                        "lastSeenDate": "2024-09-28T13:48:38.179Z",
                        "daysOnMarket": 270,
                        "mlsName": "UnlockMLS",
                        "mlsNumber": "5589475",
                        "listingAgent": {
                          "name": "Christopher Watters",
                          "phone": "7373135275",
                          "email": "sold@wattersinternational.com",
                          "website": "https://www.christopherwatters.com"
                        },
                        "listingOffice": {
                          "name": "Watters International Realty",
                          "phone": "5126460038",
                          "email": "chriswatters@wattersinternational.com",
                          "website": "https://www.christopherwatters.com"
                        },
                        "history": {
                          "2024-01-03": {
                            "event": "Sale Listing",
                            "price": 424900,
                            "listingType": "Standard",
                            "listedDate": "2024-01-03T00:00:00.000Z",
                            "removedDate": null,
                            "daysOnMarket": 270
                          }
                        }
                      },
                      {
                        "id": "54-Rainey-St,-Apt-513,-Austin,-TX-78701",
                        "formattedAddress": "54 Rainey St, Apt 513, Austin, TX 78701",
                        "addressLine1": "54 Rainey St",
                        "addressLine2": "Apt 513",
                        "city": "Austin",
                        "state": "TX",
                        "stateFips": "48",
                        "zipCode": "78701",
                        "county": "Travis",
                        "countyFips": "453",
                        "latitude": 30.257382,
                        "longitude": -97.739444,
                        "propertyType": "Condo",
                        "bedrooms": 2,
                        "bathrooms": 2,
                        "squareFootage": 1164,
                        "lotSize": 292,
                        "yearBuilt": 2005,
                        "hoa": {
                          "fee": 803
                        },
                        "status": "Active",
                        "price": 560000,
                        "listingType": "Standard",
                        "listedDate": "2024-01-04T00:00:00.000Z",
                        "removedDate": null,
                        "createdDate": "2024-01-05T00:00:00.000Z",
                        "lastSeenDate": "2024-09-28T13:48:39.150Z",
                        "daysOnMarket": 269,
                        "mlsName": "UnlockMLS",
                        "mlsNumber": "1594185",
                        "listingAgent": {
                          "name": "Adam Zell",
                          "phone": "5128204918",
                          "email": "adam.zell@compass.com",
                          "website": "https://www.compass.com"
                        },
                        "listingOffice": {
                          "name": "Compass RE Texas LLC - Austin",
                          "phone": "5125753644",
                          "email": "txbroker@compass.com",
                          "website": "https://www.compass.com"
                        },
                        "history": {
                          "2024-01-04": {
                            "event": "Sale Listing",
                            "price": 560000,
                            "listingType": "Standard",
                            "listedDate": "2024-01-04T00:00:00.000Z",
                            "removedDate": null,
                            "daysOnMarket": 269
                          }
                        }
                      },
                      {
                        "id": "15407-Patrica-St,-Austin,-TX-78728",
                        "formattedAddress": "15407 Patrica St, Austin, TX 78728",
                        "addressLine1": "15407 Patrica St",
                        "addressLine2": null,
                        "city": "Austin",
                        "state": "TX",
                        "stateFips": "48",
                        "zipCode": "78728",
                        "county": "Travis",
                        "countyFips": "453",
                        "latitude": 30.451009,
                        "longitude": -97.669682,
                        "propertyType": "Single Family",
                        "bedrooms": 3,
                        "bathrooms": 2,
                        "squareFootage": 1680,
                        "lotSize": 12632,
                        "yearBuilt": 1995,
                        "status": "Active",
                        "price": 720000,
                        "listingType": "Standard",
                        "listedDate": "2024-01-18T00:00:00.000Z",
                        "removedDate": null,
                        "createdDate": "2021-02-13T00:00:00.000Z",
                        "lastSeenDate": "2024-09-28T13:49:05.753Z",
                        "daysOnMarket": 255,
                        "mlsName": "UnlockMLS",
                        "mlsNumber": "4738210",
                        "listingAgent": {
                          "name": "Minerva Juarez",
                          "phone": "5127333557",
                          "website": "https://minervajuarez-realtor.com"
                        },
                        "listingOffice": {
                          "name": "Keller Williams Realty",
                          "phone": "5123463550",
                          "email": "mecook@kw.com"
                        },
                        "history": {
                          "2024-01-18": {
                            "event": "Sale Listing",
                            "price": 720000,
                            "listingType": "Standard",
                            "listedDate": "2024-01-18T00:00:00.000Z",
                            "removedDate": null,
                            "daysOnMarket": 255
                          }
                        }
                      },
                      {
                        "id": "2681-Crazyhorse-Pass,-Austin,-TX-78734",
                        "formattedAddress": "2681 Crazyhorse Pass, Austin, TX 78734",
                        "addressLine1": "2681 Crazyhorse Pass",
                        "addressLine2": null,
                        "city": "Austin",
                        "state": "TX",
                        "stateFips": "48",
                        "zipCode": "78734",
                        "county": "Travis",
                        "countyFips": "453",
                        "latitude": 30.377405,
                        "longitude": -97.928841,
                        "propertyType": "Manufactured",
                        "bedrooms": 3,
                        "bathrooms": 2,
                        "squareFootage": 1792,
                        "lotSize": 9496,
                        "yearBuilt": 1995,
                        "hoa": {
                          "fee": 8
                        },
                        "status": "Active",
                        "price": 299999,
                        "listingType": "Standard",
                        "listedDate": "2024-01-18T00:00:00.000Z",
                        "removedDate": null,
                        "createdDate": "2023-10-11T00:00:00.000Z",
                        "lastSeenDate": "2024-09-28T13:49:05.749Z",
                        "daysOnMarket": 255,
                        "mlsName": "SanAntonio",
                        "mlsNumber": "1745284",
                        "listingAgent": {
                          "name": "Yesenia Quevedo",
                          "phone": "2102545895",
                          "email": "yeseniaquevedosatx@gmail.com"
                        },
                        "listingOffice": {
                          "name": "LPT Realty LLC",
                          "phone": "8773662213",
                          "email": "rodney@rodneyhenson.com"
                        },
                        "history": {
                          "2024-01-18": {
                            "event": "Sale Listing",
                            "price": 299999,
                            "listingType": "Standard",
                            "listedDate": "2024-01-18T00:00:00.000Z",
                            "removedDate": null,
                            "daysOnMarket": 255
                          }
                        }
                      }
                    ],
                    "summary": "Success"
                  }
                },
                "schema": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "id": {
                        "type": "string",
                        "example": "3821-Hargis-St,-Austin,-TX-78723"
                      },
                      "formattedAddress": {
                        "type": "string",
                        "example": "3821 Hargis St, Austin, TX 78723"
                      },
                      "addressLine1": {
                        "type": "string",
                        "example": "3821 Hargis St"
                      },
                      "addressLine2": {
                        "type": "string"
                      },
                      "city": {
                        "type": "string",
                        "example": "Austin"
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
                        "example": "78723"
                      },
                      "county": {
                        "type": "string",
                        "example": "Travis"
                      },
                      "countyFips": {
                        "type": "string",
                        "example": "453"
                      },
                      "latitude": {
                        "type": "number",
                        "example": 30.290643,
                        "default": ""
                      },
                      "longitude": {
                        "type": "number",
                        "example": -97.701547,
                        "default": ""
                      },
                      "propertyType": {
                        "type": "string",
                        "example": "Single Family"
                      },
                      "bedrooms": {
                        "type": "number",
                        "example": 4,
                        "default": ""
                      },
                      "bathrooms": {
                        "type": "number",
                        "example": 2.5,
                        "default": ""
                      },
                      "squareFootage": {
                        "type": "number",
                        "example": 2345,
                        "default": ""
                      },
                      "lotSize": {
                        "type": "number",
                        "example": 3284,
                        "default": ""
                      },
                      "yearBuilt": {
                        "type": "number",
                        "example": 2008,
                        "default": ""
                      },
                      "hoa": {
                        "type": "object",
                        "properties": {
                          "fee": {
                            "type": "number",
                            "example": 65,
                            "default": ""
                          }
                        }
                      },
                      "status": {
                        "type": "string",
                        "example": "Active"
                      },
                      "price": {
                        "type": "number",
                        "example": 899000,
                        "default": ""
                      },
                      "listingType": {
                        "type": "string",
                        "example": "Standard"
                      },
                      "listedDate": {
                        "type": "string",
                        "example": "2024-06-24T00:00:00.000Z",
                        "format": "date-time"
                      },
                      "removedDate": {
                        "type": "string",
                        "format": "date-time"
                      },
                      "createdDate": {
                        "type": "string",
                        "example": "2021-06-25T00:00:00.000Z",
                        "format": "date-time"
                      },
                      "lastSeenDate": {
                        "type": "string",
                        "example": "2024-09-30T13:11:47.157Z",
                        "format": "date-time"
                      },
                      "daysOnMarket": {
                        "type": "number",
                        "example": 99,
                        "default": ""
                      },
                      "mlsName": {
                        "type": "string",
                        "example": "UnlockMLS"
                      },
                      "mlsNumber": {
                        "type": "string",
                        "example": "5519228"
                      },
                      "listingAgent": {
                        "type": "object",
                        "properties": {
                          "name": {
                            "type": "string",
                            "example": "Jennifer Welch"
                          },
                          "phone": {
                            "type": "string",
                            "example": "5124313110"
                          },
                          "email": {
                            "type": "string",
                            "example": "jennifer@gottesmanresidential.com"
                          },
                          "website": {
                            "type": "string",
                            "example": "https://www.gottesmanresidential.com"
                          }
                        }
                      },
                      "listingOffice": {
                        "type": "object",
                        "properties": {
                          "name": {
                            "type": "string",
                            "example": "Gottesman Residential R.E."
                          },
                          "phone": {
                            "type": "string",
                            "example": "5124512422"
                          },
                          "email": {
                            "type": "string",
                            "example": "nataliem@gottesmanresidential.com"
                          },
                          "website": {
                            "type": "string",
                            "example": "https://www.gottesmanresidential.com"
                          }
                        }
                      },
                      "history": {
                        "type": "object",
                        "properties": {
                          "2024-06-24": {
                            "type": "object",
                            "properties": {
                              "event": {
                                "type": "string",
                                "example": "Sale Listing"
                              },
                              "price": {
                                "type": "number",
                                "example": 899000,
                                "default": ""
                              },
                              "listingType": {
                                "type": "string",
                                "example": "Standard"
                              },
                              "listedDate": {
                                "type": "string",
                                "example": "2024-06-24T00:00:00.000Z",
                                "format": "date-time"
                              },
                              "removedDate": {
                                "type": "string",
                                "format": "date-time"
                              },
                              "daysOnMarket": {
                                "type": "number",
                                "example": 99,
                                "default": ""
                              }
                            }
                          }
                        }
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
