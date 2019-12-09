# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2017 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django_celery_beat.models import PeriodicTask, IntervalSchedule

# center = [Lat, Lon]
COUNTRIES_GEODB = [
    {
        "country.display_name": "Afghanistan",
        "country.center": [
            33.7680065,
            66.2385139
        ],
        "country.iso_3": "AFG",
        "country.iso_2": "AF"
    },
    {
        "country.display_name": "Angola",
        "country.center": [
            -11.8775768,
            17.5691241
        ],
        "country.iso_3": "AGO",
        "country.iso_2": "AO"
    },
    {
        "country.display_name": "Anguilla",
        "country.center": [
            18.1954947,
            -63.0750234
        ],
        "country.iso_3": "AIA",
        "country.iso_2": "AI"
    },
    {
        "country.display_name": "Albania",
        "country.center": [
            41.000028,
            19.9999619
        ],
        "country.iso_3": "ALB",
        "country.iso_2": "AL"
    },
    {
        "country.display_name": "Andorra",
        "country.center": [
            42.5407167,
            1.5732033
        ],
        "country.iso_3": "AND",
        "country.iso_2": "AD"
    },
    {
        "country.display_name": "United Arab Emirates",
        "country.center": [
            24.0002488,
            53.9994829
        ],
        "country.iso_3": "ARE",
        "country.iso_2": "AE"
    },
    {
        "country.display_name": "Argentina",
        "country.center": [
            -34.9964963,
            -64.9672817
        ],
        "country.iso_3": "ARG",
        "country.iso_2": "AR"
    },
    {
        "country.display_name": "Armenia",
        "country.center": [
            40.7696272,
            44.6736646
        ],
        "country.iso_3": "ARM",
        "country.iso_2": "AM"
    },
    {
        "country.display_name": "American Samoa",
        "country.center": [
            -14.289304,
            -170.692511
        ],
        "country.iso_3": "ASM",
        "country.iso_2": "AS"
    },
    {
        "country.display_name": "Antigua and Barbuda",
        "country.center": [
            17.079128,
            -61.8222516
        ],
        "country.iso_3": "ATG",
        "country.iso_2": "AG"
    },
    {
        "country.display_name": "Australia",
        "country.center": [
            -24.7761086,
            134.755
        ],
        "country.iso_3": "AUS",
        "country.iso_2": "AU"
    },
    {
        "country.display_name": "Austria",
        "country.center": [
            47.2000338,
            13.199959
        ],
        "country.iso_3": "AUT",
        "country.iso_2": "AT"
    },
    {
        "country.display_name": "Azerbaijan",
        "country.center": [
            40.3936294,
            47.7872508
        ],
        "country.iso_3": "AZE",
        "country.iso_2": "AZ"
    },
    {
        "country.display_name": "Burundi",
        "country.center": [
            -3.3634357,
            29.8870575
        ],
        "country.iso_3": "BDI",
        "country.iso_2": "BI"
    },
    {
        "country.display_name": "Belgium",
        "country.center": [
            50.6402809,
            4.6667145
        ],
        "country.iso_3": "BEL",
        "country.iso_2": "BE"
    },
    {
        "country.display_name": "Benin",
        "country.center": [
            9.5293472,
            2.2584408
        ],
        "country.iso_3": "BEN",
        "country.iso_2": "BJ"
    },
    {
        "country.display_name": "Burkina Faso",
        "country.center": [
            12.0753083,
            -1.6880314
        ],
        "country.iso_3": "BFA",
        "country.iso_2": "BF"
    },
    {
        "country.display_name": "Bangladesh",
        "country.center": [
            24.4768783,
            90.2932426
        ],
        "country.iso_3": "BGD",
        "country.iso_2": "BD"
    },
    {
        "country.display_name": "Bulgaria",
        "country.center": [
            42.6073975,
            25.4856617
        ],
        "country.iso_3": "BGR",
        "country.iso_2": "BG"
    },
    {
        "country.display_name": "Bahrain",
        "country.center": [
            26.1551249,
            50.5344606
        ],
        "country.iso_3": "BHR",
        "country.iso_2": "BH"
    },
    {
        "country.display_name": "Bahamas",
        "country.center": [
            24.7736546,
            -78.0000547
        ],
        "country.iso_3": "BHS",
        "country.iso_2": "BS"
    },
    {
        "country.display_name": "Bosnia and Herzegovina",
        "country.center": [
            44.3053476,
            17.5961467
        ],
        "country.iso_3": "BIH",
        "country.iso_2": "BA"
    },
    {
        "country.display_name": "Belarus",
        "country.center": [
            53.4250605,
            27.6971358
        ],
        "country.iso_3": "BLR",
        "country.iso_2": "BY"
    },
    {
        "country.display_name": "Belize",
        "country.center": [
            16.8259793,
            -88.7600927
        ],
        "country.iso_3": "BLZ",
        "country.iso_2": "BZ"
    },
    {
        "country.display_name": "Bermuda",
        "country.center": [
            32.3018217,
            -64.7603583
        ],
        "country.iso_3": "BMU",
        "country.iso_2": "BM"
    },
    {
        "country.display_name": "Brazil",
        "country.center": [
            -10.3333333,
            -53.2
        ],
        "country.iso_3": "BRA",
        "country.iso_2": "BR"
    },
    {
        "country.display_name": "Barbados",
        "country.center": [
            13.1500331,
            -59.5250305
        ],
        "country.iso_3": "BRB",
        "country.iso_2": "BB"
    },
    {
        "country.display_name": "Brunei Darussalam",
        "country.center": [
            4.4137155,
            114.5653908
        ],
        "country.iso_3": "BRN",
        "country.iso_2": "BN"
    },
    {
        "country.display_name": "Bhutan",
        "country.center": [
            27.549511,
            90.5119273
        ],
        "country.iso_3": "BTN",
        "country.iso_2": "BT"
    },
    {
        "country.display_name": "Botswana",
        "country.center": [
            -23.1681782,
            24.5928742
        ],
        "country.iso_3": "BWA",
        "country.iso_2": "BW"
    },
    {
        "country.display_name": "Central African Republic",
        "country.center": [
            7.0323598,
            19.9981227
        ],
        "country.iso_3": "CAF",
        "country.iso_2": "CF"
    },
    {
        "country.display_name": "Canada",
        "country.center": [
            61.0666922,
            -107.9917071
        ],
        "country.iso_3": "CAN",
        "country.iso_2": "CA"
    },
    {
        "country.display_name": "Switzerland",
        "country.center": [
            46.7985624,
            8.2319736
        ],
        "country.iso_3": "CHE",
        "country.iso_2": "CH"
    },
    {
        "country.display_name": "Chile",
        "country.center": [
            -31.7613365,
            -71.3187697
        ],
        "country.iso_3": "CHL",
        "country.iso_2": "CL"
    },
    {
        "country.display_name": "China",
        "country.center": [
            35.000074,
            104.999927
        ],
        "country.iso_3": "CHN",
        "country.iso_2": "CN"
    },
    {
        "country.display_name": "Cameroon",
        "country.center": [
            4.6125522,
            13.1535811
        ],
        "country.iso_3": "CMR",
        "country.iso_2": "CM"
    },
    {
        "country.display_name": "Congo",
        "country.center": [
            -0.7264327,
            15.6419155
        ],
        "country.iso_3": "COG",
        "country.iso_2": "CG"
    },
    {
        "country.display_name": "Cook Islands",
        "country.center": [
            -16.0492781,
            -160.3554851
        ],
        "country.iso_3": "COK",
        "country.iso_2": "CK"
    },
    {
        "country.display_name": "Colombia",
        "country.center": [
            2.8894434,
            -73.783892
        ],
        "country.iso_3": "COL",
        "country.iso_2": "CO"
    },
    {
        "country.display_name": "Comoros",
        "country.center": [
            -12.2045176,
            44.2832964
        ],
        "country.iso_3": "COM",
        "country.iso_2": "KM"
    },
    {
        "country.display_name": "Cabo Verde",
        "country.center": [
            16.0000552,
            -24.0083947
        ],
        "country.iso_3": "CPV",
        "country.iso_2": "CV"
    },
    {
        "country.display_name": "Costa Rica",
        "country.center": [
            10.2735633,
            -84.0739102
        ],
        "country.iso_3": "CRI",
        "country.iso_2": "CR"
    },
    {
        "country.display_name": "Cuba",
        "country.center": [
            23.0131338,
            -80.8328748
        ],
        "country.iso_3": "CUB",
        "country.iso_2": "CU"
    },
    {
        "country.display_name": "Cayman Islands",
        "country.center": [
            19.5417212,
            -80.5667132
        ],
        "country.iso_3": "CYM",
        "country.iso_2": "KY"
    },
    {
        "country.display_name": "Cyprus",
        "country.center": [
            34.9823018,
            33.1451285
        ],
        "country.iso_3": "CYP",
        "country.iso_2": "CY"
    },
    {
        "country.display_name": "Czechia",
        "country.center": [
            49.8167003,
            15.4749544
        ],
        "country.iso_3": "CZE",
        "country.iso_2": "CZ"
    },
    {
        "country.display_name": "Germany",
        "country.center": [
            51.0834196,
            10.4234469
        ],
        "country.iso_3": "DEU",
        "country.iso_2": "DE"
    },
    {
        "country.display_name": "Djibouti",
        "country.center": [
            11.8145966,
            42.8453061
        ],
        "country.iso_3": "DJI",
        "country.iso_2": "DJ"
    },
    {
        "country.display_name": "Dominica",
        "country.center": [
            19.0974031,
            -70.3028026
        ],
        "country.iso_3": "DMA",
        "country.iso_2": "DM"
    },
    {
        "country.display_name": "Denmark",
        "country.center": [
            55.670249,
            10.3333283
        ],
        "country.iso_3": "DNK",
        "country.iso_2": "DK"
    },
    {
        "country.display_name": "Dominican Republic",
        "country.center": [
            19.0974031,
            -70.3028026
        ],
        "country.iso_3": "DOM",
        "country.iso_2": "DO"
    },
    {
        "country.display_name": "Algeria",
        "country.center": [
            28.0000272,
            2.9999825
        ],
        "country.iso_3": "DZA",
        "country.iso_2": "DZ"
    },
    {
        "country.display_name": "Ecuador",
        "country.center": [
            -1.3397668,
            -79.3666965
        ],
        "country.iso_3": "ECU",
        "country.iso_2": "EC"
    },
    {
        "country.display_name": "Egypt",
        "country.center": [
            26.2540493,
            29.2675469
        ],
        "country.iso_3": "EGY",
        "country.iso_2": "EG"
    },
    {
        "country.display_name": "Eritrea",
        "country.center": [
            15.9500319,
            37.9999668
        ],
        "country.iso_3": "ERI",
        "country.iso_2": "ER"
    },
    {
        "country.display_name": "Spain",
        "country.center": [
            39.3262345,
            -4.8380649
        ],
        "country.iso_3": "ESP",
        "country.iso_2": "ES"
    },
    {
        "country.display_name": "Estonia",
        "country.center": [
            58.7523778,
            25.3319078
        ],
        "country.iso_3": "EST",
        "country.iso_2": "EE"
    },
    {
        "country.display_name": "Ethiopia",
        "country.center": [
            10.2116702,
            38.6521203
        ],
        "country.iso_3": "ETH",
        "country.iso_2": "ET"
    },
    {
        "country.display_name": "Finland",
        "country.center": [
            63.2467777,
            25.9209164
        ],
        "country.iso_3": "FIN",
        "country.iso_2": "FI"
    },
    {
        "country.display_name": "Fiji",
        "country.center": [
            -18.1239696,
            179.0122737
        ],
        "country.iso_3": "FJI",
        "country.iso_2": "FJ"
    },
    {
        "country.display_name": "Falkland Islands (Malvinas)",
        "country.center": [
            -51.9666424,
            -59.5500387
        ],
        "country.iso_3": "FLK",
        "country.iso_2": "FK"
    },
    {
        "country.display_name": "France",
        "country.center": [
            46.603354,
            1.8883335
        ],
        "country.iso_3": "FRA",
        "country.iso_2": "FR"
    },
    {
        "country.display_name": "Faroe Islands",
        "country.center": [
            62.0448724,
            -7.0322972
        ],
        "country.iso_3": "FRO",
        "country.iso_2": "FO"
    },
    {
        "country.display_name": "Micronesia, Federated States of",
        "country.center": [
            5.5600565,
            150.1982846
        ],
        "country.iso_3": "FSM",
        "country.iso_2": "FM"
    },
    {
        "country.display_name": "Gabon",
        "country.center": [
            -0.8999695,
            11.6899699
        ],
        "country.iso_3": "GAB",
        "country.iso_2": "GA"
    },
    {
        "country.display_name": "United Kingdom",
        "country.center": [
            54.7023545,
            -3.2765753
        ],
        "country.iso_3": "GBR",
        "country.iso_2": "GB"
    },
    {
        "country.display_name": "Georgia",
        "country.center": [
            41.6809707,
            44.0287382
        ],
        "country.iso_3": "GEO",
        "country.iso_2": "GE"
    },
    {
        "country.display_name": "Guernsey",
        "country.center": [
            49.580437,
            -2.484854
        ],
        "country.iso_3": "GGY",
        "country.iso_2": "GG"
    },
    {
        "country.display_name": "Ghana",
        "country.center": [
            8.0300284,
            -1.0800271
        ],
        "country.iso_3": "GHA",
        "country.iso_2": "GH"
    },
    {
        "country.display_name": "Gibraltar",
        "country.center": [
            36.10674695,
            -5.33527718348356
        ],
        "country.iso_3": "GIB",
        "country.iso_2": "GI"
    },
    {
        "country.display_name": "Guinea",
        "country.center": [
            10.7226226,
            -10.7083587
        ],
        "country.iso_3": "GIN",
        "country.iso_2": "GN"
    },
    {
        "country.display_name": "Gambia",
        "country.center": [
            13.470062,
            -15.4900464
        ],
        "country.iso_3": "GMB",
        "country.iso_2": "GM"
    },
    {
        "country.display_name": "Guinea-Bissau",
        "country.center": [
            12.100035,
            -14.9000214
        ],
        "country.iso_3": "GNB",
        "country.iso_2": "GW"
    },
    {
        "country.display_name": "Equatorial Guinea",
        "country.center": [
            1.613172,
            10.5170357
        ],
        "country.iso_3": "GNQ",
        "country.iso_2": "GQ"
    },
    {
        "country.display_name": "Greece",
        "country.center": [
            38.9953683,
            21.9877132
        ],
        "country.iso_3": "GRC",
        "country.iso_2": "GR"
    },
    {
        "country.display_name": "Grenada",
        "country.center": [
            12.1360374,
            -61.6904045
        ],
        "country.iso_3": "GRD",
        "country.iso_2": "GD"
    },
    {
        "country.display_name": "Greenland",
        "country.center": [
            77.6192349,
            -42.8125967
        ],
        "country.iso_3": "GRL",
        "country.iso_2": "GL"
    },
    {
        "country.display_name": "Guatemala",
        "country.center": [
            15.6356088,
            -89.8988087
        ],
        "country.iso_3": "GTM",
        "country.iso_2": "GT"
    },
    {
        "country.display_name": "Guam",
        "country.center": [
            13.445476,
            144.76507652909
        ],
        "country.iso_3": "GUM",
        "country.iso_2": "GU"
    },
    {
        "country.display_name": "Guyana",
        "country.center": [
            4.8417097,
            -58.6416891
        ],
        "country.iso_3": "GUY",
        "country.iso_2": "GY"
    },
    {
        "country.display_name": "Honduras",
        "country.center": [
            15.2572432,
            -86.0755145
        ],
        "country.iso_3": "HND",
        "country.iso_2": "HN"
    },
    {
        "country.display_name": "Croatia",
        "country.center": [
            45.5643442,
            17.0118954
        ],
        "country.iso_3": "HRV",
        "country.iso_2": "HR"
    },
    {
        "country.display_name": "Haiti",
        "country.center": [
            19.1399952,
            -72.3570972
        ],
        "country.iso_3": "HTI",
        "country.iso_2": "HT"
    },
    {
        "country.display_name": "Hungary",
        "country.center": [
            47.1817585,
            19.5060937
        ],
        "country.iso_3": "HUN",
        "country.iso_2": "HU"
    },
    {
        "country.display_name": "Indonesia",
        "country.center": [
            -2.4833826,
            117.8902853
        ],
        "country.iso_3": "IDN",
        "country.iso_2": "ID"
    },
    {
        "country.display_name": "Isle of Man",
        "country.center": [
            54.1936805,
            -4.5591148
        ],
        "country.iso_3": "IMN",
        "country.iso_2": "IM"
    },
    {
        "country.display_name": "India",
        "country.center": [
            22.3511148,
            78.6677428
        ],
        "country.iso_3": "IND",
        "country.iso_2": "IN"
    },
    {
        "country.display_name": "British Indian Ocean Territory",
        "country.center": [
            -6.4157192,
            72.1173961
        ],
        "country.iso_3": "IOT",
        "country.iso_2": "IO"
    },
    {
        "country.display_name": "Ireland",
        "country.center": [
            52.865196,
            -7.9794599
        ],
        "country.iso_3": "IRL",
        "country.iso_2": "IE"
    },
    {
        "country.display_name": "Iran, Islamic Republic of",
        "country.center": [
            32.9407495,
            52.9471344
        ],
        "country.iso_3": "IRN",
        "country.iso_2": "IR"
    },
    {
        "country.display_name": "Iraq",
        "country.center": [
            33.0955793,
            44.1749775
        ],
        "country.iso_3": "IRQ",
        "country.iso_2": "IQ"
    },
    {
        "country.display_name": "Iceland",
        "country.center": [
            64.9841821,
            -18.1059013
        ],
        "country.iso_3": "ISL",
        "country.iso_2": "IS"
    },
    {
        "country.display_name": "Israel",
        "country.center": [
            30.8760272,
            35.0015196
        ],
        "country.iso_3": "ISR",
        "country.iso_2": "IL"
    },
    {
        "country.display_name": "Italy",
        "country.center": [
            42.6384261,
            12.674297
        ],
        "country.iso_3": "ITA",
        "country.iso_2": "IT"
    },
    {
        "country.display_name": "Jamaica",
        "country.center": [
            18.1850507,
            -77.3947693
        ],
        "country.iso_3": "JAM",
        "country.iso_2": "JM"
    },
    {
        "country.display_name": "Jersey",
        "country.center": [
            49.2214561,
            -2.1358386
        ],
        "country.iso_3": "JEY",
        "country.iso_2": "JE"
    },
    {
        "country.display_name": "Jordan",
        "country.center": [
            31.1667049,
            36.941628
        ],
        "country.iso_3": "JOR",
        "country.iso_2": "JO"
    },
    {
        "country.display_name": "Japan",
        "country.center": [
            36.5748441,
            139.2394179
        ],
        "country.iso_3": "JPN",
        "country.iso_2": "JP"
    },
    {
        "country.display_name": "Kazakhstan",
        "country.center": [
            47.2286086,
            65.2093197
        ],
        "country.iso_3": "KAZ",
        "country.iso_2": "KZ"
    },
    {
        "country.display_name": "Kenya",
        "country.center": [
            1.4419683,
            38.4313975
        ],
        "country.iso_3": "KEN",
        "country.iso_2": "KE"
    },
    {
        "country.display_name": "Kyrgyzstan",
        "country.center": [
            41.5089324,
            74.724091
        ],
        "country.iso_3": "KGZ",
        "country.iso_2": "KG"
    },
    {
        "country.display_name": "Cambodia",
        "country.center": [
            13.5066394,
            104.869423
        ],
        "country.iso_3": "KHM",
        "country.iso_2": "KH"
    },
    {
        "country.display_name": "Kiribati",
        "country.center": [
            0.4483283,
            -171.6645388
        ],
        "country.iso_3": "KIR",
        "country.iso_2": "KI"
    },
    {
        "country.display_name": "Saint Kitts and Nevis",
        "country.center": [
            17.3462278,
            -62.7687277
        ],
        "country.iso_3": "KNA",
        "country.iso_2": "KN"
    },
    {
        "country.display_name": "Korea, Republic of",
        "country.center": [
            36.5581914,
            127.9408564
        ],
        "country.iso_3": "KOR",
        "country.iso_2": "KR"
    },
    {
        "country.display_name": "Kuwait",
        "country.center": [
            29.2733964,
            47.4979476
        ],
        "country.iso_3": "KWT",
        "country.iso_2": "KW"
    },
    {
        "country.display_name": "Lao People's Democratic Republic",
        "country.center": [
            20.0171109,
            103.378253
        ],
        "country.iso_3": "LAO",
        "country.iso_2": "LA"
    },
    {
        "country.display_name": "Lebanon",
        "country.center": [
            33.8750629,
            35.843409
        ],
        "country.iso_3": "LBN",
        "country.iso_2": "LB"
    },
    {
        "country.display_name": "Liberia",
        "country.center": [
            5.7499721,
            -9.3658524
        ],
        "country.iso_3": "LBR",
        "country.iso_2": "LR"
    },
    {
        "country.display_name": "Libya",
        "country.center": [
            26.8234472,
            18.1236723
        ],
        "country.iso_3": "LBY",
        "country.iso_2": "LY"
    },
    {
        "country.display_name": "Saint Lucia",
        "country.center": [
            13.8250489,
            -60.975036
        ],
        "country.iso_3": "LCA",
        "country.iso_2": "LC"
    },
    {
        "country.display_name": "Liechtenstein",
        "country.center": [
            47.1416307,
            9.5531527
        ],
        "country.iso_3": "LIE",
        "country.iso_2": "LI"
    },
    {
        "country.display_name": "Sri Lanka",
        "country.center": [
            7.5554942,
            80.7137847
        ],
        "country.iso_3": "LKA",
        "country.iso_2": "LK"
    },
    {
        "country.display_name": "Lesotho",
        "country.center": [
            -29.6039267,
            28.3350193
        ],
        "country.iso_3": "LSO",
        "country.iso_2": "LS"
    },
    {
        "country.display_name": "Lithuania",
        "country.center": [
            55.3500003,
            23.7499997
        ],
        "country.iso_3": "LTU",
        "country.iso_2": "LT"
    },
    {
        "country.display_name": "Luxembourg",
        "country.center": [
            49.8158683,
            6.1296751
        ],
        "country.iso_3": "LUX",
        "country.iso_2": "LU"
    },
    {
        "country.display_name": "Latvia",
        "country.center": [
            56.8406494,
            24.7537645
        ],
        "country.iso_3": "LVA",
        "country.iso_2": "LV"
    },
    {
        "country.display_name": "Morocco",
        "country.center": [
            31.1728205,
            -7.3362482
        ],
        "country.iso_3": "MAR",
        "country.iso_2": "MA"
    },
    {
        "country.display_name": "Monaco",
        "country.center": [
            43.7323492,
            7.4276832
        ],
        "country.iso_3": "MCO",
        "country.iso_2": "MC"
    },
    {
        "country.display_name": "Moldova, Republic of",
        "country.center": [
            47.286747,
            28.5110236
        ],
        "country.iso_3": "MDA",
        "country.iso_2": "MD"
    },
    {
        "country.display_name": "Madagascar",
        "country.center": [
            -18.9249604,
            46.4416422
        ],
        "country.iso_3": "MDG",
        "country.iso_2": "MG"
    },
    {
        "country.display_name": "Maldives",
        "country.center": [
            4.7064352,
            73.3287853
        ],
        "country.iso_3": "MDV",
        "country.iso_2": "MV"
    },
    {
        "country.display_name": "Mexico",
        "country.center": [
            22.5000485,
            -100.0000375
        ],
        "country.iso_3": "MEX",
        "country.iso_2": "MX"
    },
    {
        "country.display_name": "Marshall Islands",
        "country.center": [
            6.9518742,
            170.9985095
        ],
        "country.iso_3": "MHL",
        "country.iso_2": "MH"
    },
    {
        "country.display_name": "North Macedonia",
        "country.center": [
            41.6171214,
            21.7168387
        ],
        "country.iso_3": "MKD",
        "country.iso_2": "MK"
    },
    {
        "country.display_name": "Mali",
        "country.center": [
            16.3700359,
            -2.2900239
        ],
        "country.iso_3": "MLI",
        "country.iso_2": "ML"
    },
    {
        "country.display_name": "Malta",
        "country.center": [
            35.8885993,
            14.4476911
        ],
        "country.iso_3": "MLT",
        "country.iso_2": "MT"
    },
    {
        "country.display_name": "Myanmar",
        "country.center": [
            17.1750495,
            95.9999652
        ],
        "country.iso_3": "MMR",
        "country.iso_2": "MM"
    },
    {
        "country.display_name": "Montenegro",
        "country.center": [
            42.7728491,
            19.2408586
        ],
        "country.iso_3": "MNE",
        "country.iso_2": "ME"
    },
    {
        "country.display_name": "Mongolia",
        "country.center": [
            46.8250388,
            103.8499736
        ],
        "country.iso_3": "MNG",
        "country.iso_2": "MN"
    },
    {
        "country.display_name": "Mozambique",
        "country.center": [
            -19.302233,
            34.9144977
        ],
        "country.iso_3": "MOZ",
        "country.iso_2": "MZ"
    },
    {
        "country.display_name": "Mauritania",
        "country.center": [
            20.2540382,
            -9.2399263
        ],
        "country.iso_3": "MRT",
        "country.iso_2": "MR"
    },
    {
        "country.display_name": "Montserrat",
        "country.center": [
            16.7417041,
            -62.1916844
        ],
        "country.iso_3": "MSR",
        "country.iso_2": "MS"
    },
    {
        "country.display_name": "Mauritius",
        "country.center": [
            -20.2759451,
            57.5703566
        ],
        "country.iso_3": "MUS",
        "country.iso_2": "MU"
    },
    {
        "country.display_name": "Malawi",
        "country.center": [
            -13.2687204,
            33.9301963
        ],
        "country.iso_3": "MWI",
        "country.iso_2": "MW"
    },
    {
        "country.display_name": "Malaysia",
        "country.center": [
            4.5693754,
            102.2656823
        ],
        "country.iso_3": "MYS",
        "country.iso_2": "MY"
    },
    {
        "country.display_name": "Namibia",
        "country.center": [
            -23.2335499,
            17.3231107
        ],
        "country.iso_3": "NAM",
        "country.iso_2": "NA"
    },
    {
        "country.display_name": "New Caledonia",
        "country.center": [
            -20.4542886,
            164.55660583078
        ],
        "country.iso_3": "NCL",
        "country.iso_2": "NC"
    },
    {
        "country.display_name": "Niger",
        "country.center": [
            17.7356214,
            9.3238432
        ],
        "country.iso_3": "NER",
        "country.iso_2": "NE"
    },
    {
        "country.display_name": "Norfolk Island",
        "country.center": [
            -25.0657719,
            -130.1017823
        ],
        "country.iso_3": "NFK",
        "country.iso_2": "NF"
    },
    {
        "country.display_name": "Nigeria",
        "country.center": [
            9.6000359,
            7.9999721
        ],
        "country.iso_3": "NGA",
        "country.iso_2": "NG"
    },
    {
        "country.display_name": "Nicaragua",
        "country.center": [
            12.3724928,
            -84.8700308
        ],
        "country.iso_3": "NIC",
        "country.iso_2": "NI"
    },
    {
        "country.display_name": "Niue",
        "country.center": [
            -19.0536414,
            -169.8613411
        ],
        "country.iso_3": "NIU",
        "country.iso_2": "NU"
    },
    {
        "country.display_name": "Netherlands",
        "country.center": [
            52.5001698,
            5.7480821
        ],
        "country.iso_3": "NLD",
        "country.iso_2": "NL"
    },
    {
        "country.display_name": "Norway",
        "country.center": [
            60.5000209,
            9.0999715
        ],
        "country.iso_3": "NOR",
        "country.iso_2": "NO"
    },
    {
        "country.display_name": "Nepal",
        "country.center": [
            28.1083929,
            84.0917139
        ],
        "country.iso_3": "NPL",
        "country.iso_2": "NP"
    },
    {
        "country.display_name": "Nauru",
        "country.center": [
            -0.5252306,
            166.9324426
        ],
        "country.iso_3": "NRU",
        "country.iso_2": "NR"
    },
    {
        "country.display_name": "New Zealand",
        "country.center": [
            -41.5000831,
            172.8344077
        ],
        "country.iso_3": "NZL",
        "country.iso_2": "NZ"
    },
    {
        "country.display_name": "Oman",
        "country.center": [
            21.0000287,
            57.0036901
        ],
        "country.iso_3": "OMN",
        "country.iso_2": "OM"
    },
    {
        "country.display_name": "Pakistan",
        "country.center": [
            30.3308401,
            71.247499
        ],
        "country.iso_3": "PAK",
        "country.iso_2": "PK"
    },
    {
        "country.display_name": "Panama",
        "country.center": [
            8.3096067,
            -81.3066246
        ],
        "country.iso_3": "PAN",
        "country.iso_2": "PA"
    },
    {
        "country.display_name": "Pitcairn",
        "country.center": [
            -25.0657719,
            -130.1017823
        ],
        "country.iso_3": "PCN",
        "country.iso_2": "PN"
    },
    {
        "country.display_name": "Peru",
        "country.center": [
            -6.8699697,
            -75.0458515
        ],
        "country.iso_3": "PER",
        "country.iso_2": "PE"
    },
    {
        "country.display_name": "Philippines",
        "country.center": [
            12.7503486,
            122.7312101
        ],
        "country.iso_3": "PHL",
        "country.iso_2": "PH"
    },
    {
        "country.display_name": "Palau",
        "country.center": [
            6.097367,
            133.313631
        ],
        "country.iso_3": "PLW",
        "country.iso_2": "PW"
    },
    {
        "country.display_name": "Papua New Guinea",
        "country.center": [
            -5.6816069,
            144.2489081
        ],
        "country.iso_3": "PNG",
        "country.iso_2": "PG"
    },
    {
        "country.display_name": "Poland",
        "country.center": [
            52.215933,
            19.134422
        ],
        "country.iso_3": "POL",
        "country.iso_2": "PL"
    },
    {
        "country.display_name": "Korea, Democratic People's Republic of",
        "country.center": [
            40.3736611,
            127.0870417
        ],
        "country.iso_3": "PRK",
        "country.iso_2": "KP"
    },
    {
        "country.display_name": "Portugal",
        "country.center": [
            40.033265,
            -7.8896263
        ],
        "country.iso_3": "PRT",
        "country.iso_2": "PT"
    },
    {
        "country.display_name": "Paraguay",
        "country.center": [
            -23.3165935,
            -58.1693445
        ],
        "country.iso_3": "PRY",
        "country.iso_2": "PY"
    },
    {
        "country.display_name": "Palestine, State of",
        "country.center": [
            30.8760272,
            35.0015196
        ],
        "country.iso_3": "PSE",
        "country.iso_2": "PS"
    },
    {
        "country.display_name": "Qatar",
        "country.center": [
            25.3336984,
            51.2295295
        ],
        "country.iso_3": "QAT",
        "country.iso_2": "QA"
    },
    {
        "country.display_name": "Romania",
        "country.center": [
            45.9852129,
            24.6859225
        ],
        "country.iso_3": "ROU",
        "country.iso_2": "RO"
    },
    {
        "country.display_name": "Russian Federation",
        "country.center": [
            64.6863136,
            97.7453061
        ],
        "country.iso_3": "RUS",
        "country.iso_2": "RU"
    },
    {
        "country.display_name": "Rwanda",
        "country.center": [
            -1.9646631,
            30.0644358
        ],
        "country.iso_3": "RWA",
        "country.iso_2": "RW"
    },
    {
        "country.display_name": "Saudi Arabia",
        "country.center": [
            25.6242618,
            42.3528328
        ],
        "country.iso_3": "SAU",
        "country.iso_2": "SA"
    },
    {
        "country.display_name": "Sudan",
        "country.center": [
            14.5844444,
            29.4917691
        ],
        "country.iso_3": "SDN",
        "country.iso_2": "SD"
    },
    {
        "country.display_name": "Senegal",
        "country.center": [
            14.4750607,
            -14.4529612
        ],
        "country.iso_3": "SEN",
        "country.iso_2": "SN"
    },
    {
        "country.display_name": "Singapore",
        "country.center": [
            1.357107,
            103.8194992
        ],
        "country.iso_3": "SGP",
        "country.iso_2": "SG"
    },
    {
        "country.display_name": "South Georgia and the South Sandwich Islands",
        "country.center": [
            -54.8432857,
            -35.8090698
        ],
        "country.iso_3": "SGS",
        "country.iso_2": "GS"
    },
    {
        "country.display_name": "Saint Helena, Ascension and Tristan da Cunha",
        "country.center": [
            -37.2465,
            -12.4870384875
        ],
        "country.iso_3": "SHN",
        "country.iso_2": "SH"
    },
    {
        "country.display_name": "Solomon Islands",
        "country.center": [
            -9.7354344,
            162.8288542
        ],
        "country.iso_3": "SLB",
        "country.iso_2": "SB"
    },
    {
        "country.display_name": "Sierra Leone",
        "country.center": [
            8.6400349,
            -11.8400269
        ],
        "country.iso_3": "SLE",
        "country.iso_2": "SL"
    },
    {
        "country.display_name": "El Salvador",
        "country.center": [
            13.8000382,
            -88.9140683
        ],
        "country.iso_3": "SLV",
        "country.iso_2": "SV"
    },
    {
        "country.display_name": "San Marino",
        "country.center": [
            43.9458623,
            12.458306
        ],
        "country.iso_3": "SMR",
        "country.iso_2": "SM"
    },
    {
        "country.display_name": "Somalia",
        "country.center": [
            8.3676771,
            49.083416
        ],
        "country.iso_3": "SOM",
        "country.iso_2": "SO"
    },
    {
        "country.display_name": "Serbia",
        "country.center": [
            44.1534121,
            20.55144
        ],
        "country.iso_3": "SRB",
        "country.iso_2": "RS"
    },
    {
        "country.display_name": "South Sudan",
        "country.center": [
            7.8699431,
            29.6667897
        ],
        "country.iso_3": "SSD",
        "country.iso_2": "SS"
    },
    {
        "country.display_name": "Sao Tome and Principe",
        "country.center": [
            0.8875498,
            6.9648718
        ],
        "country.iso_3": "STP",
        "country.iso_2": "ST"
    },
    {
        "country.display_name": "Suriname",
        "country.center": [
            4.1413025,
            -56.0771187
        ],
        "country.iso_3": "SUR",
        "country.iso_2": "SR"
    },
    {
        "country.display_name": "Slovakia",
        "country.center": [
            48.7411522,
            19.4528646
        ],
        "country.iso_3": "SVK",
        "country.iso_2": "SK"
    },
    {
        "country.display_name": "Slovenia",
        "country.center": [
            45.8133113,
            14.4808369
        ],
        "country.iso_3": "SVN",
        "country.iso_2": "SI"
    },
    {
        "country.display_name": "Sweden",
        "country.center": [
            59.6749712,
            14.5208584
        ],
        "country.iso_3": "SWE",
        "country.iso_2": "SE"
    },
    {
        "country.display_name": "Eswatini",
        "country.center": [
            -26.5624806,
            31.3991317
        ],
        "country.iso_3": "SWZ",
        "country.iso_2": "SZ"
    },
    {
        "country.display_name": "Seychelles",
        "country.center": [
            -4.6574977,
            55.4540146
        ],
        "country.iso_3": "SYC",
        "country.iso_2": "SC"
    },
    {
        "country.display_name": "Syrian Arab Republic",
        "country.center": [
            34.6401861,
            39.0494106
        ],
        "country.iso_3": "SYR",
        "country.iso_2": "SY"
    },
    {
        "country.display_name": "Turks and Caicos Islands",
        "country.center": [
            21.7214683,
            -71.6201783
        ],
        "country.iso_3": "TCA",
        "country.iso_2": "TC"
    },
    {
        "country.display_name": "Chad",
        "country.center": [
            15.6134137,
            19.0156172
        ],
        "country.iso_3": "TCD",
        "country.iso_2": "TD"
    },
    {
        "country.display_name": "Togo",
        "country.center": [
            8.7800265,
            1.0199765
        ],
        "country.iso_3": "TGO",
        "country.iso_2": "TG"
    },
    {
        "country.display_name": "Thailand",
        "country.center": [
            14.8971921,
            100.83273
        ],
        "country.iso_3": "THA",
        "country.iso_2": "TH"
    },
    {
        "country.display_name": "Tajikistan",
        "country.center": [
            38.6281733,
            70.8156541
        ],
        "country.iso_3": "TJK",
        "country.iso_2": "TJ"
    },
    {
        "country.display_name": "Tokelau",
        "country.center": [
            -9.1676396,
            -171.8196878
        ],
        "country.iso_3": "TKL",
        "country.iso_2": "TK"
    },
    {
        "country.display_name": "Turkmenistan",
        "country.center": [
            39.3763807,
            59.3924609
        ],
        "country.iso_3": "TKM",
        "country.iso_2": "TM"
    },
    {
        "country.display_name": "Timor-Leste",
        "country.center": [
            -8.5151979,
            125.8375756
        ],
        "country.iso_3": "TLS",
        "country.iso_2": "TL"
    },
    {
        "country.display_name": "Tonga",
        "country.center": [
            -19.9160819,
            -175.2026424
        ],
        "country.iso_3": "TON",
        "country.iso_2": "TO"
    },
    {
        "country.display_name": "Trinidad and Tobago",
        "country.center": [
            10.8677845,
            -60.9821067
        ],
        "country.iso_3": "TTO",
        "country.iso_2": "TT"
    },
    {
        "country.display_name": "Tunisia",
        "country.center": [
            33.8439408,
            9.400138
        ],
        "country.iso_3": "TUN",
        "country.iso_2": "TN"
    },
    {
        "country.display_name": "Turkey",
        "country.center": [
            38.9597594,
            34.9249653
        ],
        "country.iso_3": "TUR",
        "country.iso_2": "TR"
    },
    {
        "country.display_name": "Tuvalu",
        "country.center": [
            -7.768959,
            178.1167698
        ],
        "country.iso_3": "TUV",
        "country.iso_2": "TV"
    },
    {
        "country.display_name": "Tanzania, United Republic of",
        "country.center": [
            -6.5247123,
            35.7878438
        ],
        "country.iso_3": "TZA",
        "country.iso_2": "TZ"
    },
    {
        "country.display_name": "Uganda",
        "country.center": [
            1.5333554,
            32.2166578
        ],
        "country.iso_3": "UGA",
        "country.iso_2": "UG"
    },
    {
        "country.display_name": "Ukraine",
        "country.center": [
            49.4871968,
            31.2718321
        ],
        "country.iso_3": "UKR",
        "country.iso_2": "UA"
    },
    {
        "country.display_name": "United States Minor Outlying Islands",
        "country.center": [
            6.4295092,
            -162.407309978782
        ],
        "country.iso_3": "UMI",
        "country.iso_2": "UM"
    },
    {
        "country.display_name": "Uruguay",
        "country.center": [
            -32.8755548,
            -56.0201525
        ],
        "country.iso_3": "URY",
        "country.iso_2": "UY"
    },
    {
        "country.display_name": "United States",
        "country.center": [
            39.7837304,
            -100.4458825
        ],
        "country.iso_3": "USA",
        "country.iso_2": "US"
    },
    {
        "country.display_name": "Uzbekistan",
        "country.center": [
            41.32373,
            63.9528098
        ],
        "country.iso_3": "UZB",
        "country.iso_2": "UZ"
    },
    {
        "country.display_name": "Saint Vincent and the Grenadines",
        "country.center": [
            12.90447,
            -61.2765569
        ],
        "country.iso_3": "VCT",
        "country.iso_2": "VC"
    },
    {
        "country.display_name": "Venezuela, Bolivarian Republic of",
        "country.center": [
            8.0018709,
            -66.1109318
        ],
        "country.iso_3": "VEN",
        "country.iso_2": "VE"
    },
    {
        "country.display_name": "Virgin Islands, British",
        "country.center": [
            18.4024395,
            -64.5661642
        ],
        "country.iso_3": "VGB",
        "country.iso_2": "VG"
    },
    {
        "country.display_name": "Viet Nam",
        "country.center": [
            13.2904027,
            108.4265113
        ],
        "country.iso_3": "VNM",
        "country.iso_2": "VN"
    },
    {
        "country.display_name": "Vanuatu",
        "country.center": [
            -16.5255069,
            168.1069154
        ],
        "country.iso_3": "VUT",
        "country.iso_2": "VU"
    },
    {
        "country.display_name": "Wallis and Futuna",
        "country.center": [
            -13.28536975,
            -176.187268263577
        ],
        "country.iso_3": "WLF",
        "country.iso_2": "WF"
    },
    {
        "country.display_name": "Samoa",
        "country.center": [
            -13.7693895,
            -172.1200508
        ],
        "country.iso_3": "WSM",
        "country.iso_2": "WS"
    },
    {
        "country.display_name": "Yemen",
        "country.center": [
            16.3471243,
            47.8915271
        ],
        "country.iso_3": "YEM",
        "country.iso_2": "YE"
    },
    {
        "country.display_name": "South Africa",
        "country.center": [
            -28.8166236,
            24.991639
        ],
        "country.iso_3": "ZAF",
        "country.iso_2": "ZA"
    },
    {
        "country.display_name": "Zambia",
        "country.center": [
            -14.5186239,
            27.5599164
        ],
        "country.iso_3": "ZMB",
        "country.iso_2": "ZM"
    },
    {
        "country.display_name": "Zimbabwe",
        "country.center": [
            -18.4554963,
            29.7468414
        ],
        "country.iso_3": "ZWE",
        "country.iso_2": "ZW"
    }
]


class CentralizedServer(models.Model):
    """
    Centralized Server for monitoring/analytics metrics data
    """
    host = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        help_text=_("Centralized Server IP address/Host name.")
    )
    port = models.IntegerField(
        null=False,
        blank=False,
        help_text=_("Centralized Server TCP port number.")
    )
    local_ip = models.GenericIPAddressField(
        null=False,
        blank=False,
        protocol='IPv4',
        help_text=_("Local Server IP address.")
    )
    interval = models.IntegerField(
        null=False,
        blank=False,
        default=3600,
        help_text=_("Data aggregation time interval (in seconds).")
    )
    db_path = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        default="logstash.db",
        help_text=_("The local SQLite database to cache log events between emitting and "
                    "transmission to the Logstash server. "
                    "This way log events are cached even across process restarts (and crashes).")
    )
    socket_timeout = models.FloatField(
        null=True,
        blank=True,
        default=5.0,
        help_text=_("Timeout in seconds for TCP connections.")
    )
    queue_check_interval = models.FloatField(
        null=True,
        blank=True,
        default=2.0,
        help_text=_("Interval in seconds to check the internal queue for new messages to be cached in the database.")
    )
    queue_events_flush_interval = models.FloatField(
        null=True,
        blank=True,
        default=0.1,
        help_text=_("Interval in seconds to send cached events from the database to Logstash.")
    )
    queue_events_flush_count = models.IntegerField(
        null=True,
        blank=True,
        default=50,
        help_text=_("Count of cached events to send from the database to Logstash; "
                    "events are sent to Logstash whenever QUEUED_EVENTS_FLUSH_COUNT or "
                    "QUEUED_EVENTS_FLUSH_INTERVAL is reached, whatever happens first.")
    )
    queue_events_batch_size = models.IntegerField(
        null=True,
        blank=True,
        default=50,
        help_text=_("Maximum number of events to be sent to Logstash in one batch. "
                    "Depending on the transport, this usually means a new connection to the Logstash is "
                    "established for the event batch.")
    )
    logstash_db_timeout = models.FloatField(
        null=True,
        blank=True,
        default=5.0,
        help_text=_("Timeout in seconds to 'connect' the SQLite database.")
    )
    last_successful_deliver = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Timestamp of the last successful deliver.")
    )
    next_scheduled_deliver = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Timestamp of the next scheduled deliver.")
    )
    last_failed_deliver = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Timestamp of the last failed deliver.")
    )

    def save(self, *args, **kwargs):
        """
        Overriding the 'save' super method.
        We have to sync PeriodicTask with CentralizedServer
        """
        self.sync_periodic_task()
        super(CentralizedServer, self).save(*args, **kwargs)

    def sync_periodic_task(self):
        """
        Sync django_celery_beat
        """
        if settings.MONITORING_ENABLED and settings.USER_ANALYTICS_ENABLED:
            try:
                i, _ci = IntervalSchedule.objects.get_or_create(
                    every=self.interval, period=IntervalSchedule.SECONDS
                )
            except IntervalSchedule.MultipleObjectsReturned:
                i = IntervalSchedule.objects.filter(
                    every=self.interval, period=IntervalSchedule.SECONDS
                ).first()
            try:
                pt, _cpt = PeriodicTask.objects.get_or_create(
                    name="dispatch-metrics-task",
                    task="geonode_logstash.tasks.dispatch_metrics",
                )
            except PeriodicTask.MultipleObjectsReturned:
                pt = PeriodicTask.objects.filter(
                    name="dispatch-metrics-task",
                    task="geonode_logstash.tasks.dispatch_metrics",
                ).first()
            pt.interval = i
            pt.enabled = True
            pt.save()
        else:
            # When MONITORING_ENABLED=True and USER_ANALYTICS_ENABLED=False we have to disable the task
            pts = PeriodicTask.objects.filter(
                name="dispatch-metrics-task",
                task="geonode_logstash.tasks.dispatch_metrics",
            )
            for pt in pts:
                pt.enabled = False
                pt.save()
