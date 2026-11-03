"""Everything the profile says about you lives in this file.

Edit it, then run `python scripts/build.py` to regenerate the artwork in /assets.
"""

LOGIN = "MohamedSayedAbdelrazek"

FULL_NAME = "Mohamed Sayed Abdulrazek"
STATUS = "Open to opportunities"
LOCATION = "Egypt"
WEBSITE = "mohamedsayedabdelrazek.github.io"
EMAIL = "m.s.abdulrazek@gmail.com"

# Hero banner. The first role is the one shown when animation is off.
GREETING = "Hi, I'm"
ROLES = [
    ".NET Backend Developer",
    "C# · Entity Framework Core · LINQ",
    "Backend developer with a Laravel background",
]
TAGLINE = "I build clean, reliable back-ends and REST APIs, now with C# and .NET."
CURRENTLY = ("Currently", ".NET Diploma at Route")

# "About me" card: a short bio next to a few key facts as (label, headline, detail).
ABOUT_BIO = (
    "I'm a backend developer from Egypt. I started out building REST APIs and full web apps "
    "with PHP, Laravel and MySQL, and I'm now growing into the .NET world with C# and "
    "Entity Framework Core. I care about clean code, clear design and software that is easy to maintain."
)
ABOUT_FACTS = [
    ("Now", ".NET Diploma at Route", "C#, OOP, LINQ, EF Core"),
    ("Before", "Backend development", "PHP, Laravel & MySQL"),
    ("Coursework", "Machine Learning", "Python & Image Processing"),
    ("Looking for", "Opportunities & internships", "Backend and .NET roles"),
]

# Tech-stack card: (group title, short caption, technology keys). The first group is highlighted.
STACK = [
    (".NET", "current focus", ["csharp", "dotnet", "efcore", "linq"]),
    ("Previously", "PHP backend", ["php", "laravel", "mysql", "restapi"]),
    ("Languages", "also used", ["python", "java", "cplusplus"]),
    ("Web", "front-end basics", ["html5", "css"]),
    ("Tools", "everyday workflow", ["git", "github", "postman", "vscode"]),
    ("Learning", "coursework", ["ml", "imageproc"]),
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
        "url": f"https://{WEBSITE}/",
    },
]

FOOTER_LINE = "Thanks for visiting — let's build something great together."
FOOTER_SUB = "Feel free to reach out on LinkedIn or by email."
