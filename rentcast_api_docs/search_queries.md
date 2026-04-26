Search Queries

# Search Queries

How to use search queries to retrieve property records and listings.

Several of our API endpoints support a robust query engine that allows you to search for property records or listings that match a variety of location, attribute, listing and other criteria.

This guide describes how to structure your search queries to retrieve the specific property data you are looking for, as well as how to retrieve data from our API in bulk.

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

## Supported Endpoints

The following API endpoints support the search queries described in this guide:

- [`/properties`](https://developers.rentcast.io/reference/property-records)
- [`/listings/sale`](https://developers.rentcast.io/reference/sale-listings)
- [`/listings/rental/long-term`](https://developers.rentcast.io/reference/rental-listings-long-term)

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

## Retrieving a Single Property

If you need to retrieve property data or listing information for a specific property, you can do so by providing its full address in the `address` query parameter, and omitting all other query parameters.

Below is an example request to the `/properties` endpoint which will retrieve available data for a property located at "5500 Grand Lake Dr, San Antonio, TX, 78244":

```curl cURL Example
curl --request GET \
  --url 'https://api.rentcast.io/v1/properties?address=5500%20Grand%20Lake%20Dr%2C%20San%20Antonio%2C%20TX%2C%2078244' \
  --header 'Accept: application/json' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

<Callout icon="📘" theme="info">
  You should always provide property addresses in the format `Street, City, State, Zip` to ensure you receive data for the correct property.
</Callout>

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

## Retrieving Bulk Property Data

In addition to retrieving data for specific properties, our property records and listings endpoints also support bulk queries, which allow you to search for all properties or listings that match specific criteria.

Each bulk query typically consists of the following components:

- **Location criteria**: including a city, state or zip code, or a circular geographical area
- **Attribute or listing criteria**: including the property type, size, year built, and other property or listing search filters
- **Pagination parameters**: including the `limit` and `offset` query parameters that control pagination of large lists of results

The following sections describe how to use the supported location, property attribute and listing query parameters in more detail.

<Callout icon="📘" theme="info">
  Bulk queries will return results in a paginated format, up to 500 results in a single response. Use the `limit` and `offset` query parameters to paginate through additional results for the same search query. [Learn more](https://developers.rentcast.io/reference/pagination) about pagination.
</Callout>

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

### Searching Properties in a City, State or Zip Code

You can search for and retrieve all property records or listings in a specific city, state or zip code.

To do this, use the `city`, `state` or `zipCode` query parameters to provide the name of the city, the 2-character state abbreviation, or the 5-digit zip code for your search.

It is typically not necessary to provide all 3 of these parameters together. We recommend providing either the `state`, the `city`/`state`, or just the `zipCode` query parameters in most cases.

Below is an example request to the `/properties` endpoint which will retrieve the first 10 property records in Austin, TX with 3 bedrooms and 2 bathrooms:

```curl cURL Example
curl --request GET \
  --url 'https://api.rentcast.io/v1/properties?city=Austin&state=TX&bedrooms=3&bathrooms=2&limit=10' \
  --header 'Accept: application/json' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

### Searching Properties in an Area

You can also search for and retrieve property records or listings in a circular geographical area, defined by a center and a radius.

To do this, first provide the center of the search area. You can either provide a location in the `latitude`/`longitude` parameters, or provide an `address` parameter to use as the search area center.

Next, provide the `radius` query parameter, which is the search radius, in miles.

Below is an example request to the `/listings/sale` endpoint which will retrieve the first 10 sale listings within a 5-mile radius of downtown Phoenix, AZ with 3 bedrooms and 2 bathrooms:

```curl cURL Example
curl --request GET \
  --url 'https://api.rentcast.io/v1/listings/sale?latitude=33.45141&longitude=-112.073827&radius=5&bedrooms=3&bathrooms=2&limit=10' \
  --header 'Accept: application/json' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

### Using Multiple Value Parameters

The following query parameters available for our property records and listings endpoints support both single and multiple values:

- `propertyType`
- `bedrooms`
- `bathrooms`
- `squareFootage`
- `lotSize`
- `yearBuilt`
- `price` (exclusive to the `/listings` endpoints)

To provide a single value for these query parameters, follow the standard HTTP request syntax, for example: `propertyType=Condo`.

To provide multiple values for these query parameters, separate them by the pipe `|` character. For example, the following query will search for records matching either the "Condo" or "Townhouse" property types: `propertyType=Condo|Townhouse`.

Below is an example request to the `/listings/sale` endpoint which will retrieve the first 10 sale listings in Austin, TX, which are either a condo or a townhouse and have either 2 or 3 bedrooms:

```curl cURL Example
curl --request GET \
  --url 'https://api.rentcast.io/v1/listings/sale?city=Austin&state=TX&propertyType=Condo|Townhouse&bedrooms=2|3&limit=10' \
  --header 'Accept: application/json' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>

### Using Numeric Range Parameters

The following query parameters available for our property records and listings endpoints support providing an inclusive numeric range, represented by a minimum and maximum value:

- `bedrooms`
- `bathrooms`
- `squareFootage`
- `lotSize`
- `yearBuilt`
- `saleDateRange`(exclusive to the `/properties` endpoint)
- `price`(exclusive to the `/listings` endpoints)
- `daysOld`(exclusive to the `/listings` endpoints)

To provide a minimum and a maximum range value for these query parameters, separate them by the colon `:` character, as shown in the examples below:

- `bedrooms=1:3`: matches properties that have between 1 and 3 bedrooms
- `price=150000:250000`: matches properties with a listed price between $150,000 and $250,000
- `daysOld=30:90`: matches properties listed between 30 and 90 days ago

You can also omit either the minimum or the maximum value by replacing it with a star character `*`. In these cases, our API will only use the remaining range value for filtering, as shown in the examples below:

- `bathrooms=*:3`: matches properties that have 3 or fewer bathrooms
- `yearBuilt=2000:*`: matches properties built in 2000 or later
- `saleDateRange=*:270`: matches properties sold within the last 270 days

Below is an example request to the `/listings/rental/long-term` endpoint which will retrieve the first 10 rental listings in Austin, TX, which have between 2 and 4 bedrooms, a listed rent of at least $1,200/month, and which have been listed for 30 or fewer days:

```curl cURL Example
curl --request GET \
  --url 'https://api.rentcast.io/v1/listings/rental/long-term?city=Austin&state=TX&bedrooms=2:4&price=1200:*&daysOld=*:30&limit=10' \
  --header 'Accept: application/json' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

<Callout icon="📘" theme="info">
  The `saleDateRange` and `daysOld` query parameters are always treated as a range. If you provide a single value for either of them, it will be treated as the maximum range value.
</Callout>

<HTMLBlock>
  {`
  &nbsp;
  `}
</HTMLBlock>
