SOURCE_GROUPS = {
    "خبرگزاری‌های داخلی": {
        "label": "خبرگزاری‌های داخلی",
        "domains": ["irna.com", "isna.ir", "mehrnews.com", "tasnimnews.com", "farsnews.ir", "ilna.ir", "ana.ir"],
    },
    "خبرگزاری‌های خارجی": {
        "label": "خبرگزاری‌ها و رسانه‌های خارجی",
        "domains": ["reuters.com", "apnews.com", "bbc.com", "dw.com", "france24.com", "aljazeera.com", "asharq.com"],
    },
    "دانشگاهی": {
        "label": "مراکز پژوهشی دانشگاهی",
        "domains": ["harvard.edu", "stanford.edu", "mit.edu", "columbia.edu", "georgetown.edu", "ox.ac.uk", "cam.ac.uk", "uchicago.edu", "princeton.edu"],
    },
    "راهبردی و سیاسی": {
        "label": "مراکز مطالعات راهبردی و سیاسی",
        "domains": ["csis.org", "brookings.edu", "chathamhouse.org", "carnegieendowment.org", "cfr.org", "iiss.org", "rand.org", "ecfr.eu"],
    },
    "نظامی و امنیتی": {
        "label": "مراکز نظامی و امنیتی",
        "domains": ["iiss.org", "rand.org", "rusi.org", "inss.org.il", "csis.org", "nato.int"],
    },
    "اقتصاد و انرژی": {
        "label": "اقتصاد و انرژی",
        "domains": ["imf.org", "worldbank.org", "iea.org", "opec.org", "unctad.org", "ec.europa.eu", "energy.gov"],
    },
    "رسمی بین‌المللی": {
        "label": "منابع رسمی بین‌المللی",
        "domains": ["un.org", "undp.org", "dppa.un.org", "unmissions.org", "nato.int", "europa.eu", "eeas.europa.eu", "osce.org", "iaea.org", "who.int"],
    },
    "عربی": {
        "label": "خبرگزاری‌ها و مراکز پژوهشی عربی",
        "domains": ["aljazeera.com", "studies.aljazeera.net", "asharq.com", "arabcenterdc.org", "ecssr.ae", "gulf-research.org", "carnegie-mec.org"],
    },
    "اسرائیلی": {
        "label": "رسانه‌ها و مراکز پژوهشی اسرائیلی",
        "domains": ["inss.org.il", "timesofisrael.com", "jpost.com", "haaretz.com", "idi.org.il", "israelpolicyforum.org"],
    },
    "غیررسمی": {
        "label": "منابع غیررسمی / تحلیلگران",
        "domains": ["substack.com", "medium.com", "foreignpolicy.com", "responsiblestatecraft.org", "al-monitor.com"],
    },
}

ALL_DOMAINS = sorted({d for group in SOURCE_GROUPS.values() for d in group["domains"]})


def get_group(name):
    return SOURCE_GROUPS.get(name)


def source_groups_for_query(group):
    if not group or group == "همه":
        return SOURCE_GROUPS
    return {group: SOURCE_GROUPS[group]} if group in SOURCE_GROUPS else SOURCE_GROUPS
