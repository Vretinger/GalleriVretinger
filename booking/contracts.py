from django.utils.translation import get_language
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

def get_contract_text(event, user):
    lang = get_language()

    # Safely handle your booking date fields
    start_date = getattr(event, "start_date", None)
    end_date = getattr(event, "end_date", None)

    start_str = start_date.strftime("%Y-%m-%d") if start_date else ("Ej angivet" if lang.startswith("sv") else "Not specified")
    end_str = end_date.strftime("%Y-%m-%d") if end_date else ("Ej angivet" if lang.startswith("sv") else "Not specified")

    if lang.startswith("sv"):
        # 🇸🇪 Swedish version
        return f"""
📄 Uthyrningsavtal – Galleri Vretinger

Mellan:
Uthyrare: Galleri Vretinger, Wallingatan 37, org.nr 750901
Hyresgäst (Utställare): [Namn], personnummer/org.nr, [adress]

§1. Hyresperiod & öppettider
Galleri Vretinger hyrs ut för konstutställning.
Hyresperiod: {start_str} – {end_str}

§2. Hyra och betalning
Pris: Enligt överenskommelse.
En betalning på 50% av kostnaden inom 3 dagar.
Hyran ska vara betald senast 14 dagar före utställningsstart.
Vid försenad betalning kan Galleri Vretinger avboka utställningen utan återbetalning.

§3. Avbokning
Vid avbokning tidigare än 14 dagar före hyresstart återbetalas 50% av hyran.
Vid senare avbokning sker ingen återbetalning.

§4. Ansvar och försäkring
Galleri Vretingers försäkring täcker inte konstnärens verk.
Utställaren ansvarar själv för eventuell försäkring.
All vistelse och förvaring sker på egen risk.

§5. Användning av lokalen
Lokalen får endast användas för konstutställning och försäljning.
Rökning är förbjuden. Dryck/förtäring ansvarar utställaren själv för.

§6. Skötsel, skador och återställning
Lokalen ska lämnas i rent skick. Städavgift 500 kr vid bristande städning.
Skador ersätts av utställaren.

§7. Försäljning
Galleri Vretinger tar ingen provision.

§8. Närvaro och marknadsföring
Galleri Vretinger marknadsför via sociala medier. Utställaren bidrar gärna med bilder.

§9. Underskrifter
Jag har läst, förstått och godkänner ovanstående villkor.

Ort och datum: ____________________________
Utställare: {user.get_full_name() or user.username}
Underskrift: _______________________________

Galleri Vretinger
Underskrift: _______________________________
        """
    else:
        # 🇬🇧 English
        return f"""
📄 Rental Agreement – Galleri Vretinger

Between:
Lessor: Galleri Vretinger, Wallingatan 37, org. no. 750901
Lessee (Exhibitor): [Name], personalnumber/org.nr, [address]

§1. Rental Period & Opening Hours
Galleri Vretinger is rented for art exhibitions.
Rental period: {start_str} – {end_str}

§2. Rent and Payment
Price: As agreed.
50% payment within 3 days.
Full rent must be paid 14 days before exhibition start.
Late payment may result in cancellation without refund.

§3. Cancellation
If cancelled more than 14 days before start: 50% refund.
Later cancellations are non-refundable.

§4. Liability and Insurance
Galleri Vretinger’s insurance does not cover the exhibitor’s works.
The exhibitor is responsible for their own insurance.
All presence and storage are at the exhibitor’s own risk.

§5. Use of the Venue
The venue may only be used for exhibitions and sales.
Smoking is prohibited. Any refreshments are the exhibitor’s responsibility.

§6. Care, Damage and Restoration
The venue must be left clean. Cleaning fee: 500 SEK if not properly cleaned.
Damages caused by the exhibitor must be compensated.

§7. Sales
Galleri Vretinger takes no commission on sales.

§8. Attendance and Marketing
Galleri Vretinger promotes the exhibition via social media. The exhibitor may provide materials.

§9. Signatures
I have read, understood, and accept the above terms.

Place and date: ____________________________
Exhibitor: {user.get_full_name() or user.username}
Signature: _______________________________

Galleri Vretinger
Signature: _______________________________
        """
