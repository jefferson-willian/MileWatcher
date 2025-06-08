import google.generativeai as genai
import os

def check_mileage_promo_from_text(text_content):
    """
    Uses Gemini to identify Itaú to Latam mileage promotions
    within a provided text string, and returns a boolean and a summary of the promotion, if found.
    Also shows the prompt's token count before generating the response.

    Args:
        text_content (str): The text string to be analyzed.

    Returns:
        tuple: (bool, str) - A boolean indicating if the promotion was found and a summary of the promotion.
    """
    try:
        # 1. Configure the Gemini API
        api_key = '<GEMINI-API-TOKEN>'
        if not api_key:
            return False, "Error: Google Gemini API key not found. Please set the 'GOOGLE_API_KEY' environment variable."
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel('gemini-2.0-flash-lite')

        # 2. Prompt for Gemini
        prompt = f"""
        Analise o seguinte conteúdo de texto e identifique se ele contém informações sobre uma promoção de transferência de milhas do banco Itaú para a Latam.
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

        # 3. Count tokens before generating the response
        try:
            token_count_response = model.count_tokens(prompt)
            print(f"Tokens in prompt: {token_count_response.total_tokens}")
        except Exception as e:
            print(f"Error counting tokens: {e}")

        # 4. Call the Gemini API
        gemini_response = model.generate_content(prompt)
        text_response = gemini_response.text

        # 5. Process the Gemini response
        is_promo = False
        summary = "N/A"

        lines = text_response.split('\n')
        for line in lines:
            if line.startswith("Booleano:"):
                is_promo_str = line.split(":", 1)[1].strip().upper()
                is_promo = (is_promo_str == "TRUE")
            elif line.startswith("Sumário:"):
                summary = line.split(":", 1)[1].strip()

        return is_promo, summary

    except Exception as e:
        return False, f"An error occurred: {e}"

if __name__ == "__main__":
    # Example usage with a text string
    text = """
    This is example text
    """

    print("Analyzing text:")
    found_promo, promo_summary = check_mileage_promo_from_text(text)
    print(f"Promotion found: {found_promo}")
    print(f"Promotion summary: {promo_summary}")
