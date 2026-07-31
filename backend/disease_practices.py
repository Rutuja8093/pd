# All disease practices from the document
DISEASE_PRACTICES = {
    "Brown Rust": {
        "cultural": ["Keep 4-5 feet spacing for good airflow and healthy growth", "Use less urea and more potash to strengthen plants", "Rotate crops; avoid growing sugarcane in the same field every season"],
        "mechanical": ["Remove lower dry and infected leaves", "Uproot infected plants and bury them to stop spread"],
        "biological": ["Treat seed canes in hot water (50°C for 2 hours)", "Spray Pseudomonas fluorescens (10 g/L water) on leaves", "Mix Trichoderma viride with organic manure and apply in soil"],
        "chemical": ["Propiconazole: 400 ml/acre in 200 L water", "Difenoconazole: 150 ml/acre in 200 L water", "Carbendazim: 400 g/acre in 200 L water"],
        "timing": ["Early morning (6-9 AM) or evening (4-6:30 PM)", "Avoid spraying during hot daytime"]
    },
    "Brown Spot": {
        "cultural": ["Keep 4-5 feet spacing for good air flow", "Rotate with crops like legumes after sugarcane", "Use disease-resistant sugarcane varieties"],
        "mechanical": ["Remove lower dry and infected leaves", "Remove and bury or burn infected plants", "Keep field borders clean from weeds"],
        "biological": ["Treat seed canes in hot water (50°C for 2 hours)", "Spray Pseudomonas fluorescens (10 g/L water) on leaves", "Mix Trichoderma viride with manure before applying to soil"],
        "chemical": ["Carbendazim 50% WP: 400 g/acre in 200 L water (early stage)", "Propiconazole 25% EC: 400 ml/acre in 200 L water (fast spread control)", "Difenoconazole 25% EC: 150 ml/acre in 200 L water (protect new leaves)"],
        "timing": ["First spray: at first spot appearance (Aug/Sept)", "Second spray: repeat after 15 days if weather is humid/cloudy", "Spray early morning (6-9 AM) or evening (4-6:30 PM)"]
    },
    "Early Shoot Borer": {
        "cultural": ["Plant sugarcane early (Dec-Jan) to avoid pest season", "Give light and regular irrigation in summer", "Grow pulses like cowpea or green gram between rows", "Use dry leaves as mulch to keep soil cool and stop egg laying"],
        "mechanical": ["Remove and destroy dead hearts with caterpillars inside", "Use light traps in March-April to catch moths", "Do earthing up after 4-6 weeks of planting to protect base"],
        "biological": ["Release Trichogramma wasps every 7-10 days from 4th week", "Spray Granulosis virus at 35 and 50 days to kill borers"],
        "chemical": ["Thiamethoxam: 160 g/acre in 200 L water (early protection)", "Chlorantraniliprole: 150 ml/acre in 200 L water (30-45 days protection)"],
        "timing": ["First spray: March-April at 30-45 days crop stage", "Spray near base and soil where borer enters", "Spray early morning (6-8:30 AM) or evening (5:30-7 PM)"]
    },
    "Eye Spot": {
        "cultural": ["Avoid excess urea; it makes plants soft and weak", "Use more potash to strengthen leaves", "Keep 4-5 feet spacing for good air flow"],
        "mechanical": ["Remove and bury infected plants to stop spread", "Keep field edges clean from weeds and grasses"],
        "biological": ["Spray Pseudomonas fluorescens (10 g/L water) on leaves", "Treat seed canes in hot water (50°C for 2 hours)"],
        "chemical": ["Carbendazim: 400 g/acre in 200 L water (early infection)", "Propiconazole: 400 ml/acre in 200 L water (fast spread in cold/fog)", "Difenoconazole: 150 ml/acre in 200 L water (protect new leaves)"],
        "timing": ["Spray on top young leaves (crown)", "Start in October when red lines appear", "Repeat after 15 days if fog continues", "Spray late afternoon (4-6:30 PM) after dew dries"]
    },
    "Grassy Shoot Disease": {
        "cultural": ["Use only healthy, disease-free seed canes", "Do not take ratoon crop if disease is present"],
        "mechanical": ["Remove and bury yellow, grass-like infected plants", "Clean tools with boiling water or disinfectant"],
        "biological": ["Treat seed pieces in hot water (50°C for 2 hours)", "Use tissue-cultured (lab-grown) disease-free plants"],
        "chemical": ["Carbendazim: 200 g/acre, dip seed pieces before planting", "Dinotefuran: 25 g/acre in 200 L water, spray to kill disease-spreading insects"],
        "timing": ["Spray during July-August (25-35°C, humid weather)", "Cover whole plant, especially leaf underside and middle", "Spray early morning (6-9 AM) or evening (4:30-6:30 PM)"]
    },
    "Internode Borer": {
        "cultural": ["Give regular irrigation to keep plants healthy", "Apply potash early to make cane strong and hard"],
        "mechanical": ["Remove lower dry leaves from 5th month to stop moth hiding", "Cut and destroy badly damaged canes after monsoon"],
        "biological": ["Release Trichogramma chilonis (2.5 cards/acre) every 15 days from 4th month to harvest to kill borer eggs"],
        "chemical": ["Install 5-10 pheromone (IB) traps per acre after monsoon to catch male moths", "Apply Fipronil 0.3% GR (10 kg/acre) near roots with light irrigation"],
        "timing": ["Start traps when monsoon slows and humidity is ~80%", "Apply Fipronil at 4-5 months before peak attack", "Use in moist soil so it reaches roots properly"]
    },
    "Leaf Footed Bug": {
        "cultural": ["Keep field and borders clean by removing weeds and wild grass", "Avoid excess urea; it makes plants soft and attracts pests"],
        "mechanical": ["Remove lower dry leaves to stop bugs hiding and laying eggs", "Pick and destroy young bugs by cutting leaves and dropping them in soapy water"],
        "biological": ["Protect birds, spiders, and other helpful insects by avoiding unnecessary chemical sprays", "Spray neem oil (1500 ppm, 1 L/acre) on young pests to stop growth"],
        "chemical": ["Malathion 50% EC: 300 ml/acre in 200 L water", "Chlorpyriphos + Cypermethrin: 300 ml/acre in 200 L water"],
        "timing": ["Spray at first sign of bugs or eggs; don't wait for damage", "Spray on leaves, especially underside and inside dense canopy", "Spray early morning (6-9 AM) or evening (4:30-6:30 PM)"]
    },
    "Mites": {
        "cultural": ["Give light, regular irrigation in summer to reduce mites", "Keep field clean by removing weeds", "Avoid excess urea to reduce sap-sucking pests"],
        "mechanical": ["Remove infected leaves early and destroy them outside the field", "Keep field borders clean from wild grasses"],
        "biological": ["Protect ladybugs and lacewings by avoiding strong pesticides", "Spray neem oil (1500 ppm, 1 L/acre) to control young mites naturally"],
        "chemical": ["Spiromesifen: 200 ml/acre in 200 L water (kills eggs and young mites)", "Propargite: 400 ml/acre in 200 L water (controls adult mites)", "Sulphur: 1 kg/acre in 200 L water (kills mites and improves plant health)"],
        "timing": ["Spray upward to reach underside of leaves where mites hide", "Start in April-June at first sign of white/red patches", "Spray early morning (6-9 AM) or evening (4:30-6:30 PM)"]
    },
    "Mosaic": {
        "cultural": ["Use only certified, disease-free seed canes", "Do not grow maize, sorghum, or millet near sugarcane (Aug-Nov)", "Keep field clean from wild grasses"],
        "mechanical": ["Remove infected plants with roots and bury them", "Clean tools with boiling water or disinfectant before use in other fields"],
        "biological": ["Use tissue culture plants (virus-free)", "Protect ladybugs and lacewings by avoiding heavy chemical sprays"],
        "chemical": ["Imidacloprid: 40 ml/acre in 200 L water (long protection)", "Dimethoate: 300 ml/acre in 200 L water (quick aphid control)"],
        "timing": ["Start in Aug-Nov when aphids or mosaic symptoms appear", "Spray whole plant, especially underside of leaves and inside canopy", "Spray early morning (6-9 AM) or evening (4:30-6:30 PM)"]
    },
    "Pokkah Boeng": {
        "cultural": ["Keep 4-5 feet spacing for good air flow", "Avoid excess urea in monsoon to reduce fungus attack", "Use only healthy seed canes from clean fields"],
        "mechanical": ["Remove infected plants and burn them", "Remove lower dry leaves to keep field clean and airy"],
        "biological": ["Spray Pseudomonas fluorescens (10 g/L water) before rains", "Treat seed canes in hot water (50°C for 2 hours) before planting"],
        "chemical": ["Carbendazim: 200 g/acre in 200 L water (internal fungal control)", "Copper oxychloride: 400 g/acre in 200 L water (leaf protection)"],
        "timing": ["Spray on young top leaves and inside leaf whorl", "Start in July at first sign or onset of rains; repeat after 15 days if needed", "Spray early morning (6-9 AM) or evening (4:30-6:30 PM)"]
    },
    "Pyrilla": {
        "cultural": ["Avoid excess urea; it attracts pests", "Keep 4-5 feet spacing for good air flow", "Keep field borders clean from weeds and wild grass"],
        "mechanical": ["Remove lower dry leaves in 5th-6th month to destroy Pyrilla eggs", "Remove and bury yellow grass-like infected plants"],
        "biological": ["Protect the natural wasp (Epiricania melanoleuca) that kills Pyrilla; avoid sprays when it is present", "Spray neem oil (1500 ppm, 1 L/acre) at early stage to repel insects"],
        "chemical": ["Dimethoate: 300 ml/acre in 200 L water for quick control", "Imidacloprid: 100 ml/acre in 200 L water for systemic control"],
        "timing": ["Spray underside of leaves and inside canopy", "Start at first sign of eggs or black sticky mold", "Spray early morning (6-9 AM) or evening (4:30-6:30 PM)"]
    },
    "Red Rot": {
        "cultural": ["Use only healthy seed canes from disease-free fields", "Rotate crops for 1-2 years after Red Rot infection", "Ensure good drainage; avoid waterlogging"],
        "mechanical": ["Remove infected plants with roots and bury them", "Apply 100-150 g lime in the pit after removal", "Do not take ratoon crop from infected fields"],
        "biological": ["Mix Trichoderma viride (1-2 kg) with 100 kg cow dung per acre and apply in soil", "Treat seed canes in hot water (50°C for 2 hours)"],
        "chemical": ["Carbendazim: 200 g in 200 L water, dip seed pieces for 10-15 min before planting", "Thiophanate Methyl: 300 g/acre in 200 L water for soil drenching"],
        "timing": ["Treat seed before planting", "Apply soil drench during early growth stage"]
    },
    "Scale Insect": {
        "cultural": ["Use only healthy seed canes from pest-free fields", "Avoid ratoon crop in heavily infested fields", "Avoid excess or late urea to prevent soft, pest-prone plants"],
        "mechanical": ["Remove lower dry leaves from 5th month to expose scale insects", "Cut and destroy heavily infested canes early"],
        "biological": ["Protect ladybugs and other helpful insects by avoiding unnecessary sprays"],
        "chemical": ["Malathion: 400 ml/acre in 200 L water after leaf stripping", "Imidacloprid: 100 ml/acre in 200 L water for systemic control", "Fish Oil Rosin Soap (FORS): 2 kg/acre in 200 L water to suffocate insects"],
        "timing": ["Spray directly on stalks and internodes", "Start in Sept-Oct when grey crust appears", "Spray early morning (6-9 AM) or evening (4:30-6:30 PM)"]
    },
    "Whiplash Smut": {
        "cultural": ["Use only healthy, certified seed canes", "Do not take ratoon crop from smut-affected fields", "Inspect field regularly (April-June) and remove infected plants early"],
        "mechanical": ["Cover smut whip with a bag, then cut it and destroy it safely", "Clean tools with boiling water or disinfectant after use"],
        "biological": ["Treat seed canes in hot water (50°C for 2 hours) before planting", "Use smut-resistant sugarcane varieties"],
        "chemical": ["Carbendazim: 200 g in 200 L water, soak seed pieces for 10-15 min before planting", "Propiconazole: 400 ml/acre in 200 L water, spray after removing smut whips"],
        "timing": ["Spray in May-June after removing smut whips", "Cover full canopy and top growing shoots", "Spray early morning (6-9 AM) or evening (4:30-6:30 PM)"]
    },
    "Wilt": {
        "cultural": ["Use only healthy, certified seed canes", "Do not take ratoon crop if disease is present", "Regularly inspect fields (April-June) and remove infected plants early"],
        "mechanical": ["Remove infected plants and destroy safely outside the field", "Clean tools with boiling water or disinfectant after use"],
        "biological": ["Treat seed canes in hot water (50°C for 2 hours) before planting", "Use wilt-resistant sugarcane varieties recommended locally"],
        "chemical": ["Carbendazim: 200 g in 200 L water, soak seed pieces for 10-15 min before planting", "Propiconazole: 400 ml/acre in 200 L water"],
        "timing": ["Spray in May-June", "Cover full plant, especially top growing shoots and leaves", "Spray early morning (6-9 AM) or evening (4:30-6:30 PM)"]
    },
    "Woolly Aphids": {
        "cultural": ["Keep 4-5 feet spacing for good air flow and sunlight", "Avoid excess urea to reduce soft, pest-prone leaves", "Keep field borders clean and avoid nearby aphid-host crops"],
        "mechanical": ["Remove lower old leaves from 5th month to stop aphid hiding", "Cut infected leaves early, bag them, and destroy (burn/bury)"],
        "biological": ["Encourage natural enemies like wasps, ladybugs, and predator insects to control aphids", "Avoid strong chemical sprays when beneficial insects are present"],
        "chemical": ["Dimethoate: 300 ml/acre in 200 L water (quick control)", "Imidacloprid: 100 ml/acre in 200 L water (systemic control)", "Thiamethoxam: 100 g/acre in 200 L water (strong control)"],
        "timing": ["Spray upward to target underside of leaves where aphids hide", "Start July-November at first white cotton patch appearance", "Spray early morning (6-9 AM) or evening (4:30-6:30 PM)"]
    },
    "Top Shoot Borer": {
        "cultural": ["Don't use too much urea in hot weather, it makes plants soft", "Use pest-resistant sugarcane varieties", "Keep field edges clean from weeds and grasses"],
        "mechanical": ["Remove and destroy dead hearts and damaged shoots", "Crush egg masses on leaves before they hatch", "Use light traps to catch adult moths", "Cut and remove heavily infested tops"],
        "biological": ["Release Trichogramma wasps regularly to kill pest eggs", "Protect helpful insects like ladybugs and spiders", "Use Bt spray for young larvae"],
        "chemical": ["Chlorantraniliprole 18.5% SC: 150 ml/acre in 200 L water", "Fipronil 0.3% GR: 10 kg/acre in leaf whorl", "Cartap Hydrochloride 4G: 10 kg/acre in leaf whorl", "Quinalphos 25% EC: 400 ml/acre in 200 L water"],
        "timing": ["Start checking crop from 3-4 months after planting", "Apply into leaf whorl (center top growth point)", "Spray when first pinholes or bunchy tops appear", "Spray early morning (6-9 AM) or evening (4:30-6:30 PM)"]
    },
    "White Grub": {
        "cultural": ["Plough deeply in summer to expose grubs to sun and birds", "Keep field clean by removing weeds and crop waste", "Give proper water; dry soil increases white grub attack"],
        "mechanical": ["Shake nearby trees in evening and collect beetles manually", "Use light traps during monsoon to catch adult beetles", "Remove and destroy badly damaged sugarcane clumps", "Do regular deep tillage to expose grubs to predators"],
        "biological": ["Use Metarhizium anisopliae in soil to kill grubs naturally", "Use Beauveria bassiana as soil bio-control", "Apply neem cake in root zone", "Protect birds and natural enemies"],
        "chemical": ["Fipronil 0.3% GR: 10 kg/acre near roots", "Chlorantraniliprole 0.4% GR: 4 kg/acre in root zone", "Imidacloprid 17.8% SL: 100 ml/acre soil drench", "Phorate 10G: 10 kg/acre in soil around plant base"],
        "timing": ["Start after first monsoon rains", "Apply near root zone", "Apply when yellowing or wilting starts", "Apply early morning (6-9 AM) or evening (4:30-6:30 PM)"]
    },
    "Mealy Bug": {
        "cultural": ["Keep field clean by removing weeds and nearby host plants", "Avoid excess urea; soft growth attracts mealy bugs", "Use healthy, pest-free seed canes", "Apply balanced potash for stronger plants"],
        "mechanical": ["Remove lower dry leaves where pests hide", "Remove and destroy heavily infested plants", "Control ants near field (they spread mealy bugs)", "Check field regularly and remove early infestation"],
        "biological": ["Protect ladybird beetles that eat mealy bugs", "Release Cryptolaemus beetles for control", "Spray neem oil (1500 ppm, 1 L/acre) on young pests", "Avoid harsh chemicals to save helpful insects"],
        "chemical": ["Imidacloprid: 100 ml/acre in 200 L water", "Thiamethoxam: 100 g/acre in 200 L water", "Buprofezin: 400 ml/acre in 200 L water", "Dimethoate: 300 ml/acre in 200 L water"],
        "timing": ["Start at first white cottony colonies", "Spray on nodes, leaf sheaths, and lower cane parts", "Repeat after 10-15 days if needed", "Spray early morning (6-9 AM) or evening (4:30-6:30 PM)"]
    },
    "Grasshopper": {
        "cultural": ["Keep field and borders clean from weeds and grasses", "Avoid excess urea, it attracts grasshoppers", "Plant at proper time to avoid peak pest season", "Clean crop residues after harvest"],
        "mechanical": ["Collect and destroy grasshoppers in early morning", "Use light traps at night to kill adults", "Use sweep nets in heavy attack areas", "Deep plough in summer to destroy eggs"],
        "biological": ["Protect birds, frogs, spiders, and other natural enemies", "Use Metarhizium anisopliae to kill grasshoppers naturally", "Use Beauveria bassiana against nymphs and adults", "Spray neem oil (1500 ppm, 1 L/acre) to repel insects"],
        "chemical": ["Lambda-cyhalothrin 5% EC: 100 ml/acre in 200 L water", "Quinalphos 25% EC: 400 ml/acre in 200 L water", "Chlorpyriphos 20% EC: 500 ml/acre in 200 L water", "Malathion 50% EC: 300 ml/acre in 200 L water"],
        "timing": ["Start at first sign of young grasshoppers", "Spray on leaves and field borders", "Target early nymph stage", "Spray early morning (6-9 AM) or evening (4:30-6:30 PM)"]
    },
    "Yellow Leaf Disease": {
        "cultural": ["Use only healthy, virus-free seed canes", "Do not take ratoon crop from infected fields", "Control aphids, they spread the disease", "Avoid too much urea; use enough potash"],
        "mechanical": ["Remove and destroy infected plants early", "Pull out badly infected clumps and remove from field", "Clean tools before using in another field", "Check crop every 10-15 days"],
        "biological": ["Use tissue culture plants (virus-free)", "Spray neem oil (1500 ppm, 1 L/acre) to control aphids", "Protect ladybugs and lacewings", "Use organic manure and biofertilizers"],
        "chemical": ["Imidacloprid: 40 ml/acre in 200 L water", "Dimethoate: 300 ml/acre in 200 L water", "Thiamethoxam: 100 g/acre in 200 L water", "Acetamiprid: 40 g/acre in 200 L water"],
        "timing": ["Start when aphids or yellowing first appears", "Spray both sides of leaves, especially underside", "Repeat after 10-15 days if needed", "Spray early morning (6-9 AM) or evening (4:30-6:30 PM)"]
    },
    "Orange Rust": {
        "cultural": ["Use rust-resistant sugarcane varieties", "Avoid excess urea; it increases disease risk", "Keep 4-5 feet spacing for good air flow", "Apply potash for stronger leaves and resistance"],
        "mechanical": ["Remove and destroy rust-infected leaves", "Strip lower dry leaves to improve air movement", "Remove and destroy heavily infected plants", "Clean field after harvest and remove old debris"],
        "biological": ["Spray Pseudomonas fluorescens (10 g/L water) on leaves", "Apply Trichoderma viride with FYM before planting", "Use hot water treatment (50°C for 2 hours) for seed canes", "Use organic manure to improve plant health"],
        "chemical": ["Azoxystrobin + Cyproconazole: 200 ml/acre in 200 L water", "Propiconazole: 400 ml/acre in 200 L water", "Difenoconazole: 150 ml/acre in 200 L water", "Hexaconazole: 400 ml/acre in 200 L water"],
        "timing": ["Start when first orange rust spots appear (July-Nov)", "Spray both sides of leaves, especially middle and lower canopy", "Repeat after 15 days if humidity continues", "Spray early morning (6-9 AM) or evening (4:30-6:30 PM)"]
    },
    "Leafscald": {
        "cultural": ["Use only disease-free seed canes", "Do not plant sugarcane again for one season after severe infection", "Keep field well-drained; avoid waterlogging", "Avoid excess urea and use enough potash"],
        "mechanical": ["Clean and disinfect all cutting tools before use", "Do not take ratoon crop from infected fields", "Remove and destroy infected plants immediately", "Inspect field regularly during rainy season"],
        "biological": ["Treat seed canes in hot water (50°C for 2 hours)", "Use tissue culture plants free from disease", "Apply FYM and biofertilizers to improve soil health", "Use resistant or tolerant varieties"],
        "chemical": ["Streptocycline: 25 g/acre in 200 L water", "Plantomycin: 100 g/acre in 200 L water", "Copper Oxychloride: 400 g/acre in 200 L water", "Copper Hydroxide: 500 g/acre in 200 L water"],
        "timing": ["Start monitoring from early growth stage", "Treat seed before planting", "Spray after first symptoms appear", "Repeat after 10-15 days if needed", "Spray early morning (6-9 AM) or evening (4:30-6:30 PM)"]
    }
}
