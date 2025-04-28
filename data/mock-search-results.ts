import type { SearchResult } from "@/types"

export const mockSearchResults: SearchResult[] = [
  {
    id: "1",
    title: "Methotrexate in the Treatment of Rheumatoid Arthritis: A Systematic Review",
    url: "https://pubmed.ncbi.nlm.nih.gov/example1",
    source: "PubMed",
    date: "2023-11-15",
    snippet:
      "This systematic review evaluates the efficacy and safety of methotrexate in the treatment of rheumatoid arthritis. The review includes 24 randomized controlled trials with a total of 3,874 participants.",
    authors: ["Johnson, A.", "Smith, B.", "Williams, C."],
  },
  {
    id: "2",
    title: "Pharmacokinetics of Methotrexate in Pediatric Patients",
    url: "https://go.drugbank.com/example2",
    source: "DrugBank",
    date: "2023-09-22",
    snippet:
      "This study examines the pharmacokinetics of methotrexate in pediatric patients with acute lymphoblastic leukemia. The results indicate significant variability in drug metabolism based on age and genetic factors.",
    authors: ["Chen, D.", "Garcia, E."],
  },
  {
    id: "3",
    title: "Comparative Study of Methotrexate and Biologics in Psoriatic Arthritis",
    url: "https://clinicaltrials.gov/example3",
    source: "ClinicalTrials.gov",
    date: "2023-12-05",
    snippet:
      "A randomized controlled trial comparing the efficacy of methotrexate versus biologic agents in the treatment of psoriatic arthritis. The primary outcome measure is the ACR20 response at 24 weeks.",
    authors: ["Brown, F.", "Miller, G.", "Davis, H.", "Wilson, J."],
  },
  {
    id: "4",
    title: "Long-term Safety of Low-dose Methotrexate in Rheumatoid Arthritis",
    url: "https://pubmed.ncbi.nlm.nih.gov/example4",
    source: "PubMed",
    date: "2023-10-18",
    snippet:
      "This 10-year observational study evaluates the long-term safety profile of low-dose methotrexate in patients with rheumatoid arthritis. The study found that the risk of serious adverse events was low when appropriate monitoring protocols were followed.",
    authors: ["Thompson, K.", "Roberts, L."],
  },
  {
    id: "5",
    title: "Methotrexate Drug Interactions: A Comprehensive Review",
    url: "https://go.drugbank.com/example5",
    source: "DrugBank",
    date: "2023-08-30",
    snippet:
      "This review article provides a comprehensive analysis of potential drug interactions with methotrexate. The article highlights clinically significant interactions and provides recommendations for managing concomitant medications.",
    authors: ["Patel, M.", "Nguyen, N.", "Kim, S."],
  },
  {
    id: "6",
    title: "Efficacy of Subcutaneous versus Oral Methotrexate in Psoriasis",
    url: "https://clinicaltrials.gov/example6",
    source: "ClinicalTrials.gov",
    date: "2023-11-28",
    snippet:
      "A multicenter trial comparing the efficacy and tolerability of subcutaneous versus oral methotrexate in moderate to severe plaque psoriasis. The study includes 210 participants followed for 52 weeks.",
    authors: ["Anderson, P.", "White, R."],
  },
]
