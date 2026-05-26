"""
Comprehensive Testing Dataset
Mix of REAL and FAKE news articles for testing all models
"""

TEST_ARTICLES = [
    {
        "id": 1,
        "label": "FAKE",
        "category": "Health Conspiracy",
        "article": """
        BREAKING: Scientists Discover Miracle Cure for All Cancers Using Lemon Juice!
        A revolutionary study conducted by independent researchers has revealed that drinking 
        lemon juice mixed with baking soda can cure all types of cancer within 30 days. 
        Big Pharma doesn't want you to know this secret because it would destroy their 
        trillion-dollar industry. Doctors are being paid to hide this information from patients.
        The cure costs only $2 and pharmaceutical companies are desperately trying to suppress 
        this groundbreaking discovery. Share this before it gets deleted!
        """
    },
    {
        "id": 2,
        "label": "REAL",
        "category": "Politics",
        "article": """
        Washington - President Biden announced new infrastructure legislation today during 
        a press conference at the White House. The bipartisan bill, which passed the Senate 
        with 69 votes, allocates $1.2 trillion for roads, bridges, and broadband expansion 
        over the next decade. Transportation Secretary Pete Buttigieg stated that the funding 
        will create approximately 2 million jobs. The legislation received support from both 
        Democratic and Republican lawmakers, marking a rare moment of bipartisan cooperation.
        """
    },
    {
        "id": 3,
        "label": "FAKE",
        "category": "Political Conspiracy",
        "article": """
        SHOCKING REVELATION: Government Admits to Controlling Weather Using Secret Technology!
        Leaked documents from anonymous sources reveal that world governments have been 
        manipulating weather patterns for decades using HAARP technology. Hurricanes, 
        earthquakes, and floods are all artificially created to control populations and 
        increase profits for disaster relief companies. Mainstream media refuses to cover 
        this story because they are controlled by the same elites. Wake up sheeple! 
        The truth is being hidden from you. Share this everywhere before they silence us!
        """
    },
    {
        "id": 4,
        "label": "REAL",
        "category": "Science",
        "article": """
        NASA's James Webb Space Telescope has captured unprecedented images of distant 
        galaxies formed just 300 million years after the Big Bang. The observations, 
        published in the journal Nature, provide new insights into early universe formation. 
        Lead researcher Dr. Jane Smith from the Space Telescope Science Institute stated 
        that these findings challenge existing models of galaxy evolution. The telescope, 
        launched in December 2021, continues to exceed expectations in its mission to 
        explore the cosmos.
        """
    },
    {
        "id": 5,
        "label": "FAKE",
        "category": "Celebrity Hoax",
        "article": """
        BREAKING: Tom Hanks Arrested by FBI for International Conspiracy!
        Hollywood actor Tom Hanks was reportedly arrested at his Los Angeles home early 
        this morning by federal agents. Sources claim he is involved in a massive 
        international conspiracy that goes all the way to the top. Mainstream media is 
        completely silent on this story - ask yourself why! This is the biggest cover-up 
        in history. The truth will shock you. All evidence is being scrubbed from the 
        internet as we speak. Download and share before it's too late!
        """
    },
    {
        "id": 6,
        "label": "REAL",
        "category": "Business",
        "article": """
        New York - The Federal Reserve announced a 0.25% interest rate increase today, 
        marking the fifth consecutive rate hike this year. Fed Chairman Jerome Powell 
        stated that the decision aims to combat persistent inflation, which remains above 
        the target 2% rate. Wall Street responded with mixed reactions, with the Dow Jones 
        falling 1.2% while tech stocks showed resilience. Economists predict additional 
        rate increases may be necessary if inflation continues at current levels.
        """
    },
    {
        "id": 7,
        "label": "FAKE",
        "category": "Technology Hoax",
        "article": """
        URGENT: 5G Towers Confirmed to Cause Brain Cancer and Mind Control!
        Thousands of secret documents leaked by whistleblowers prove that 5G radiation 
        is 1000 times more dangerous than previously thought. Governments worldwide are 
        installing these towers to control your thoughts and make you sick. Symptoms include 
        headaches, fatigue, and memory loss. Telecom companies are paying scientists to 
        lie about safety. Protect your family NOW! Wrap your phone in aluminum foil and 
        destroy nearby 5G towers. They don't want you to know the TRUTH!
        """
    },
    {
        "id": 8,
        "label": "REAL",
        "category": "Environment",
        "article": """
        Geneva - The United Nations Climate Change Conference concluded today with 
        195 countries agreeing to strengthen emission reduction targets. The agreement 
        includes commitments to phase out coal power by 2040 and increase renewable 
        energy investments. UN Secretary-General António Guterres called it a significant 
        step forward, though environmental groups argue the measures don't go far enough. 
        Developed nations pledged $100 billion annually to help developing countries 
        transition to clean energy.
        """
    },
    {
        "id": 9,
        "label": "FAKE",
        "category": "Vaccine Misinformation",
        "article": """
        EXPOSED: COVID Vaccines Contain Microchips for Population Tracking!
        Insider sources from pharmaceutical companies reveal that all COVID-19 vaccines 
        contain microscopic tracking chips developed by tech billionaires. These chips 
        activate with 5G signals and can monitor your location, thoughts, and health data. 
        Doctors are being paid $1000 for every person they vaccinate. This is the biggest 
        conspiracy in human history! The mainstream media won't report this because they're 
        controlled by the same people. Do your own research! Don't be a sheep!
        """
    },
    {
        "id": 10,
        "label": "REAL",
        "category": "Sports",
        "article": """
        Paris - The International Olympic Committee announced that Paris will host the 
        2024 Summer Olympics from July 26 to August 11. The event will feature 32 sports 
        and approximately 10,500 athletes from over 200 countries. New additions include 
        breaking, sport climbing, and surfing. Paris Mayor Anne Hidalgo emphasized the 
        city's commitment to sustainability, with 95% of venues being existing or temporary 
        structures. Security measures will be enhanced following consultations with 
        international law enforcement agencies.
        """
    }
]

def get_test_articles():
    """Return all test articles"""
    return TEST_ARTICLES

def get_fake_articles():
    """Return only fake articles"""
    return [a for a in TEST_ARTICLES if a['label'] == 'FAKE']

def get_real_articles():
    """Return only real articles"""
    return [a for a in TEST_ARTICLES if a['label'] == 'REAL']

def print_dataset_summary():
    """Print summary of test dataset"""
    print("\n" + "="*60)
    print("TEST DATASET SUMMARY")
    print("="*60)
    print(f"Total Articles: {len(TEST_ARTICLES)}")
    print(f"FAKE Articles: {len(get_fake_articles())}")
    print(f"REAL Articles: {len(get_real_articles())}")
    print("\nCategories:")
    categories = {}
    for article in TEST_ARTICLES:
        cat = article['category']
        categories[cat] = categories.get(cat, 0) + 1
    for cat, count in categories.items():
        print(f"  - {cat}: {count}")
    print("="*60 + "\n")

if __name__ == "__main__":
    print_dataset_summary()
    
    print("\nSample Articles:\n")
    for article in TEST_ARTICLES[:3]:
        print(f"[{article['id']}] {article['label']} - {article['category']}")
        print(f"{article['article'][:100]}...")
        print()
