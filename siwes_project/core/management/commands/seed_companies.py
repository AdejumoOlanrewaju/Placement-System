from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import User, CompanyProfile, State, LGA
import secrets
import string

COMPANIES = [
    {
        "company_name": "Andela",
        "industry": "Software Development",
        "description": "Andela is a global technology talent company founded in Lagos. SIWES students can gain exposure to software engineering, QA, DevOps, cloud technologies and AI.",
        "address": "55A Adebisi Omotola Close, Victoria Island, Lagos",
        "website": "https://andela.com",
        "state": "Lagos",
        "lga": "Eti-Osa",
        "contact": {
            "first": "Talent",
            "last": "Team",
            "email": "careers@andela.com",
            "phone": ""
        }
    },
    {
        "company_name": "Interswitch Group",
        "industry": "FinTech",
        "description": "Africa's leading digital payments company offering SIWES opportunities in backend engineering, payment systems, DevOps, cybersecurity and data engineering.",
        "address": "Plot 1648C Oko-Awo Close, Victoria Island, Lagos",
        "website": "https://interswitchgroup.com",
        "state": "Lagos",
        "lga": "Eti-Osa",
        "contact": {
            "first": "Talent",
            "last": "Acquisition",
            "email": "careers@interswitchgroup.com",
            "phone": ""
        }
    },
    {
        "company_name": "Flutterwave",
        "industry": "FinTech",
        "description": "Payment technology company providing internship opportunities in software engineering, product development, infrastructure and security.",
        "address": "8 Providence Street, Lekki Phase 1, Lagos",
        "website": "https://flutterwave.com",
        "state": "Lagos",
        "lga": "Eti-Osa",
        "contact": {
            "first": "HR",
            "last": "Team",
            "email": "careers@flutterwavego.com",
            "phone": ""
        }
    },
    {
        "company_name": "Paystack",
        "industry": "FinTech",
        "description": "Online payment infrastructure company offering experience in APIs, backend engineering, infrastructure and product design.",
        "address": "126 Joel Ogunnaike Street, Ikeja GRA, Lagos",
        "website": "https://paystack.com",
        "state": "Lagos",
        "lga": "Ikeja",
        "contact": {
            "first": "People",
            "last": "Operations",
            "email": "careers@paystack.com",
            "phone": ""
        }
    },
    {
        "company_name": "Moniepoint",
        "industry": "FinTech",
        "description": "Digital banking and payment infrastructure company with opportunities in software engineering, QA and cloud infrastructure.",
        "address": "Victoria Island, Lagos",
        "website": "https://moniepoint.com",
        "state": "Lagos",
        "lga": "Eti-Osa",
        "contact": {
            "first": "People",
            "last": "Team",
            "email": "careers@moniepoint.com",
            "phone": ""
        }
    },
    {
        "company_name": "SystemSpecs",
        "industry": "Software Development",
        "description": "Developers of Remita and enterprise software solutions with SIWES opportunities in software engineering, QA and product development.",
        "address": "20 Opebi Road, Ikeja, Lagos",
        "website": "https://systemspecs.com.ng",
        "state": "Lagos",
        "lga": "Ikeja",
        "contact": {
            "first": "Human",
            "last": "Resources",
            "email": "careers@systemspecs.com.ng",
            "phone": ""
        }
    },
    {
        "company_name": "CWG Plc",
        "industry": "Information Technology",
        "description": "Pan-African technology company providing enterprise software, cloud, cybersecurity and managed services.",
        "address": "Block 54A, Plot 10, Off Rufus Giwa Street, Lekki Phase 1, Lagos",
        "website": "https://cwg-plc.ng",
        "state": "Lagos",
        "lga": "Eti-Osa",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "info@cwg-plc.com",
            "phone": "07074699822"
        }
    },
    {
        "company_name": "ByteWorks Technology Solutions",
        "industry": "Software Development",
        "description": "Enterprise software company delivering e-government, AI and revenue automation solutions. SIWES students gain practical software engineering experience.",
        "address": "12 Y.P.O Shodeinde Street, Utako, Abuja",
        "website": "https://byteworks.com.ng",
        "state": "Federal Capital Territory",
        "lga": "Abuja Municipal Area Council",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "info@byteworks.com.ng",
            "phone": "09094257562"
        }
    },
    {
        "company_name": "Galaxy Backbone",
        "industry": "Government ICT",
        "description": "Federal Government ICT infrastructure provider offering SIWES opportunities in networking, cloud computing, cybersecurity and software engineering.",
        "address": "1243 Kur Mohammed Avenue, Central Business District, Abuja",
        "website": "https://galaxybackbone.com.ng",
        "state": "Federal Capital Territory",
        "lga": "Abuja Municipal Area Council",
        "contact": {
            "first": "Service",
            "last": "Desk",
            "email": "servicedesk@galaxybackbone.com.ng",
            "phone": "08073990518"
        }
    },
    {
        "company_name": "NIGCOMSAT Ltd",
        "industry": "Satellite Communications",
        "description": "Nigeria's satellite communications company offering SIWES placements in ICT, networking, software systems and satellite technology.",
        "address": "Obasanjo Space Centre, Airport Road, Abuja",
        "website": "https://nigcomsat.gov.ng",
        "state": "Federal Capital Territory",
        "lga": "Abuja Municipal Area Council",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "info@nigcomsat.gov.ng",
            "phone": ""
        }
    },
    {
        "company_name": "MTN Nigeria",
        "industry": "Telecommunications",
        "description": "Nigeria's largest telecommunications company offering SIWES opportunities in software engineering, networking, cloud infrastructure, cybersecurity and data analytics.",
        "address": "MTN Plaza, No. 1 Awolowo Road, Falomo, Ikoyi, Lagos",
        "website": "https://www.mtn.ng",
        "state": "Lagos",
        "lga": "Lagos Island",
        "contact": {
            "first": "HR",
            "last": "Team",
            "email": "careers@mtn.com",
            "phone": ""
        }
    },
    {
        "company_name": "Airtel Nigeria",
        "industry": "Telecommunications",
        "description": "Leading telecommunications provider offering SIWES placements in IT, software development, network engineering and enterprise systems.",
        "address": "Plot L2, Banana Island, Ikoyi, Lagos",
        "website": "https://www.airtel.com.ng",
        "state": "Lagos",
        "lga": "Eti-Osa",
        "contact": {
            "first": "Talent",
            "last": "Acquisition",
            "email": "careers@ng.airtel.com",
            "phone": ""
        }
    },
    {
        "company_name": "Globacom",
        "industry": "Telecommunications",
        "description": "Nigerian telecommunications company with opportunities in software engineering, networking, infrastructure and IT support.",
        "address": "Mike Adenuga Towers, Adeola Odeku Street, Victoria Island, Lagos",
        "website": "https://www.gloworld.com",
        "state": "Lagos",
        "lga": "Eti-Osa",
        "contact": {
            "first": "Human",
            "last": "Resources",
            "email": "careers@gloworld.com",
            "phone": ""
        }
    },
    {
        "company_name": "9mobile",
        "industry": "Telecommunications",
        "description": "Telecommunications provider offering SIWES opportunities in network operations, IT systems and enterprise technology.",
        "address": "Plot 19, Zone L, Banana Island, Ikoyi, Lagos",
        "website": "https://www.9mobile.com.ng",
        "state": "Lagos",
        "lga": "Eti-Osa",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "care@9mobile.com.ng",
            "phone": ""
        }
    },
    {
        "company_name": "MainOne",
        "industry": "Cloud & Data Centre",
        "description": "West African connectivity and cloud solutions company providing SIWES opportunities in cloud engineering, networking and cybersecurity.",
        "address": "Ligali Ayorinde Street, Victoria Island, Lagos",
        "website": "https://www.mainone.net",
        "state": "Lagos",
        "lga": "Eti-Osa",
        "contact": {
            "first": "People",
            "last": "Team",
            "email": "careers@mainone.net",
            "phone": ""
        }
    },
    {
        "company_name": "ipNX Nigeria",
        "industry": "Internet Service Provider",
        "description": "Broadband and fibre internet provider offering practical experience in networking, VoIP, systems administration and software engineering.",
        "address": "2B Oyinkan Abayomi Drive, Ikoyi, Lagos",
        "website": "https://www.ipnxnigeria.net",
        "state": "Lagos",
        "lga": "Lagos Island",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "careers@ipnxnigeria.net",
            "phone": ""
        }
    },
    {
        "company_name": "Layer3",
        "industry": "Cloud & Managed Services",
        "description": "Enterprise ICT company specializing in cloud services, networking, cybersecurity and managed infrastructure.",
        "address": "5th Floor, IGI House, 3 Gwani Street, Wuse Zone 4, Abuja",
        "website": "https://layer3.ng",
        "state": "Federal Capital Territory",
        "lga": "Abuja Municipal Area Council",
        "contact": {
            "first": "People",
            "last": "Operations",
            "email": "careers@layer3.ng",
            "phone": ""
        }
    },
    {
        "company_name": "eTranzact International",
        "industry": "FinTech",
        "description": "Electronic payment technology company offering SIWES opportunities in payment systems, backend development and infrastructure engineering.",
        "address": "Fortune Towers, 27/29 Adeyemo Alakija Street, Victoria Island, Lagos",
        "website": "https://www.etranzact.com",
        "state": "Lagos",
        "lga": "Eti-Osa",
        "contact": {
            "first": "Human",
            "last": "Resources",
            "email": "careers@etranzact.com",
            "phone": ""
        }
    },
    {
        "company_name": "Paga",
        "industry": "FinTech",
        "description": "Digital payments company providing SIWES opportunities in backend engineering, product management, QA and mobile development.",
        "address": "176 Herbert Macaulay Way, Yaba, Lagos",
        "website": "https://www.mypaga.com",
        "state": "Lagos",
        "lga": "Lagos Mainland",
        "contact": {
            "first": "Talent",
            "last": "Team",
            "email": "careers@mypaga.com",
            "phone": ""
        }
    },
    {
        "company_name": "Konga",
        "industry": "E-Commerce",
        "description": "Leading Nigerian e-commerce company offering SIWES opportunities in software engineering, logistics technology, data analysis and IT operations.",
        "address": "1 Konga Place, Yudala Heights, Gbagada Expressway, Lagos",
        "website": "https://www.konga.com",
        "state": "Lagos",
        "lga": "Kosofe",
        "contact": {
            "first": "HR",
            "last": "Team",
            "email": "careers@konga.com",
            "phone": ""
        }
    },
    {
        "company_name": "Hotels.ng",
        "industry": "Software Development",
        "description": "Hotels.ng is a Nigerian travel technology company offering SIWES placements in software engineering, UI/UX design, digital marketing and data analysis.",
        "address": "3 Birabi Street, GRA Phase 1, Port Harcourt",
        "website": "https://hotels.ng",
        "state": "Rivers",
        "lga": "Port Harcourt",
        "contact": {
            "first": "HR",
            "last": "Team",
            "email": "careers@hotels.ng",
            "phone": ""
        }
    },
    {
        "company_name": "BlueChip Technologies",
        "industry": "Information Technology",
        "description": "Enterprise technology company providing AI, cloud computing, cybersecurity and business intelligence solutions.",
        "address": "Trans Amadi Industrial Layout, Port Harcourt",
        "website": "https://bluechiptech.biz",
        "state": "Rivers",
        "lga": "Port Harcourt",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "info@bluechiptech.biz",
            "phone": ""
        }
    },
    {
        "company_name": "Enugu Electricity Distribution Company (EEDC)",
        "industry": "Power & Utilities",
        "description": "Electricity distribution company offering placements in ICT, software systems, networking and electrical engineering.",
        "address": "62 Okpara Avenue, Enugu",
        "website": "https://enugudisco.com",
        "state": "Enugu",
        "lga": "Enugu North",
        "contact": {
            "first": "Corporate",
            "last": "Affairs",
            "email": "info@enugudisco.com",
            "phone": ""
        }
    },
    {
        "company_name": "Genesys Tech Hub",
        "industry": "Software Development",
        "description": "Technology innovation hub providing software engineering, UI/UX, AI and startup incubation opportunities.",
        "address": "No. 1 Edinburgh Road, Enugu",
        "website": "https://genesystechhub.com",
        "state": "Enugu",
        "lga": "Enugu North",
        "contact": {
            "first": "Community",
            "last": "Manager",
            "email": "info@genesystechhub.com",
            "phone": ""
        }
    },
    {
        "company_name": "Proforce Limited",
        "industry": "Defense Technology",
        "description": "Nigerian defence and armored vehicle manufacturer with opportunities in embedded systems, mechanical engineering and software integration.",
        "address": "Ota Industrial Estate, Ogun State",
        "website": "https://proforcedefence.com",
        "state": "Ogun",
        "lga": "Ado-Odo/Ota",
        "contact": {
            "first": "Human",
            "last": "Resources",
            "email": "info@proforcedefence.com",
            "phone": ""
        }
    },
    {
        "company_name": "MicCom Cables",
        "industry": "Manufacturing",
        "description": "Manufacturer of fibre optic and electrical cables with SIWES opportunities in production engineering and industrial automation.",
        "address": "Ota, Ogun State",
        "website": "https://miccomcables.com",
        "state": "Ogun",
        "lga": "Ado-Odo/Ota",
        "contact": {
            "first": "HR",
            "last": "Office",
            "email": "info@miccomcables.com",
            "phone": ""
        }
    },
    {
        "company_name": "Nigerian Breweries Ibadan",
        "industry": "Manufacturing",
        "description": "Leading beverage manufacturer offering SIWES opportunities in automation, ICT, electrical engineering and production systems.",
        "address": "Ibadan Brewery, Ibadan",
        "website": "https://nbplc.com",
        "state": "Oyo",
        "lga": "Ibadan South-West",
        "contact": {
            "first": "HR",
            "last": "Team",
            "email": "careers@heineken.com",
            "phone": ""
        }
    },
    {
        "company_name": "Kaduna Electric",
        "industry": "Power Distribution",
        "description": "Electric power distribution company offering industrial training in ICT infrastructure, networking and electrical systems.",
        "address": "1-2 Ahmadu Bello Way, Kaduna",
        "website": "https://kadunaelectric.com",
        "state": "Kaduna",
        "lga": "Kaduna North",
        "contact": {
            "first": "Corporate",
            "last": "Services",
            "email": "info@kadunaelectric.com",
            "phone": ""
        }
    },
    {
        "company_name": "Dangote Cement Plc",
        "industry": "Manufacturing",
        "description": "Africa's largest cement manufacturer with opportunities in automation, software systems, industrial networking and engineering.",
        "address": "Obajana Plant",
        "website": "https://dangotecement.com",
        "state": "Kogi",
        "lga": "Lokoja",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "careers@dangote.com",
            "phone": ""
        }
    },
    {
        "company_name": "Zinox Technologies",
        "industry": "Computer Hardware & ICT",
        "description": "Leading Nigerian ICT company involved in computer manufacturing, enterprise solutions and digital transformation projects.",
        "address": "Akanu Ibiam Road, Enugu",
        "website": "https://zinox.com",
        "state": "Enugu",
        "lga": "Enugu East",
        "contact": {
            "first": "People",
            "last": "Operations",
            "email": "info@zinox.com",
            "phone": ""
        }
    },
    {
        "company_name": "Nestlé Nigeria Plc",
        "industry": "Food & Beverage",
        "description": "Leading food and beverage manufacturer offering SIWES placements in production engineering, ICT, quality assurance, food technology and supply chain.",
        "address": "Agbara Industrial Estate, Ogun State",
        "website": "https://www.nestle-cwa.com",
        "state": "Ogun",
        "lga": "Ado-Odo/Ota",
        "contact": {
            "first": "Human",
            "last": "Resources",
            "email": "communications@ng.nestle.com",
            "phone": ""
        }
    },
    {
        "company_name": "Cadbury Nigeria Plc",
        "industry": "Food Manufacturing",
        "description": "Manufacturer of beverages and confectioneries with SIWES opportunities in automation, engineering, ICT and production management.",
        "address": "Lateef Jakande Road, Ikeja, Lagos",
        "website": "https://www.cadburynigeria.com",
        "state": "Lagos",
        "lga": "Ikeja",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "info@cadburynigeria.com",
            "phone": ""
        }
    },
    {
        "company_name": "Unilever Nigeria Plc",
        "industry": "Consumer Goods",
        "description": "Global FMCG company offering internships in IT, engineering, manufacturing, marketing and supply chain.",
        "address": "Billings Way, Oregun, Ikeja, Lagos",
        "website": "https://www.unilever.com.ng",
        "state": "Lagos",
        "lga": "Ikeja",
        "contact": {
            "first": "Careers",
            "last": "Team",
            "email": "careers.ng@unilever.com",
            "phone": ""
        }
    },
    {
        "company_name": "Nigerian Bottling Company",
        "industry": "Food & Beverage",
        "description": "Bottling partner of Coca-Cola offering SIWES placements in production engineering, automation and IT systems.",
        "address": "Asejire Plant, Ibadan",
        "website": "https://nbcplc.com",
        "state": "Oyo",
        "lga": "Egbeda",
        "contact": {
            "first": "HR",
            "last": "Office",
            "email": "info@nbcplc.com",
            "phone": ""
        }
    },
    {
        "company_name": "Flour Mills of Nigeria Plc",
        "industry": "Food Processing",
        "description": "Leading food processing company with opportunities in engineering, ICT, automation and quality control.",
        "address": "Apapa Wharf, Lagos",
        "website": "https://www.fmnplc.com",
        "state": "Lagos",
        "lga": "Apapa",
        "contact": {
            "first": "Talent",
            "last": "Team",
            "email": "info@fmnplc.com",
            "phone": ""
        }
    },
    {
        "company_name": "Dangote Sugar Refinery",
        "industry": "Food Processing",
        "description": "Sugar refining company offering industrial training in engineering, ICT and manufacturing processes.",
        "address": "Apapa, Lagos",
        "website": "https://www.dangote.com",
        "state": "Lagos",
        "lga": "Apapa",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "careers@dangote.com",
            "phone": ""
        }
    },
    {
        "company_name": "BUA Foods Plc",
        "industry": "Food Manufacturing",
        "description": "Food manufacturing company producing flour, pasta and sugar with SIWES opportunities in engineering and ICT.",
        "address": "Port Harcourt Road, Kano",
        "website": "https://www.buafoods.com",
        "state": "Kano",
        "lga": "Kano Municipal",
        "contact": {
            "first": "People",
            "last": "Operations",
            "email": "info@buafoods.com",
            "phone": ""
        }
    },
    {
        "company_name": "Honeywell Flour Mills",
        "industry": "Food Processing",
        "description": "Food manufacturing company providing industrial training in automation, engineering and information technology.",
        "address": "Apapa, Lagos",
        "website": "https://www.honeywellfoods.com",
        "state": "Lagos",
        "lga": "Apapa",
        "contact": {
            "first": "HR",
            "last": "Office",
            "email": "info@honeywellfoods.com",
            "phone": ""
        }
    },
    {
        "company_name": "Seven-Up Bottling Company",
        "industry": "Beverage Manufacturing",
        "description": "Leading beverage manufacturer offering SIWES opportunities in engineering, IT infrastructure and production.",
        "address": "Mobolaji Johnson Avenue, Lagos",
        "website": "https://www.sevenup.org",
        "state": "Lagos",
        "lga": "Oshodi-Isolo",
        "contact": {
            "first": "Human",
            "last": "Resources",
            "email": "careers@sevenup.org",
            "phone": ""
        }
    },
    {
        "company_name": "FrieslandCampina WAMCO",
        "industry": "Dairy Manufacturing",
        "description": "Dairy company producing Peak and Three Crowns milk with SIWES placements in engineering, quality assurance and ICT.",
        "address": "Ogba, Ikeja, Lagos",
        "website": "https://www.frieslandcampina.com",
        "state": "Lagos",
        "lga": "Ikeja",
        "contact": {
            "first": "HR",
            "last": "Team",
            "email": "info@frieslandcampina.com",
            "phone": ""
        }
    },
        {
        "company_name": "BUA Cement Plc",
        "industry": "Manufacturing",
        "description": "One of Africa’s largest cement producers offering SIWES opportunities in industrial automation, electrical engineering and plant operations.",
        "address": "Okpella Plant, Edo State",
        "website": "https://www.buacement.com",
        "state": "Edo",
        "lga": "Etsako East",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "info@buacement.com",
            "phone": ""
        }
    },
    {
        "company_name": "Lafarge Africa Plc",
        "industry": "Manufacturing",
        "description": "Building materials company providing industrial training in engineering, automation, ICT and production systems.",
        "address": "Ewekoro Plant, Ogun State",
        "website": "https://www.lafargeafrica.com",
        "state": "Ogun",
        "lga": "Ewekoro",
        "contact": {
            "first": "Human",
            "last": "Resources",
            "email": "info@lafarge.com",
            "phone": ""
        }
    },
    {
        "company_name": "Okomu Oil Palm Company",
        "industry": "Agriculture",
        "description": "Leading oil palm plantation company offering SIWES experience in agro-processing, engineering and environmental management.",
        "address": "Ovia South-West, Edo State",
        "website": "https://www.okomuoil.com",
        "state": "Edo",
        "lga": "Ovia South-West",
        "contact": {
            "first": "HR",
            "last": "Office",
            "email": "info@okomuoil.com",
            "phone": ""
        }
    },
    {
        "company_name": "Presco Plc",
        "industry": "Agriculture",
        "description": "Large agro-industrial company specializing in palm oil production and offering SIWES in engineering and processing systems.",
        "address": "Obaretin Estate, Edo State",
        "website": "https://www.presco-plc.com",
        "state": "Edo",
        "lga": "Ikpoba-Okha",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "info@presco-plc.com",
            "phone": ""
        }
    },
    {
        "company_name": "Seplat Energy",
        "industry": "Oil & Gas",
        "description": "Independent oil and gas company offering SIWES placements in engineering, data systems, automation and infrastructure.",
        "address": "Lagos & Delta Operations",
        "website": "https://www.seplatenergy.com",
        "state": "Lagos",
        "lga": "Eti-Osa",
        "contact": {
            "first": "Talent",
            "last": "Team",
            "email": "careers@seplatenergy.com",
            "phone": ""
        }
    },
    {
        "company_name": "Shell Nigeria",
        "industry": "Oil & Gas",
        "description": "Global energy company providing SIWES opportunities in engineering, software systems, data analytics and automation.",
        "address": "Shell Industrial Area, Port Harcourt",
        "website": "https://www.shell.com.ng",
        "state": "Rivers",
        "lga": "Port Harcourt",
        "contact": {
            "first": "HR",
            "last": "Team",
            "email": "careers@shell.com",
            "phone": ""
        }
    },
    {
        "company_name": "TotalEnergies Nigeria",
        "industry": "Oil & Gas",
        "description": "Energy company offering SIWES opportunities in engineering, ICT, operations and environmental systems.",
        "address": "Victoria Island, Lagos",
        "website": "https://totalenergies.ng",
        "state": "Lagos",
        "lga": "Eti-Osa",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "careers@totalenergies.com",
            "phone": ""
        }
    },
    {
        "company_name": "Chevron Nigeria",
        "industry": "Oil & Gas",
        "description": "Energy company offering SIWES placements in engineering, ICT systems and petroleum operations.",
        "address": "Lekki Peninsula, Lagos",
        "website": "https://www.chevron.com",
        "state": "Lagos",
        "lga": "Eti-Osa",
        "contact": {
            "first": "HR",
            "last": "Team",
            "email": "careers@chevron.com",
            "phone": ""
        }
    },
    {
        "company_name": "ExxonMobil Nigeria",
        "industry": "Oil & Gas",
        "description": "Oil company offering industrial training in engineering, data systems and automation.",
        "address": "Eket, Akwa Ibom",
        "website": "https://corporate.exxonmobil.com",
        "state": "Akwa Ibom",
        "lga": "Eket",
        "contact": {
            "first": "HR",
            "last": "Office",
            "email": "careers@exxonmobil.com",
            "phone": ""
        }
    },
    {
        "company_name": "Ardova Plc",
        "industry": "Energy",
        "description": "Energy and downstream petroleum company offering SIWES in logistics, ICT systems and engineering.",
        "address": "Victoria Island, Lagos",
        "website": "https://www.ardovaplc.com",
        "state": "Lagos",
        "lga": "Eti-Osa",
        "contact": {
            "first": "People",
            "last": "Operations",
            "email": "info@ardova.com",
            "phone": ""
        }
    },

    {
        "company_name": "Union Bank of Nigeria",
        "industry": "Banking",
        "description": "Commercial bank offering SIWES in fintech systems, software engineering and data analytics.",
        "address": "Adeola Odeku, Victoria Island, Lagos",
        "website": "https://www.unionbankng.com",
        "state": "Lagos",
        "lga": "Eti-Osa",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "careers@unionbankng.com",
            "phone": ""
        }
    },
    {
        "company_name": "Polaris Bank",
        "industry": "Banking",
        "description": "Digital-focused bank offering SIWES opportunities in IT systems, fintech and cybersecurity.",
        "address": "Lagos Island, Lagos",
        "website": "https://www.polarisbanklimited.com",
        "state": "Lagos",
        "lga": "Lagos Island",
        "contact": {
            "first": "HR",
            "last": "Team",
            "email": "careers@polarisbank.com",
            "phone": ""
        }
    },
    {
        "company_name": "Stanbic IBTC",
        "industry": "Banking",
        "description": "Financial services group offering SIWES in data engineering, fintech and IT systems.",
        "address": "Walter Carrington Crescent, Lagos",
        "website": "https://www.stanbicibtc.com",
        "state": "Lagos",
        "lga": "Lagos Island",
        "contact": {
            "first": "Talent",
            "last": "Acquisition",
            "email": "careers@stanbicibtc.com",
            "phone": ""
        }
    },
    {
        "company_name": "AIICO Insurance",
        "industry": "Insurance",
        "description": "Insurance company offering SIWES in actuarial science, data systems and fintech operations.",
        "address": "Victoria Island, Lagos",
        "website": "https://www.aiicoplc.com",
        "state": "Lagos",
        "lga": "Eti-Osa",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "careers@aiicoplc.com",
            "phone": ""
        }
    },
    {
        "company_name": "AXA Mansard",
        "industry": "Insurance",
        "description": "Insurance and financial services company offering SIWES in IT systems, data analytics and finance.",
        "address": "Victoria Island, Lagos",
        "website": "https://www.axamansard.com",
        "state": "Lagos",
        "lga": "Eti-Osa",
        "contact": {
            "first": "HR",
            "last": "Team",
            "email": "careers@axamansard.com",
            "phone": ""
        }
    },
    {
        "company_name": "Leadway Assurance",
        "industry": "Insurance",
        "description": "Insurance firm offering SIWES placements in ICT systems, underwriting and financial analytics.",
        "address": "Ikorodu Road, Lagos",
        "website": "https://www.leadway.com",
        "state": "Lagos",
        "lga": "Kosofe",
        "contact": {
            "first": "HR",
            "last": "Office",
            "email": "careers@leadway.com",
            "phone": ""
        }
    },

    {
        "company_name": "Eko Hotels & Suites",
        "industry": "Hospitality",
        "description": "Luxury hotel offering SIWES in IT systems, operations management and digital guest services.",
        "address": "Victoria Island, Lagos",
        "website": "https://www.ekohotels.com",
        "state": "Lagos",
        "lga": "Eti-Osa",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "info@ekohotels.com",
            "phone": ""
        }
    },
    {
        "company_name": "Transcorp Hilton Abuja",
        "industry": "Hospitality",
        "description": "Luxury hotel offering SIWES in IT infrastructure, hospitality systems and operations technology.",
        "address": "Abuja",
        "website": "https://www.hilton.com",
        "state": "Federal Capital Territory",
        "lga": "Abuja Municipal Area Council",
        "contact": {
            "first": "HR",
            "last": "Team",
            "email": "careers@hilton.com",
            "phone": ""
        }
    },
        {
        "company_name": "Nigerian Railway Corporation",
        "industry": "Transport",
        "description": "National rail operator offering SIWES opportunities in ICT systems, operations technology, signaling systems and engineering.",
        "address": "Ikeja, Lagos",
        "website": "https://nrc.gov.ng",
        "state": "Lagos",
        "lga": "Ikeja",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "info@nrc.gov.ng",
            "phone": ""
        }
    },
    {
        "company_name": "Federal Airports Authority of Nigeria (FAAN)",
        "industry": "Aviation",
        "description": "Manages airports in Nigeria and offers SIWES in ICT, aviation systems, engineering and security operations.",
        "address": "Murtala Muhammed Airport, Lagos",
        "website": "https://faan.gov.ng",
        "state": "Lagos",
        "lga": "Ikeja",
        "contact": {
            "first": "Corporate",
            "last": "Affairs",
            "email": "info@faan.gov.ng",
            "phone": ""
        }
    },
    {
        "company_name": "Nigerian Civil Aviation Authority (NCAA)",
        "industry": "Aviation Regulation",
        "description": "Regulatory body offering SIWES exposure in aviation safety systems, ICT, data analysis and compliance monitoring.",
        "address": "Abuja",
        "website": "https://ncaa.gov.ng",
        "state": "Federal Capital Territory",
        "lga": "Abuja Municipal Area Council",
        "contact": {
            "first": "HR",
            "last": "Unit",
            "email": "info@ncaa.gov.ng",
            "phone": ""
        }
    },
    {
        "company_name": "Nigerian Ports Authority",
        "industry": "Maritime & Logistics",
        "description": "Manages seaports and provides SIWES in logistics systems, ICT infrastructure and engineering operations.",
        "address": "Marina, Lagos",
        "website": "https://npa.gov.ng",
        "state": "Lagos",
        "lga": "Lagos Island",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "info@npa.gov.ng",
            "phone": ""
        }
    },
    {
        "company_name": "Nigerian Customs Service",
        "industry": "Government Agency",
        "description": "Federal agency offering SIWES in ICT systems, data analytics, border technology and logistics management.",
        "address": "Abuja",
        "website": "https://customs.gov.ng",
        "state": "Federal Capital Territory",
        "lga": "Abuja Municipal Area Council",
        "contact": {
            "first": "Public",
            "last": "Relations",
            "email": "info@customs.gov.ng",
            "phone": ""
        }
    },
    {
        "company_name": "National Information Technology Development Agency (NITDA)",
        "industry": "Government ICT",
        "description": "Federal ICT agency offering SIWES in software development, cybersecurity, policy and digital innovation.",
        "address": "Abuja",
        "website": "https://nitda.gov.ng",
        "state": "Federal Capital Territory",
        "lga": "Abuja Municipal Area Council",
        "contact": {
            "first": "IT",
            "last": "Department",
            "email": "info@nitda.gov.ng",
            "phone": ""
        }
    },
    {
        "company_name": "Galaxy Motors",
        "industry": "Automotive & Transport",
        "description": "Transport company offering SIWES in logistics systems, fleet management and IT operations.",
        "address": "Lagos",
        "website": "https://galaxymotors.ng",
        "state": "Lagos",
        "lga": "Ikeja",
        "contact": {
            "first": "HR",
            "last": "Team",
            "email": "info@galaxymotors.ng",
            "phone": ""
        }
    },
    {
        "company_name": "Dana Air",
        "industry": "Aviation",
        "description": "Airline company offering SIWES in aviation IT systems, customer platforms and operations management.",
        "address": "Ikeja, Lagos",
        "website": "https://flydanaair.com",
        "state": "Lagos",
        "lga": "Ikeja",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "careers@flydanaair.com",
            "phone": ""
        }
    },
    {
        "company_name": "Air Peace",
        "industry": "Aviation",
        "description": "Largest Nigerian airline offering SIWES in aviation systems, ICT, logistics and operations.",
        "address": "Ikeja, Lagos",
        "website": "https://airpeace.com",
        "state": "Lagos",
        "lga": "Ikeja",
        "contact": {
            "first": "Talent",
            "last": "Team",
            "email": "careers@airpeace.com",
            "phone": ""
        }
    },
    {
        "company_name": "Green Africa Airways",
        "industry": "Aviation",
        "description": "Low-cost airline offering SIWES in digital systems, IT infrastructure and aviation operations.",
        "address": "Lagos",
        "website": "https://greenafrica.com",
        "state": "Lagos",
        "lga": "Eti-Osa",
        "contact": {
            "first": "HR",
            "last": "Office",
            "email": "careers@greenafrica.com",
            "phone": ""
        }
    },

    {
        "company_name": "Shoprite Nigeria",
        "industry": "Retail",
        "description": "Retail supermarket chain offering SIWES in logistics systems, IT operations and supply chain technology.",
        "address": "Ikeja City Mall, Lagos",
        "website": "https://shoprite.com.ng",
        "state": "Lagos",
        "lga": "Ikeja",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "info@shoprite.com.ng",
            "phone": ""
        }
    },
    {
        "company_name": "Spar Nigeria",
        "industry": "Retail",
        "description": "Retail chain offering SIWES in business systems, inventory management and IT operations.",
        "address": "Lekki, Lagos",
        "website": "https://sparnigeria.com",
        "state": "Lagos",
        "lga": "Eti-Osa",
        "contact": {
            "first": "HR",
            "last": "Team",
            "email": "info@sparnigeria.com",
            "phone": ""
        }
    },

    {
        "company_name": "Lagos State Government ICT Office",
        "industry": "Government ICT",
        "description": "State ICT office offering SIWES in software development, e-government systems and data analytics.",
        "address": "Alausa, Ikeja",
        "website": "https://lagosstate.gov.ng",
        "state": "Lagos",
        "lga": "Ikeja",
        "contact": {
            "first": "ICT",
            "last": "Department",
            "email": "info@lagosstate.gov.ng",
            "phone": ""
        }
    },
    {
        "company_name": "Innoson Vehicle Manufacturing",
        "industry": "Automotive Manufacturing",
        "description": "Nigeria’s indigenous car manufacturer offering SIWES in robotics, engineering and industrial automation.",
        "address": "Nnewi, Anambra State",
        "website": "https://innosonvehicles.com",
        "state": "Anambra",
        "lga": "Nnewi North",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "info@innosonvehicles.com",
            "phone": ""
        }
    },

    {
        "company_name": "Notore Chemical Industries",
        "industry": "Chemical Manufacturing",
        "description": "Fertilizer and chemical company offering SIWES in industrial chemistry, engineering and production systems.",
        "address": "Onne, Rivers State",
        "website": "https://notore.com",
        "state": "Rivers",
        "lga": "Eleme",
        "contact": {
            "first": "HR",
            "last": "Office",
            "email": "info@notore.com",
            "phone": ""
        }
    },
    {
        "company_name": "Indorama Eleme Petrochemicals",
        "industry": "Petrochemicals",
        "description": "Petrochemical company offering SIWES in chemical engineering, industrial systems and automation.",
        "address": "Eleme, Rivers State",
        "website": "https://indoramafertilizers.com",
        "state": "Rivers",
        "lga": "Eleme",
        "contact": {
            "first": "HR",
            "last": "Team",
            "email": "info@indorama.com",
            "phone": ""
        }
    },

    {
        "company_name": "University of Lagos (UNILAG ICT Unit)",
        "industry": "Education & ICT",
        "description": "University ICT center offering SIWES in software development, networking, systems administration and cybersecurity.",
        "address": "Akoka, Lagos",
        "website": "https://unilag.edu.ng",
        "state": "Lagos",
        "lga": "Lagos Mainland",
        "contact": {
            "first": "ICT",
            "last": "Directorate",
            "email": "ict@unilag.edu.ng",
            "phone": ""
        }
    },
    {
        "company_name": "Kano State ICT Development Agency",
        "industry": "Government ICT",
        "description": "State ICT agency offering SIWES in software development, digital governance and IT infrastructure.",
        "address": "Kano",
        "website": "https://kano.gov.ng",
        "state": "Kano",
        "lga": "Kano Municipal",
        "contact": {
            "first": "ICT",
            "last": "Department",
            "email": "info@kano.gov.ng",
            "phone": ""
        }
    },
    {
        "company_name": "Dangote Fertilizer Limited",
        "industry": "Manufacturing",
        "description": "Large fertilizer plant offering SIWES in chemical engineering, industrial automation and production systems.",
        "address": "Lekki Free Zone, Lagos",
        "website": "https://dangote.com",
        "state": "Lagos",
        "lga": "Ibeju-Lekki",
        "contact": {
            "first": "HR",
            "last": "Department",
            "email": "careers@dangote.com",
            "phone": ""
        }
    }
]

def generate_password(company_name):
    # takes first word of company name + fixed suffix + 3 digit number
    first_word = company_name.split()[0].lower()
    number     = str(secrets.randbelow(900) + 100)  # 100-999
    return f"{first_word}@{number}"

class Command(BaseCommand):
    help = 'Seed 10 demo companies into the database'

    def handle(self, *args, **kwargs):
        created_count = 0
        skipped_count = 0

        for data in COMPANIES:
            # check if company already exists
            if CompanyProfile.objects.filter(company_name=data['company_name']).exists():
                self.stdout.write(f"  Skipped (exists): {data['company_name']}")
                skipped_count += 1
                continue

            # get state and LGA
            try:
                state = State.objects.get(name=data['state'])
            except State.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"  State not found: {data['state']} — skipping {data['company_name']}")
                )
                continue

            try:
                lga = LGA.objects.get(name=data['lga'], state=state)
            except LGA.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"  LGA not found: {data['lga']} — skipping {data['company_name']}")
                )
                continue

            # generate unique username
            base_username = data['company_name'].lower().replace(' ', '_')[:15]
            username      = base_username
            counter       = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            password = generate_password(data["company_name"])  
            # create user
            user = User.objects.create_user(
                username   = username,
                password   = password,
                email      = data['contact']['email'],
                first_name = data['contact']['first'],
                last_name  = data['contact']['last'],
                phone      = data['contact']['phone'],
                role       = 'company',
            )

            # create company profile — pre-verified
            CompanyProfile.objects.create(
                user         = user,
                company_name = data['company_name'],
                industry     = data['industry'],
                description  = data['description'],
                address      = data['address'],
                website      = data['website'],
                state        = state,
                lga          = lga,
                status       = 'verified',
                verified_at  = timezone.now(),
            )

            self.stdout.write(
                self.style.SUCCESS(f"  Created: {data['company_name']} — username: {username} - password: {password}")
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nDone. {created_count} companies created, {skipped_count} skipped.'
        ))