"""
test_fake_article.py
Test BiLSTM with realistic fake news article
"""

from dl_predictor import DLPredictor

# Short clickbait (what you tested)
short_fake = """
BREAKING: Secret government documents reveal shocking truth about alien 
technology being used in smartphones! Whistleblower claims major tech 
companies have been hiding this for decades. Click here to learn what 
THEY don't want you to know!
"""

# Longer, more realistic fake article
long_fake = """
BREAKING NEWS: Leaked Government Documents Expose Alien Technology Cover-Up

Washington D.C. - In a shocking revelation that could change everything we 
know about modern technology, classified government documents obtained by 
anonymous sources reveal that major smartphone manufacturers have been 
secretly using alien technology for over two decades.

According to the leaked files, a whistleblower from inside a major tech 
company claims that the rapid advancement in smartphone capabilities is not 
due to human innovation, but rather reverse-engineered extraterrestrial 
technology recovered from a 1947 incident in New Mexico.

"They've been lying to us for years," the anonymous source stated in an 
encrypted message. "The touchscreen technology, the microprocessors, even 
the camera sensors - all of it came from alien spacecraft."

The documents, which cannot be independently verified, allegedly show 
communication between government agencies and tech CEOs discussing how to 
keep this information hidden from the public. Industry experts are calling 
this the biggest cover-up in modern history.

Several unnamed scientists have reportedly confirmed these claims, though 
none were willing to go on record due to fear of retaliation. The government 
has not yet responded to requests for comment.

This revelation raises serious questions about what else authorities might 
be hiding from citizens. Many are now demanding full disclosure and 
transparency about the true origins of modern technology.

SHARE THIS BEFORE IT GETS DELETED! The mainstream media won't report this 
because they're controlled by the same people hiding the truth. Wake up and 
see what THEY don't want you to know!
"""

# Real news article for comparison
real_article = """
Apple Announces New iPhone Model with Enhanced Camera Features

Cupertino, California - Apple Inc. announced today the launch of its latest 
iPhone model, featuring significant improvements to camera technology and 
processing power.

The new device, unveiled at the company's annual product event, includes a 
48-megapixel main camera sensor and an upgraded A17 Pro chip that enables 
faster image processing and improved battery efficiency.

"We're excited to bring these innovations to our customers," said Greg 
Joswiak, Apple's senior vice president of Worldwide Marketing, during the 
presentation at the Steve Jobs Theater.

The smartphone will be available for pre-order starting Friday, with prices 
beginning at $799 for the base model. Industry analysts predict strong sales 
based on the feature improvements and competitive pricing.

According to market research firm IDC, the global smartphone market has shown 
signs of recovery this quarter, with shipments increasing 3.2% compared to 
the same period last year. Apple maintains approximately 18% market share in 
the worldwide smartphone segment.

The new iPhone will ship with iOS 17, which includes enhanced privacy features 
and improved integration with other Apple devices. The company also announced 
extended software support, promising security updates for at least five years.

Shares of Apple rose 1.2% in after-hours trading following the announcement.
"""

def test_all():
    print("="*70)
    print("BiLSTM Fake News Detection - Comprehensive Test")
    print("="*70)
    
    predictor = DLPredictor()
    
    if not predictor.model:
        print("\n[ERROR] Model not loaded!")
        return
    
    print("\n" + "="*70)
    print("TEST 1: Short Clickbait (Your Example)")
    print("="*70)
    print(short_fake[:100] + "...")
    result1 = predictor.predict(short_fake)
    print(f"\nVERDICT: {result1['verdict']}")
    print(f"Confidence: {result1['confidence']*100:.2f}%")
    print("\n[WARNING] SHORT TEXT ISSUE: Not enough context for accurate detection")
    
    print("\n" + "="*70)
    print("TEST 2: Long Fake Article (More Realistic)")
    print("="*70)
    print(long_fake[:150] + "...")
    result2 = predictor.predict(long_fake)
    print(f"\nVERDICT: {result2['verdict']}")
    print(f"Confidence: {result2['confidence']*100:.2f}%")
    
    print("\n" + "="*70)
    print("TEST 3: Real News Article")
    print("="*70)
    print(real_article[:150] + "...")
    result3 = predictor.predict(real_article)
    print(f"\nVERDICT: {result3['verdict']}")
    print(f"Confidence: {result3['confidence']*100:.2f}%")
    
    print("\n" + "="*70)
    print("ANALYSIS")
    print("="*70)
    print(f"Short Fake:  {result1['verdict']} - [WARNING] Unreliable (too short)")
    print(f"Long Fake:   {result2['verdict']} - Should detect better")
    print(f"Real News:   {result3['verdict']} - Should be REAL")
    print("\n[TIP] BiLSTM works best with complete articles (200+ words)")
    print("="*70)

if __name__ == "__main__":
    test_all()
