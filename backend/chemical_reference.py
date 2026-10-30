# Structured chemical-control reference (product / dosage / FRAC-IRAC resistance group)
# Sourced from: "Sugarcane Chemical Control Practices Framework" (chemicals_final_.pdf)
#
# Keys match the disease/pest names used in disease_practices.py / disease_practices_mr.py
# so the API can attach this table alongside the existing narrative "chemical" bullet list.
#
# Each entry is a list of {"product", "dosage", "group"} dicts, in the same order as the
# source document's Section 3 registry.

CHEMICAL_REFERENCE = {
    "Brown Rust": [
        {"product": "Tebuconazole 25.9 EC", "dosage": "1 ml/L", "group": "FRAC 3, CIB"},
        {"product": "Azoxystrobin 18.2% + Difenoconazole 11.4% SC", "dosage": "1 ml/L", "group": "FRAC 11 + 3, CIB"},
        {"product": "Azoxystrobin 23 SC", "dosage": "1 ml/L", "group": "FRAC 11"},
        {"product": "Propiconazole 25 EC", "dosage": "1 ml/L", "group": "FRAC 3"},
    ],
    "Brown Spot": [
        {"product": "Mancozeb 75 WP", "dosage": "1.5 g/L", "group": "FRAC M03"},
        {"product": "Tebuconazole 25.9 EC", "dosage": "1 ml/L", "group": "FRAC 3, CIB"},
        {"product": "Azoxystrobin 18.2% + Difenoconazole 11.4% SC", "dosage": "1 ml/L", "group": "FRAC 11 + 3, CIB"},
        {"product": "Propiconazole 25 EC", "dosage": "1 ml/L", "group": "FRAC 3"},
        {"product": "Azoxystrobin 23 SC", "dosage": "1 ml/L", "group": "FRAC 11"},
    ],
    "Early Shoot Borer": [
        {"product": "Chlorantraniliprole 18.5 SC", "dosage": "0.25 ml/L", "group": "IRAC 28, CIB"},
        {"product": "Carbofuran 3G", "dosage": "8.1 kg/acre by drip", "group": "IRAC 1A, CIB"},
        {"product": "Chloropyrifos 20 EC", "dosage": "2.5 ml/L", "group": "IRAC 1B, CIB"},
        {"product": "Flubendiamide 39.35 SC", "dosage": "0.3 ml/L", "group": "IRAC 28, CIB"},
        {"product": "Fipronil 0.3 GR", "dosage": "10.12 kg/acre by drip", "group": "IRAC 2B, CIB"},
    ],
    "Eye Spot": [
        {"product": "Mancozeb 75 WP", "dosage": "1.5 g/L", "group": "FRAC M03, VSI"},
        {"product": "Copper Oxychloride 50 WP", "dosage": "2 g/L", "group": "FRAC M01, VSI"},
        {"product": "Propiconazole 25 EC", "dosage": "1 ml/L", "group": "FRAC 3"},
        {"product": "Azoxystrobin 23 SC", "dosage": "1 ml/L", "group": "FRAC 11"},
    ],
    "Grassy Shoot Disease": [
        {"product": "Imidacloprid 17.8 SL", "dosage": "0.5 ml/L", "group": "IRAC 4A, TNAU"},
        {"product": "Thiamethoxam 25 WG", "dosage": "0.5 g/L", "group": "IRAC 4A"},
        {"product": "Flonicamid 50 WG", "dosage": "0.3-0.4 g/L", "group": "IRAC 29"},
        {"product": "Carbendazim 50 WP + Urea (sett treatment)", "dosage": "1 g/L + 10 g/L", "group": "FRAC 1, TNAU"},
    ],
    "Internode Borer": [
        {"product": "Chlorantraniliprole 18.5 SC", "dosage": "0.25 ml/L", "group": "IRAC 28"},
        {"product": "Flubendiamide 39.35 SC", "dosage": "0.3 ml/L", "group": "IRAC 28"},
        {"product": "Fipronil 5 SC", "dosage": "1 ml/L", "group": "IRAC 2B"},
    ],
    "Leaf Footed Bug": [
        {"product": "Thiamethoxam 25 WG (Actara)", "dosage": "0.5 g/L", "group": "IRAC 4A"},
        {"product": "Dinotefuran 20 SG (Token)", "dosage": "0.4 g/L", "group": "IRAC 4A"},
        {"product": "Flonicamid 50 WG (Ulala)", "dosage": "0.3-0.4 g/L", "group": "IRAC 29"},
    ],
    "Mosaic": [
        {"product": "Imidacloprid 17.8 SL", "dosage": "0.5 ml/L", "group": "IRAC 4A, ICAR"},
        {"product": "Dinotefuran 20 SG", "dosage": "0.4 g/L", "group": "IRAC 4A, ICAR"},
        {"product": "Thiamethoxam 25 WG", "dosage": "0.5 g/L", "group": "IRAC 4A"},
        {"product": "Flonicamid 50 WG", "dosage": "0.3-0.4 g/L", "group": "IRAC 29"},
    ],
    "Pokkah Boeng": [
        {"product": "Carbendazim 50 WP", "dosage": "1 g/L", "group": "FRAC 1, CIB, VSI"},
        {"product": "Mancozeb 75 WP", "dosage": "1.5 g/L", "group": "FRAC M03, CIB, VSI"},
        {"product": "Propiconazole 25 EC", "dosage": "1 ml/L", "group": "FRAC 3"},
        {"product": "Azoxystrobin + Difenoconazole", "dosage": "1 ml/L", "group": "FRAC 11 + 3"},
    ],
    "Pyrilla": [
        {"product": "Chloropyrifos 20 EC", "dosage": "2.5 ml/L", "group": "IRAC 1B, CIB"},
        {"product": "Imidacloprid 17.8 SL (Confidor Super)", "dosage": "0.5 ml/L", "group": "IRAC 4A"},
        {"product": "Flonicamid 50 WG (Ulala)", "dosage": "0.3-0.4 g/L", "group": "IRAC 29"},
        {"product": "Thiamethoxam 25 WG (Actara)", "dosage": "0.5 g/L", "group": "IRAC 4A"},
    ],
    "Red Rot": [
        {"product": "Carbendazim 50 WP", "dosage": "1 g/L", "group": "FRAC 1, CIB, VSI, TNAU"},
        {"product": "Azoxystrobin 18.2% + Difenoconazole 11.4% SC", "dosage": "1 ml/L", "group": "FRAC 11 + 3, CIB"},
        {"product": "Propiconazole 25 EC", "dosage": "1 ml/L", "group": "FRAC 3"},
        {"product": "Tebuconazole 25.9 EC", "dosage": "1 ml/L", "group": "FRAC 3"},
    ],
    "Scale Insect": [
        {"product": "Monocrotophos 36 SL", "dosage": "2 ml/L", "group": "IRAC 1B, CIB"},
        {"product": "Quinalphos 25 EC", "dosage": "2 ml/L", "group": "IRAC 1B, CIB"},
        {"product": "Buprofezin 25 SC (Applaud)", "dosage": "2 ml/L", "group": "IRAC 16"},
        {"product": "Spirotetramat 150 OD (Movento)", "dosage": "1 ml/L", "group": "IRAC 23"},
        {"product": "Pyriproxyfen 10 EC (Lano)", "dosage": "2 ml/L", "group": "IRAC 7C"},
        {"product": "Flonicamid 50 WG (Ulala)", "dosage": "0.3-0.4 g/L", "group": "IRAC 29"},
    ],
    "Whiplash Smut": [
        {"product": "Carbendazim 50 WP", "dosage": "1 g/L", "group": "FRAC 1, CIB"},
        {"product": "Azoxystrobin 18.2% + Difenoconazole 11.4% SC", "dosage": "1 ml/L", "group": "FRAC 11 + 3, CIB"},
        {"product": "Propiconazole 25 EC", "dosage": "1 ml/L", "group": "FRAC 3"},
        {"product": "Tebuconazole 25.9 EC", "dosage": "1 ml/L", "group": "FRAC 3"},
    ],
    "Wilt": [
        {"product": "Carbendazim 50 WP", "dosage": "1 g/L", "group": "FRAC 1, VSI"},
        {"product": "Propiconazole 25 EC", "dosage": "1 ml/L", "group": "FRAC 3"},
        {"product": "Tebuconazole 25.9 EC", "dosage": "1 ml/L", "group": "FRAC 3"},
    ],
    "Woolly Aphids": [
        {"product": "Imidacloprid 17.8 SL", "dosage": "0.5 ml/L", "group": "IRAC 4A"},
        {"product": "Flonicamid 50 WG (Ulala)", "dosage": "0.3-0.4 g/L", "group": "IRAC 29"},
        {"product": "Thiamethoxam 25 WG (Actara)", "dosage": "0.5 g/L", "group": "IRAC 4A"},
    ],
    "Top Shoot Borer": [
        {"product": "Chlorantraniliprole 18.5 SC", "dosage": "0.25 ml/L", "group": "IRAC 28, CIB"},
        {"product": "Chlorantraniliprole 0.4 GR", "dosage": "7.6 kg/acre by drip", "group": "IRAC 28, CIB"},
        {"product": "Flubendiamide 39.35 SC", "dosage": "0.3 ml/L", "group": "IRAC 28"},
        {"product": "Fipronil 5 SC", "dosage": "1 ml/L", "group": "IRAC 2B"},
    ],
    "White Grub": [
        {"product": "Fipronil 40% + Imidacloprid 40% WG", "dosage": "0.4 g/L", "group": "IRAC 2B + 4A, CIB"},
        {"product": "Thiamethoxam 0.9% + Fipronil 0.2% GR", "dosage": "6.1 kg/acre by drip", "group": "IRAC 4A + 2B, CIB"},
        {"product": "Chlorantraniliprole 0.4 GR", "dosage": "4 kg/acre", "group": "IRAC 28"},
        {"product": "Imidacloprid 17.8 SL", "dosage": "0.5 ml/L", "group": "IRAC 4A"},
    ],
    "Mealy Bug": [
        {"product": "Monocrotophos 36 SL", "dosage": "2 ml/L", "group": "IRAC 1B, CIB"},
        {"product": "Quinalphos 25 EC", "dosage": "2 ml/L", "group": "IRAC 1B, CIB"},
        {"product": "Buprofezin 25 SC (Applaud)", "dosage": "2 ml/L", "group": "IRAC 16"},
        {"product": "Spirotetramat 150 OD (Movento)", "dosage": "1 ml/L", "group": "IRAC 23"},
        {"product": "Pyriproxyfen 10 EC (Lano)", "dosage": "2 ml/L", "group": "IRAC 7C"},
        {"product": "Flonicamid 50 WG (Ulala)", "dosage": "0.3-0.4 g/L", "group": "IRAC 29"},
    ],
    "Yellow Leaf Disease": [
        {"product": "Imidacloprid 17.8 SL", "dosage": "0.5 ml/L", "group": "IRAC 4A, ICAR"},
        {"product": "Dinotefuran 20 SG (Token)", "dosage": "0.4 g/L", "group": "IRAC 4A, ICAR"},
        {"product": "Flonicamid 50 WG", "dosage": "0.3-0.4 g/L", "group": "IRAC 29"},
        {"product": "Thiamethoxam 25 WG", "dosage": "0.5 g/L", "group": "IRAC 4A"},
    ],
    "Leafscald": [
        {"product": "Copper Oxychloride 50 WP", "dosage": "2 g/L", "group": "FRAC M01"},
        {"product": "Copper Hydroxide", "dosage": "2 g/L", "group": "FRAC M01"},
    ],
}


def get_chemical_reference(disease_name: str):
    """Return the structured chemical reference table for a disease/pest, or an empty list."""
    return CHEMICAL_REFERENCE.get(disease_name, [])
