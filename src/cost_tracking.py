# Estimates token counts and USD costs for display after each agent response.
# Uses tiktoken for counting rather than calling the API -- it's an estimate,
# not a billing-accurate figure, but close enough to show users what a session costs.

# prices are per 1,000 tokens, sourced from OpenRouter's published rates (May 2026)
PRICING = {
    # OpenRouter models
    "openai/gpt-4o-mini":                       {"input": 0.00015,  "output": 0.00060},
    "openai/gpt-4o":                            {"input": 0.00250,  "output": 0.01000},
    "anthropic/claude-haiku-4-5":               {"input": 0.00025,  "output": 0.00125},
    "google/gemini-2.0-flash-001":              {"input": 0.00010,  "output": 0.00040},
    "meta-llama/llama-3.3-70b-instruct:free":   {"input": 0.00000,  "output": 0.00000},
    # Ollama Cloud models -- billed directly to ollama.com account, not OpenRouter
    "gpt-oss:120b":                             {"input": 0.00000,  "output": 0.00000},
    "gpt-oss:20b":                              {"input": 0.00000,  "output": 0.00000},
    "gemma3:27b":                               {"input": 0.00000,  "output": 0.00000},
}


def estimate_tokens(text):
    """Count tokens using tiktoken cl100k_base encoding, with a len//4 fallback.

    cl100k_base is GPT-4's tokenizer -- close enough for all models we use.
    The fallback fires if tiktoken isn't installed or encoding fails; it's
    an undercount for short texts but good enough for a cost display.
    """
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        return len(text) // 4


def estimate_cost(input_text, output_text, model):
    """Return a cost estimate for one LLM call given the raw text strings.

    Unknown models default to zero cost rather than raising -- this keeps the
    UI working when a new model is added to the sidebar before its price is added here.
    """
    input_tokens = estimate_tokens(input_text)
    output_tokens = estimate_tokens(output_text)

    rates = PRICING.get(model, {"input": 0.0, "output": 0.0})
    cost = (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": round(cost, 6),
    }


if __name__ == "__main__":
    sample_input = "We are looking for an AI education specialist with bootcamp delivery experience."
    sample_output = (
        "Based on the retrieved evidence, the candidate has strong proof points for this "
        "role including the GenAI bootcamp at HIKE (hike_case_study.md) and the AI literacy "
        "curriculum described in application_examples.md."
    )

    print("Cost estimates for sample input/output:\n")
    for model in PRICING:
        result = estimate_cost(sample_input, sample_output, model)
        print(f"  {model}")
        print(
            f"    {result['input_tokens']} in . {result['output_tokens']} out . "
            f"${result['estimated_cost_usd']:.6f}"
        )
