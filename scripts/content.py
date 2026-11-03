"""Everything the profile says about you lives in this file.

Edit it, then run `python scripts/build.py` to regenerate the artwork in /assets.
"""

LOGIN = "MohamedSayedAbdelrazek"

NAME_LINE_1 = "Mohamed Sayed"
NAME_LINE_2 = "Abdelrazek"
FULL_NAME = f"{NAME_LINE_1} {NAME_LINE_2}"
MONOGRAM = "MS"
HANDLE = "~/mohamed-sayed"
STATUS = "OPEN TO OPPORTUNITIES"
LOCATION = "Egypt"
WEBSITE = "mosayed.me"
EMAIL = "m.s.abdulrazek@gmail.com"

# Cycled by the typing effect in the hero banner.
ROLES = [
    "Backend Developer",
    "Laravel Artisan",
    "REST API Designer",
    "Clean Code Advocate",
    "System Design Enthusiast",
]
TAGLINE = "Computer Science student building clean, reliable back-ends."
HERO_CHIPS = ["PHP", "Laravel", "C# / .NET", "MySQL", "REST APIs"]

# The animated request that travels through the hero diagram.
LIFECYCLE = ["Client", "Router", "Middleware", "Controller", "Service", "MySQL"]
REQUEST = ("GET", "/api/v1/developer")
RESPONSE_BODY = '{ "role": "backend", "status": "shipping" }'

# Rendered as `php artisan about` in the terminal card.
# Item styles: None (default), "ok" (green, bold) or "link" (accent).
ABOUT = [
    (
        "Developer",
        [
            ("Name", FULL_NAME, None),
            ("Role", "Backend Developer", None),
            ("Education", "Computer Science Student", None),
            ("Location", LOCATION, None),
            ("Status", STATUS, "ok"),
        ],
    ),
    (
        "Stack",
        [
            ("Backend", "PHP · Laravel · C# · .NET", None),
            ("Data & APIs", "MySQL · RESTful APIs", None),
            ("Frontend", "HTML5 · CSS3", None),
            ("Languages", "Java · C++ · Python", None),
            ("Tooling", "Git · GitHub · Postman · VS Code", None),
        ],
    ),
    (
        "Mindset",
        [
            ("Believes in", "Clean code · Robust design · Practical solutions", None),
            ("Exploring", "Design Patterns · System Architecture", None),
            ("Off-duty", "Solving programming puzzles", None),
        ],
    ),
    (
        "Contact",
        [
            ("Email", EMAIL, "link"),
            ("Portfolio", WEBSITE, "link"),
        ],
    ),
]

# Rack units in the tech-stack card: (unit label, caption, technology keys).
STACK = [
    ("BACKEND", "core services", ["php", "laravel", "csharp", "dotnet"]),
    ("DATA · API", "storage & contracts", ["mysql", "restapi", "postman"]),
    ("FRONTEND", "interfaces", ["html5", "css"]),
    ("LANGUAGES", "general purpose", ["java", "cplusplus", "python"]),
    ("TOOLING", "daily workflow", ["git", "github", "vscode"]),
    ("FOCUS", "levelling up", ["patterns", "architecture", "problems", "teamwork"]),
]

# Contact buttons under the hero.
LINKS = [
    {
        "id": "linkedin",
        "label": "LinkedIn",
        "sub": "mohamed-sayed-abdulrazek",
        "icon": "linkedin",
        "url": "https://www.linkedin.com/in/mohamed-sayed-abdulrazek/",
    },
    {
        "id": "email",
        "label": "Email",
        "sub": EMAIL,
        "icon": "gmail",
        "url": f"mailto:{EMAIL}",
    },
    {
        "id": "portfolio",
        "label": "Portfolio",
        "sub": WEBSITE,
        "icon": "globe",
        "url": f"https://{WEBSITE}",
    },
]

FOOTER_HEADERS = [
    ("HTTP/1.1", "200 OK"),
    ("Content-Type:", "application/thanks+json"),
    ("Connection:", "keep-alive"),
]
FOOTER_LINE = "Let's build something reliable together."
