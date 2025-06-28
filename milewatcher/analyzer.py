import google.generativeai as genai
import os
import logging

logger = logging.getLogger(__name__)

class MileagePromotionChecker:
    """
    A class to check for mileage transfer promotions within text content using
    the Google Gemini API.
    """

    def __init__(self):
        """
        Initializes the MileagePromotionChecker with a Gemini model and API key.
        """
        self._api_key = os.getenv('GOOGLE_API_KEY')
        if not self._api_key:
            raise ValueError("Google Gemini API key not found. Please provide it or set the 'GOOGLE_API_KEY' environment variable.")

        genai.configure(api_key=self._api_key)
        self._model = genai.GenerativeModel('gemini-2.0-flash-lite')
        logger.debug(f"MileagePromotionCheck successfully configured")

    def _build_promo_detection_prompt(self, text_content: str, promo_description: str) -> str:
        """
        Constructs the prompt to be sent to the Gemini model for promotion detection
        with a customizable promotion description.

        Args:
            text_content (str): The text content to be analyzed.
            promo_description (str): A description of the promotion to search for.

        Returns:
            str: The formatted prompt.
        """
        # --- Gemini Prompt (Portuguese as requested, now with dynamic promotion description) ---
        prompt = f"""
Analise o seguinte conteúdo de texto e identifique se ele contém informações sobre: {promo_description}.
Por favor, retorne TRUE se houver tal promoção e FALSE caso contrário.
Se a promoção for encontrada, forneça também um breve sumário dos principais detalhes da promoção (por exemplo, período da promoção, bônus percentual, condições).

Conteúdo do texto:
---
{text_content}
---

Formato da resposta esperado:
Booleano: [TRUE/FALSE]
Sumário: [Sumário da promoção, se TRUE. Caso contrário, 'N/A']
        """
        logger.debug(f"Generated prompt: {prompt[:200]}...") # Log first 200 chars for brevity
        return prompt

    def _parse_gemini_response(self, gemini_raw_response: str) -> tuple[bool, str]:
        """
        Processes the raw text response from Gemini and extracts the boolean and summary.

        Args:
            gemini_raw_response (str): The raw text response from the Gemini model.

        Returns:
            tuple: (bool, str) - Boolean indicating if the promotion was found and the summary.
        """
        logger.debug(f"Parsing Gemini raw response: {gemini_raw_response.strip()[:200]}...")
        is_promo = False
        summary = "N/A"

        lines = gemini_raw_response.split('\n')
        for line in lines:
            if line.startswith("Booleano:"):
                is_promo_str = line.split(":", 1)[1].strip().upper()
                is_promo = (is_promo_str == "TRUE")
                logger.debug(f"Parsed boolean: {is_promo_str} -> {is_promo}")
            elif line.startswith("Sumário:"):
                summary = line.split(":", 1)[1].strip()
                logger.debug(f"Parsed summary: '{summary}'")
        return is_promo, summary

    def check_promotion(self, text_content: str, promo_description: str = "uma promoção de transferência de milhas do banco Itaú para a Latam") -> tuple[bool, str]:
        """
        Checks for a specific promotion within a given text content using the Gemini model.

        Args:
            text_content (str): The text string to be analyzed.
            promo_description (str): A description of the promotion to search for.
                                     Defaults to "uma promoção de transferência de milhas do banco Itaú para a Latam".

        Returns:
            tuple: (bool, str) - A boolean indicating if the promotion was found and a summary of the promotion.
        """
        logger.info("Starting promotion check.")
        if not self._model:
            logger.error("Gemini model is not initialized. API configuration might have failed earlier.")
            return False, "Gemini model not initialized. API configuration failed."

        try:
            # Build the prompt with the dynamic promotion description
            prompt = self._build_promo_detection_prompt(text_content, promo_description)

            # Count tokens before generating the response
            try:
                token_count_response = self._model.count_tokens(prompt)
                logger.info(f"Tokens in prompt: {token_count_response.total_tokens}")
            except Exception as e:
                logger.warning(f"Error counting tokens: {e}")

            logger.info("Calling Gemini API to generate content.")
            # Call the Gemini API
            gemini_response = self._model.generate_content(prompt)
            text_response = gemini_response.text
            logger.debug(f"Raw Gemini response received: {text_response.strip()[:200]}...")

            # Process the response
            is_promo, summary = self._parse_gemini_response(text_response)
            logger.info(f"Promotion check completed. Found: {is_promo}, Summary: '{summary}'")

            return is_promo, summary

        except Exception as e:
            logger.exception(f"An unexpected error occurred during promotion check: {e}")
            return False, f"An error occurred: {e}"

# --- Main Execution Block ---
if __name__ == "__main__":
    # Example usage with text strings
    promo_text_itaulatampass = """
    Grandes notícias para os clientes Itaú Personnalité! Somente nesta semana, transferindo seus pontos do programa Pão de Açúcar ou Sempre Presente para o Latam Pass, você ganha 40% de bônus! A promoção é válida de 05/06/2025 a 12/06/2025. Não perca essa chance de viajar mais! Termos e condições aplicáveis.
    """

    promo_text_golkilos = """
    Atenção, clientes Esfera! Bônus de 50% na transferência de pontos para a Smiles. Promoção válida de 10/07/2025 a 15/07/2025. Voe mais com a GOL!
    """

    no_promo_text = """
    Bem-vindo ao site do Itaú. Aqui você encontra todas as informações sobre seus investimentos, cartões de crédito e serviços bancários. Para mais detalhes, acesse sua conta.
    """

    try:
        # Instantiate the checker. It will try to get the API key from environment variable.
        # You can also pass the key directly: checker = MileagePromotionChecker(api_key="YOUR_API_KEY")
        checker = MileagePromotionChecker() # Uses default model 'gemini-2.0-flash-lite'
    except ValueError as e:
        print(f"Initialization error: {e}")
        print("Please set the GOOGLE_API_KEY environment variable or provide the API key directly.")
        exit()

    print("---")
    print("Analyzing text for Itaú to Latam Pass promotion:")
    found_promo, promo_summary = checker.check_promotion(promo_text_itaulatampass)
    print(f"Promotion found: {found_promo}")
    print(f"Promotion summary: {promo_summary}")
    print("---")

    print("\n---")
    print("Analyzing text for a different promotion (Esfera to Smiles):")
    # Pass a custom promotion description
    found_promo, promo_summary = checker.check_promotion(
        promo_text_golkilos,
        "uma promoção de transferência de pontos do programa Esfera para a Smiles"
    )
    print(f"Promotion found: {found_promo}")
    print(f"Promotion summary: {promo_summary}")
    print("---")

    print("\n---")
    print("Analyzing text without any promotion:")
    found_promo, promo_summary = checker.check_promotion(no_promo_text) # Uses default promo_description
    print(f"Promotion found: {found_promo}")
    print(f"Promotion summary: {promo_summary}")
    print("---")
