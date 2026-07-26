"""
India Seismic, Hydrological, and Disaster Evidence Database.
Sources: IS 1893:2016, TNSDMA, NDMA, NRSC Bhuvan ISRO, IMD, CGWB, CPCB.
"""

# State → default seismic zone (IS 1893:2016)
STATE_SEISMIC_ZONE = {
    # Zone V - Very High
    "jammu and kashmir": 5, "ladakh": 5, "himachal pradesh": 5,
    "uttarakhand": 5, "sikkim": 5, "northeast india": 5,
    "arunachal pradesh": 5, "nagaland": 5, "manipur": 5,
    "mizoram": 5, "assam": 5, "meghalaya": 5, "tripura": 5,

    # Zone IV - High
    "punjab": 4, "haryana": 4, "delhi": 4, "uttar pradesh": 4,
    "bihar": 4, "west bengal": 4, "gujarat": 4,

    # Zone III - Moderate
    "rajasthan": 3, "madhya pradesh": 3, "jharkhand": 3,
    "odisha": 3, "maharashtra": 3, "goa": 3,
    "karnataka": 3, "andhra pradesh": 3, "telangana": 3,

    # Zone II - Low
    "tamil nadu": 2, "kerala": 2, "chhattisgarh": 2,
}

COASTAL_STATES = {
    "odisha", "west bengal", "andhra pradesh", "tamil nadu",
    "kerala", "karnataka", "goa", "maharashtra", "gujarat",
    "pondicherry", "lakshadweep", "andaman and nicobar islands"
}

FLOOD_PRONE_STATES = {
    "assam", "bihar", "uttar pradesh", "west bengal", "odisha",
    "manipur", "tripura", "arunachal pradesh", "punjab",
    "haryana", "uttarakhand", "himachal pradesh"
}

LANDSLIDE_PRONE_STATES = {
    "uttarakhand", "himachal pradesh", "jammu and kashmir",
    "arunachal pradesh", "assam", "manipur", "meghalaya",
    "mizoram", "nagaland", "sikkim", "west bengal"
}

MAJOR_RIVERS = [
    # Major rivers with wider coverage ranges
    {"name": "Ganga", "lat_range": (24, 31), "lon_range": (77, 89)},
    {"name": "Yamuna", "lat_range": (25, 31), "lon_range": (76, 82)},
    {"name": "Brahmaputra", "lat_range": (26, 28), "lon_range": (89, 97)},
    {"name": "Godavari", "lat_range": (17, 21), "lon_range": (73, 82)},
    {"name": "Krishna", "lat_range": (14, 18), "lon_range": (74, 81)},
    {"name": "Mahanadi", "lat_range": (19, 22), "lon_range": (80, 87)},
    {"name": "Narmada", "lat_range": (21, 23), "lon_range": (72, 82)},
    {"name": "Tapti", "lat_range": (21, 22), "lon_range": (73, 78)},
    {"name": "Cauvery", "lat_range": (10, 13), "lon_range": (75, 79)},
    {"name": "Periyar", "lat_range": (9.5, 10.5), "lon_range": (76, 77.5)},
    {"name": "Bharathapuzha", "lat_range": (10.5, 11.5), "lon_range": (76, 76.8)},
    {"name": "Pamba", "lat_range": (9.2, 9.8), "lon_range": (76.5, 77.2)},
    {"name": "Chambal", "lat_range": (24, 27), "lon_range": (75, 80)},
    {"name": "Betwa", "lat_range": (23, 25.5), "lon_range": (77, 81)},
    {"name": "Son", "lat_range": (22, 25), "lon_range": (82, 85)},
    {"name": "Gandak", "lat_range": (26, 28), "lon_range": (83, 86)},
    {"name": "Kosi", "lat_range": (25, 27.5), "lon_range": (86, 88)},
    {"name": "Ghaghra", "lat_range": (25.5, 28), "lon_range": (81, 84)},
    {"name": "Rapti", "lat_range": (26, 28), "lon_range": (82, 84)},
    {"name": "Saryu", "lat_range": (28.5, 30), "lon_range": (80, 82)},
    {"name": "Ramganga", "lat_range": (28, 30), "lon_range": (78, 80)},
    {"name": "Gomti", "lat_range": (25.5, 27.5), "lon_range": (80, 83)},
    {"name": "Gandhi Sagar Dam tributaries", "lat_range": (24, 25), "lon_range": (74, 76)},
    {"name": "Indravati", "lat_range": (18, 20), "lon_range": (80, 83)},
    {"name": "Pranhita", "lat_range": (18, 20), "lon_range": (78, 80)},
    {"name": "Wainganga", "lat_range": (19, 22), "lon_range": (78, 81)},
    {"name": "Pench", "lat_range": (21, 22), "lon_range": (78, 80)},
    {"name": "Tawa", "lat_range": (22, 23), "lon_range": (76, 78)},
    # Chennai rivers
    {"name": "Cooum", "lat_range": (13.0, 13.15), "lon_range": (80.05, 80.3)},
    {"name": "Adyar", "lat_range": (12.9, 13.1), "lon_range": (80.05, 80.3)},
    {"name": "Buckingham Canal", "lat_range": (12.8, 13.2), "lon_range": (80.2, 80.35)},
    # Mumbai rivers
    {"name": "Mithi River", "lat_range": (19.0, 19.12), "lon_range": (72.82, 72.95)},
    {"name": "Poisar River", "lat_range": (19.1, 19.25), "lon_range": (72.85, 72.95)},
    {"name": "Oshiwara River", "lat_range": (19.1, 19.2), "lon_range": (72.82, 72.9)},
    # Bengaluru
    {"name": "Vrishabhavathi", "lat_range": (12.8, 13.05), "lon_range": (77.4, 77.65)},
    {"name": "Arkavathy", "lat_range": (13.0, 13.4), "lon_range": (77.3, 77.6)},
    # Other important rivers
    {"name": "Sabarmati", "lat_range": (22.5, 24), "lon_range": (72, 73.5)},
    {"name": "Mahi", "lat_range": (22, 24), "lon_range": (73, 75)},
    {"name": "Luni", "lat_range": (24, 27), "lon_range": (71, 74)},
    {"name": "Banas", "lat_range": (24.5, 26.5), "lon_range": (74, 76.5)},
    {"name": "Chambal", "lat_range": (24, 27), "lon_range": (75, 80)},
    {"name": "Kali", "lat_range": (14.5, 15.5), "lon_range": (74, 74.8)},
    {"name": "Sharavathi", "lat_range": (13.5, 14.5), "lon_range": (74.5, 75)},
    {"name": "Netravathi", "lat_range": (12.5, 13.5), "lon_range": (75, 75.8)},
    {"name": "Kabini", "lat_range": (11.5, 12.5), "lon_range": (76, 76.8)},
    {"name": "Bhavani", "lat_range": (11, 12), "lon_range": (76.5, 77.2)},
    {"name": "Noyyal", "lat_range": (10.5, 11.5), "lon_range": (76.8, 77.3)},
    {"name": "Vaigai", "lat_range": (9.8, 10.5), "lon_range": (77.5, 78.5)},
    {"name": "Thamirabarani", "lat_range": (8.5, 9.5), "lon_range": (77.2, 77.8)},
    {"name": "Palar", "lat_range": (12.5, 13.5), "lon_range": (78.5, 79.5)},
    {"name": "Pennar", "lat_range": (13, 15), "lon_range": (77, 80)},
]

CYCLONE_RISK_COASTAL = {
    "odisha": 90, "andhra pradesh": 85, "tamil nadu": 80,
    "west bengal": 75, "gujarat": 70, "maharashtra": 40,
    "kerala": 25, "karnataka": 20, "goa": 20,
    "andaman and nicobar islands": 85, "lakshadweep": 60,
}

STATE_ANNUAL_RAINFALL = {
    "meghalaya": 11000, "arunachal pradesh": 4000, "assam": 3000,
    "mizoram": 2500, "manipur": 2300, "nagaland": 2200,
    "tripura": 2200, "kerala": 3000, "goa": 2900,
    "west bengal": 1800, "odisha": 1500, "andhra pradesh": 1000,
    "karnataka": 1150, "maharashtra": 1200, "gujarat": 800,
    "rajasthan": 400, "haryana": 600, "punjab": 700,
    "uttar pradesh": 900, "bihar": 1100, "jharkhand": 1200,
    "madhya pradesh": 1100, "chhattisgarh": 1300, "tamil nadu": 950,
    "himachal pradesh": 1500, "uttarakhand": 2000,
    "jammu and kashmir": 700, "delhi": 700, "sikkim": 3000,
}

# ─── LOCAL REGULATORY AUTHORITIES BY STATE / CITY ────────────────────────────
# City-level authorities (checked first)
CITY_REGULATORY_AUTHORITIES = {
    "chennai":   {"name": "Chennai Metropolitan Development Authority (CMDA)", "buffer_req": "15m-30m water body & canal buffer zone per TN Combined Development Rules"},
    "mumbai":    {"name": "Mumbai Metropolitan Region Development Authority (MMRDA) / MCGM", "buffer_req": "CRZ II/III 50m buffer & Mithi River Coastal Regulation compliance"},
    "bengaluru": {"name": "Bruhat Bengaluru Mahanagara Palike (BBMP) / BDA", "buffer_req": "30m primary Nallah / 15m secondary Nallah buffer zone compliance"},
    "hyderabad": {"name": "Hyderabad Metropolitan Development Authority (HMDA) / GHMC", "buffer_req": "30m Full Tank Level (FTL) buffer zone for lakes & tanks (HYDRAA enforcement)"},
    "delhi":     {"name": "Delhi Development Authority (DDA)", "buffer_req": "Yamuna Floodplain Zone O construction ban (300m-500m buffer)"},
    "kolkata":   {"name": "Kolkata Metropolitan Development Authority (KMDA)", "buffer_req": "East Kolkata Wetlands Ramsar Buffer Protection Act"},
    "pune":      {"name": "Pune Metropolitan Region Development Authority (PMRDA)", "buffer_req": "Mutha River Blue Line / Red Line flood zone restrictions"},
    "gurugram":  {"name": "Haryana Real Estate Regulatory Authority (HRERA) / DTCP Haryana", "buffer_req": "DTCP building plan approval & Aravalli ridge buffer compliance"},
    "faridabad": {"name": "Haryana Urban Development Authority (HSVP) / DTCP Haryana", "buffer_req": "DTCP Haryana building plan approval & setback compliance"},
    "ahmedabad": {"name": "Ahmedabad Urban Development Authority (AUDA)", "buffer_req": "Gujarat RERA & Sabarmati riverfront buffer compliance"},
    "surat":     {"name": "Surat Municipal Corporation / SUDA", "buffer_req": "Gujarat Coastal Zone CRZ compliance & Tapi River buffer"},
    "jaipur":    {"name": "Jaipur Development Authority (JDA)", "buffer_req": "Rajasthan RERA building approval & Bisalpur catchment buffer"},
    "lucknow":   {"name": "Lucknow Development Authority (LDA) / UPEIDA", "buffer_req": "UP RERA & Gomti River flood plain buffer compliance"},
    "bhopal":    {"name": "Bhopal Municipal Corporation / BHEL Township Authority", "buffer_req": "MP RERA & Upper Lake (Bada Talab) 1km buffer compliance"},
    "indore":    {"name": "Indore Development Authority (IDA)", "buffer_req": "MP RERA & Kahn River buffer zone compliance"},
    "nagpur":    {"name": "Nagpur Metropolitan Region Development Authority (NMRDA)", "buffer_req": "Maharashtra RERA & Nag River buffer zone compliance"},
    "patna":     {"name": "Patna Regional Development Authority (PRDA)", "buffer_req": "Bihar RERA & Ganga floodplain Zone compliance"},
    "chandigarh":{"name": "Chandigarh Administration / Estate Office", "buffer_req": "Chandigarh Master Plan 2031 & Sukhna Lake 1km ESZ compliance"},
    "amritsar":  {"name": "Punjab Urban Planning and Development Authority (PUDA)", "buffer_req": "Punjab RERA & urban waterbody buffer compliance"},
    "kochi":     {"name": "Kochi Corporation / Kerala RERA", "buffer_req": "CRZ & Vembanad Lake Ramsar buffer compliance"},
    "thiruvananthapuram": {"name": "Thiruvananthapuram Corporation / Kerala RERA", "buffer_req": "CRZ & Western Ghat ESA compliance"},
    "bhubaneswar": {"name": "Bhubaneswar Development Authority (BDA)", "buffer_req": "Odisha RERA & Mahanadi flood zone compliance"},
    "visakhapatnam": {"name": "Greater Visakhapatnam Municipal Corporation / VUDA", "buffer_req": "CRZ & ANDHRA RERA coastal buffer compliance"},
    "coimbatore": {"name": "Coimbatore Corporation / DTCP Tamil Nadu", "buffer_req": "TN RERA & Noyyal River buffer zone compliance"},
    "general":   {"name": "State RERA & Local Planning Authority (LPA)", "buffer_req": "State RERA building approval & local body water body buffer compliance"},
}

# State-level fallback authorities (used when city is not in the city map above)
STATE_REGULATORY_AUTHORITIES = {
    "haryana":           {"name": "DTCP Haryana / Haryana RERA (HRERA)", "buffer_req": "DTCP building plan approval, HRERA registration & local Nala buffer compliance"},
    "punjab":            {"name": "Punjab Urban Planning and Development Authority (PUDA) / Punjab RERA", "buffer_req": "PUDA layout approval & waterbody setback compliance"},
    "uttar pradesh":     {"name": "UP RERA / Local Development Authority (LDA/ADA/GDA)", "buffer_req": "UP RERA registration & Ganga/Yamuna floodplain buffer compliance"},
    "rajasthan":         {"name": "Rajasthan RERA / Local Urban Body", "buffer_req": "Rajasthan RERA & desert eco-sensitive zone compliance"},
    "gujarat":           {"name": "Gujarat RERA / Urban Development Authority (UDA)", "buffer_req": "GDCR building rules & CRZ coastal buffer compliance"},
    "maharashtra":       {"name": "MahaRERA / Local Municipal Corporation", "buffer_req": "DCR flood line & CRZ buffer zone compliance"},
    "karnataka":         {"name": "Karnataka RERA / BDA / Local Planning Authority", "buffer_req": "BMRDA & Rajakaluve buffer zone compliance"},
    "tamil nadu":        {"name": "Tamil Nadu RERA (TNRERA) / CMDA / DTCP Tamil Nadu", "buffer_req": "TN Combined Development & Building Rules water body buffer"},
    "kerala":            {"name": "Kerala RERA / Local Self Government (LSG)", "buffer_req": "CRZ & Western Ghats Eco-Sensitive Zone (ESZ) compliance"},
    "andhra pradesh":    {"name": "AP RERA / CRDA / VMRDA", "buffer_req": "CRZ & Krishna/Godavari river buffer zone compliance"},
    "telangana":         {"name": "Telangana RERA / HMDA / HYDRAA", "buffer_req": "FTL lake buffer (HYDRAA) & GHMC layout approval"},
    "madhya pradesh":    {"name": "MP RERA / Local Development Authority", "buffer_req": "MP RERA & river/lake buffer compliance"},
    "bihar":             {"name": "Bihar RERA / Patna Regional Development Authority (PRDA)", "buffer_req": "Ganga floodplain buffer & Bihar RERA compliance"},
    "west bengal":       {"name": "West Bengal HIRA / KMDA / Local Urban Body", "buffer_req": "Wetland buffer (KMDA) & Howrah/Kolkata CRZ compliance"},
    "odisha":            {"name": "Odisha RERA / BDA / Local Municipal Body", "buffer_req": "CRZ & Mahanadi floodplain buffer compliance"},
    "jharkhand":         {"name": "Jharkhand RERA / Local Urban Body", "buffer_req": "Jharkhand RERA & mining buffer zone compliance"},
    "chhattisgarh":      {"name": "Chhattisgarh RERA / Local Urban Body", "buffer_req": "Mahanadi buffer zone & forest ESZ compliance"},
    "uttarakhand":       {"name": "Uttarakhand RERA / UDA", "buffer_req": "Himalayan Eco-Sensitive Zone & river buffer compliance"},
    "himachal pradesh":  {"name": "Himachal Pradesh RERA / TCP Department", "buffer_req": "Forest buffer & river setback compliance under HP TCP Act"},
    "jammu and kashmir": {"name": "J&K RERA / Housing Board", "buffer_req": "Dal Lake buffer & J&K land development compliance"},
    "goa":               {"name": "Goa RERA / TCP Goa", "buffer_req": "CRZ & Goa Regional Plan buffer compliance"},
    "delhi":             {"name": "Delhi Development Authority (DDA) / RERA Delhi", "buffer_req": "Yamuna Floodplain Zone O (300m-500m) construction ban"},
    "assam":             {"name": "Assam RERA / Guwahati Metropolitan Development Authority (GMDA)", "buffer_req": "Brahmaputra floodplain buffer & NE state RERA compliance"},
    "general":           {"name": "State RERA & Local Planning Authority (LPA)", "buffer_req": "State RERA building approval & local body water body buffer compliance"},
}

# ─── HISTORICAL DISASTER EVIDENCE DATABASE (expanded to cover all Indian states) ──
# Geofenced historical event intersections (Lat, Lon bounding boxes)
HISTORICAL_DISASTER_LOG = [
    # CHENNAI
    {
        "city": "chennai",
        "lat_range": (12.8, 13.2),
        "lon_range": (80.05, 80.35),
        "events": [
            {"year": 2023, "event_name": "Cyclone Michaung Extreme Inundation", "severity": "Very High", "details": "Record 450mm 24-hr rainfall triggered widespread urban flooding across South Chennai. Storm drains overflowed by up to 1.2m.", "inundation_status": "Coordinates Submerged in 2023 Inundation Map", "source": "TNSDMA 2023"},
            {"year": 2015, "event_name": "December 2015 Chembarambakkam Reservoir Overflow", "severity": "Extreme", "details": "Release of 29,000 cusecs into Adyar River combined with 490mm torrential rain, causing catastrophic flooding.", "inundation_status": "Historic HFL Exceeded", "source": "NDMA & ISRO NRSC Bhuvan 2015"},
            {"year": 2021, "event_name": "Northeast Monsoon Urban Flash Floods", "severity": "High", "details": "Nungambakkam & T. Nagar micro-drainage channels backed up, causing 0.5m inundation.", "inundation_status": "Micro-Watershed Outfall Overflow", "source": "Chennai Corporation 2021"},
        ]
    },
    # MUMBAI
    {
        "city": "mumbai",
        "lat_range": (18.85, 19.35),
        "lon_range": (72.7, 73.05),
        "events": [
            {"year": 2005, "event_name": "July 26 Deluge & Mithi River Breach", "severity": "Extreme", "details": "944mm single-day rainfall led to severe overflow of Mithi river, submerging surrounding plots up to 2m.", "inundation_status": "Historic Max Inundation Zone", "source": "MCGM Fact-Finding Committee 2005"},
            {"year": 2020, "event_name": "Cyclone Nisarga & High-Tide Surge", "severity": "High", "details": "Coinciding 4.8m spring high tide and coastal gale winds caused severe backflow into storm drains.", "inundation_status": "High-Tide Storm Surge Outfall Blockage", "source": "Maharashtra SDMP 2020"},
        ]
    },
    # BENGALURU
    {
        "city": "bengaluru",
        "lat_range": (12.8, 13.15),
        "lon_range": (77.4, 77.8),
        "events": [
            {"year": 2022, "event_name": "September 2022 Rajakaluve Lake Cascade Breach", "severity": "High", "details": "Overtopping of Bellandur and Varthur lake cascades following 130mm intense cloudburst. Encroached Rajakaluves overflowed.", "inundation_status": "Rajakaluve Buffer Zone Inundation", "source": "BBMP Lake Audit 2022"},
            {"year": 2024, "event_name": "May 2024 Cloudburst Event", "severity": "High", "details": "Extreme rainfall event caused flooding in multiple low-lying areas of Bengaluru.", "inundation_status": "Urban Flooding Recorded", "source": "KSNDMC 2024"},
        ]
    },
    # HYDERABAD
    {
        "city": "hyderabad",
        "lat_range": (17.2, 17.6),
        "lon_range": (78.3, 78.6),
        "events": [
            {"year": 2020, "event_name": "October 2020 Cloudburst & Nala Overflow", "severity": "High", "details": "192mm 24-hr record rainfall caused Hussain Sagar outlet nalas to overflow, flooding 35+ colonies.", "inundation_status": "Nala Encroachment Flood Zone", "source": "TSDMA 2020"},
        ]
    },
    # PATNA
    {
        "city": "patna",
        "lat_range": (25.4, 25.75),
        "lon_range": (84.9, 85.35),
        "events": [
            {"year": 2019, "event_name": "September 2019 Gangetic Plain Urban Waterlogging", "severity": "Extreme", "details": "Failure of main outfall sump houses along the Ganga caused Rajendra Nagar and Kankarbagh to remain submerged under 1.5m water for 6 days.", "inundation_status": "Sump House Outfall Backwater", "source": "BSDMA 2019"},
        ]
    },
    # CHENNAI (neighborhood-level boxes)
    {
        "city": "chennai_pallavaram",
        "lat_range": (12.94, 13.00),
        "lon_range": (80.12, 80.18),
        "events": [
            {"year": 2023, "event_name": "Pallavaram/Chrompet Waterlogging", "severity": "High", "details": "Cyclone Michaung caused flooding in Pallavaram, Chrompet, and Tambaram areas from Adyar river backflow.", "inundation_status": "Local flooding recorded", "source": "TNSDMA 2023"},
            {"year": 2015, "event_name": "South Chennai Floods 2015", "severity": "Extreme", "details": "Pallavaram and surrounding areas affected by Chembarambakkam reservoir release.", "inundation_status": "Reservoir release flooding", "source": "NDMA 2015"},
        ]
    },
    {
        "city": "chennai_velachery",
        "lat_range": (12.95, 13.02),
        "lon_range": (80.18, 80.26),
        "events": [
            {"year": 2023, "event_name": "Velachery Flooding 2023", "severity": "Very High", "details": "Velachery lake overflow and Pallikaranai marsh backwater affected residential areas.", "inundation_status": "Lake overflow + marsh backflow", "source": "TNSDMA 2023"},
            {"year": 2015, "event_name": "Velachery Lake Breach 2015", "severity": "Extreme", "details": "Velachery lake bund breach submerged multiple apartment complexes.", "inundation_status": "Lake bund breach", "source": "NDMA 2015"},
        ]
    },
    {
        "city": "chennai_adyar",
        "lat_range": (12.98, 13.04),
        "lon_range": (80.22, 80.28),
        "events": [
            {"year": 2023, "event_name": "Adyar River Overflow 2023", "severity": "Very High", "details": "Adyar river overflow near Adyar bridge, flooding adjacent localities.", "inundation_status": "River overflow", "source": "TNSDMA 2023"},
            {"year": 2021, "event_name": "Adyar Flood 2021", "severity": "High", "details": "Heavy rainfall caused Adyar river to breach banks in Adyar area.", "inundation_status": "River bank breach", "source": "Chennai Corporation 2021"},
        ]
    },
    {
        "city": "chennai_north",
        "lat_range": (13.05, 13.15),
        "lon_range": (80.18, 80.28),
        "events": [
            {"year": 2023, "event_name": "North Chennai Waterlogging", "severity": "High", "details": "Tondiarpet and Royapuram areas faced waterlogging from poor drainage.", "inundation_status": "Drainage overflow", "source": "Chennai Corporation 2023"},
        ]
    },
    # MUMBAI (neighborhood-level)
    {
        "city": "mumbai_andheri",
        "lat_range": (19.08, 19.16),
        "lon_range": (72.80, 72.88),
        "events": [
            {"year": 2005, "event_name": "Andheri Flooding 2005", "severity": "Extreme", "details": "Andheri subway submerged under 6ft water. Mithi river overflow.", "inundation_status": "Subway submergence", "source": "MCGM 2005"},
            {"year": 2019, "event_name": "Andheri Waterlogging 2019", "severity": "High", "details": "Heavy rainfall caused severe waterlogging in Andheri east and west.", "inundation_status": "Urban flooding", "source": "MCGM 2019"},
        ]
    },
    {
        "city": "mumbai_low_parel",
        "lat_range": (18.98, 19.04),
        "lon_range": (72.82, 72.88),
        "events": [
            {"year": 2005, "event_name": "Hindmata Flood 2005", "severity": "Extreme", "details": "Hindmata junction submerged. Multiple deaths reported.", "inundation_status": "Extreme urban flooding", "source": "MCGM 2005"},
        ]
    },
    # BENGALURU (neighborhood-level)
    {
        "city": "bengaluru_koramangala",
        "lat_range": (12.91, 12.96),
        "lon_range": (77.60, 77.65),
        "events": [
            {"year": 2022, "event_name": "Koramangala Flooding 2022", "severity": "High", "details": "Bellandur lake overflow affected Koramangala and HSR Layout.", "inundation_status": "Lake overflow", "source": "BBMP 2022"},
        ]
    },
    {
        "city": "bengaluru_east",
        "lat_range": (12.95, 13.02),
        "lon_range": (77.65, 77.78),
        "events": [
            {"year": 2022, "event_name": "Mahadevapura Flood 2022", "severity": "Very High", "details": "Rajakaluve breach flooded Mahadevapura and Whitefield areas.", "inundation_status": "Rajakaluve breach", "source": "BBMP 2022"},
        ]
    },
    # KERALA (wider coverage)
    {
        "city": "kerala_state",
        "lat_range": (8.3, 12.5),
        "lon_range": (74.8, 77.5),
        "events": [
            {"year": 2018, "event_name": "Kerala Floods 2018", "severity": "Extreme", "details": "Worst floods in a century. Idukki, Wayanad, Ernakulam worst hit. 483 deaths.", "inundation_status": "Dam discharge + monsoon flooding", "source": "Kerala SDMA 2018"},
            {"year": 2019, "event_name": "Kerala Floods 2019", "severity": "Very High", "details": "Second consecutive year of severe flooding.", "inundation_status": "Dam release flooding", "source": "Kerala SDMA 2019"},
        ]
    },
    # ASSAM (wider coverage)
    {
        "city": "assam_state",
        "lat_range": (24.5, 28.5),
        "lon_range": (89.5, 96.5),
        "events": [
            {"year": 2022, "event_name": "Assam Floods 2022", "severity": "Extreme", "details": "Brahmaputra floods affected 32 of 35 districts. 200+ deaths.", "inundation_status": "Brahmaputra basin flooding", "source": "Assam SDMA 2022"},
            {"year": 2024, "event_name": "Assam Floods 2024", "severity": "Very High", "details": "Severe flooding from Brahmaputra and Barak rivers.", "inundation_status": "Multi-river flooding", "source": "Assam SDMA 2024"},
        ]
    },
    # BIHAR (wider coverage)
    {
        "city": "bihar_state",
        "lat_range": (24.2, 27.5),
        "lon_range": (83.2, 88.2),
        "events": [
            {"year": 2019, "event_name": "Bihar Floods 2019", "severity": "Extreme", "details": "Kosi, Bagmati, and Mahananda rivers flooded 12 districts. 130+ deaths.", "inundation_status": "Gangetic floodplain flooding", "source": "BSDMA 2019"},
            {"year": 2023, "event_name": "Bihar Floods 2023", "severity": "Very High", "details": "Extensive flooding from Kosi and Gandak rivers.", "inundation_status": "Multi-river flooding", "source": "BSDMA 2023"},
        ]
    },
    # UTTARAKHAND
    {
        "city": "uttarakhand_state",
        "lat_range": (28.5, 31.5),
        "lon_range": (77.5, 81.0),
        "events": [
            {"year": 2013, "event_name": "Kedarnath Disaster 2013", "severity": "Extreme", "details": "Glacial lake outburst killed 5000+. Worst Himalayan disaster.", "inundation_status": "Glacial burst", "source": "NDMA 2013"},
            {"year": 2023, "event_name": "Uttarakhand Cloudburst 2023", "severity": "Very High", "details": "Multiple cloudburst events in Chamoli, Tehri, Pauri.", "inundation_status": "Hill slope flooding", "source": "UK SDMA 2023"},
        ]
    },
    # HIMACHAL PRADESH
    {
        "city": "himachal_state",
        "lat_range": (30.5, 33.0),
        "lon_range": (75.5, 79.0),
        "events": [
            {"year": 2023, "event_name": "HP Monsoon Disaster 2023", "severity": "Extreme", "details": "400+ landslides and 50 flash floods in single season.", "inundation_status": "Landslide + flash flood", "source": "HP SDMA 2023"},
        ]
    },
    # WEST BENGAL
    {
        "city": "kolkata",
        "lat_range": (22.3, 22.8),
        "lon_range": (88.1, 88.6),
        "events": [
            {"year": 2020, "event_name": "Cyclone Amphan", "severity": "Extreme", "details": "Super cyclone 185kmph. 98 deaths, 13B USD damage.", "inundation_status": "Cyclone surge + river flooding", "source": "IMD & WB SDMA 2020"},
        ]
    },
    # ODISHA
    {
        "city": "odisha_state",
        "lat_range": (17.8, 22.6),
        "lon_range": (81.3, 87.5),
        "events": [
            {"year": 1999, "event_name": "Odisha Super Cyclone 1999", "severity": "Extreme", "details": "10000+ deaths. 260kmph winds and 5m surge.", "inundation_status": "Extreme storm surge", "source": "IMD 1999"},
            {"year": 2019, "event_name": "Cyclone Fani 2019", "severity": "Extreme", "details": "185kmph winds hit Puri. 64 deaths.", "inundation_status": "Extreme wind + surge", "source": "IMD 2019"},
        ]
    },
    # ANDHRA PRADESH
    {
        "city": "visakhapatnam",
        "lat_range": (17.5, 17.9),
        "lon_range": (83.0, 83.5),
        "events": [
            {"year": 2014, "event_name": "Cyclone Hudhud 2014", "severity": "Very High", "details": "185kmph winds devastated Visakhapatnam. 124 deaths.", "inundation_status": "Cyclone landfall zone", "source": "IMD 2014"},
        ]
    },
    # GUJARAT
    {
        "city": "gujarat_state",
        "lat_range": (20.0, 24.5),
        "lon_range": (68.0, 74.5),
        "events": [
            {"year": 2001, "event_name": "Bhuj Earthquake 2001", "severity": "Extreme", "details": "Mw 7.7 killed 20000+. Ahmedabad had structural damage.", "inundation_status": "Seismic zone V", "source": "GSI 2001"},
            {"year": 2023, "event_name": "Gujarat Floods 2023", "severity": "High", "details": "Saurashtra and Kutch received extreme rainfall.", "inundation_status": "Flash flooding", "source": "Gujarat SDMA 2023"},
        ]
    },
    # JAMMU & KASHMIR
    {
        "city": "kashmir_valley",
        "lat_range": (33.5, 34.5),
        "lon_range": (74.0, 75.5),
        "events": [
            {"year": 2014, "event_name": "Kashmir Floods 2014", "severity": "Extreme", "details": "Jhelum overflow flooded Srinagar. 277 deaths.", "inundation_status": "River overflow flooding", "source": "J&K SDMA 2014"},
            {"year": 2005, "event_name": "Kashmir Earthquake 2005", "severity": "Extreme", "details": "Mw 7.6 killed 86000+ across Kashmir.", "inundation_status": "Seismic zone V", "source": "GSI 2005"},
        ]
    },
    # DELHI
    {
        "city": "delhi",
        "lat_range": (28.4, 28.9),
        "lon_range": (76.8, 77.4),
        "events": [
            {"year": 2023, "event_name": "Delhi Flooding 2023", "severity": "Very High", "details": "Yamuna river breached danger mark, flooding low-lying areas.", "inundation_status": "River overflow", "source": "Delhi SDMA 2023"},
            {"year": 2020, "event_name": "Yamuna Floodplain Flooding", "severity": "High", "details": "Yamuna water levels rose significantly affecting riverside areas.", "inundation_status": "Floodplain inundation", "source": "Delhi SDMA 2020"},
        ]
    },
    # TAMIL NADU (beyond Chennai)
    {
        "city": "madurai",
        "lat_range": (9.8, 10.1),
        "lon_range": (78.0, 78.4),
        "events": [
            {"year": 2015, "event_name": "TN Floods 2015", "severity": "Very High", "details": "Cuddalore, Thanjavur, Madurai districts severely flooded.", "inundation_status": "Regional flooding", "source": "TNSDMA 2015"},
        ]
    },
    # NORTHEAST INDIA
    {
        "city": "northeast_states",
        "lat_range": (23.5, 29.0),
        "lon_range": (89.0, 98.0),
        "events": [
            {"year": 2024, "event_name": "Manipur Floods 2024", "severity": "Very High", "details": "Severe flooding in Imphal valley and surrounding hills.", "inundation_status": "Valley flooding", "source": "Manipur SDMA 2024"},
            {"year": 2022, "event_name": "Assam-Meghalaya Floods", "severity": "Very High", "details": "Widespread flooding across northeastern states.", "inundation_status": "Multi-state flooding", "source": "NE SDMA 2022"},
        ]
    },
]

# Named Fault Lines for Seismic Proximity Reasoning (expanded)
NAMED_FAULT_LINES = [
    # Zone V - Very High Damage Risk
    {"name": "Main Boundary Thrust (MBT) Himalayan Arc", "lat": 30.5, "lon": 78.5, "zone": "Zone V", "last_active": "1991 Uttarkashi & 1999 Chamoli"},
    {"name": "Kutch Mainland Fault (KMF)", "lat": 23.5, "lon": 70.2, "zone": "Zone V", "last_active": "2001 Bhuj Mw 7.7"},
    {"name": "Naga Thrust Fault", "lat": 26.0, "lon": 94.5, "zone": "Zone V", "last_active": "2016 Manipur Mw 6.7"},
    {"name": "Dhubri Fault Zone", "lat": 26.0, "lon": 90.0, "zone": "Zone V", "last_active": "2016 Assam Mw 6.7"},
    {"name": "Tripura Thrust Belt", "lat": 23.5, "lon": 91.5, "zone": "Zone V", "last_active": "2017 Tripura Mw 5.8"},
    {"name": "Kameng Fault Zone", "lat": 27.5, "lon": 92.5, "zone": "Zone V", "last_active": "2009 Arunachal Mw 6.2"},
    {"name": "Kopili Fault", "lat": 26.2, "lon": 92.5, "zone": "Zone V", "last_active": "2018 Assam Mw 5.6"},

    # Zone IV - High Damage Risk
    {"name": "Narmada-Tapti Lineament Zone", "lat": 21.8, "lon": 75.0, "zone": "Zone IV", "last_active": "1997 Jabalpur Mw 6.0"},
    {"name": "Delhi-Moradabad Fault", "lat": 28.8, "lon": 78.5, "zone": "Zone IV", "last_active": "1991 Uttarkashi Mw 6.1 (felt strongly)"},
    {"name": "Sohna Fault", "lat": 28.2, "lon": 77.0, "zone": "Zone IV", "last_active": "2004 Delhi tremors"},
    {"name": "Mathura Fault", "lat": 27.5, "lon": 77.7, "zone": "Zone IV", "last_active": "Potential seismic gap zone"},
    {"name": "Frontal Himalayan Thrust", "lat": 29.5, "lon": 77.5, "zone": "Zone IV", "last_active": "1991 Uttarkashi Mw 6.6"},
    {"name": "Satpura Zone Fault", "lat": 22.5, "lon": 78.0, "zone": "Zone IV", "last_active": "1997 Jabalpur Mw 6.0"},
    {"name": "West Coast Fault", "lat": 15.5, "lon": 73.5, "zone": "Zone IV", "last_active": "2018 Goa tremors"},
    {"name": "Aravalli Delhi Fault", "lat": 28.0, "lon": 77.2, "zone": "Zone IV", "last_active": "2007 Delhi Mw 4.2"},
    {"name": "Godavari Graben", "lat": 18.5, "lon": 79.5, "zone": "Zone IV", "last_active": "2011 Andhra tremors"},
    {"name": "Pranhita-Godavari Graben", "lat": 19.5, "lon": 79.0, "zone": "Zone IV", "last_active": "1969 Adilabad Mw 5.3"},

    # Zone III - Moderate Damage Risk
    {"name": "Panvel Flexure Fault", "lat": 19.0, "lon": 73.1, "zone": "Zone III", "last_active": "1993 Latur regional intraplate activity"},
    {"name": "Palghat Gap Shear Zone", "lat": 10.8, "lon": 76.6, "zone": "Zone III", "last_active": "Micro-seismic tremors 2018"},
    {"name": "Chennai Fault Zone", "lat": 13.1, "lon": 80.2, "zone": "Zone III", "last_active": "2001 Chennai Mw 4.0"},
    {"name": "Srivilliputtur Fault", "lat": 9.5, "lon": 77.6, "zone": "Zone III", "last_active": "2014 Tamil Nadu tremors"},
    {"name": "Cambay Graben", "lat": 22.5, "lon": 72.5, "zone": "Zone III", "last_active": "2001 Bhuj aftershocks"},
    {"name": "Bhuj-Kutch Fault System", "lat": 23.8, "lon": 69.5, "zone": "Zone III", "last_active": "2001 Bhuj Mw 7.7"},
    {"name": "Jabalpur Fault Zone", "lat": 23.2, "lon": 79.9, "zone": "Zone III", "last_active": "1997 Jabalpur Mw 6.0"},
    {"name": "Pune Fault Zone", "lat": 18.5, "lon": 73.8, "zone": "Zone III", "last_active": "2018 Pune Mw 3.5"},
    {"name": "Koyna Fault Zone", "lat": 17.4, "lon": 73.7, "zone": "Zone III", "last_active": "2017 Koyna Mw 5.0 (reservoir induced)"},
    {"name": "Bengaluru Fault Zone", "lat": 13.0, "lon": 77.5, "zone": "Zone III", "last_active": "2012 Bengaluru tremors"},
]
