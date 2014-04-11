#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''getquote

Fetches quotes for commodities for Ledger.
'''

import os, sys, argparse
from bs4 import BeautifulSoup
import urllib.request
import urllib.error
from urllib.parse import urlparse
from decimal import *
import re
import json

# Set decimal precision to 8
getcontext().prec = 8

class Quote:
    '''Fetches quotes for commodities in Ledger'''

    def __init__(self, symbol):
        self.symbol = symbol
        self.providers = {
            'stocks':{
                'url':"http://uk.finance.yahoo.com/d/quotes.csv?s={0}&f=l1",
                'parse_symbol':"{0}.L", # Do we need to process Ledger's symbol before searching with this service?
                'conversion_factor':Decimal('0.001'),
            },
            'forex':{
                'url':"http://openexchangerates.org/api/latest.json?app_id=YOUR_API_CODE_HERE"
            },
            'funds':{
                'url':"https://www.fidelity.co.uk/investor/research-funds/fund-supermarket/factsheet/summary.page?idtype=ISIN&fundid={0}",
                'bs_parse':("soup.find(id='sellprice').contents","soup.find(id='buyprice').contents")
            }
        }
        self.currencies = {
            "AED": "United Arab Emirates Dirham",
            "AFN": "Afghan Afghani",
            "ALL": "Albanian Lek",
            "AMD": "Armenian Dram",
            "ANG": "Netherlands Antillean Guilder",
            "AOA": "Angolan Kwanza",
            "ARS": "Argentine Peso",
            "AUD": "Australian Dollar",
            "AWG": "Aruban Florin",
            "AZN": "Azerbaijani Manat",
            "BAM": "Bosnia-Herzegovina Convertible Mark",
            "BBD": "Barbadian Dollar",
            "BDT": "Bangladeshi Taka",
            "BGN": "Bulgarian Lev",
            "BHD": "Bahraini Dinar",
            "BIF": "Burundian Franc",
            "BMD": "Bermudan Dollar",
            "BND": "Brunei Dollar",
            "BOB": "Bolivian Boliviano",
            "BRL": "Brazilian Real",
            "BSD": "Bahamian Dollar",
            "BTC": "Bitcoin",
            "BTN": "Bhutanese Ngultrum",
            "BWP": "Botswanan Pula",
            "BYR": "Belarusian Ruble",
            "BZD": "Belize Dollar",
            "CAD": "Canadian Dollar",
            "CDF": "Congolese Franc",
            "CHF": "Swiss Franc",
            "CLF": "Chilean Unit of Account (UF)",
            "CLP": "Chilean Peso",
            "CNY": "Chinese Yuan",
            "COP": "Colombian Peso",
            "CRC": "Costa Rican Colón",
            "CUP": "Cuban Peso",
            "CVE": "Cape Verdean Escudo",
            "CZK": "Czech Republic Koruna",
            "DJF": "Djiboutian Franc",
            "DKK": "Danish Krone",
            "DOP": "Dominican Peso",
            "DZD": "Algerian Dinar",
            "EEK": "Estonian Kroon",
            "EGP": "Egyptian Pound",
            "ERN": "Eritrean Nakfa",
            "ETB": "Ethiopian Birr",
            "EUR": "Euro",
            "FJD": "Fijian Dollar",
            "FKP": "Falkland Islands Pound",
            "GBP": "British Pound Sterling",
            "GEL": "Georgian Lari",
            "GHS": "Ghanaian Cedi",
            "GIP": "Gibraltar Pound",
            "GMD": "Gambian Dalasi",
            "GNF": "Guinean Franc",
            "GTQ": "Guatemalan Quetzal",
            "GYD": "Guyanaese Dollar",
            "HKD": "Hong Kong Dollar",
            "HNL": "Honduran Lempira",
            "HRK": "Croatian Kuna",
            "HTG": "Haitian Gourde",
            "HUF": "Hungarian Forint",
            "IDR": "Indonesian Rupiah",
            "ILS": "Israeli New Sheqel",
            "INR": "Indian Rupee",
            "IQD": "Iraqi Dinar",
            "IRR": "Iranian Rial",
            "ISK": "Icelandic Króna",
            "JEP": "Jersey Pound",
            "JMD": "Jamaican Dollar",
            "JOD": "Jordanian Dinar",
            "JPY": "Japanese Yen",
            "KES": "Kenyan Shilling",
            "KGS": "Kyrgystani Som",
            "KHR": "Cambodian Riel",
            "KMF": "Comorian Franc",
            "KPW": "North Korean Won",
            "KRW": "South Korean Won",
            "KWD": "Kuwaiti Dinar",
            "KYD": "Cayman Islands Dollar",
            "KZT": "Kazakhstani Tenge",
            "LAK": "Laotian Kip",
            "LBP": "Lebanese Pound",
            "LKR": "Sri Lankan Rupee",
            "LRD": "Liberian Dollar",
            "LSL": "Lesotho Loti",
            "LTL": "Lithuanian Litas",
            "LVL": "Latvian Lats",
            "LYD": "Libyan Dinar",
            "MAD": "Moroccan Dirham",
            "MDL": "Moldovan Leu",
            "MGA": "Malagasy Ariary",
            "MKD": "Macedonian Denar",
            "MMK": "Myanma Kyat",
            "MNT": "Mongolian Tugrik",
            "MOP": "Macanese Pataca",
            "MRO": "Mauritanian Ouguiya",
            "MTL": "Maltese Lira",
            "MUR": "Mauritian Rupee",
            "MVR": "Maldivian Rufiyaa",
            "MWK": "Malawian Kwacha",
            "MXN": "Mexican Peso",
            "MYR": "Malaysian Ringgit",
            "MZN": "Mozambican Metical",
            "NAD": "Namibian Dollar",
            "NGN": "Nigerian Naira",
            "NIO": "Nicaraguan Córdoba",
            "NOK": "Norwegian Krone",
            "NPR": "Nepalese Rupee",
            "NZD": "New Zealand Dollar",
            "OMR": "Omani Rial",
            "PAB": "Panamanian Balboa",
            "PEN": "Peruvian Nuevo Sol",
            "PGK": "Papua New Guinean Kina",
            "PHP": "Philippine Peso",
            "PKR": "Pakistani Rupee",
            "PLN": "Polish Zloty",
            "PYG": "Paraguayan Guarani",
            "QAR": "Qatari Rial",
            "RON": "Romanian Leu",
            "RSD": "Serbian Dinar",
            "RUB": "Russian Ruble",
            "RWF": "Rwandan Franc",
            "SAR": "Saudi Riyal",
            "SBD": "Solomon Islands Dollar",
            "SCR": "Seychellois Rupee",
            "SDG": "Sudanese Pound",
            "SEK": "Swedish Krona",
            "SGD": "Singapore Dollar",
            "SHP": "Saint Helena Pound",
            "SLL": "Sierra Leonean Leone",
            "SOS": "Somali Shilling",
            "SRD": "Surinamese Dollar",
            "STD": "São Tomé and Príncipe Dobra",
            "SVC": "Salvadoran Colón",
            "SYP": "Syrian Pound",
            "SZL": "Swazi Lilangeni",
            "THB": "Thai Baht",
            "TJS": "Tajikistani Somoni",
            "TMT": "Turkmenistani Manat",
            "TND": "Tunisian Dinar",
            "TOP": "Tongan Paʻanga",
            "TRY": "Turkish Lira",
            "TTD": "Trinidad and Tobago Dollar",
            "TWD": "New Taiwan Dollar",
            "TZS": "Tanzanian Shilling",
            "UAH": "Ukrainian Hryvnia",
            "UGX": "Ugandan Shilling",
            "USD": "United States Dollar",
            "UYU": "Uruguayan Peso",
            "UZS": "Uzbekistan Som",
            "VEF": "Venezuelan Bolívar Fuerte",
            "VND": "Vietnamese Dong",
            "VUV": "Vanuatu Vatu",
            "WST": "Samoan Tala",
            "XAF": "CFA Franc BEAC",
            "XAG": "Silver (troy ounce)",
            "XAU": "Gold (troy ounce)",
            "XCD": "East Caribbean Dollar",
            "XDR": "Special Drawing Rights",
            "XOF": "CFA Franc BCEAO",
            "XPF": "CFP Franc",
            "YER": "Yemeni Rial",
            "ZAR": "South African Rand",
            "ZMK": "Zambian Kwacha (pre-2013)",
            "ZMW": "Zambian Kwacha",
            "ZWL": "Zimbabwean Dollar"
        }
        self.price = None # Last price as a Decimal object
        self.last_price = None # Last price as a string (suitable for output)

    def parse_symbol(self):
        '''Parses a symbol and processes provider URLs to a usable form'''
        for provider in self.providers:
            if 'parse_symbol' in self.providers[provider]:
                self.providers[provider]['parse_symbol'] = self.providers[provider]['parse_symbol'].format(self.symbol)
            else:
                self.providers[provider]['parse_symbol'] = self.symbol
            self.providers[provider]['url'] = self.providers[provider]['url'].format(self.providers[provider]['parse_symbol'])
        return self

    def get_html(self, url):
        """Returns a string containing the HTML of the supplied URL"""
        try:
            html = urllib.request.urlopen(url)
        except urllib.error.URLError as e:
            print("URL error for {0}: {1}".format(url, e.reason))
        except urllib.error.HTTPError as e:
            print("HTTP error for {0}: {1} - {2}".format(url, e.code, e.reason))
        return html

    def lookup(self):
        self.parse_symbol()
        # Which service to use?
        r = re.compile("^[a-z]{2}[a-z0-9]{10}$") # Regex for an ISIN
        if self.symbol in self.currencies:
            provider = 'forex'
        elif r.match(self.symbol.lower()):
            provider = 'funds'
        else:
            provider = 'stocks'

        html = self.get_html(self.providers[provider]['url']).read().decode('utf-8')

        if provider == 'forex':
            forex_json = json.loads(html)
            temp_price = Decimal(str(forex_json['rates']['GBP'])) * (Decimal(1)/Decimal(str(forex_json['rates'][self.symbol])))
        elif 'bs_parse' in self.providers[provider]:
            soup = BeautifulSoup(html)
            for search_method in self.providers[provider]['bs_parse']:
                try:
                    temp_price = eval(search_method)[0]
                    if temp_price:
                        break
                except AttributeError:
                    msg = 'WARNING: Could not find price for "{0}" when searching "{1}" with "{2}"'.format(self.symbol, provider, search_method)
        else:
            temp_price = str(html)

        if temp_price:
            if 'conversion_factor' in self.providers[provider]:
                self.price = Decimal(temp_price) * self.providers[provider]['conversion_factor']
            else:
                self.price = Decimal(temp_price)
            self.last_price = '£{:.3f}'.format(self.price)
        else:
            self.price = None
            raise RuntimeError('Cannot find price for "{0}"'.format(self.symbol))
        return self

def main():
    parser = argparse.ArgumentParser(description="Fetches quotes for commodities for Ledger")
    parser.add_argument("symbol", type=str, default=None, help="The symbol (e.g. ISIN) of the commodity.")
    args = parser.parse_args()
    if args.symbol:
        output = Quote(args.symbol)
        try:
            output.lookup()
        except RuntimeError as e:
            print(e)
            sys.exit(1)
        print(output.last_price)
    else:
        msg = "No arguments supplied"
        raise parser.ArgumentTypeError(msg)
    return parser.exit()

if __name__ == "__main__":
    main()