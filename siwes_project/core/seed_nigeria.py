from core.models import State, LGA

def seed(): 
    data = {
        "Lagos": ["Ikeja", "Surulere", "Lekki", "Oshodi", "Badagry"],
        "Abuja (FCT)": ["Garki", "Wuse", "Maitama", "Asokoro", "Bwari"],
        "Ondo": ["Okitipupa", "Akure", "Ondo", "Ile-Oluji", "Ore"],
        "Oyo": ["Ibadan North", "Ibadan South", "Ogbomoso", "Oyo", "Iseyin"],
        "Rivers": ["Port Harcourt", "Obio-Akpor", "Eleme", "Ikwerre", "Bonny"],
    }

    for state_name, lgas in data.items():
        state, _ = State.objects.get_or_create(name=state_name)
        for lga_name in lgas:
            LGA.objects.get_or_create(state=state, name=lga_name)
        print(f"✓ {state_name} seeded")

    print("Done. ")
