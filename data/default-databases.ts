import type { Database } from "@/types"

// Group databases by region/organization for better organization
export const defaultDatabases: Database[] = [
  // Australia
  {
    id: "tga-cmi",
    name: "TGA - Consumer Medicines Information",
    url: "https://www.tga.gov.au/products/australian-register-therapeutic-goods-artg/consumer-medicines-information-cmi",
    description: "Australian Register of Therapeutic Goods - Consumer Medicines Information",
  },
  {
    id: "tga-product-info",
    name: "TGA - Product Information",
    url: "https://www.tga.gov.au/products/australian-register-therapeutic-goods-artg/product-information",
    description: "Australian Register of Therapeutic Goods - Product Information",
  },
  {
    id: "tga-safety",
    name: "TGA - Safety",
    url: "https://www.tga.gov.au/safety",
    description: "Therapeutic Goods Administration Safety Information",
  },
  {
    id: "tga-safety-updates",
    name: "TGA - Safety Updates",
    url: "https://www.tga.gov.au/news/safety-updates",
    description: "Therapeutic Goods Administration Safety Updates",
  },
  {
    id: "tga-main",
    name: "TGA - Main Site",
    url: "https://www.tga.gov.au/",
    description: "Therapeutic Goods Administration Main Website",
  },
  {
    id: "tga-monitoring",
    name: "TGA - Monitoring Communications",
    url: "https://www.tga.gov.au/current-year-monitoring-communications",
    description: "TGA Current Year Monitoring Communications",
  },
  {
    id: "tga-alerts",
    name: "TGA - Alerts",
    url: "https://www.tga.gov.au/current-year-alerts",
    description: "TGA Current Year Alerts",
  },

  // Austria
  {
    id: "basg-register",
    name: "BASG - Medicine Register",
    url: "https://aspregister.basg.gv.at/aspregister/faces/aspregister.jspx",
    description: "Austrian Medicines and Medical Devices Agency Register",
  },
  {
    id: "basg-safety",
    name: "BASG - Safety Information",
    url: "https://www.basg.gv.at/gesundheitsberufe/sicherheitsinformationen-dhpc",
    description: "Austrian Safety Information for Healthcare Professionals",
  },
  {
    id: "basg-main",
    name: "BASG - Main Site",
    url: "https://www.basg.gv.at/en/",
    description: "Austrian Medicines and Medical Devices Agency Main Website",
  },
  {
    id: "basg-health",
    name: "BASG - Health Professionals",
    url: "https://www.basg.gv.at/gesundheitsberufe",
    description: "BASG Information for Health Professionals",
  },

  // Belgium
  {
    id: "famhp-news",
    name: "FAMHP - News",
    url: "https://www.famhp.be/en/news",
    description: "Belgian Federal Agency for Medicines and Health Products News",
  },
  {
    id: "belgium-medicines",
    name: "Belgium Medicines Database",
    url: "https://medicinesdatabase.be/human-use",
    description: "Belgian Medicines Database for Human Use",
  },
  {
    id: "famhp-main",
    name: "FAMHP - Main Site",
    url: "https://www.famhp.be/en",
    description: "Belgian Federal Agency for Medicines and Health Products Main Website",
  },

  // Canada
  {
    id: "canada-drug-db",
    name: "Health Canada - Drug Product Database",
    url: "https://www.canada.ca/en/health-canada/services/drugs-health-products/drug-products/drug-product-database.html",
    description: "Health Canada Drug Product Database",
  },
  {
    id: "canada-infowatch",
    name: "Health Canada - Health Product InfoWatch",
    url: "https://www.canada.ca/en/health-canada/services/drugs-health-products/medeffect-canada/health-product-infowatch.html",
    description: "Health Canada MedEffect Product InfoWatch",
  },
  {
    id: "health-canada",
    name: "Health Canada - Main Site",
    url: "https://www.canada.ca/en/health-canada.html",
    description: "Health Canada Main Website",
  },
  {
    id: "canada-newsletters",
    name: "Health Canada - Published Newsletters",
    url: "https://www.canada.ca/en/health-canada/services/drugs-health-products/medeffect-canada/health-product-infowatch/published-newsletters.html",
    description: "Health Canada Published Health Product InfoWatch Newsletters",
  },
  {
    id: "canada-recalls",
    name: "Health Canada - Recalls and Safety Alerts",
    url: "https://recalls-rappels.canada.ca/en/search/site?f[0]=category:180",
    description: "Health Canada Recalls and Safety Alerts Database",
  },

  // Denmark
  {
    id: "denmark-safety",
    name: "Danish Medicines Agency - Safety Information",
    url: "https://laegemiddelstyrelsen.dk/da/bivirkninger/direkte-sikkerhedsinformation/udsendte-meddelelser/",
    description: "Danish Medicines Agency Direct Safety Information",
  },
  {
    id: "denmark-main",
    name: "Danish Medicines Agency - Main Site",
    url: "https://laegemiddelstyrelsen.dk/en/",
    description: "Danish Medicines Agency Main Website",
  },

  // European Union
  {
    id: "ema-medicines",
    name: "EMA - Medicines Database",
    url: "https://www.ema.europa.eu/en/medicines",
    description: "European Medicines Agency Medicines Database",
  },
  {
    id: "ema-dhpc",
    name: "EMA - Direct Healthcare Professional Communications",
    url: "https://www.ema.europa.eu/en/human-regulatory/post-authorisation/pharmacovigilance/direct-healthcare-professional-communications",
    description: "EMA Direct Healthcare Professional Communications",
  },
  {
    id: "ema-main",
    name: "EMA - Main Site",
    url: "https://www.ema.europa.eu/en/homepage",
    description: "European Medicines Agency Main Website",
  },
  {
    id: "ema-signals",
    name: "EMA - PRAC Safety Signals",
    url: "https://www.ema.europa.eu/en/human-regulatory/post-authorisation/pharmacovigilance/signal-management/prac-recommendations-safety-signals#prac-recommendations-on-safety-signals:-monthly-overviews-section",
    description: "EMA PRAC Recommendations on Safety Signals",
  },
  {
    id: "ema-alt",
    name: "EMA - Alternative Site",
    url: "http://www.ema.europa.eu/ema/",
    description: "European Medicines Agency Alternative Website",
  },
  {
    id: "ema-dhcp-search",
    name: "EMA - DHCP Search",
    url: "https://www.ema.europa.eu/en/medicines?search_api_views_fulltext=DHCP",
    description: "EMA Search for Direct Healthcare Professional Communications",
  },
  {
    id: "ema-risk-search",
    name: "EMA - Additive Risk Search",
    url: "https://www.ema.europa.eu/en/medicines?search_api_views_fulltext=additive+Risk",
    description: "EMA Search for Additive Risk Information",
  },

  // Finland
  {
    id: "fimea-web",
    name: "Fimea - Web Database",
    url: "https://fimea.fi/en/databases_and_registers/fimeaweb",
    description: "Finnish Medicines Agency Web Database",
  },
  {
    id: "fimea-safety-mkt",
    name: "Fimea - Marketing Authorization Holder Bulletins",
    url: "https://fimea.fi/ajankohtaista/laaketurvatiedotteet/myyntiluvanhaltijoiden_tiedotteet",
    description: "Finnish Medicines Agency Marketing Authorization Holder Safety Bulletins",
  },
  {
    id: "fimea-safety",
    name: "Fimea - Safety Bulletins",
    url: "https://fimea.fi/ajankohtaista/laaketurvallisuustiedotteet",
    description: "Finnish Medicines Agency Safety Bulletins",
  },
  {
    id: "fimea-main",
    name: "Fimea - Main Site",
    url: "https://fimea.fi/en/frontpage",
    description: "Finnish Medicines Agency Main Website",
  },

  // France
  {
    id: "france-medicines",
    name: "France - Public Medicines Database",
    url: "https://base-donnees-publique.medicaments.gouv.fr/",
    description: "French Public Medicines Database",
  },
  {
    id: "ansm-main",
    name: "ANSM - Main Site",
    url: "https://ansm.sante.fr/",
    description: "French National Agency for Medicines and Health Products Safety",
  },
  {
    id: "ansm-alt",
    name: "ANSM - Alternative Site",
    url: "http://www.ansm.sante.fr/",
    description: "ANSM Alternative Website",
  },

  // Germany
  {
    id: "germany-drug-info",
    name: "Germany - Drug Information System",
    url: "https://www.pharmnet-bund.de/PharmNet/EN/Public/Drug-information-system/_node.html",
    description: "German Drug Information System",
  },
  {
    id: "bfarm-risk",
    name: "BfArM - Risk Information",
    url: "https://www.bfarm.de/EN/Medicinal-products/Pharmacovigilance/Risk-information/Rote-Hand-Briefe-and-Information-Letters/_node.html",
    description: "German Federal Institute for Drugs and Medical Devices Risk Information",
  },
  {
    id: "bfarm-risk-search",
    name: "BfArM - Risk Information Search",
    url: "https://www.bfarm.de/EN/Medicinal-products/Pharmacovigilance/Risk-information/SucheRisikoinfos/_node.html",
    description: "German Federal Institute for Drugs and Medical Devices Risk Information Search",
  },
  {
    id: "bfarm-main",
    name: "BfArM - Main Site",
    url: "https://www.bfarm.de/EN/Home/_node.html",
    description: "German Federal Institute for Drugs and Medical Devices Main Website",
  },

  // Iceland
  {
    id: "iceland-medicines",
    name: "Iceland - Medicines Register",
    url: "https://www.serlyfjaskra.is/",
    description: "Icelandic Medicines Register",
  },
  {
    id: "iceland-dhpc",
    name: "Iceland - DHPC Letters",
    url: "http://www.lyfjastofnun.is/lyf/lyfjagat/bref-til-heilbrigdisstarfsmanna-dhpc/",
    description: "Icelandic Medicines Agency DHPC Letters",
  },
  {
    id: "iceland-ima",
    name: "Iceland - Medical Association",
    url: "https://www.ima.is/",
    description: "Icelandic Medical Association",
  },

  // Ireland
  {
    id: "hpra-medicines",
    name: "HPRA - Medicines",
    url: "https://www.hpra.ie/homepage/medicines",
    description: "Health Products Regulatory Authority Medicines Information",
  },
  {
    id: "hpra-safety",
    name: "HPRA - Safety Notices",
    url: "https://www.hpra.ie/homepage/medicines/safety-notices",
    description: "Health Products Regulatory Authority Safety Notices",
  },
  {
    id: "hpra-newsletters",
    name: "HPRA - Newsletters",
    url: "http://www.hpra.ie/homepage/about-us/publications-forms/newsletters",
    description: "Health Products Regulatory Authority Newsletters",
  },
  {
    id: "hpra-main",
    name: "HPRA - Main Site",
    url: "https://www.hpra.ie/",
    description: "Health Products Regulatory Authority Main Website",
  },

  // Italy
  {
    id: "italy-medicines",
    name: "AIFA - Medicines Database",
    url: "https://medicinali.aifa.gov.it/it/#/it/",
    description: "Italian Medicines Agency Medicines Database",
  },
  {
    id: "aifa-safety",
    name: "AIFA - Drug Safety",
    url: "https://www.aifa.gov.it/sicurezza-dei-farmaci",
    description: "Italian Medicines Agency Drug Safety Information",
  },
  {
    id: "aifa-main",
    name: "AIFA - Main Site",
    url: "https://www.aifa.gov.it/en/",
    description: "Italian Medicines Agency Main Website",
  },

  // Japan
  {
    id: "pmda-search",
    name: "PMDA - Medicine Search",
    url: "https://www.pmda.go.jp/PmdaSearch/iyakuSearch/",
    description: "Japanese Pharmaceuticals and Medical Devices Agency Medicine Search",
  },
  {
    id: "pmda-english-search",
    name: "PMDA - English Search",
    url: "https://www.pmda.go.jp/english/search_index.html",
    description: "PMDA English Search Index",
  },
  {
    id: "pmda-precautions",
    name: "PMDA - Revision of Precautions",
    url: "https://www.pmda.go.jp/english/safety/info-services/drugs/revision-of-precautions/0001.html",
    description: "PMDA Revision of Precautions for Drugs",
  },
  {
    id: "pmda-mhlw",
    name: "PMDA - MHLW Released Information",
    url: "https://www.pmda.go.jp/english/safety/info-services/drugs/mhlw-released/0001.html",
    description: "PMDA MHLW Released Safety Information",
  },
  {
    id: "pmda-safety",
    name: "PMDA - Safety Information",
    url: "https://www.pmda.go.jp/english/safety/info-services/safety-information/0001.html",
    description: "PMDA Safety Information",
  },
  {
    id: "pmda-main",
    name: "PMDA - Main Site",
    url: "https://www.pmda.go.jp/english/",
    description: "Japanese Pharmaceuticals and Medical Devices Agency Main Website",
  },
  {
    id: "pmda-safety-alt",
    name: "PMDA - Safety Information Alternative",
    url: "http://www.pmda.go.jp/english/safety/info-services/safety-information/0001.html",
    description: "PMDA Safety Information Alternative Link",
  },
  {
    id: "pmda-mhlw-search",
    name: "PMDA - MHLW Search",
    url: "https://ss.pmda.go.jp/en_all/search.x?nccharset=77538246&nccharset=FEF28A70&q=MHLW&ie=UTF-8&page=1",
    description: "PMDA MHLW Search",
  },

  // Luxembourg
  {
    id: "luxembourg-medicines",
    name: "Luxembourg - Medicines List",
    url: "https://cns.public.lu/en/legislations/textes-coordonnes/liste-med-comm.html",
    description: "Luxembourg Medicines List",
  },
  {
    id: "luxembourg-dhcp",
    name: "Luxembourg - DHCP Letters",
    url: "https://sante.public.lu/fr/espace-professionnel/domaines/pharmacies-et-medicaments/pharmacovigilance/gestion-risques/dhcp.html",
    description: "Luxembourg DHCP Letters",
  },
  {
    id: "luxembourg-main",
    name: "Luxembourg - CNS Main Site",
    url: "https://cns.public.lu/en.html",
    description: "Luxembourg National Health Fund Main Website",
  },
  {
    id: "luxembourg-almps",
    name: "Luxembourg - ALMPS News",
    url: "https://www.iml.lu/en/news/luxembourg-agency-medicines-and-health-products-almps",
    description: "Luxembourg Agency for Medicines and Health Products News",
  },
  {
    id: "luxembourg-dhcp-alt",
    name: "Luxembourg - DHCP Alternative",
    url: "https://santesecu.public.lu/fr/espace-professionnel/domaines/pharmacies-et-medicaments/pharmacovigilance/gestion-riques/dhcp.html",
    description: "Luxembourg DHCP Letters Alternative Link",
  },

  // Netherlands
  {
    id: "netherlands-medicines-en",
    name: "Netherlands - Medicines Database (EN)",
    url: "https://www.geneesmiddeleninformatiebank.nl/ords/f?p=111:1:0::NO:1:P0_DOMAIN,P0_LANG:H,EN",
    description: "Dutch Medicines Information Bank (English)",
  },
  {
    id: "netherlands-medicines-nl",
    name: "Netherlands - Medicines Database (NL)",
    url: "https://www.geneesmiddeleninformatiebank.nl/ords/f?p=111:1:0::NO:1:P0_DOMAIN,P0_LANG:H,NL",
    description: "Dutch Medicines Information Bank (Dutch)",
  },
  {
    id: "cbg-safety",
    name: "CBG - Safety News",
    url: "https://www.cbg-meb.nl/onderwerpen/medicijninformatie-nieuws-over-veiligheid-van-medicijnen",
    description: "Dutch Medicines Evaluation Board Safety News",
  },
  {
    id: "cbg-main",
    name: "CBG - Main Site",
    url: "https://english.cbg-meb.nl/",
    description: "Dutch Medicines Evaluation Board Main Website",
  },
  {
    id: "cbg-marketing",
    name: "CBG - Marketing Authorization",
    url: "https://english.cbg-meb.nl/sections/marketing-authorisation-medicines-for-human-use",
    description: "CBG Marketing Authorization for Medicines for Human Use",
  },

  // New Zealand
  {
    id: "medsafe-search",
    name: "Medsafe - Medicine Search",
    url: "https://www.medsafe.govt.nz/Medicines/infoSearch.asp",
    description: "New Zealand Medicines and Medical Devices Safety Authority Search",
  },
  {
    id: "medsafe-db",
    name: "Medsafe - Database Search",
    url: "https://www.medsafe.govt.nz/regulatory/dbsearch.asp",
    description: "Medsafe Database Search",
  },
  {
    id: "medsafe-dhcp",
    name: "Medsafe - DHCP Letters",
    url: "https://www.medsafe.govt.nz/safety/DHCPLetters.asp",
    description: "Medsafe DHCP Letters",
  },
  {
    id: "medsafe-prescriber",
    name: "Medsafe - Prescriber Update",
    url: "https://www.medsafe.govt.nz/publications/prescriber-update.asp",
    description: "Medsafe Prescriber Update",
  },
  {
    id: "medsafe-safety",
    name: "Medsafe - Safety Communications",
    url: "https://www.medsafe.govt.nz/safety/SafetyCommunications.asp",
    description: "Medsafe Safety Communications",
  },
  {
    id: "medsafe-main",
    name: "Medsafe - Main Site",
    url: "https://www.medsafe.govt.nz/",
    description: "New Zealand Medicines and Medical Devices Safety Authority Main Website",
  },
  {
    id: "medsafe-media",
    name: "Medsafe - Media",
    url: "http://www.medsafe.govt.nz/hot/MediaContents.asp",
    description: "Medsafe Media Contents",
  },
  {
    id: "medsafe-articles",
    name: "Medsafe - Articles",
    url: "https://www.medsafe.govt.nz/profs/PUArticles.asp",
    description: "Medsafe Prescriber Update Articles",
  },

  // Norway
  {
    id: "norway-medicines",
    name: "Norway - Medicine Search",
    url: "http://www.legemiddelsok.no/",
    description: "Norwegian Medicines Search",
  },
  {
    id: "norway-dhcp",
    name: "Norway - DHCP Letters",
    url: "https://www.dmp.no/bivirkninger-og-sikkerhet/tiltak-for-a-forebygge-bivirkninger/sikkerhetsinformasjon-til-helsepersonell-og-pasient/kjere-helsepersonell-brev",
    description: "Norwegian Medicines Agency DHCP Letters",
  },
  {
    id: "norway-main",
    name: "Norway - DMP Main Site",
    url: "https://www.dmp.no/",
    description: "Norwegian Medicines Agency Main Website",
  },
  {
    id: "norway-english",
    name: "Norway - DMP English Site",
    url: "https://www.dmp.no/en",
    description: "Norwegian Medicines Agency English Website",
  },

  // Portugal
  {
    id: "infarmed-main",
    name: "INFARMED - Main Site",
    url: "https://www.infarmed.pt/",
    description: "Portuguese National Authority of Medicines and Health Products Main Website",
  },
  {
    id: "infarmed-circulars",
    name: "INFARMED - Circulars",
    url: "https://www.infarmed.pt/web/infarmed/circulares?p_p_id=paginasagregadoras_WAR_paginasagregadorasportlet&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_pos=1&p_p_col_count=2&_paginasagregadoras_WAR_paginasagregadorasportlet_javax.portlet.action=advanceSearch&_paginasagregadoras_WAR_paginasagregadorasportlet_selectedOrderBy=default",
    description: "INFARMED Circulars",
  },
  {
    id: "infarmed-circulars-alt",
    name: "INFARMED - Circulars Alternative",
    url: "https://www.infarmed.pt/web/infarmed/circulares",
    description: "INFARMED Circulars Alternative Link",
  },

  // Singapore
  {
    id: "singapore-products",
    name: "Singapore - Product Search",
    url: "https://eservice.hsa.gov.sg/prism/common/enquirepublic/SearchDRBProduct.do?action=load&_ga=2.183810082.563179921.1554083187-551332391.1551944793",
    description: "Singapore Health Sciences Authority Product Search",
  },
  {
    id: "hsa-announcements",
    name: "HSA - Announcements",
    url: "https://www.hsa.gov.sg/announcements",
    description: "Singapore Health Sciences Authority Announcements",
  },
  {
    id: "hsa-main",
    name: "HSA - Main Site",
    url: "https://www.hsa.gov.sg/",
    description: "Singapore Health Sciences Authority Main Website",
  },
  {
    id: "hsa-press",
    name: "HSA - Press Releases",
    url: "https://www.hsa.gov.sg/announcements?contenttype=press%20releases",
    description: "HSA Press Releases",
  },

  // South Korea
  {
    id: "korea-health",
    name: "Korea - Health Portal",
    url: "https://www.health.kr/",
    description: "Korean Health Portal",
  },
  {
    id: "korea-safety",
    name: "Korea - Safety Notices",
    url: "https://www.health.kr/notice/safety.asp",
    description: "Korean Health Portal Safety Notices",
  },
  {
    id: "mfds-main",
    name: "MFDS - Main Site",
    url: "https://www.mfds.go.kr/eng/index.do",
    description: "Korean Ministry of Food and Drug Safety Main Website",
  },
  {
    id: "korea-nedrug",
    name: "Korea - NEDRUG",
    url: "https://nedrug.mfds.go.kr/CCBAR01F012/getList",
    description: "Korean NEDRUG Database",
  },

  // Spain
  {
    id: "spain-medicines",
    name: "Spain - Medicines Database",
    url: "https://cima.aemps.es/cima/publico/home.html",
    description: "Spanish Medicines Database",
  },
  {
    id: "aemps-dhcp",
    name: "AEMPS - DHCP Letters",
    url: "https://www.aemps.gob.es/medicamentos-de-uso-humano/farmacovigilancia-de-medicamentos-de-uso-humano/cartas_segprofsani/?lang=en",
    description: "Spanish Agency of Medicines and Medical Devices DHCP Letters",
  },
  {
    id: "aemps-safety",
    name: "AEMPS - Safety Communications",
    url: "https://www.aemps.gob.es/medicamentos-de-uso-humano/farmacovigilancia-de-medicamentos-de-uso-humano/?lang=en#comunicaSegPrevRiesgo",
    description: "AEMPS Safety Communications",
  },
  {
    id: "aemps-main",
    name: "AEMPS - Main Site",
    url: "https://www.aemps.gob.es/?lang=en",
    description: "Spanish Agency of Medicines and Medical Devices Main Website",
  },
  {
    id: "aemps-harmonisation",
    name: "AEMPS - Harmonisation Procedure",
    url: "https://www.aemps.gob.es/informa-en/the-spanish-agency-of-medicines-and-medical-devices-aemps-recommends-using-voluntary-harmonisation-procedure-before-the-official-submission-of-a-multi-state-ct-application/?lang=en",
    description: "AEMPS Harmonisation Procedure Information",
  },

  // Sweden
  {
    id: "sweden-medicines",
    name: "Sweden - Medicines Search",
    url: "https://www.lakemedelsverket.se/sv/sok-lakemedelsfakta?activeTab=1",
    description: "Swedish Medicines Search",
  },
  {
    id: "sweden-safety",
    name: "Sweden - Safety News",
    url: "https://www.lakemedelsverket.se/sv/nyheter?c=225&c=76&p=2",
    description: "Swedish Medical Products Agency Safety News",
  },
  {
    id: "sweden-news",
    name: "Sweden - News",
    url: "https://www.lakemedelsverket.se/sv/nyheter?p=2",
    description: "Swedish Medical Products Agency News",
  },
  {
    id: "sweden-main",
    name: "Sweden - Main Site",
    url: "https://www.lakemedelsverket.se/sv",
    description: "Swedish Medical Products Agency Main Website",
  },
  {
    id: "sweden-main-alt",
    name: "Sweden - Main Site Alternative",
    url: "https://www.lakemedelsverket.se/sv",
    description: "Swedish Medical Products Agency Main Website Alternative Link",
  },

  // Switzerland
  {
    id: "swiss-medicines",
    name: "Switzerland - Medicines Info",
    url: "https://www.swissmedicinfo.ch/?Lang=EN",
    description: "Swiss Medicines Information",
  },
  {
    id: "swissmedic-hpc",
    name: "Swissmedic - HPC",
    url: "https://www.swissmedic.ch/swissmedic/en/home/humanarzneimittel/markt-surveillance/health-professional-communication--hpc-.html",
    description: "Swissmedic Health Professional Communication",
  },
  {
    id: "swissmedic-updates",
    name: "Swissmedic - Updates",
    url: "https://www.swissmedic.ch/swissmedic/en/home/news/updates.html",
    description: "Swissmedic Updates",
  },
  {
    id: "swissmedic-main",
    name: "Swissmedic - Main Site",
    url: "https://www.swissmedic.ch/swissmedic/en/home.html",
    description: "Swiss Agency for Therapeutic Products Main Website",
  },
  {
    id: "swissmedic-hpc-alt",
    name: "Swissmedic - HPC Alternative",
    url: "https://www.swissmedic.ch/swissmedic/en/home/humanarzneimittel/market-surveillance/health-professional-communication--hpc-.html",
    description: "Swissmedic Health Professional Communication Alternative Link",
  },

  // United Kingdom
  {
    id: "uk-products",
    name: "UK - Products Database",
    url: "http://products.mhra.gov.uk/",
    description: "UK Medicines and Healthcare products Regulatory Agency Products Database",
  },
  {
    id: "mhra-dsu",
    name: "MHRA - Drug Safety Update",
    url: "https://www.gov.uk/government/publications/drug-safety-update-monthly-newsletter",
    description: "MHRA Drug Safety Update Monthly Newsletter",
  },
  {
    id: "mhra-alerts",
    name: "MHRA - Drug Device Alerts",
    url: "https://www.gov.uk/drug-device-alerts",
    description: "MHRA Drug Device Alerts",
  },
  {
    id: "mhra-main",
    name: "MHRA - Main Site",
    url: "https://www.gov.uk/government/organisations/medicines-and-healthcare-products-regulatory-agency",
    description: "UK Medicines and Healthcare products Regulatory Agency Main Website",
  },
  {
    id: "mhra-dsu-alt",
    name: "MHRA - Drug Safety Update Alternative",
    url: "https://www.gov.uk/drug-safety-update",
    description: "MHRA Drug Safety Update Alternative Link",
  },

  // United States
  {
    id: "fda-drugs",
    name: "FDA - Drugs@FDA",
    url: "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm",
    description: "US Food and Drug Administration Drugs Database",
  },
  {
    id: "fda-main",
    name: "FDA - Main Site",
    url: "https://www.fda.gov/",
    description: "US Food and Drug Administration Main Website",
  },
  {
    id: "fda-press",
    name: "FDA - Press Announcements",
    url: "https://www.fda.gov/NewsEvents/Newsroom/PressAnnouncements/default.htm?Page=1",
    description: "FDA Press Announcements",
  },
  {
    id: "fda-drug-safety",
    name: "FDA - Drug Safety",
    url: "https://www.fda.gov/Drugs/DrugSafety/ucm199082.htm",
    description: "FDA Drug Safety Information",
  },
  {
    id: "fda-podcasts",
    name: "FDA - Drug Safety Podcasts",
    url: "https://www.fda.gov/Drugs/DrugSafety/DrugSafetyPodcasts/default.htm",
    description: "FDA Drug Safety Podcasts",
  },
  {
    id: "fda-faers",
    name: "FDA - FAERS Signals",
    url: "https://www.fda.gov/drugs/questions-and-answers-fdas-adverse-event-reporting-system-faers/january-march-2024-potential-signals-serious-risksnew-safety-information-identified-fda-adverse",
    description: "FDA Adverse Event Reporting System Signals",
  },
  {
    id: "fda-recalls",
    name: "FDA - Drug Recalls",
    url: "https://www.fda.gov/Drugs/DrugSafety/DrugRecalls/default.htm",
    description: "FDA Drug Recalls",
  },

  // Saudi Arabia
  {
    id: "sfda-warnings",
    name: "SFDA - Warnings",
    url: "https://www.sfda.gov.sa/en/warnings?tags=All",
    description: "Saudi Food and Drug Authority Warnings",
  },
  {
    id: "sfda-rmm",
    name: "SFDA - Risk Minimization Measures",
    url: "https://www.sfda.gov.sa/en/RMM",
    description: "SFDA Risk Minimization Measures",
  },
  {
    id: "sfda-safety",
    name: "SFDA - Drug Safety Labeling",
    url: "https://www.sfda.gov.sa/en/drugs-safety-labeling",
    description: "SFDA Drug Safety Labeling",
  },

  // South Africa
  {
    id: "sahpra-safety",
    name: "SAHPRA - Safety Updates",
    url: "https://www.sahpra.org.za/safety-information-and-updates/",
    description: "South African Health Products Regulatory Authority Safety Updates",
  },

  // Egypt
  {
    id: "eda-safety",
    name: "EDA - Pharmacovigilance",
    url: "https://www.edaegypt.gov.eg/ar/إصدارات-الهيئة/نشرات-اليقظة-الدوائية/",
    description: "Egyptian Drug Authority Pharmacovigilance Bulletins",
  },

  // WHO and International
  {
    id: "who-emh",
    name: "WHO - Eastern Mediterranean Health Journal",
    url: "http://www.emro.who.int/emh-journal/eastern-mediterranean-health-journal/about-the-journal.html",
    description: "WHO Eastern Mediterranean Health Journal",
  },
  {
    id: "who-pharmacovigilance",
    name: "WHO - Pharmacovigilance",
    url: "https://www.who.int/teams/regulation-prequalification/regulation-and-safety/pharmacovigilance/guidance/reports-and-newsletters",
    description: "WHO Pharmacovigilance Reports and Newsletters",
  },
  {
    id: "who-iris",
    name: "WHO - IRIS",
    url: "https://iris.who.int/handle/10665/26722",
    description: "WHO Institutional Repository for Information Sharing",
  },

  // Medical Journals
  {
    id: "arab-gastro",
    name: "Arab Journal of Gastroenterology",
    url: "http://www.sciencedirect.com/journal/arab-journal-of-gastroenterology",
    description: "Arab Journal of Gastroenterology",
  },
  {
    id: "tehj",
    name: "Tropical and Endemic Health Journal",
    url: "https://tehj.springeropen.com/",
    description: "Tropical and Endemic Health Journal",
  },
  {
    id: "ejms",
    name: "Egyptian Journal of Medical Sciences",
    url: "http://www.ejmsonline.org/",
    description: "Egyptian Journal of Medical Sciences",
  },
  {
    id: "ejnpn",
    name: "The Egyptian Journal of Neurology, Psychiatry and Neurosurgery",
    url: "https://ejnpn.springeropen.com/",
    description: "The Egyptian Journal of Neurology, Psychiatry and Neurosurgery",
  },
  {
    id: "epj",
    name: "The Egyptian Pharmaceutical Journal",
    url: "http://www.epj.eg.net/",
    description: "The Egyptian Pharmaceutical Journal",
  },
  {
    id: "eglj",
    name: "Egyptian Liver Journal",
    url: "https://eglj.springeropen.com/",
    description: "Egyptian Liver Journal",
  },
  {
    id: "egyptian-rheumatologist",
    name: "The Egyptian Rheumatologist",
    url: "https://www.journals.elsevier.com/the-egyptian-rheumatologist",
    description: "The Egyptian Rheumatologist",
  },
  {
    id: "ebwhj",
    name: "Evidence-Based Women's Health Journal",
    url: "https://ebwhj.journals.ekb.eg/issue_22830_27658_.html",
    description: "Evidence-Based Women's Health Journal",
  },
  {
    id: "jp",
    name: "Journal of Pregnancy",
    url: "https://www.hindawi.com/journals/jp/",
    description: "Journal of Pregnancy",
  },
  {
    id: "jesp",
    name: "Journal of the Egyptian Society of Parasitology",
    url: "https://jesp.journals.ekb.eg/",
    description: "Journal of the Egyptian Society of Parasitology",
  },
  {
    id: "ejode",
    name: "Egyptian Journal of Diabetes and Obesity",
    url: "http://www.ejode.eg.net/currentissue.asp?sabs=n",
    description: "Egyptian Journal of Diabetes and Obesity",
  },
  {
    id: "jeos",
    name: "Journal of the Egyptian Ophthalmological Society",
    url: "http://www.jeos.eg.net/",
    description: "Journal of the Egyptian Ophthalmological Society",
  },
  {
    id: "jepha",
    name: "Journal of the Egyptian Public Health Association",
    url: "https://jepha.springeropen.com/",
    description: "Journal of the Egyptian Public Health Association",
  },
  {
    id: "afju",
    name: "African Journal of Urology",
    url: "https://afju.springeropen.com/",
    description: "African Journal of Urology",
  },
  {
    id: "azmj",
    name: "Al-Azhar Medical Journal",
    url: "https://www.azmj.eg.net/",
    description: "Al-Azhar Medical Journal",
  },
  {
    id: "ejpsy",
    name: "Egyptian Journal of Psychiatry",
    url: "http://new.ejpsy.eg.net/",
    description: "Egyptian Journal of Psychiatry",
  },
  {
    id: "imr",
    name: "International Medical Research",
    url: "https://journals.sagepub.com/toc/imr/current",
    description: "International Medical Research",
  },
  {
    id: "medsci",
    name: "Medical Sciences",
    url: "http://www.medsci.org/",
    description: "Medical Sciences",
  },
  {
    id: "acta-paediatrica",
    name: "Acta Paediatrica",
    url: "https://onlinelibrary.wiley.com/journal/16512227",
    description: "Acta Paediatrica",
  },
  {
    id: "ejdv",
    name: "Egyptian Journal of Dermatology and Venereology",
    url: "https://www.ejdv.eg.net/",
    description: "Egyptian Journal of Dermatology and Venereology",
  },
  {
    id: "nejm",
    name: "New England Journal of Medicine",
    url: "https://www.nejm.org/toc/nejm/medical-journal",
    description: "New England Journal of Medicine",
  },
  {
    id: "amjmed",
    name: "The American Journal of Medicine",
    url: "https://www.amjmed.com/current",
    description: "The American Journal of Medicine",
  },
  {
    id: "eglj-articles",
    name: "Egyptian Liver Journal Articles",
    url: "https://eglj.springeropen.com/articles",
    description: "Egyptian Liver Journal Articles",
  },

  // PubMed
  {
    id: "pubmed",
    name: "PubMed Advanced Search",
    url: "https://pubmed.ncbi.nlm.nih.gov/advanced/",
    description: "PubMed Advanced Search Interface",
  },
]
