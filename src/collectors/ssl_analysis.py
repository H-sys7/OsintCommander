import ssl
import socket
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from src.collectors.base import BaseCollector
from src.core.logger import logger

class SslCollector(BaseCollector):
    def run(self, target: str) -> list:
        logger.info(f"[SSL] Analyse du certificat pour : {target}")
        self.results = []

        # Nettoyage cible (on veut juste le domaine, pas https://)
        clean_target = target.replace("https://", "").replace("http://", "").split("/")[0]
        # On enlève le port s'il y en a un
        hostname = clean_target.split(":")[0]
        port = 443

        try:
            # Connexion Socket pour récupérer le certificat binaire
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    with socket.create_connection((hostname, port), timeout=10) as sock:
                        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                            der_cert = ssock.getpeercert(binary_form=True)
                    
                    if der_cert is not None:
                        cert = x509.load_der_x509_certificate(der_cert, default_backend())
                        # Extraction des infos
                        subject = cert.subject.rfc4514_string()

                    else:
                        raise ValueError("No certificate received from server.")
                  
            
            # Parsing avec Cryptography
            cert = x509.load_der_x509_certificate(der_cert, default_backend())
            
            # Extraction des infos
            subject = cert.subject.rfc4514_string()
            issuer = cert.issuer.rfc4514_string()
            not_before = cert.not_valid_before_utc
            not_after = cert.not_valid_after_utc
            
            # Calcul jours restants
            days_left = (not_after.replace(tzinfo=None) - datetime.utcnow()).days
            
            # Extraction des SANs (Subject Alternative Names) -> TRÈS IMPORTANT EN OSINT
            san_list = []
            try:
                ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
                san_list = ext.value.get_values_for_type(x509.DNSName)
            except:
                pass

            data = {
                "subject": subject,
                "issuer": issuer,
                "valid_from": not_before.strftime("%Y-%m-%d"),
                "valid_until": not_after.strftime("%Y-%m-%d"),
                "days_remaining": days_left,
                "sans_count": len(san_list),
                "sans": san_list[:20] # On garde les 20 premiers pour ne pas polluer
            }

            self.results.append({
                "source": "SSL_Analyzer",
                "type": "ssl_certificate",
                "value": clean_target,
                "details": data
            })
            
            # On envoie aussi les SANs comme sous-domaines découverts
            if san_list:
                self.results.append({
                    "source": "SSL_SANs",
                    "type": "subdomains_found",
                    "count": len(san_list),
                    "data": san_list
                })

            logger.info(f"[SSL] Certificat valide ({days_left} jours restants). {len(san_list)} sous-domaines trouvés.")

        except Exception as e:
            logger.error(f"[SSL] Erreur : {e}")
            self.results.append({"error": str(e)})

        return self.results