SOURCES = {
    "Amazon": {
        "tier_1": [
            {"name": "Amazon Press Releases", "url": "https://www.aboutamazon.com/news", "signal": "Strategy shifts, pricing, logistics"},
            {"name": "Amazon Shareholder Letters", "url": "https://www.amazon.com/gp/help/customer/display.html?nodeId=588276", "signal": "Long-term priorities: cost vs growth, AI, marketplace"},
            {"name": "Amazon Science Blog", "url": "https://www.amazon.science/blog", "signal": "Tech and AI direction before commercialization"},
            {"name": "AWS Blog", "url": "https://aws.amazon.com/blogs/aws/", "signal": "Infrastructure investments affecting retail & logistics"}
        ],
        "tier_2": [
            {"name": "Retail Dive - Amazon", "url": "https://www.retaildive.com/?s=amazon", "signal": "Organization changes and margin pressure"},
            {"name": "Marketplace Pulse", "url": "https://www.marketplacepulse.com/", "signal": "Seller fees and policy shifts"}
        ],
        "tier_3": [
            {"name": "Amazon Job Postings", "url": "https://www.amazon.jobs/en/", "signal": "Hiring trends in logistics, ads, AI"}
        ]
    },
    "Walmart": {
        "tier_1": [
            {"name": "Walmart Newsroom", "url": "https://corporate.walmart.com/news", "signal": "Pricing, store strategy, automation"},
            {"name": "Walmart Investor Relations", "url": "https://corporate.walmart.com/investors", "signal": "Margin defense vs price leadership"},
            {"name": "Walmart Connect", "url": "https://walmartconnect.com/", "signal": "Retail media monetization priorities"}
        ],
        "tier_2": [
            {"name": "Retail Dive - Walmart", "url": "https://www.retaildive.com/?s=walmart", "signal": "Automation and fulfillment investments"},
            {"name": "Supply Chain Dive", "url": "https://www.supplychaindive.com/?s=walmart", "signal": "Logistics and supply chain strategy"}
        ],
        "tier_3": [
            {"name": "Sam's Club Updates", "url": "https://www.samsclub.com/", "signal": "Signals for Walmart-wide direction"}
        ]
    },
    "Target": {
        "tier_1": [
            {"name": "Target Press Room", "url": "https://corporate.target.com/press", "signal": "Pricing, loyalty, owned brands"},
            {"name": "Target Investor Relations", "url": "https://corporate.target.com/investors", "signal": "Category focus and sourcing priorities"}
        ],
        "tier_2": [
            {"name": "Retail Dive - Target", "url": "https://www.retaildive.com/?s=target", "signal": "Strategy shifts and competitive moves"},
            {"name": "Modern Retail", "url": "https://www.modernretail.co/?s=target", "signal": "Digital and loyalty strategy"}
        ],
        "tier_3": [
            {"name": "Target Creative Updates", "url": "https://corporate.target.com/", "signal": "Marketing positioning shifts"}
        ]
    },
    "CVS": {
        "tier_1": [
            {"name": "CVS Health Newsroom", "url": "https://www.cvshealth.com/newsroom", "signal": "Healthcare strategy and partnerships"},
            {"name": "CVS Investor Relations", "url": "https://investors.cvshealth.com/", "signal": "Pharmacy economics and services mix"},
            {"name": "MinuteClinic Updates", "url": "https://www.minuteclinic.com/", "signal": "Healthcare vertical integration"}
        ],
        "tier_2": [
            {"name": "Healthcare Dive", "url": "https://www.healthcaredive.com/?s=cvs", "signal": "Policy impact and reimbursement changes"},
            {"name": "STAT News", "url": "https://www.statnews.com/?s=cvs", "signal": "Industry dynamics and partnerships"}
        ],
        "tier_3": [
            {"name": "CVS Regulatory Commentary", "url": "https://investors.cvshealth.com/", "signal": "State and federal policy impact"}
        ]
    },
    "Walgreens": {
        "tier_1": [
            {"name": "Walgreens Boots Alliance Newsroom", "url": "https://www.walgreensbootsalliance.com/news", "signal": "Store footprint and restructuring"},
            {"name": "Walgreens Investor Relations", "url": "https://investor.walgreensbootsalliance.com/", "signal": "Financial strategy and repositioning"}
        ],
        "tier_2": [
            {"name": "Healthcare Dive - Walgreens", "url": "https://www.healthcaredive.com/?s=walgreens", "signal": "Healthcare and pharmacy strategy"},
            {"name": "Retail Dive - Walgreens", "url": "https://www.retaildive.com/?s=walgreens", "signal": "Retail and store strategy"}
        ],
        "tier_3": [
            {"name": "VillageMD & Walgreens", "url": "https://www.villagemd.com/", "signal": "Healthcare clinic rollouts"},
            {"name": "Store Closure Announcements", "url": "https://www.walgreensbootsalliance.com/news", "signal": "Footprint changes"}
        ]
    }
}

def get_all_sources():
    """Return flat list of all sources for crawling."""
    all_sources = {}
    for retailer, tiers in SOURCES.items():
        all_sources[retailer] = []
        for tier_key in ['tier_1', 'tier_2', 'tier_3']:
            if tier_key in tiers:
                for source in tiers[tier_key]:
                    source['tier'] = tier_key.replace('tier_', '')
                    all_sources[retailer].append(source)
    return all_sources
