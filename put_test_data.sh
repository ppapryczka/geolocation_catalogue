#!/bin/bash

echo "Putting facebook.com"
curl -X 'PUT' \
  'http://127.0.0.1:8000/address?address=facebook.com' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
   "continent_code":"EU",
   "continent_name":"Europe",
   "country_code":"PL",
   "country_name":"Poland",
   "region_code":"MZ",
   "region_name":"MZ",
   "city":"Warsaw",
   "zip":"00-025",
   "latitude":52.2317008972168,
   "longitude":21.018339157104492
}' --silent --output /dev/null

echo "Putting google.com"
curl -X 'PUT' \
  'http://127.0.0.1:8000/address?address=google.com' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
   "continent_code":"NA",
   "continent_name":"North America",
   "country_code":"US",
   "country_name":"United States",
   "region_code":"CA",
   "region_name":"CA",
   "city":"Mountain View",
   "zip":"94041",
   "latitude":37.38801956176758,
   "longitude":-122.07431030273438
}'  --silent --output /dev/null

echo "Putting stackoverflow.com"
curl -X 'PUT' \
  'http://127.0.0.1:8000/address?address=stackoverflow.com' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
   "continent_code":"NA",
   "continent_name":"North America",
   "country_code":"US",
   "country_name":"United States",
   "region_code":"CA",
   "region_name":"CA",
   "city":"San Jose",
   "zip":"95122",
   "latitude":37.330528259277344,
   "longitude":-121.83822631835938
}' --silent --output /dev/null


echo "Done!"
