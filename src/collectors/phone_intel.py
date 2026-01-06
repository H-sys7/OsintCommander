import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from src.collectors.base import BaseCollector
from src.core.logger import logger

class PhoneCollector(BaseCollector):
    def run(self, target: str) -> list:
        logger.info(f"[PhoneIntel] Analyse approfondie du numéro : {target}")
        self.results = []

        try:
            parsed_number = phonenumbers.parse(target, None)

            if not phonenumbers.is_valid_number(parsed_number):
                self.results.append({"error": "Numéro invalide."})
                return self.results

            # Extraction de données
            country = geocoder.description_for_number(parsed_number, "fr")
            operator = carrier.name_for_number(parsed_number, "fr")
            time_zones = timezone.time_zones_for_number(parsed_number)
            
            # Type de ligne précis (Mobile, Fixe, VoIP...)
            n_type = phonenumbers.number_type(parsed_number)
            type_str = "Inconnu"
            risk_level = "Faible"
            risk_reason = "Numéro standard"

            if n_type == phonenumbers.PhoneNumberType.MOBILE:
                type_str = "Mobile"
            elif n_type == phonenumbers.PhoneNumberType.FIXED_LINE:
                type_str = "Fixe"
            elif n_type == phonenumbers.PhoneNumberType.VOIP:
                type_str = "VoIP (Voice over IP)"
                risk_level = "Moyen/Élevé"
                risk_reason = "Les numéros VoIP sont souvent utilisés pour l'anonymat ou les arnaques."
            elif n_type == phonenumbers.PhoneNumberType.TOLL_FREE:
                type_str = "Numéro Vert"
# ...existing code...

            # Structuration des données pour l'OSINT
            data = {
                "format_e164": phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164),
                "pays": country,
                "operateur": operator if operator else "Inconnu (ou portabilité)",
                "type_ligne": type_str,
                "timezone": list(time_zones),
                "analyse_risque": {
                    "niveau": risk_level,
                    "raison": risk_reason
                },
                "educatif": "En OSINT, l'opérateur peut indiquer l'ancienneté de la ligne. Le type VoIP nécessite une vigilance accrue."
            }

            self.results.append({
                "source": "PhoneInfoga_Lite",
                "type": "phone_intel_advanced",
                "value": target,
                "details": data
            })
            
            logger.info(f"[PhoneIntel] {type_str} - {country} - {operator}")

        except Exception as e:
            logger.error(f"[PhoneIntel] Erreur : {e}")
            self.results.append({"error": str(e)})

        return self.results