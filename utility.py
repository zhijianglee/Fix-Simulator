import sys

import requests
from flask import Flask, request, jsonify, app

app = Flask(__name__)

country_code_mapping = {
    '60': 'MY',  # Malaysia
    '1': 'US',   # United States
    '91': 'IN',  # India
    '65': 'SG',  # Singapore
    '86': 'CN'  , # China
    '81': 'JP',   # Japan
    '82': 'KR',   # South Korea
    '66': 'TH',   # Thailand
    '84': 'VN',   # Vietnam
    '62': 'ID',   # Indonesia
    '63': 'PH',   # Philippines
    # Europe Countries below this
    '33': 'FR',   # France
    '49': 'DE',   # Germany
    '39': 'IT',   # Italy
    '34': 'ES',   # Spain
    '31': 'NL',   # Netherlands
    '41': 'CH',   # Switzerland
    '46': 'SE',   # Sweden
    '45': 'DK',   # Denmark
    '47': 'NO',   # Norway
    '358': 'FI',  # Finland
    '48': 'PL',   # Poland
    '420': 'CZ',  # Czech Republic
    '421': 'SK',  # Slovakia
    '36': 'HU',   # Hungary
    '43': 'AT',   # Austria
    '44': 'GB',   # United Kingdom
    '353': 'IE',  # Ireland
    '32': 'BE',   # Belgium
    '30': 'GR',   # Greece
    '90': 'TR',   # Turkey
    '7': 'RU',    # Russia
    '380': 'UA',  # Ukraine
    '375': 'BY',  # Belarus
    '373': 'MD',  # Moldova
    '40': 'RO',   # Romania
    '359': 'BG',  # Bulgaria
    '381': 'RS',  # Serbia
    '387': 'BA',  # Bosnia and Herzegovina
    '385': 'HR',  # Croatia
    '386': 'SI',  # Slovenia
    # Kosovo
    '389': 'MK',  # North Macedonia
    '355': 'AL',  # Albania
    # Add more country codes and their short names as needed
}

# Function to lookup country short name based on country code
def get_country_short_name(phone_number):
    # Check for 3-digit country code first
    country_code = phone_number[:3]
    if country_code in country_code_mapping:
        return country_code_mapping[country_code]

    # Check for 2-digit country code if 3-digit code is not found
    country_code = phone_number[:2]
    return country_code_mapping.get(country_code, 'Unknown')

@app.route('/tool/get_caller_identity', methods=['GET'])
def get_caller_identity():
    # Retrieve thee phone number of the caller which passed as query param
    phone_number = request.args.get('phone_number')

    # First attempt to extract caller country code. Check if country code is present in the phone number.
    # If not, then use the default country code of Malaysia as MY
    country_short_name = get_country_short_name(phone_number)

    if country_short_name == 'Unknown':
        country_short_name = 'MY'

    # Call the Truecaller API to get the caller identity



    url = "https://asia-south1-truecaller-web.cloudfunctions.net/webapi/noneu/search/v1?q="+phone_number+"&countryCode="+country_short_name+"&type=40"

    payload = {}
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,ms;q=0.8,zh-CN;q=0.7,zh;q=0.6',
        'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDI1MTExNjUxNzEsInRva2VuIjoiYTF3MFktLUlmc3pvU1ZFa2lpLWZqdmo5VmV2MDlfdkVTcmhHVzFoV3V3dld0c2NKQnlFRWF1OVNjN2M2QzZ1SSIsImVuaGFuY2VkU2VhcmNoIjp0cnVlLCJjb3VudHJ5Q29kZSI6Im15IiwibmFtZSI6IkxlZSBaaGkgSmlhbmciLCJlbWFpbCI6InpoaWppYW5nLnhpYW9tYW9AZ21haWwuY29tIiwiaW1hZ2UiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NMVVg0U0ZGcXFEaWhqNkNPMmdleUNnWXdYXzFBRVR6T1lHQTBlMmtjMnNxSkpXcnRvPXM5Ni1jIiwiaWF0IjoxNzQwMDkxOTY1fQ.3Fc2G1tz0A9fzzj8TC6U92dtQSR6h2TkFbFGtIsQJGs',
        'origin': 'https://www.truecaller.com',
        'priority': 'u=1, i',
        'referer': 'https://www.truecaller.com/',
        'sec-ch-ua': '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return jsonify(response.json())

# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True, port=5000)