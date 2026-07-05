import os
import json
import re

# Set directories
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")
I18N_DIR = os.path.join(DATA_DIR, "i18n")

def clean_quotes(text):
    if not text:
        return text
    # Replace double-double quotes with single double quotes
    text = text.replace('""', '"')
    # Strip whitespace
    text = text.strip()
    # Strip leading/trailing double quotes if it wraps the whole string
    if text.startswith('"') and text.endswith('"') and len(text) >= 2:
        text = text[1:-1].strip()
    # Re-replace double-double quotes if any were made by stripping
    text = text.replace('""', '"')
    return text

def clean_usda_suffix(text):
    if not text:
        return text
    # Remove Slovak suffixes
    text = re.sub(r'\s+z\s+databázy\s+USDA\.?$', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+podľa\s+databázy\s+USDA\.?$', '', text, flags=re.IGNORECASE)
    # Remove English suffixes
    text = re.sub(r'\s+from\s+the\s+USDA\s+database\.?$', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+as\s+defined\s+by\s+the\s+USDA\s+database\.?$', '', text, flags=re.IGNORECASE)
    # Strip any trailing whitespace or duplicate periods
    text = text.strip()
    # Remove trailing dots
    text = re.sub(r'\.+\s*$', '', text)
    if text:
        text = text + "."
    return text

# English abbreviation mapping
EN_REPLACEMENTS = [
    # Infant formula specific (long combos first)
    (r"\binf\s+fo\b", "infant formula"),
    (r"\binf\s+for\b", "infant formula"),
    (r"\bin\s+for\b", "infant formula"),
    (r"\binf\s+form\b", "infant formula"),
    (r"\binf\s+formula\b", "infant formula"),
    (r"\bchild\s+formula\b", "toddler formula"),
    
    (r"\bme\s+jo\b", "Mead Johnson"),
    (r"\bme\s+john\b", "Mead Johnson"),
    (r"\bm\s+john\b", "Mead Johnson"),
    (r"\bmejohn\b", "Mead Johnson"),
    (r"\bme\s+johns\b", "Mead Johnson"),
    (r"\bme\s+johnson\b", "Mead Johnson"),
    
    (r"\benfac\s+lip\b", "EnfaCare Lipil"),
    (r"\benfac\s+lipil\b", "EnfaCare Lipil"),
    (r"\benfamillipil\b", "Enfamil Lipil"),
    
    (r"\bwith/\s*ir\b", "with iron"),
    (r"\bwith\s+ir\b", "with iron"),
    (r"\bw/\s*iron\b", "with iron"),
    (r"\bw\s+iron\b", "with iron"),
    (r"\bsirn\b", "with iron"),
    (r"\bsiron\b", "with iron"),
    
    (r"\bliquids\s+co\b", "liquid concentrate"),
    (r"\bnot\s+re\b", "not reconstituted"),
    (r"\bnotrecn\b", "not reconstituted"),
    (r"\bre\s+to\s+fe\b", "ready-to-feed"),
    (r"\brtf\b", "ready-to-feed"),
    
    (r"\bwi\s+ara\s+and\s+dh\b", "with ARA and DHA"),
    (r"\bwi\s+ara\s+and\s+dha\b", "with ARA and DHA"),
    (r"\bwith/\s*ara\s*&\s*dha\b", "with ARA and DHA"),
    (r"\bwith\s+ara\s*&\s*dha\b", "with ARA and DHA"),
    (r"\bs/\s*ara\s*&\s*dha\b", "with ARA and DHA"),
    (r"\bwi\b", "with"), # wi -> with (infant formula)
    
    (r"\bprosobee\s+lipil\b", "ProSobee Lipil"),
    (r"\bpros\s+lipil\b", "ProSobee Lipil"),
    (r"\bpros\b", "ProSobee"),
    (r"\bnutr\s+lipil\b", "Nutramigen Lipil"),
    (r"\bnutr\b", "Nutramigen"),
    (r"\benf\b", "Enfamil"),
    (r"\blactof\b", "Lactofree"),
    (r"\bpdr\b", "powder"),
    (r"\bpo\b", "powder"),
    
    # Skin patterns in English (placed early to prevent general wo/ from splitting wo/skn)
    (r"\bwo/\s*skn\b", "without skin"),
    (r"\bwoskn\b", "without skin"),
    (r"\bwithout/\s*skn\b", "without skin"),
    (r"\bwithskn\b", "with skin"),
    (r"\bwith/\s*skn\b", "with skin"),
    (r"\bsskn\b", "with skin"),
    (r"\bw/\s*skn\b", "with skin"),
    (r"\bin\s+skn\b", "in skin"),
    (r"\bin_skn\b", "in skin"),
    (r"\bin\s+skin\b", "in skin"),
    
    # Special double/triple combos
    (r"\bcroissan'wich\b", "croissan'wich"),
    (r"\bcroissanwich\b", "croissan'wich"),
    (r"\bmozzarella stks\b", "mozzarella sticks"),
    (r"\bmozzarella chs stks\b", "mozzarella cheese sticks"),
    (r"\bfat_free\b", "fat free"),
    (r"\blo_na\b", "low sodium"),
    (r"\blo_fat\b", "low fat"),
    (r"\bred_cal\b", "reduced calorie"),
    (r"\bpnut butter\b", "peanut butter"),
    (r"\bpnut\b", "peanut"),
    (r"\bshrt\s+loin\b", "short loin"),
    (r"\btop\s+loin\b", "top loin"),
    (r"\bsoy\s+bean\b", "soybean"),
    
    # Fast foods specific
    (r"\bhmburgr\b", "hamburger"),
    (r"\bchsburgr\b", "cheeseburger"),
    (r"\bptty\b", "patty"),
    (r"\bppty\b", "patty"),
    (r"\bdbl\s+bn\b", "double bun"),
    (r"\bdbl\b", "double"),
    (r"\bbn\b", "bun"),
    (r"\bcndmnt\b", "condiment"),
    (r"\bspl\s+k\b", "Special K"),
    (r"\bspl\b", "special"),
    (r"\bmeat\s+sau\b", "meat sauce"),
    (r"\btomato\s+sau\b", "tomato sauce"),
    (r"\bchili\s+sau\b", "chili sauce"),
    (r"\bcheese\s+sau\b", "cheese sauce"),
    (r"\bsau\b", "sauce"),
    (r"\bsng\b", "single"),
    (r"\brg\s+ptty\b", "regular patty"),
    (r"\breg\s+ptty\b", "regular patty"),
    
    # Beef cuts
    (r"\bbn-in\b", "bone-in"),
    (r"\bbn_in\b", "bone-in"),
    (r"\blip-on\b", "lip-on"),
    (r"\blip_on\b", "lip-on"),
    (r"\bal\s+gds\b", "all grades"),
    (r"\bal\s+grd\b", "all grades"),
    
    # Slash representations
    (r"\bw/o\b", "without"),
    (r"\bw/\b", "with"),
    (r"\bwo/\b", "without"),
    (r"\bwithout/\b", "without"),
    (r"s/ cndmnt", "with condiments"),
    
    # Packs and Syrups
    (r"\bh2o pk\b", "water pack"),
    (r"\bjuc pk\b", "juice pack"),
    (r"\blt syrup pk\b", "light syrup pack"),
    (r"\bhvy syrup pk\b", "heavy syrup pack"),
    (r"\bhvy syrup\b", "heavy syrup"),
    (r"\blt syrup\b", "light syrup"),
    (r"\bconc\b", "concentrate"),
    (r"\bundil\b", "undiluted"),
    (r"\bdil\s+s\b", "diluted with"),
    (r"\bvolume h2o\b", "volumes of water"),
    
    # Sweets & Juices
    (r"\bbtld\b", "bottled"),
    (r"\bjuc\b", "juice"),
    (r"\bswt\b", "sweet"),
    (r"\byel\b", "yellow"),
    (r"\bdrk\b", "drink"),
    (r"\bappl\b", "apple"),
    (r"\bbrkfst\b", "breakfast"),
    (r"\bpulp\b", "pulp"),
    (r"\bdup\b", "pulp"),
    (r"\bchick\b", "chicken"),
    (r"\bchery\b", "cherry"),
    (r"\bwhl kernel\b", "whole kernel"),
    (r"\bkrnls\b", "kernels"),
    
    # USDA Commodity English removals
    (r"\b\(?includes usda commodity food program\)?\b", ""),
    (r"\b\(?includes food program\)?\b", ""),
    (r"\b\(?includes usda commod\)?\b", ""),
    (r"\b\(?including usda cmdty\)?\b", ""),
    (r"\busda\s+cmdty\s+fd\b", ""),
    (r"\busda\s+cmdty\b", ""),
    (r"\busda\s+commodity\b", ""),
    (r"\bbf\b", "beef"),
    (r"\brefried bns\b", "refried beans"),
    (r"\bsmmr\b", "summer"),
    (r"\bwntr\b", "winter"),
    
    # Single abbreviations (with word boundaries)
    (r"\bckd\b", "cooked"),
    (r"\bbld\b", "boiled"),
    (r"\bbkd\b", "baked"),
    (r"\bdrnd\b", "drained"),
    (r"\bdr\b", "drained"),
    (r"\bcnd\b", "canned"),
    (r"\bwo\b", "without"),
    (r"\bw\b", "with"),
    (r"\bskn\b", "skin"),
    (r"\bsol\b", "solids"),
    (r"\bliquids\b", "liquids"),
    (r"\bliq\b", "liquids"),
    (r"\bunprep\b", "unprepared"),
    (r"\bln\b", "lean"),
    (r"\bft\b", "fat"),
    (r"\bstk\b", "steak"),
    (r"\bstks\b", "steaks"),
    (r"\bgld\b", "grilled"),
    (r"\bgrld\b", "grilled"),
    (r"\bbrld\b", "broiled"),
    (r"\bbnl\b", "boneless"),
    (r"\bbnless\b", "boneless"),
    (r"\bwhl\b", "whole"),
    (r"\bchoc\b", "chocolate"),
    (r"\bcomm\b", "commercial"),
    (r"\breg\b", "regular"),
    (r"\bevap\b", "evaporated"),
    (r"\bcond\b", "condensed"),
    (r"\bswtnd\b", "sweetened"),
    (r"\bchoic\b", "choice"),
    (r"\bsel\b", "select"),
    (r"\bgrd\b", "grade"),
    (r"\bgrds\b", "grades"),
    (r"\bpkg\b", "package"),
    (r"\bshrt\b", "short"),
    (r"\bcntr\b", "center"),
    (r"\bshldr\b", "shoulder"),
    (r"\bbttrmlk\b", "buttermilk"),
    (r"\bveg\b", "vegetable"),
    (r"\bdrsng\b", "dressing"),
    (r"\bcrm\b", "cream"),
    (r"\bstmd\b", "steamed"),
    
    # Heating / Cooling
    (r"\bunhtd\b", "unheated"),
    (r"\bprehtd\b", "preheated"),
    (r"\bhtd\b", "heated"),
    (r"\brefr\b", "refrigerated"),
    (r"\boven-htd\b", "oven-heated"),
    
    # Newly identified
    (r"\bunckd\b", "uncooked"),
    (r"\bpreckd\b", "precooked"),
    (r"\bdehyd\b", "dehydrated"),
    (r"\bfrz\b", "frozen"),
    (r"\bdk\b", "dark"),
    (r"\binst\b", "instant"),
    (r"\benr\b", "enriched"),
    (r"\brehtd\b", "reheated"),
    (r"\bchopd\b", "chopped"),
    (r"\bcereals\s+rte\b", "Cereals, ready-to-eat"),
    (r"\brte\b", "ready-to-eat"),
    
    # Clean up duplicate commas or extra spaces resulting from replacements
    (r",\s*,", ","),
    (r"\s+", " "),
]

# Slovak translation mapping
SK_REPLACEMENTS = [
    # Brand/Infant formula specific corrections (done first to avoid mead -> medovina)
    (r"\bmedovina\s+johnson\b", "Mead Johnson"),
    (r"\bmedovina\s+johns\b", "Mead Johnson"),
    (r"\bme\s+johns\b", "Mead Johnson"),
    (r"\bme\s+john\b", "Mead Johnson"),
    (r"\bme\s+jo\b", "Mead Johnson"),
    (r"\bm\s+john\b", "Mead Johnson"),
    (r"\bmejohn\b", "Mead Johnson"),
    (r"\bmead\s+johnson\b", "Mead Johnson"),
    
    (r"\benfac\s+lip\b", "EnfaCare Lipil"),
    (r"\benfac\s+lipil\b", "EnfaCare Lipil"),
    (r"\benfamillipil\b", "Enfamil Lipil"),
    
    (r"\bprosobee\s+lipil\b", "ProSobee Lipil"),
    (r"\bpros\s+lipil\b", "ProSobee Lipil"),
    (r"\bpros\b", "ProSobee"),
    (r"\bnutr\s+lipil\b", "Nutramigen Lipil"),
    (r"\bnutr\b", "Nutramigen"),
    (r"\benf\b", "Enfamil"),
    (r"\ben\b", "Enfamil"),
    (r"\blactof\b", "bezlaktózová"),
    
    (r"\binf\s+vzorec\b", "dojčenská výživa"),
    (r"\binf\s+forma\b", "dojčenská výživa"),
    (r"\binf\s+form\b", "dojčenská výživa"),
    (r"\binf\s+for\b", "dojčenská výživa"),
    (r"\binf\s+fo\b", "dojčenská výživa"),
    (r"\bin\s+for\b", "dojčenská výživa"),
    (r"\binf\s+forma\b", "dojčenská výživa"),
    (r"\bchild\s+formula\b", "detská výživa"),
    (r"\bdetská\s+výživa\b", "detská výživa"),
    
    (r"\brtf\b", "pripravená na kŕmenie"),
    (r"\bpdr\b", "prášok"),
    (r"\bpo\b", "prášok"),
    (r"\bre\s+to\s+fe\b", "pripravená na kŕmenie"),
    (r"\bready\s+to\s+feed\b", "pripravená na kŕmenie"),
    
    (r"\bnot\s+re\b", "nepripravená"),
    (r"\bnotrecn\b", "nepripravená"),
    (r"\bnie\s+rekonštrukcia\b", "nepripravená"),
    (r"\bnie\s+rekon\b", "nepripravená"),
    (r"\bnie\s+rec\b", "nepripravená"),
    (r"\bbez\s+recon\b", "nepripravená"),
    (r"\bnie\s+rekonštituované\b", "nepripravené"),
    
    (r"\blo\s+železo\b", "s nízkym obsahom železa"),
    (r"\blo\s+iron\b", "s nízkym obsahom železa"),
    (r"\bsiron\b", "so železom"),
    (r"\bsirn\b", "so železom"),
    (r"\bwith/\s*iron\b", "so železom"),
    (r"\bs/\s*iron\b", "so železom"),
    (r"\bwith\s+ir\b", "so železom"),
    (r"\bs\s+ir\b", "so železom"),
    
    (r"\bwi\s+ara\s+and\s+dh\b", "s ARA a DHA"),
    (r"\bwi\s+ara\s+and\s+dha\b", "s ARA a DHA"),
    (r"\bbez\s+ara\s+a\s+dh\b", "s ARA a DHA"), # Fixes previous mistaken replacement
    (r"\bs/\s*ara\s*&\s*dha\b", "s ARA a DHA"),
    (r"\bs\s+ara\s*&\s*dha\b", "s ARA a DHA"),
    (r"\bwi\b", "s"), # wi -> s
    
    # Specific Juices/Drinks Slovak mapping (placed early)
    (r"\bBrusnicovo-jablkový juc drk\b", "Brusnicovo-jablkový džúsový nápoj"),
    (r"\bPomarančovo-marhuľový juc drk\b", "Pomarančovo-marhuľový džúsový nápoj"),
    (r"\bAnanás & grapefruit juc drk\b", "Ananásový a grapefruitový džúsový nápoj"),
    (r"\bAnanás&pomarančový juc drk\b", "Ananásovo-pomarančový džúsový nápoj"),
    (r"\bPomarančový drk, typ brkfst, s/ juc & dup\b", "Pomarančový nápoj, raňajkový typ, s džúsovou dužinou"),
    (r"\bPomarančová zmes pnappl juc\b", "Pomarančovo-ananásová džúsová zmes"),
    (r"\bovocné a juc tyčinky\b", "tyčinky z ovocnej šťavy"),
    (r"\btyp juc\b", "šťavového typu"),
    (r"\bjuc s/ krém\b", "šťava so smotanou"),
    (r"\bTomato&zelenina juc\b", "Paradajkovo-zeleninová šťava"),
    (r"\bGrapefruit juc\b", "Grapefruitový džús"),
    (r"\bOrange juc\b", "Pomarančový džús"),
    (r"\bOrange Juc\b", "Pomarančový džús"),
    (r"\bAnanás juc\b", "Ananásový džús"),
    (r"\bAnanásový džús\b", "Ananásový džús"),
    (r"\bBlackberry juc\b", "Černicový džús"),
    (r"\bCranberry juc\b", "Brusnicový džús"),
    (r"\bJuc z granátového jablka\b", "Granátové jablko šťava"),
    
    # Babyfood juices
    (r"\bdetská výživa, juc, pomaranč&appl&banana\b", "detská výživa, džús, pomaranč, jablko a banán"),
    (r"\bdetská výživa, juc, mxd ovocie\b", "detská výživa, džús, miešané ovocie"),
    (r"\bdetská výživa, juc, appl&cherry\b", "detská výživa, džús, jablko a čerešňa"),
    (r"\bdetská výživa, juc, appl - cherry\b", "detská výživa, džús, jablko a čerešňa"),
    (r"\bdetská výživa, juc, appl&broskyne\b", "detská výživa, džús, jablko a broskyňa"),
    (r"\bdetská výživa, juc, appl&slivka\b", "detská výživa, džús, jablko a slivka"),
    (r"\bdetská výživa, juc, appl&slivky\b", "detská výživa, džús, jablko a slivky"),
    (r"\bdetská výživa, juc, appl&prune\b", "detská výživa, džús, jablko a sušené slivky"),
    (r"\bdetská výživa, juc\b", "detská výživa, džús"),
    
    # Generic juice mapping
    (r"\bJuc\b", "Šťava"),
    (r"\bjuc\b", "šťava"),
    
    # Lime specific
    (r"\blime\s+juc\b", "limetková šťava"),
    (r"\blime\s+šťava\b", "limetková šťava"),
    (r"\blime\b", "limetka"),
    
    # Bottled specific
    (r"\bkonzervované alebo btld\b", "konzervované alebo vo fľaši"),
    (r"\bkonzervované, btld\b", "konzervované, vo fľaši"),
    (r"\bdžúsový kokteil, btld\b", "džúsový kokteil, vo fľaši"),
    (r"\bčili omáčka, btld\b", "čili omáčka, vo fľaši"),
    (r"\bparadajková čili omáčka, btld\b", "paradajková čili omáčka, vo fľaši"),
    (r"\bbtld\b", "vo fľaši"),
    
    # Sweet specific
    (r"\bčerešne, swt\b", "čerešne, sladké"),
    (r"\bčerešne, sladké, mrazené, sladené\b", "čerešne, sladké, mrazené, sladené"),
    (r"\bkukurica, swt, yel\b", "kukurica, sladká, žltá"),
    (r"\bkukurica, swt\b", "kukurica, sladká"),
    (r"\buhorky, swt\b", "uhorky, sladké"),
    (r"\bsalvadorský swt chs\b", "salvádorský sladký syrový"),
    (r"\bsbravčové mäso & swt\b", "s bravčovým mäsom a sladkou omáčkou"),
    (r"\bswt & kyslé\b", "sladko-kyslé"),
    (r"\bswt & sour\b", "sladko-kyslé"),
    (r"\bswt&sour\b", "sladko-kyslé"),
    (r"\bex swt var\b", "extra sladká odroda"),
    (r"\bmučenkový džús, yel\b", "marakujový džús, žltý"),
    (r"\bpaprika, swt\b", "paprika, sladká"),
    (r"\bpapriky, swt\b", "paprika, sladká"),
    (r"\bpaprika swt\b", "paprika, sladká"),
    (r"\bswt zemiaky\b", "sladké zemiaky"),
    (r"\bswt čokoládou\b", "sladkou čokoládou"),
    (r"\bcibuľa, swt\b", "cibuľa, sladká"),
    (r"\bswt\b", "sladké"),
    (r"\byel\b", "žltý"),
    
    # USDA Commodity Slovak removals
    (r"\b\(?vrátane usda cmdty\)?\b", ""),
    (r"\b\(?zahŕňa usda commod\)?\b", ""),
    (r"\b\(?zahŕňa komoditu usda\)?\b", ""),
    (r"\b\(?zahŕňa potraviny pre program distribúcie potravín USDA\)?\b", ""),
    (r"\b\(?Zahŕňa potraviny pre program distribúcie potravín USDA\)?\b", ""),
    (r"\busda\s+cmdty\s+fd\b", ""),
    (r"\busda\s+cmdty\b", ""),
    (r"\busda\s+commodity\b", ""),
    (r"\bkomoditu\s+usda\b", ""),
    (r"\bbf\b", "hovädzie"),
    (r"\bkuriatko\b", "kurča"),
    (r"\brefried bns\b", "roztlačená fazuľa"),
    (r"\bsmmr\b", "letná"),
    (r"\bwntr\b", "zimná"),
    
    # Double/triple combos
    (r"\bmozzarella stks\b", "mozzarella tyčinky"),
    (r"\bmozzarella chs stks\b", "mozzarella syrové tyčinky"),
    (r"\bcroissan'wich\b", "croissan'wich"),
    (r"\bcroissanwich\b", "croissan'wich"),
    (r"\bshrt\s+loin\b", "krátke bedro"),
    (r"\btop\s+loin\b", "nízku roštenku"),
    (r"\bsoy\s+bean\b", "sójový bôb"),
    (r"\bpnut\s+butter\b", "arašidové maslo"),
    (r"\bpnut\b", "arašidové"),
    
    # Fast foods specific
    (r"\bhmburgr\b", "hamburger"),
    (r"\bchsburgr\b", "cheeseburger"),
    (r"\bchesebrger\b", "cheeseburger"),
    (r"\bsng\b", "single"),
    (r"\bdbl\s+bn\b", "dvojitá žemľa"),
    (r"\bdbl\b", "dvojitý"),
    (r"\bbn\b", "žemľa"),
    (r"\bptty\b", "placka"),
    (r"\bppty\b", "placka"),
    (r"\blrg\s+paty\b", "veľká placka"),
    (r"\blrg\s+patty\b", "veľká placka"),
    (r"\bspievať\b", "single"), # Fixes translation "sing" -> "spievať"
    (r"\bhriech\b", "single"),   # Fixes translation "single" -> "hriech"
    (r"\bpríkrmami\b", "ochucovadlami"),
    (r"\bcndmnt\b", "ochucovadlá"),
    (r"\bcondmnt\b", "ochucovadlá"),
    (r"\bspl\s+k\b", "Special K"),
    (r"\bspl\s+sau\b", "špeciálna omáčka"),
    (r"\bspl\b", "špeciálny"),
    (r"\bmeat\s+sau\b", "mäsová omáčka"),
    (r"\btomato\s+sau\b", "paradajková omáčka"),
    (r"\bchili\s+sau\b", "čili omáčka"),
    (r"\bcheese\s+sau\b", "syrová omáčka"),
    (r"\bsyrové\s+sau\b", "syrová omáčka"),
    (r"\bparadajkovom\s+sau\b", "paradajkovej omáčke"),
    (r"\bparadajkovou\s+sau\b", "paradajkovou omáčkou"),
    (r"\bsau\b", "omáčka"),
    (r"s/\s*cndmnt", "s ochucovadlami"),
    (r"w/\s*cndmnt", "s ochucovadlami"),
    
    # Specific phrasing replacements
    (r"\bln\s*&\s*ft\b", "chudé a tučné mäso"),
    (r"\bln\s*&\s*fat\b", "chudé a tučné mäso"),
    (r"\bln\s*&\s*tuk\b", "chudé a tučné mäso"),
    (r"\bln,\s+0\" fa\b", "chudé, bez tuku"),
    (r"\bln,\s+0\"\" fa\b", "chudé, bez tuku"),
    (r"\bln,\s+0\"\" tuk\b", "chudé, bez tuku"),
    (r"\bln,\s+0\" tuk\b", "chudé, bez tuku"),
    (r"\b0\" fat\b", "bez tuku"),
    (r"\b0\" tuk\b", "bez tuku"),
    (r"\b0\"\" fat\b", "bez tuku"),
    (r"\b0\"\" tuk\b", "bez tuku"),
    (r"\b1/8\" fat\b", "s 1/8\" tuku"),
    (r"\b1/8\" tuk\b", "s 1/8\" tuku"),
    (r"\b1/8\"\" fat\b", "s 1/8\" tuku"),
    (r"\b1/8\"\" tuk\b", "s 1/8\" tuku"),
    (r"\b1/4\" fat\b", "s 1/4\" tuku"),
    (r"\b1/4\" tuk\b", "s 1/4\" tuku"),
    (r"\b1/4\"\" fat\b", "s 1/4\" tuku"),
    (r"\b1/4\"\" tuk\b", "s 1/4\" tuku"),
    (r"\b1\" steak\b", "1\" steak"),
    (r"\b1\"\" steak\b", "1\" steak"),
    
    # Beef cuts
    (r"\bbn-in\b", "s kosťou"),
    (r"\bbn_in\b", "s kosťou"),
    (r"\blip-on\b", "s tukovým okrajom"),
    (r"\blip_on\b", "s tukovým okrajom"),
    (r"\bal\s+gds\b", "všetky triedy"),
    (r"\bal\s+grd\b", "všetky triedy"),
    (r"\brg\s+ptty\b", "klasické mäso"),
    (r"\breg\s+ptty\b", "klasické mäso"),
    
    # Slashes and basic preps
    (r"\bbez/\s*vit\s+c\b", "bez vitamínu C"),
    (r"\bbez/\s*soľ\b", "bez soli"),
    (r"\bbez/\s*soli\b", "bez soli"),
    (r"\bbez/\b", "bez"),
    (r"\bs/\s*ara\b", "s ara"),
    (r"\bs/\s*dha\b", "s dha"),
    (r"\bs/\b", "s"),
    (r"\bwo/\b", "bez"),
    (r"\bw/\b", "s"),
    (r"\bwithout/\b", "bez"),
    (r"\bwo\b", "bez"),
    (r"\bw\b", "s"),
    (r"\bmäso&skn\b", "mäso a koža"),
    (r"\bmäso\s*&\s*skn\b", "mäso a koža"),
    (r"\blen\s+skn\b", "iba koža"),
    (r"\bskn\s+only\b", "iba koža"),
    (r"\bdk\s+mäso\b", "tmavé mäso"),
    (r"\blt\s+mäso\b", "svetlé mäso"),
    (r"\bvyprážané,\s+flr\b", "vyprážané, obalené v múke"),
    (r"\bvyprážané,\s+in\s+flr\b", "vyprážané, obalené v múke"),
    (r"\bkuriatka\b", "kuracie"), # egg rolls, chicken
    (r"\bdrumstk\b", "spodné stehno"),
    (r"\blt\s+alebo\s+tmavé\b", "svetlé alebo tmavé mäso"),
    
    # Specific incorrect translations
    (r"sušené, s cukrom", "dusené, bez cukru"),
    (r"pevný podiel&tekutiny", "pevný podiel a tekutina"),
    (r"solid, bezsoľ", "pevný podiel, bez soli"),
    (r"s prídavkom soli", "bez pridania soli"), # for tomato cnd paste wo salt which had wrong s prídavkom soli
    (r"sól a kvapalín", "pevný podiel a tekutina"),
    (r"soli a tekutín", "pevný podiel a tekutina"),
    (r"soli a kvapalín", "pevný podiel a tekutina"),
    (r"\bnektár,\s+konzervované\b", "nektár, konzervovaný"),
    (r"\bbez\s+vit\s+c\b", "bez vitamínu C"),
    
    # Pack & Syrup translations
    (r"\bh2o pk\b", "balené vo vode"),
    (r"\bjuc pk\b", "balené v šťave"),
    (r"\blt sirup pk\b", "v ľahkom sirupe"),
    (r"\blt syrup pk\b", "v ľahkom sirupe"),
    (r"\bhvy sirup pk\b", "v hustom sirupe"),
    (r"\bhvy syrup pk\b", "v hustom sirupe"),
    (r"\bhvy sirup\b", "v hustom sirupe"),
    (r"\blt sirup\b", "v ľahkom sirupe"),
    (r"\bconc\b", "koncentrát"),
    (r"\bundil\b", "neriedené"),
    (r"\bdil\s+s3\s+volume\s+h2o\b", "riedené 3 dielmi vody"),
    
    # Other leftovers
    (r"\bdrk\b", "nápoj"),
    (r"\bwhl kernel\b", "celé zrná"),
    (r"\bkrnls on cob\b", "klasy"),
    (r"\bkrnls odrezaný klas\b", "zrná odrezané z klasu"),
    (r"\bkrnls\b", "zrná"),
    (r"\bchose\b", "výber"),
    (r"\brts\b", "pripravená"),
    (r"\bred\b", "červená"),
    (r"\bchick\b", "kuracie"),
    
    # Slovak diacritics fixes
    (r"\bcervene\b", "červené"),
    (r"\bcervené\b", "červené"),
    (r"\bcervený\b", "červený"),
    (r"\bcervená\b", "červená"),
    (r"\bcervenej\b", "červenej"),
    (r"\bbezsoľ\b", "bez soli"),
    (r"\bhrusky\b", "hrušky"),
    (r"\bhruska\b", "hruška"),
    (r"\bhrusiek\b", "hrušiek"),
    
    # Single word Slovak replacements
    (r"\bckd\b", "varené"),
    (r"\brstd\b", "pečené"),
    (r"\bstwd\b", "dusené"),
    (r"\braw\b", "surové"),
    (r"\bfried\b", "vyprážané"),
    (r"\bfrie\b", "vyprážané"),
    (r"\bstk\b", "steak"),
    (r"\bstks\b", "steaky"),
    (r"\bbrld\b", "grilované"),
    (r"\bgrld\b", "grilované"),
    (r"\bgld\b", "grilované"),
    (r"\bbnl\b", "vykostené"),
    (r"\bbnless\b", "vykostené"),
    (r"\bln\b", "chudé"),
    (r"\bskn\b", "koža"),
    (r"\bsolids\b", "pevný podiel"),
    (r"\bdrained\b", "odkvapkané"),
    (r"\bliquid\b", "tekutina"),
    (r"\bchoic\b", "výber"),
    (r"\bchoice\b", "výber"),
    (r"\bsel\b", "výber"),
    (r"\bselect\b", "výber"),
    (r"\ball\s+grd\b", "všetky triedy"),
    (r"\ball\s+grade\b", "všetky triedy"),
    (r"\ball\s+grds\b", "všetky triedy"),
    (r"\bshrt\b", "krátke"),
    (r"\bveg\b", "zelenina"),
    (r"\bdrsng\b", "dresing"),
    (r"\bcrm\b", "krém"),
    (r"\bflr\b", "múka"),
    (r"\bstmd\b", "parené"),
    (r"\bvýrobky bkd\b", "pečené výrobky"),
    (r"\bbkd\b", "pečené"),
    
    # Heating / Cooling
    (r"\bunhtd\b", "neohriate"),
    (r"\bprehtd\b", "predhriate"),
    (r"\bhtd\b", "ohriate"),
    (r"\brefr\b", "chladené"),
    (r"\brúra-htd\b", "pečené v rúre"),
    (r"\btrouba-htd\b", "pečené v rúre"),
    (r"\bovn-htd\b", "pečené v rúre"),
    
    # Newly identified
    (r"\bunckd\b", "surové"),
    (r"\bpreckd\b", "predvarené"),
    (r"\bdehyd\b", "sušené"),
    (r"\bfrz\b", "mrazené"),
    (r"\bdk\b", "tmavé"),
    (r"\binst\b", "instantné"),
    (r"\benr\b", "obohatené"),
    (r"\brehtd\b", "ohriate"),
    (r"\bchopd\b", "sekané"),
    (r"\bbld\b", "varené"),
    (r"\bdrnd\b", "scedené"),
    (r"\bdr\b", "scedené"),
    (r"\bcnd\b", "konzervované"),
    (r"\bsol\b", "pevný podiel"),
    (r"\bliq\b", "tekutina"),
    (r"\bunprep\b", "neupravené"),
    (r"\bbttrmlk\b", "cmar"),
    (r"\bobilniny\s+rte\b", "Raňajkové cereálie"),
    (r"\brte\b", "ready-to-eat"),
    
    # Sweetened/Unsweetened
    (r"\bswtnd\b", "sladené"),
    (r"\bunswtnd\b", "nesladené"),

    # Double commas / spacing cleanup
    (r",\s*,", ","),
    (r"\s+", " "),
]

def context_replace(food_id, category, text):
    is_poultry_or_meat = any(x in food_id.lower() or x in category.lower() for x in ["chicken", "turkey", "poultry", "duck", "goose", "game", "meat", "pork", "beef", "ham", "frank"])
    
    # Define match patterns for "with skin"
    with_skin_patterns = [
        r"\bsskn\b",
        r"\bwithskn\b",
        r"\bwith/skn\b",
        r"\bwith/\s+skn\b",
        r"\bw/\s*skn\b",
        r"\bs/\s*skn\b",
        r"\bs\s+skn\b",
        r"\bin_skn\b",
        r"\bin\s+skn\b",
        r"\bin_skin\b",
        r"\bin\s+skin\b"
    ]
    
    # Define match patterns for "without skin"
    without_skin_patterns = [
        r"\bbezskn\b",
        r"\bbez\s+skn\b",
        r"\bbez/\s*skn\b",
        r"\bwo/\s*skn\b",
        r"\bw/o\s*skn\b",
        r"\bwoskn\b",
        r"\bwithout\s+skin\b",
        r"\bwithout/skn\b"
    ]
    
    if is_poultry_or_meat:
        for p in with_skin_patterns:
            if "in" in p:
                text = re.sub(p, "v koži", text, flags=re.IGNORECASE)
            else:
                text = re.sub(p, "s kožou", text, flags=re.IGNORECASE)
        for p in without_skin_patterns:
            text = re.sub(p, "bez kože", text, flags=re.IGNORECASE)
        text = re.sub(r"\bv\s+koža\b", "v koži", text, flags=re.IGNORECASE)
        text = re.sub(r"\bv\s+koži\b", "v koži", text, flags=re.IGNORECASE)
    else:
        for p in with_skin_patterns:
            if "in" in p:
                text = re.sub(p, "v šupke", text, flags=re.IGNORECASE)
            else:
                text = re.sub(p, "so šupkou", text, flags=re.IGNORECASE)
        for p in without_skin_patterns:
            text = re.sub(p, "bez šupky", text, flags=re.IGNORECASE)
            
        # Non-poultry specific corrections for "meat and skin"
        text = re.sub(r"\bv\s+koža\b", "v šupke", text, flags=re.IGNORECASE)
        text = re.sub(r"\bv\s+koži\b", "v šupke", text, flags=re.IGNORECASE)
        text = re.sub(r"\bmäso\s+a\s+koža\b", "dužina a šupka", text, flags=re.IGNORECASE)
        text = re.sub(r"\bdužina\s+a\s+koža\b", "dužina a šupka", text, flags=re.IGNORECASE)
        text = re.sub(r"\bdužinou\s+&\s+koža\b", "dužinou a šupkou", text, flags=re.IGNORECASE)
        text = re.sub(r"\bvrátane\s+koža\b", "vrátane šupky", text, flags=re.IGNORECASE)
        text = re.sub(r"\bkoža\b", "šupka", text, flags=re.IGNORECASE)
        text = re.sub(r"\bkoži\b", "šupke", text, flags=re.IGNORECASE)
        text = re.sub(r"\bkožu\b", "šupku", text, flags=re.IGNORECASE)
        
    return text

def fix_translation_errors(food_id, text):
    # If ID contains 'wo_sugar' or 'without_sugar' or 'unswtnd'
    if any(x in food_id.lower() for x in ["wo_sugar", "without_sugar", "unswtnd", "unsweetened"]):
        text = text.replace("s cukrom", "bez cukru")
        # Replace standalone words only to avoid duplicate prefix like "nenesladené"
        text = re.sub(r"\bsladené\b", "nesladené", text, flags=re.IGNORECASE)
        text = re.sub(r"\bsladená\b", "nesladená", text, flags=re.IGNORECASE)
        text = re.sub(r"\bsladený\b", "nesladený", text, flags=re.IGNORECASE)
    return text

def deduplicate_words(text):
    text = re.sub(r"\bvarené,\s*varené\b", "varené", text, flags=re.IGNORECASE)
    text = re.sub(r"\bvarená,\s*varená\b", "varená", text, flags=re.IGNORECASE)
    text = re.sub(r"\bvarený,\s*varený\b", "varený", text, flags=re.IGNORECASE)
    text = re.sub(r"\bsurové,\s*surové\b", "surové", text, flags=re.IGNORECASE)
    text = re.sub(r"\bsurová,\s*surová\b", "surová", text, flags=re.IGNORECASE)
    text = re.sub(r"\bsurový,\s*surový\b", "surový", text, flags=re.IGNORECASE)
    text = re.sub(r"\bsušené,\s*sušené\b", "sušené", text, flags=re.IGNORECASE)
    text = re.sub(r"\bsušená,\s*sušená\b", "sušená", text, flags=re.IGNORECASE)
    text = re.sub(r"\bsušený,\s*sušený\b", "sušený", text, flags=re.IGNORECASE)
    return text

def clean_text_with_replacements(text, replacements, food_id, category, is_slovak):
    cleaned = clean_quotes(text)
    
    # Strip USDA suffixes from description before doing other replacements
    cleaned = clean_usda_suffix(cleaned)
    
    # Apply context replacements (Slovak only)
    if is_slovak:
        cleaned = context_replace(food_id, category, cleaned)
    
    # Apply specific translation corrections
    cleaned = fix_translation_errors(food_id, cleaned)
    
    # Apply standard mappings
    for pattern, repl in replacements:
        cleaned = re.sub(pattern, repl, cleaned, flags=re.IGNORECASE)
    
    # Apply word deduplication
    cleaned = deduplicate_words(cleaned)
    
    # Clean up leading/trailing punctuation, spaces and parentheses
    cleaned = cleaned.strip()
    cleaned = re.sub(r'^[,\s\(\)]+', '', cleaned)
    cleaned = re.sub(r'[,\s\(\)]+$', '', cleaned)
    
    # Clean up double commas, extra spaces
    cleaned = re.sub(r',\s*,', ',', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()
    
    # Capitalize first letter
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]
        
    # Make sure it still has a period if it's a description
    if text.endswith('.') and not cleaned.endswith('.'):
        cleaned = cleaned + "."
    elif not text.endswith('.') and cleaned.endswith('.'):
        cleaned = cleaned.rstrip('.')
        
    return cleaned

def clean_file(filepath, replacements, category_name, is_slovak):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return
            
    modified = False
    new_data = {}
    
    for food_id, content in data.items():
        name = content.get("name", "")
        description = content.get("description", "")
        alt_names = content.get("alternative_names", [])
        
        cleaned_name = clean_text_with_replacements(name, replacements, food_id, category_name, is_slovak)
        cleaned_desc = clean_text_with_replacements(description, replacements, food_id, category_name, is_slovak)
        cleaned_alt_names = [clean_text_with_replacements(a, replacements, food_id, category_name, is_slovak) for a in alt_names]
        
        # Ensure description doesn't end with "from the USDA database." or "z databázy USDA."
        cleaned_desc = clean_usda_suffix(cleaned_desc)
        
        if cleaned_name != name or cleaned_desc != description or cleaned_alt_names != alt_names:
            modified = True
            content["name"] = cleaned_name
            content["description"] = cleaned_desc
            content["alternative_names"] = cleaned_alt_names
            
        new_data[food_id] = content
        
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        print(f"[CLEANED] {os.path.basename(filepath)}")
    else:
        print(f"[NO CHANGES] {os.path.basename(filepath)}")

def main():
    print("Starting translation files cleanup...")
    
    # Process English translation files
    en_dir = os.path.join(I18N_DIR, "en")
    print("\n--- Cleaning English Files ---")
    for file in os.listdir(en_dir):
        if file.endswith(".json") and file != "common.json":
            category_name = file[:-5]
            clean_file(os.path.join(en_dir, file), EN_REPLACEMENTS, category_name, is_slovak=False)
            
    # Process Slovak translation files
    sk_dir = os.path.join(I18N_DIR, "sk")
    print("\n--- Cleaning Slovak Files ---")
    for file in os.listdir(sk_dir):
        if file.endswith(".json") and file != "common.json":
            category_name = file[:-5]
            clean_file(os.path.join(sk_dir, file), SK_REPLACEMENTS, category_name, is_slovak=True)
            
    print("\nCleanup completed.")

if __name__ == "__main__":
    main()
