"""normalize (fu7): variant grid — legal forms, umlauts, punctuation;
exact-match-only."""

from leadhs.normalize import identity, ident_type_of, norm_ident, norm_manufacturer, norm_name


def test_legal_form_suffix_strip():
    assert norm_manufacturer("Acme GmbH") == "acme"
    assert norm_manufacturer("Acme Paints AB") == "acme paints"
    assert norm_manufacturer("Beier Oy") == "beier"
    assert norm_manufacturer("Farben Ltd") == "farben"
    assert norm_manufacturer("Peintures S.A.") == "peintures"
    assert norm_manufacturer("Maalit A/S") == "maalit"
    # repeated stripping (nested forms)
    assert norm_manufacturer("Acme GmbH & Co. KG") == "acme gmbh"


def test_case_and_diacritic_fold():
    assert norm_manufacturer("MÜLLER Farben") == norm_manufacturer("Müller Farben GmbH")
    assert norm_manufacturer("NORDIC COATINGS AB") == norm_manufacturer("Nordic Coatings ab")


def test_punctuation_collapse():
    assert norm_manufacturer("Acme, Ltd.") == "acme"
    assert norm_manufacturer("A - B  Farben  GmbH") == "a b farben"


def test_single_token_kept():
    assert norm_manufacturer("TINTA") == "tinta"
    assert norm_manufacturer("") == ""
    assert norm_manufacturer(None) == ""


def test_norm_ident_strips_separators_keeps_case():
    assert norm_ident("DE-1234") == "DE1234"
    assert norm_ident("DE 1234") == "DE1234"
    assert norm_ident(" DE\u00a01234 ") == "DE1234"
    assert norm_ident("007") == "007"  # leading zero survives
    assert norm_ident(None) == ""


def test_norm_name_folds_but_keeps_words():
    assert norm_name("Müller Blau Seidenmatt") == "müller blau seidenmatt".replace("ü", "u")
    assert norm_name("  Paint   A  ") == "paint a"


def test_ident_type_hints():
    assert ident_type_of("licence_no") == "licence"
    assert ident_type_of("EAN") == "gtin"
    assert ident_type_of("article_code") == "article"
    assert ident_type_of("product_name") == "none"
    assert ident_type_of(None) == "none"


def test_identity_basis_pinning():
    ident = identity("Acme GmbH", "DE-1234", "licence_no", "Paint A")
    assert ident == {
        "manufacturer_raw": "Acme GmbH",
        "manufacturer_norm": "acme",
        "ident_raw": "DE-1234",
        "ident_norm": "DE1234",
        "ident_type": "licence",
        "ident_basis": "ident",
    }
    # name fallback: no ident → basis name, type none
    ident = identity("Acme GmbH", "", "licence_no", "Paint  A")
    assert ident["ident_basis"] == "name"
    assert ident["ident_type"] == "none"
    assert ident["ident_norm"] == "paint a"
