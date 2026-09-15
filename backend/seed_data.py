import asyncio
import logging
import time

from google.genai.errors import ClientError

from embedding_service import EmbeddingService
from models import Prestataire
from vector_store import InMemoryVectorStore

logger = logging.getLogger(__name__)

SEED_PRESTATAIRES: list[Prestataire] = [
    # --- Construction (3) ---
    Prestataire(
        name="Jean Dupont Plumbing",
        specialty="Plumbing",
        description="Experienced plumber specializing in emergency repairs, sanitary fixture installation, and drain unclogging. Fast response within 1 hour.",
        services=["leak repair", "drain unclogging", "sanitary installation", "water heater"],
        city="Paris",
        country="France",
        hourly_rate=55.0,
        phone="+33 6 12 34 56 78",
        email="jean.dupont@plumbing.com",
        rating=4.7,
    ),
    Prestataire(
        name="Elec Pro Services",
        specialty="Electrical",
        description="Certified electrician for new installations, code compliance upgrades, and electrical troubleshooting for residential and commercial buildings.",
        services=["electrical installation", "code compliance", "troubleshooting", "electrical panel", "home automation"],
        city="Lyon",
        country="France",
        hourly_rate=50.0,
        phone="+33 6 23 45 67 89",
        email="contact@elecpro.com",
        rating=4.5,
    ),
    Prestataire(
        name="Colors & Finishes",
        specialty="Painting",
        description="House painter for interior and exterior work. Wallpaper hanging, plastering, and facade renovation.",
        services=["interior painting", "exterior painting", "wallpaper", "plastering", "facade renovation"],
        city="Marseille",
        country="France",
        hourly_rate=40.0,
        phone="+33 6 34 56 78 90",
        email="info@colors-finishes.com",
        rating=4.3,
    ),
    # --- Beauty (2) ---
    Prestataire(
        name="Elegance Salon",
        specialty="Hairdressing",
        description="Hair salon offering cuts, coloring, highlights, and event hairstyling. Specialist in curly and coily hair.",
        services=["haircut", "coloring", "highlights", "straightening", "wedding hairstyle"],
        city="Bordeaux",
        country="France",
        hourly_rate=45.0,
        phone="+33 5 56 78 90 12",
        email="booking@elegance-salon.com",
        rating=4.8,
    ),
    Prestataire(
        name="Zen Beauty Institute",
        specialty="Esthetics",
        description="Beauty institute offering facial care, waxing, manicures, and relaxing massages. Organic and natural products.",
        services=["facial care", "waxing", "manicure", "pedicure", "massage"],
        city="Nice",
        country="France",
        hourly_rate=50.0,
        phone="+33 4 93 12 34 56",
        email="contact@zen-beauty.com",
        rating=4.6,
    ),
    # --- Auto (2) ---
    Prestataire(
        name="Martin Garage",
        specialty="Auto mechanics",
        description="Multi-brand garage for maintenance, repair, oil changes, brakes, and electronic diagnostics. Free quote.",
        services=["oil change", "brakes", "diagnostics", "clutch", "air conditioning"],
        city="Toulouse",
        country="France",
        hourly_rate=60.0,
        phone="+33 5 61 23 45 67",
        email="martin.garage@auto.com",
        rating=4.4,
    ),
    Prestataire(
        name="Prestige Bodywork",
        specialty="Auto bodywork",
        description="Specialist in bodywork repair, paintless dent removal, automotive painting, and polishing.",
        services=["dent removal", "auto painting", "polishing", "bumper repair", "rust protection"],
        city="Nantes",
        country="France",
        hourly_rate=65.0,
        phone="+33 2 40 12 34 56",
        email="contact@prestige-bodywork.com",
        rating=4.2,
    ),
    # --- IT (2) ---
    Prestataire(
        name="WebDev Studio",
        specialty="Web development",
        description="Freelance web developer specializing in landing pages, e-commerce, and custom web applications. React, Node.js, Python stack.",
        services=["landing page", "e-commerce", "web application", "SEO", "maintenance"],
        city="Paris",
        country="France",
        hourly_rate=75.0,
        phone="+33 6 45 67 89 01",
        email="hello@webdev-studio.com",
        rating=4.9,
    ),
    Prestataire(
        name="SOS Computing",
        specialty="Computer repair",
        description="On-site computer repair: PC/Mac repair, virus removal, data recovery, WiFi network setup.",
        services=["PC repair", "virus removal", "data recovery", "WiFi setup", "training"],
        city="Lille",
        country="France",
        hourly_rate=45.0,
        phone="+33 3 20 12 34 56",
        email="help@sos-computing.com",
        rating=4.3,
    ),
    # --- Health (2) ---
    Prestataire(
        name="Kine Plus Clinic",
        specialty="Physiotherapy",
        description="Certified physiotherapist for post-operative rehabilitation, back pain treatment, sports and respiratory physiotherapy.",
        services=["rehabilitation", "back pain", "sports physiotherapy", "respiratory physiotherapy", "therapeutic massage"],
        city="Strasbourg",
        country="France",
        hourly_rate=55.0,
        phone="+33 3 88 12 34 56",
        email="booking@kine-plus.com",
        rating=4.7,
    ),
    Prestataire(
        name="Express Home Care",
        specialty="Nursing care",
        description="Home-visit nurse for injections, dressings, IV drips, blood draws, and post-hospitalization follow-up. Available 7 days a week.",
        services=["injections", "dressings", "IV drips", "blood draws", "post-op follow-up"],
        city="Montpellier",
        country="France",
        hourly_rate=40.0,
        phone="+33 4 67 12 34 56",
        email="contact@home-care.com",
        rating=4.8,
    ),
    # --- Home (2) ---
    Prestataire(
        name="Clean & Shine",
        specialty="Cleaning",
        description="Professional home cleaning service. Regular cleaning, deep cleaning, post-move cleaning. Trusted staff.",
        services=["regular cleaning", "deep cleaning", "ironing", "window cleaning", "post-move cleaning"],
        city="Lyon",
        country="France",
        hourly_rate=25.0,
        phone="+33 6 56 78 90 12",
        email="reservations@clean-shine.com",
        rating=4.5,
    ),
    Prestataire(
        name="Eden Gardens",
        specialty="Gardening",
        description="Landscape gardener for garden maintenance, hedge trimming, lawn mowing, green space design, and tree pruning.",
        services=["lawn mowing", "hedge trimming", "tree pruning", "garden design", "automatic watering"],
        city="Rennes",
        country="France",
        hourly_rate=35.0,
        phone="+33 2 99 12 34 56",
        email="contact@eden-gardens.com",
        rating=4.4,
    ),
    # --- Miscellaneous (2) ---
    Prestataire(
        name="Lumiere Photo Studio",
        specialty="Photography",
        description="Professional photographer for weddings, portraits, corporate events, and product shoots. Retouching included.",
        services=["wedding", "portrait", "event", "product shoot", "photo retouching"],
        city="Paris",
        country="France",
        hourly_rate=80.0,
        phone="+33 6 67 89 01 23",
        email="booking@lumiere-studio.com",
        rating=4.9,
    ),
    Prestataire(
        name="Math+ Private Tutor",
        specialty="Private tutoring",
        description="Certified private tutor for math, physics, and chemistry classes from middle school to prep courses. Study skills and exam preparation.",
        services=["math", "physics", "chemistry", "high school exam prep", "entrance exam prep"],
        city="Grenoble",
        country="France",
        hourly_rate=35.0,
        phone="+33 4 76 12 34 56",
        email="classes@math-plus.com",
        rating=4.6,
    ),
]


async def load_seed_prestataires(
    store: InMemoryVectorStore,
    embed_svc: EmbeddingService,
    max_retries: int = 3,
) -> None:
    start = time.time()
    total = len(SEED_PRESTATAIRES)
    logger.info("Loading %d seed providers...", total)

    for i, prestataire in enumerate(SEED_PRESTATAIRES):
        for attempt in range(max_retries):
            try:
                embedding = embed_svc.embed_prestataire(prestataire)
                store.add(prestataire, embedding)
                logger.info("[%d/%d] Loaded: %s (%s)", i + 1, total, prestataire.name, prestataire.specialty)
                break
            except ClientError as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    wait = 2 ** (attempt + 1)
                    logger.warning("Rate limited, retrying in %ds...", wait)
                    await asyncio.sleep(wait)
                else:
                    raise

    elapsed = time.time() - start
    logger.info("Seed loading complete: %d providers in %.1fs", store.count, elapsed)
