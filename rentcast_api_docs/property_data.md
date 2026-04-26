Property Data

# Property Data

Retrieve data for residential and commercial properties in the US.

The `/properties` endpoints allow you to retrieve public record data for over 140 million properties in the United States, covering most residential and commercial properties in the country.

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

## Property Records

Each property record contains several fields with information for that specific property:

- **Location attributes**: including the full property address, address components, county, FIPS codes, and geographical coordinates
- **Property attributes**: including the property type, number of bedrooms, number of bathrooms, living area size, lot size, year built, etc.
- **HOA fees**: including the homeowner's association monthly fee or assessment amount
- **Property features**: including room count, floor count, architecture type, parking, pool type, cooling and heating types, construction materials, etc.
- **Tax assessment history**: including the assessed values of the land and building structures
- **Tax history**: including the tax year and the total tax amount
- **Sale history**: including the property's last sold date and price, as well as the sale transaction history
- **Current owner information**: including the owner's name, type, mailing address, and owner-occupied status

View the full [property data schema](https://developers.rentcast.io/reference/property-data-schema) to learn more about the returned fields and their possible values.

Below is an example of a property record returned by our API:

```json Property Record Example
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
```

<Callout icon="📘" theme="info">
  Data availability of specific property record fields may vary by county and state. Our API will always return all available fields and data for each property.
</Callout>

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

## Data Sources and Coverage

Our property record data is obtained from various sources, including public county records, recorded deeds, and tax assessor databases.

We continuously update our property database, and each individual property record is updated about once per week. Certain updates, including recent property sales and tax assessments, may take longer to be reflected in our database, based on the availability of recent data in public records.

We aim to provide at least 96% property record coverage for residential properties in all 50 US states, including single-family, condos, townhomes, manufactured, and 2-4 unit multi-family properties. This includes vacant land parcels.

We also aim to provide at least 90% property record coverage for 5+ unit commercial dwellings, including apartment buildings, condo complexes, and other large residential developments. At this time, we do not have property records coverage for office, retail, industrial, manufacturing, farm or other non-residential commercial properties.

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

## Search Queries

The [`/properties`](https://developers.rentcast.io/reference/property-records) endpoint supports retrieving data for a specific address; searching for properties in a city, state or zip code; or searching for them in a circular geographical area.

[See this guide](https://developers.rentcast.io/reference/search-queries) for an overview of how to structure your search queries to retrieve the specific property data you are looking for, how to retrieve property data in bulk, as well as how to use multiple value and numeric range query parameters.

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

## Pagination

The [`/properties`](https://developers.rentcast.io/reference/property-records) endpoint will return large lists of property records in sets, up to 500 records at a time, and supports pagination.

[See this guide](https://developers.rentcast.io/reference/pagination) for an overview of how to use the `limit` and `offset` query parameters to retrieve additional sets of results, as well as how to retrieve the total number of results matching a specific query.

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

## Retrieving Sold Properties

A common use case of our [`/properties`](https://developers.rentcast.io/reference/property-records) endpoint is retrieving a list of sold properties in a specific area, or retrieving sold comps for a particular subject property (similar properties that have sold nearby).

To do this, we recommend providing the following query parameters in your requests to this endpoint:

- `city`, `state` or `zipCode`: provide a combination of these parameters to search for sold properties in a specific city, state or zip code. [Learn more](https://developers.rentcast.io/reference/search-queries#searching-properties-in-a-city-state-or-zip-code) about this approach
- `address` and `radius`: alternatively, provide an address of the subject property to use as the search area center and a search radius in miles, to search for properties in a circular area. [Learn more](https://developers.rentcast.io/reference/search-queries#searching-properties-in-an-area) about this approach
- `saleDateRange`: provide the look back window to use when searching for sold properties, in days. For example, to retrieve properties sold in the last 6 months, provide 180 for this parameter
- `propertyType`: provide one or more property types to narrow down your search to properties of specific types
- `limit`: provide the total number of sold properties that should be returned

You can further narrow down your search by providing a combination of the `bedrooms`, `bathrooms`, `squareFootage`, `lotSize` and `yearBuilt` query parameters. These parameters support [numeric ranges](https://developers.rentcast.io/reference/search-queries#/using-numeric-range-parameters), so you can provide a minimum and maximum value for each (ex. `bedrooms=2:3`).

Below is an example request to the `/properties` endpoint which will retrieve up to 25 properties sold in the last 180 days, around a 3-mile radius of the subject property, which also match its property type and have similar bedroom and bathroom counts:

```curl cURL Example
curl --request GET \
  --url 'https://api.rentcast.io/v1/properties?address=2629%20Bonnybrook%20Dr%20SW,%20Atlanta,%20GA%2030311&radius=3&propertyType=Single%20Family&bedrooms=3&bathrooms=1:2&saleDateRange=180&limit=25' \
  --header 'Accept: application/json' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

<Callout icon="📘" theme="info">
  Alternatively, you can use our property [value estimate](https://developers.rentcast.io/reference/value-estimate) endpoint to retrieve comparable sale listings and an estimated property value based on our internal automated valuation model (AVM).
</Callout>

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

## Available Endpoints

The following endpoints are available for retrieving property data and records:

- [`/properties`](https://developers.rentcast.io/reference/property-records): an endpoint that allows you to retrieve a group of property records matching specific criteria, or a single property record for a specific address

- [`/properties/random`](https://developers.rentcast.io/reference/property-records-random): an endpoint that allows you to retrieve up to 500 property records selected at random, to facilitate testing or use cases that require a random sampling of property data

- [`/properties/{id}`](https://developers.rentcast.io/reference/property-record-by-id): an endpoint that allows you to retrieve a specific property record, given its internal id. The id can be retrieved using the other `/properties`, [`/avm`](https://developers.rentcast.io/reference/property-valuation) or [`/listings`](https://developers.rentcast.io/reference/property-listings) endpoints, or cached in your application from prior requests

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>
